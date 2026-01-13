from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import errno
import shutil
import subprocess
import tempfile
import os
import sys

from markitdown import MarkItDown


@dataclass
class ConvertResult:
    success: bool
    input_path: Path
    output_path: Optional[Path] = None
    markdown: str = ""
    title: Optional[str] = None
    error: Optional[str] = None


class Any2MDConverter:
    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".doc",
        ".pptx",
        ".ppt",
        ".xlsx",
        ".xls",
        ".html",
        ".htm",
        ".xml",
        ".json",
        ".csv",
        ".txt",
        ".md",
        ".rtf",
        ".zip",
    }

    _soffice_cache: Optional[str] = None
    _powershell_cache: Optional[str] = None

    def __init__(self, enable_plugins: bool = False):
        self.md = MarkItDown(enable_plugins=enable_plugins)

    def _find_powershell(self) -> Optional[str]:
        if Any2MDConverter._powershell_cache is not None:
            return Any2MDConverter._powershell_cache or None
        result = shutil.which("pwsh") or shutil.which("powershell")
        Any2MDConverter._powershell_cache = result or ""
        return result

    def _find_soffice(self) -> Optional[str]:
        if Any2MDConverter._soffice_cache is not None:
            return Any2MDConverter._soffice_cache or None

        for env_key in ("ANY2MD_SOFFICE", "SOFFICE_PATH"):
            env_val = os.environ.get(env_key)
            if env_val:
                path = Path(env_val).expanduser()
                if path.exists():
                    Any2MDConverter._soffice_cache = str(path)
                    return Any2MDConverter._soffice_cache

        candidates = [shutil.which("soffice"), shutil.which("soffice.exe")]
        candidates.extend(
            [
                "/Applications/LibreOffice.app/Contents/MacOS/soffice",
                "/Applications/LibreOffice.app/Contents/MacOS/soffice.bin",
                "/usr/bin/soffice",
                "/usr/local/bin/soffice",
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            ]
        )
        for candidate in candidates:
            if not candidate:
                continue
            path = Path(candidate)
            if path.exists():
                Any2MDConverter._soffice_cache = str(path)
                return Any2MDConverter._soffice_cache
        Any2MDConverter._soffice_cache = ""
        return None

    def _convert_via_windows_com(self, input_path: Path, out_dir: Path) -> Path:
        input_path = Path(input_path)
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        powershell = self._find_powershell()
        if powershell is None:
            raise RuntimeError("未检测到 PowerShell，无法调用 Office/WPS 转换")

        suffix = input_path.suffix.lower()
        mapping = {
            ".doc": ("docx", 16, ["Word.Application", "kwps.Application"]),
            ".ppt": ("pptx", 24, ["PowerPoint.Application", "kwpp.Application"]),
            ".xls": ("xlsx", 51, ["Excel.Application", "ket.Application"]),
        }
        if suffix not in mapping:
            raise ValueError(f"Unsupported legacy suffix: {suffix}")

        target_ext, save_format, prog_ids = mapping[suffix]
        output_path = out_dir / f"{input_path.stem}.{target_ext}"

        prog_ids_ps = ",".join([f"'{p}'" for p in prog_ids])

        script = rf"""
$ErrorActionPreference = "Stop"
$in = "{str(input_path).replace('"', '""')}"
$out = "{str(output_path).replace('"', '""')}"
$format = {save_format}
$progIds = @({prog_ids_ps})

function TryConvertWord($app, $in, $out, $format) {{
  $app.Visible = $false
  try {{ $app.DisplayAlerts = 0 }} catch {{}}
  $doc = $app.Documents.Open($in, $false, $true)
  try {{
    try {{ $doc.SaveAs2($out, $format) }} catch {{ $doc.SaveAs($out, $format) }}
  }} finally {{
    $doc.Close($false) | Out-Null
  }}
}}

function TryConvertExcel($app, $in, $out, $format) {{
  $app.Visible = $false
  try {{ $app.DisplayAlerts = 0 }} catch {{}}
  $wb = $app.Workbooks.Open($in, $null, $true)
  try {{
    $wb.SaveAs($out, $format) | Out-Null
  }} finally {{
    $wb.Close($false) | Out-Null
  }}
}}

function TryConvertPowerPoint($app, $in, $out, $format) {{
  $app.Visible = $false
  try {{ $app.DisplayAlerts = 0 }} catch {{}}
  $pres = $app.Presentations.Open($in, $true, $true, $false)
  try {{
    $pres.SaveAs($out, $format) | Out-Null
  }} finally {{
    $pres.Close() | Out-Null
  }}
}}

$lastErr = $null
foreach ($pid in $progIds) {{
  try {{
    $app = New-Object -ComObject $pid
    try {{
      if ($format -eq 16) {{ TryConvertWord $app $in $out $format }}
      elseif ($format -eq 51) {{ TryConvertExcel $app $in $out $format }}
      else {{ TryConvertPowerPoint $app $in $out $format }}
    }} finally {{
      try {{ $app.Quit() | Out-Null }} catch {{}}
    }}
    if (Test-Path -LiteralPath $out) {{ exit 0 }}
    throw "Converted output not found: $out"
  }} catch {{
    $lastErr = $_
  }}
}}

if ($lastErr) {{ throw $lastErr }}
throw "Office/WPS conversion failed"
"""

        proc = subprocess.run(
            [powershell, "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            stdout = (proc.stdout or "").strip()
            raise RuntimeError(
                "Office/WPS 转换失败"
                + (f": {stderr}" if stderr else f": {stdout}" if stdout else "")
            )

        if not output_path.exists():
            raise RuntimeError("Office/WPS 转换未生成输出文件")
        return output_path

    def _prepare_output_dir(self, output_dir: Path) -> Path:
        output_dir = Path(output_dir)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            return output_dir
        except OSError as e:
            if e.errno in {errno.EROFS, errno.EACCES} and not output_dir.is_absolute():
                fallback = Path.home() / output_dir
                fallback.mkdir(parents=True, exist_ok=True)
                return fallback
            raise

    def can_convert(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def _convert_via_textutil(self, input_path: Path, out_dir: Path) -> Path:
        """macOS only: Convert .doc to .docx using textutil"""
        if shutil.which("textutil") is None:
            raise RuntimeError("textutil not found")

        input_path = Path(input_path)
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        output_path = out_dir / f"{input_path.stem}.docx"

        # textutil -convert docx input.doc -output output.docx
        cmd = [
            "textutil",
            "-convert",
            "docx",
            str(input_path),
            "-output",
            str(output_path),
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            stdout = (proc.stdout or "").strip()
            raise RuntimeError(f"textutil conversion failed: {stderr or stdout}")

        if output_path.exists():
            return output_path
        raise RuntimeError("textutil output not found")

    def _convert_via_soffice(self, input_path: Path, out_dir: Path) -> Path:
        input_path = Path(input_path)
        out_dir = Path(out_dir)
        suffix = input_path.suffix.lower()
        target_ext = {".doc": "docx", ".ppt": "pptx", ".xls": "xlsx"}[suffix]

        soffice = self._find_soffice()
        if soffice is None:
            raise RuntimeError(
                "未检测到 LibreOffice（soffice），无法转换旧格式文件；请先安装 LibreOffice，或设置环境变量 ANY2MD_SOFFICE 指向 soffice 可执行文件"
            )

        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            soffice,
            "--headless",
            "--nologo",
            "--nolockcheck",
            "--norestore",
            "--convert-to",
            target_ext,
            "--outdir",
            str(out_dir),
            str(input_path),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            stdout = (proc.stdout or "").strip()
            raise RuntimeError(
                "LibreOffice 转换失败"
                + (f": {stderr}" if stderr else f": {stdout}" if stdout else "")
            )

        expected = out_dir / f"{input_path.stem}.{target_ext}"
        if expected.exists():
            return expected

        matches = list(out_dir.glob(f"*.{target_ext}"))
        if matches:
            return matches[0]
        raise RuntimeError("LibreOffice 转换未生成输出文件")

    def _convert_xls_with_xlrd(self, input_path: Path) -> str:
        try:
            import xlrd  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "缺少 `xlrd`，请安装 `any2md[legacy]` 或安装 LibreOffice 后重试"
            ) from e

        book = xlrd.open_workbook(str(input_path))
        if book.nsheets == 0:
            return ""
        sheet = book.sheet_by_index(0)

        max_cols = sheet.ncols
        rows: list[list[str]] = []
        for r in range(sheet.nrows):
            row = []
            for c in range(max_cols):
                val = sheet.cell_value(r, c)
                row.append("" if val is None else str(val))
            rows.append(row)

        if not rows:
            return ""

        header = rows[0]
        body = rows[1:] if len(rows) > 1 else []
        lines = []
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * len(header)) + " |")
        for row in body:
            lines.append("| " + " | ".join(row) + " |")
        return "\n".join(lines) + "\n"

    def _write_markdown(
        self, markdown_content: str, input_path: Path, output_dir: Optional[Path]
    ) -> Optional[Path]:
        if not output_dir:
            return None
        output_dir = self._prepare_output_dir(output_dir)
        output_path = output_dir / f"{input_path.stem}.md"
        try:
            output_path.write_text(markdown_content, encoding="utf-8")
        except OSError as e:
            if e.errno in {errno.EROFS, errno.EACCES} and not output_dir.is_absolute():
                output_dir = self._prepare_output_dir(Path.home() / output_dir)
                output_path = output_dir / f"{input_path.stem}.md"
                output_path.write_text(markdown_content, encoding="utf-8")
            else:
                raise
        return output_path

    def convert_file(
        self, input_path: Path, output_dir: Optional[Path] = None
    ) -> ConvertResult:
        input_path = Path(input_path)

        if not input_path.exists():
            return ConvertResult(
                success=False, input_path=input_path, error=f"文件不存在: {input_path}"
            )

        if not self.can_convert(input_path):
            return ConvertResult(
                success=False,
                input_path=input_path,
                error=f"不支持的格式: {input_path.suffix}",
            )

        try:
            legacy_suffix = input_path.suffix.lower()
            if legacy_suffix in {".doc", ".ppt", ".xls"}:
                with tempfile.TemporaryDirectory(prefix="any2md_lo_") as td:
                    out_dir = Path(td)
                    try:
                        converted_path = self._convert_via_soffice(input_path, out_dir)
                    except Exception:
                        if sys.platform == "win32":
                            try:
                                converted_path = self._convert_via_windows_com(
                                    input_path, out_dir
                                )
                            except Exception:
                                converted_path = None
                        elif sys.platform == "darwin" and legacy_suffix == ".doc":
                            # macOS fallback: try textutil
                            try:
                                converted_path = self._convert_via_textutil(
                                    input_path, out_dir
                                )
                            except Exception:
                                converted_path = None
                        else:
                            converted_path = None

                    try:
                        if converted_path is None:
                            raise RuntimeError("No legacy converter available")
                        result = self.md.convert(str(converted_path))
                        markdown_content = result.text_content or ""
                        title = getattr(result, "title", None)
                    except Exception:
                        if legacy_suffix != ".xls":
                            msg = "未检测到可用的旧格式转换器："
                            if sys.platform == "win32":
                                msg += (
                                    "Windows 请安装 Microsoft Office/WPS 或 LibreOffice"
                                )
                            elif sys.platform == "darwin":
                                msg += "macOS 请安装 LibreOffice"
                                if legacy_suffix == ".doc":
                                    msg += " (textutil fallback 同时也失败)"
                            else:
                                msg += "Linux 请安装 LibreOffice"
                            raise RuntimeError(msg)
                        markdown_content = self._convert_xls_with_xlrd(input_path)
                        title = input_path.stem

                    output_path = self._write_markdown(
                        markdown_content, input_path, output_dir
                    )
                    return ConvertResult(
                        success=True,
                        input_path=input_path,
                        output_path=output_path,
                        markdown=markdown_content,
                        title=title,
                    )

            result = self.md.convert(str(input_path))
            markdown_content = result.text_content or ""
            title = getattr(result, "title", None)

            output_path = self._write_markdown(markdown_content, input_path, output_dir)

            return ConvertResult(
                success=True,
                input_path=input_path,
                output_path=output_path,
                markdown=markdown_content,
                title=title,
            )
        except Exception as e:
            return ConvertResult(success=False, input_path=input_path, error=str(e))

    def convert_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        recursive: bool = True,
        max_workers: int = 4,
    ) -> list[ConvertResult]:
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)

        pattern = "**/*" if recursive else "*"
        files_to_convert = [
            (file_path, output_dir / file_path.relative_to(input_dir).parent)
            for file_path in input_dir.glob(pattern)
            if file_path.is_file() and self.can_convert(file_path)
        ]

        if not files_to_convert:
            return []

        results: list[ConvertResult] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.convert_file, fp, od): fp
                for fp, od in files_to_convert
            }
            for future in as_completed(futures):
                results.append(future.result())

        return results

    def merge_markdown(
        self, results: list[ConvertResult], base_dir: Optional[Path]
    ) -> str:
        base_dir_path = Path(base_dir) if base_dir else None

        parts: list[str] = []
        parts.append("# Any2MD 合并文档\n")

        for r in results:
            if not r.success:
                continue
            try:
                rel = (
                    str(r.input_path.relative_to(base_dir_path))
                    if base_dir_path is not None
                    else r.input_path.name
                )
            except Exception:
                rel = r.input_path.name

            parts.append(f"\n---\n\n## {rel}\n")
            if r.title:
                parts.append(f"\n**标题**：{r.title}\n")
            parts.append("\n")
            parts.append((r.markdown or "").rstrip() + "\n")

        return "".join(parts)

    def write_merged_markdown(
        self, results: list[ConvertResult], merged_path: Path, base_dir: Optional[Path]
    ) -> Path:
        merged_path = Path(merged_path)
        merged_path.parent.mkdir(parents=True, exist_ok=True)
        content = self.merge_markdown(results=results, base_dir=base_dir)
        merged_path.write_text(content, encoding="utf-8")
        return merged_path

from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import errno
import shutil
import subprocess
import tempfile
import os

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

    def __init__(self, enable_plugins: bool = False):
        self.md = MarkItDown(enable_plugins=enable_plugins)

    def _find_soffice(self) -> Optional[str]:
        for env_key in ("ANY2MD_SOFFICE", "SOFFICE_PATH"):
            env_val = os.environ.get(env_key)
            if env_val:
                path = Path(env_val).expanduser()
                if path.exists():
                    return str(path)

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
                return str(path)
        return None

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
                        result = self.md.convert(str(converted_path))
                        markdown_content = result.text_content or ""
                        title = getattr(result, "title", None)
                    except Exception:
                        if legacy_suffix != ".xls":
                            raise
                        markdown_content = self._convert_xls_with_xlrd(input_path)
                        title = input_path.stem
                    output_path = None
                    if output_dir:
                        output_dir = self._prepare_output_dir(output_dir)
                        output_path = output_dir / f"{input_path.stem}.md"
                        try:
                            output_path.write_text(markdown_content, encoding="utf-8")
                        except OSError as e:
                            if (
                                e.errno in {errno.EROFS, errno.EACCES}
                                and not output_dir.is_absolute()
                            ):
                                output_dir = self._prepare_output_dir(
                                    Path.home() / output_dir
                                )
                                output_path = output_dir / f"{input_path.stem}.md"
                                output_path.write_text(
                                    markdown_content, encoding="utf-8"
                                )
                            else:
                                raise
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

            output_path = None
            if output_dir:
                output_dir = self._prepare_output_dir(output_dir)
                output_path = output_dir / f"{input_path.stem}.md"
                try:
                    output_path.write_text(markdown_content, encoding="utf-8")
                except OSError as e:
                    if (
                        e.errno in {errno.EROFS, errno.EACCES}
                        and not output_dir.is_absolute()
                    ):
                        output_dir = self._prepare_output_dir(Path.home() / output_dir)
                        output_path = output_dir / f"{input_path.stem}.md"
                        output_path.write_text(markdown_content, encoding="utf-8")
                    else:
                        raise

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
        self, input_dir: Path, output_dir: Path, recursive: bool = True
    ) -> list[ConvertResult]:
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        results = []

        pattern = "**/*" if recursive else "*"
        for file_path in input_dir.glob(pattern):
            if file_path.is_file() and self.can_convert(file_path):
                rel_path = file_path.relative_to(input_dir)
                file_output_dir = output_dir / rel_path.parent
                result = self.convert_file(file_path, file_output_dir)
                results.append(result)

        return results

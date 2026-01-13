from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import errno

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

        if input_path.suffix.lower() in {".doc", ".ppt", ".xls"}:
            return ConvertResult(
                success=False,
                input_path=input_path,
                error=(
                    f"暂不支持旧格式 {input_path.suffix}，请另存为 "
                    ".docx/.pptx/.xlsx 后再转换"
                ),
            )

        try:
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

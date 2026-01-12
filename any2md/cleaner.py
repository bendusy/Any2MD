import re
from pathlib import Path
from typing import Optional


class FilenameCleaner:
    ILLEGAL_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
    MULTIPLE_SPACES_PATTERN = re.compile(r"\s+")
    MULTIPLE_UNDERSCORES_PATTERN = re.compile(r"_+")

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {
            "remove_special_chars": True,
            "replace_spaces_with": "_",
            "lowercase": False,
            "max_length": 200,
        }

    def clean(self, filename: str) -> str:
        name = Path(filename).stem
        ext = Path(filename).suffix

        if self.config.get("remove_special_chars", True):
            name = self.ILLEGAL_CHARS_PATTERN.sub("", name)

        name = self.MULTIPLE_SPACES_PATTERN.sub(" ", name).strip()

        replace_char = self.config.get("replace_spaces_with", "_")
        if replace_char:
            name = name.replace(" ", replace_char)
            if replace_char == "_":
                name = self.MULTIPLE_UNDERSCORES_PATTERN.sub("_", name)

        if self.config.get("lowercase", False):
            name = name.lower()

        max_length = self.config.get("max_length", 200)
        if len(name) > max_length:
            name = name[:max_length]

        return f"{name}{ext}"

    def clean_path(self, file_path: Path) -> Path:
        cleaned_name = self.clean(file_path.name)
        return file_path.parent / cleaned_name

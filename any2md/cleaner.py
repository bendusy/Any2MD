import re
from pathlib import Path
from typing import Optional


class FilenameCleaner:
    ILLEGAL_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
    MULTIPLE_SPACES_PATTERN = re.compile(r"\s+")
    MULTIPLE_UNDERSCORES_PATTERN = re.compile(r"_+")

    def __init__(self, config: Optional[dict] = None):
        config = config or {}
        self._remove_special_chars = config.get("remove_special_chars", True)
        self._replace_spaces_with = config.get("replace_spaces_with", "_")
        self._lowercase = config.get("lowercase", False)
        self._max_length = config.get("max_length", 200)

    def clean(self, filename: str) -> str:
        name, dot, ext = filename.rpartition(".")
        if not dot:
            name = filename
            ext = ""
        else:
            ext = dot + ext

        if self._remove_special_chars:
            name = self.ILLEGAL_CHARS_PATTERN.sub("", name)

        name = self.MULTIPLE_SPACES_PATTERN.sub(" ", name).strip()

        if self._replace_spaces_with:
            name = name.replace(" ", self._replace_spaces_with)
            if self._replace_spaces_with == "_":
                name = self.MULTIPLE_UNDERSCORES_PATTERN.sub("_", name)

        if self._lowercase:
            name = name.lower()
            ext = ext.lower()

        if len(name) > self._max_length:
            name = name[: self._max_length]

        return f"{name}{ext}"

    def clean_path(self, file_path: Path) -> Path:
        cleaned_name = self.clean(file_path.name)
        return file_path.parent / cleaned_name

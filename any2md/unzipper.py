import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional


_MOJIBAKE_HINT_CHARS = set("╬║═╔╦╩╚╠╣╧╨╤┐┘┌└─│▒▓░╪╫╘╛╒╓╜╞╟╢╖╕╝╗")


def _decode_legacy_zip_name(name: str) -> str:
    if not name:
        return name
    if name.isascii():
        return name
    if not any(ch in _MOJIBAKE_HINT_CHARS for ch in name):
        return name
    try:
        raw = name.encode("cp437")
        return raw.decode("gbk")
    except Exception:
        return name


def _safe_join(root: Path, relative: str) -> Path:
    root_resolved = root.resolve()
    dest = (root / relative).resolve()
    try:
        dest.relative_to(root_resolved)
    except ValueError as e:
        raise ValueError(f"Unsafe zip path: {relative}") from e
    return dest


class Unzipper:
    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir
        self._temp_dirs: list[Path] = []

    def is_zip(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".zip" and zipfile.is_zipfile(file_path)

    def extract(self, zip_path: Path, output_dir: Optional[Path] = None) -> Path:
        zip_path = Path(zip_path)

        if output_dir is None:
            temp = tempfile.mkdtemp(prefix="any2md_")
            output_dir = Path(temp)
            self._temp_dirs.append(output_dir)
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            for info in zf.infolist():
                decoded_name = _decode_legacy_zip_name(info.filename)
                dest_path = _safe_join(output_dir, decoded_name)

                if info.is_dir():
                    dest_path.mkdir(parents=True, exist_ok=True)
                    continue

                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info, "r") as src, dest_path.open("wb") as dst:
                    shutil.copyfileobj(src, dst)

        return output_dir

    def extract_recursive(
        self, zip_path: Path, output_dir: Optional[Path] = None
    ) -> Path:
        extracted_dir = self.extract(zip_path, output_dir)

        for nested_zip in extracted_dir.rglob("*.zip"):
            if zipfile.is_zipfile(nested_zip):
                nested_output = nested_zip.parent / nested_zip.stem
                self.extract_recursive(nested_zip, nested_output)
                nested_zip.unlink()

        return extracted_dir

    def cleanup(self) -> None:
        for temp_dir in self._temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        self._temp_dirs.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

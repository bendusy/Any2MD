from __future__ import annotations

import shutil
import sys
from pathlib import Path

REMOVABLE_DIRS = ("translations", "qml")
KEEP_PLUGINS = {"platforms", "styles", "imageformats", "iconengines"}


def _remove(path: Path) -> bool:
    if not path.exists() and not path.is_symlink():
        return False
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    return True


def _find_contents_dir(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        if parent.name == "Contents" and parent.is_dir():
            return parent
    return None


def _prune_dirs(qt6_dir: Path) -> int:
    count = 0
    for name in REMOVABLE_DIRS:
        if _remove(qt6_dir / name):
            count += 1
    plugins = qt6_dir / "plugins"
    if plugins.is_dir():
        for child in plugins.iterdir():
            if child.is_dir() and child.name not in KEEP_PLUGINS:
                if _remove(child):
                    count += 1
    return count


def prune_qt(qt_root: Path) -> None:
    qt_root = qt_root.resolve()
    if not qt_root.exists():
        raise SystemExit(f"Path not found: {qt_root}")

    if qt_root.is_dir() and qt_root.name != "Qt6":
        matches = list(qt_root.glob("**/PyQt6/Qt6"))
        if matches:
            qt_root = matches[0].resolve()
        else:
            raise SystemExit(f"Qt root not found under: {qt_root}")

    total = _prune_dirs(qt_root)

    contents_dir = _find_contents_dir(qt_root)
    if contents_dir:
        for subdir in ("Frameworks", "Resources"):
            alt_qt6 = contents_dir / subdir / "PyQt6" / "Qt6"
            if alt_qt6.exists() and alt_qt6 != qt_root:
                total += _prune_dirs(alt_qt6)

    print(f"Pruned {total} items from Qt6")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "Usage: python scripts/prune_qt.py <QtRootDir|AppRootDir>", file=sys.stderr
        )
        return 2
    prune_qt(Path(argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def _remove_if_exists(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path, ignore_errors=True)


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

    # Low-risk removals that typically save space.
    _remove_if_exists(qt_root / "translations")
    _remove_if_exists(qt_root / "qml")

    plugins = qt_root / "plugins"
    if plugins.is_dir():
        keep = {"platforms", "styles", "imageformats", "iconengines"}
        for child in plugins.iterdir():
            if child.is_dir() and child.name not in keep:
                _remove_if_exists(child)


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

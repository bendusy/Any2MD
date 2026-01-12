from __future__ import annotations

import importlib


def run_gui() -> None:
    """
    GUI entrypoint.

    Kept import-light so `any2md` can be installed without GUI deps (`any2md[gui]`).
    """
    try:
        gui_app = importlib.import_module("any2md.gui_app")
        gui_app.run_gui()
    except ImportError as e:
        raise SystemExit(
            "GUI 依赖未安装：请使用 `pip install 'any2md[gui]'` 后再运行 GUI。\n"
            f"{e}"
        ) from e

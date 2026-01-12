# -*- mode: python ; coding: utf-8 -*-

from __future__ import annotations

from pathlib import Path


def _read_project_version() -> str:
    try:
        import tomllib  # py>=3.11

        candidates = [
            Path.cwd() / "pyproject.toml",
            Path(__file__).resolve().with_name("pyproject.toml"),
        ]
        pyproject_path = next((p for p in candidates if p.exists()), None)
        if pyproject_path is None:
            return "0.0.0"

        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
        return str(data["project"]["version"])
    except Exception:
        return "0.0.0"


_VERSION = _read_project_version()
_BUNDLE_ID = "com.dustbinchen.any2md"

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('README.md', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Any2MD',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['docs/icon.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Any2MD',
)
app = BUNDLE(
    coll,
    name='Any2MD.app',
    icon='docs/icon.png',
    bundle_identifier=_BUNDLE_ID,
    info_plist={
        "CFBundleDisplayName": "Any2MD",
        "CFBundleName": "Any2MD",
        "CFBundleShortVersionString": _VERSION,
        "CFBundleVersion": _VERSION,
        "NSHighResolutionCapable": True,
    },
)

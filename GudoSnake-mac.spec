# -*- mode: python ; coding: utf-8 -*-
# Build on macOS: bash scripts/build-mac.sh

import os

icon_path = "assets/icon.icns"
if not os.path.isfile(icon_path):
    icon_path = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("color/colors.yaml", "color"),
        ("assets/monster.jpg", "assets"),
    ],
    hiddenimports=["pygame", "yaml", "color", "color.get_color"],
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
    name="GudoSnake",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="GudoSnake",
)

app = BUNDLE(
    coll,
    name="GudoSnake.app",
    icon=icon_path,
    bundle_identifier="com.gudosnake.app",
    info_plist={
        "CFBundleDisplayName": "Gudo Snake",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1.0.0",
        "NSHighResolutionCapable": True,
    },
)

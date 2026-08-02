# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ["gui.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("Crystal.mp3", "."),
        ("config.json", "."),
    ],
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
    name="ZaraStockChecker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
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
    name="ZaraStockChecker",
)

app = BUNDLE(
    coll,
    name="ZaraStockChecker.app",
    icon=None,
    bundle_identifier=None,
)

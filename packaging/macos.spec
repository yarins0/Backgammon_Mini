# -*- mode: python ; coding: utf-8 -*-
# macOS — app bundle build
# Produces dist/BackgammonAI.app — a standard Mac application bundle.
# Must be built on a Mac (PyInstaller only targets the OS it runs on).
# Build: python -m PyInstaller packaging/macos.spec
import os
from PyInstaller.utils.hooks import collect_all

ROOT = os.path.dirname(SPECPATH)

datas = [(os.path.join(ROOT, 'HeuristicNets', '*.pth'), 'HeuristicNets/')]
binaries = []
hiddenimports = ['torch']
tmp_ret = collect_all('torch')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    [os.path.join(ROOT, 'run.py')],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='BackgammonAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX is not recommended on macOS
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
    upx=False,
    upx_exclude=[],
    name='BackgammonAI',
)
app = BUNDLE(
    coll,
    name='BackgammonAI.app',
    icon=None,  # Replace with 'packaging/icon.icns' if you add a Mac icon
    bundle_identifier='com.yarins0.backgammon',
)

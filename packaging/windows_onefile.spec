# -*- mode: python ; coding: utf-8 -*-
# Windows — single-file build
# Produces one portable BackgammonAI.exe that works from any directory.
# First launch is slow (~60s) while PyTorch extracts to a temp folder.
# Build: python -m PyInstaller packaging/windows_onefile.spec
import os
from PyInstaller.utils.hooks import collect_all

# SPECPATH is the directory containing this spec file (packaging/).
# ROOT is the project root one level up.
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
    a.binaries,
    a.datas,
    name='BackgammonAI',
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

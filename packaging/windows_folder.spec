# -*- mode: python ; coding: utf-8 -*-
# Windows — folder build
# Distributes as a zip of the entire output folder.
# Users extract the zip and run BackgammonAI.exe from inside it.
# Build: python -m PyInstaller packaging/windows_folder.spec
import os
from PyInstaller.utils.hooks import collect_all

# SPECPATH is the directory containing this spec file (packaging/).
# ROOT is the project root one level up.
ROOT = os.path.dirname(SPECPATH)

datas = [(os.path.join(ROOT, 'HeuristicNets', '*.pth'), 'HeuristicNets/')]
# Place python313.dll next to the exe so Windows finds it regardless of
# which directory the user launches from (Windows checks the exe's own
# directory first in its DLL search order).
binaries = [('C:/Python313/python313.dll', '.')]
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
    runtime_hooks=[os.path.join(SPECPATH, 'hooks', 'rthook_dlldir.py')],
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
    name='BackgammonAI',
    contents_directory='.',
)

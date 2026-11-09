# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['tape_master_studio.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['core', 'gui', 'serial', 'serial.tools.list_ports', 'pyqtgraph', 'scipy', 'scipy.signal'],
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
    [],
    name='Tape_Master_Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

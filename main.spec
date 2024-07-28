# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('settings.ini', '.'), ('icon.ico', '.')],
    hiddenimports=['yt_dlp', 'customtkinter', 'tkinter', 'configparser', 'threading', 're'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='最強無敵スーパーウルトラ神神神ダウンローダー',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='最強無敵スーパーウルトラ神神神ダウンローダー',
)

app = BUNDLE(
    coll,
    name='最強無敵スーパーウルトラ神神神ダウンローダー',
    icon='icon.ico',
    onefile=True,
)

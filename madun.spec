# -*- mode: python ; coding: utf-8 -*-

# ── 主程序 ──
main = Analysis(
    ['madun.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('settings_window.py', '.'),
        ('dataguard_settings.html', '.'),
        ('icon.png', '.'),
        ('icon_clean.png', '.'),
        ('madun.icns', '.'),
    ],
    hiddenimports=['rumps'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
main_pyz = PYZ(main.pure)
main_exe = EXE(
    main_pyz,
    main.scripts,
    [],
    exclude_binaries=True,
    name='码盾MaDun',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)

# ── 设置窗口（独立 .app）──
settings = Analysis(
    ['settings_window.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter', 'tkinter.font'],
    hookspath=[],
    runtime_hooks=[],
    excludes=['rumps'],
    noarchive=False,
)
settings_pyz = PYZ(settings.pure)
settings_exe = EXE(
    settings_pyz,
    settings.scripts,
    [],
    exclude_binaries=True,
    name='码盾设置',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)
settings_coll = COLLECT(
    settings_exe,
    settings.binaries,
    settings.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='码盾设置',
)
settings_app = BUNDLE(
    settings_coll,
    name='码盾设置.app',
    icon='madun.icns',
    bundle_identifier='com.madun.settings',
    info_plist={
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
    },
)

# ── 主程序 App ──
main_coll = COLLECT(
    main_exe,
    main.binaries,
    main.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='码盾MaDun',
)

app = BUNDLE(
    main_coll,
    name='码盾 MaDun.app',
    icon='madun.icns',
    bundle_identifier='com.madun.app',
    info_plist={
        'LSUIElement': True,
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIconFile': 'madun',
        'CFBundleName': '码盾',
        'CFBundleDisplayName': '码盾 MaDun',
        'LSEnvironment': {
            'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin',
            'PYTHONHOME': '/Library/Frameworks/Python.framework/Versions/Current',
        },
    },
)

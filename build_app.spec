# -- mode: python ; coding: utf-8 --

APP_NAME = "EDO Analyzer"

block_cipher = None
added_files = [
                ('.\\logo.ico', '.'),
]

a = Analysis(['.\\edo_analyzer.py'],
             pathex=[],
             binaries=[],
             datas=added_files,
             hiddenimports=['pyarrow.vendored.version', 'matplotlib.backends.backend_tkagg'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name=APP_NAME,
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon='.\\logo.ico')


# a.datas += Tree(".\\..\\qml\\Media\\Videos", prefix="qml\\Media\\Videos")
# a.datas += [(".\\app\\frontend\\sm_activation.scxml",   ".\\..\\app\\frontend\\sm_activation.scxml", "DATA")]

# coll = COLLECT(exe,
#                a.binaries,
#                a.zipfiles,
#                a.datas,
#                strip=None,
#                upx=False,
#                name=APP_NAME)

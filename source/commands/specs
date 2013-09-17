# -*- mode: python -*-
a = Analysis(['./source/commands/cba_main.py'],
             pathex=['/Users/rabshakeh/workspace/cryptobox/cryptobox_app'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'cba_main'),
          debug=False,
          strip=None,
          upx=False,
          console=True )

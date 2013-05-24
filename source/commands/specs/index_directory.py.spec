# -*- mode: python -*-
a = Analysis(['./source/commands/index_directory.py.py'],
             pathex=['/Users/rabshakeh/workspace/cryptobox/cryptobox_app'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'index_directory.py'),
          debug=False,
          strip=None,
          upx=False,
          console=True )

#!/bin/sh
rm -Rf ./build
python3 setup.py build
python3 setup.py bdist_mac --iconfile="app.icns"
cp ./Resources/* ./build/Cryptobox-1.app/Contents/Resources

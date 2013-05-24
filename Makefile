package:
	cp ../www_cryptobox_nl/source/js/app_basic.min.js ./Cryptobox/js/
	rm -rf ./build
	mkdir ./build	
	cp -r ./node-webkit.app build/Cryptobox.app
	cp resource/app.icns build/Cryptobox.app/Contents/Resources/nw.icns
	mkdir ./build/Cryptobox.app/Contents/Resources/app.nw/
	cp -r ./Cryptobox/* ./build/Cryptobox.app/Contents/Resources/app.nw/	
	hdiutil create /tmp/tmp.dmg -ov -volname "Cryptobox" -fs HFS+ -srcfolder "./build/" 
	hdiutil convert /tmp/tmp.dmg -format UDZO -o ./build/Cryptobox.dmg
	rm /tmp/tmp.dmg

run:
	cp ../www_cryptobox_nl/source/js/app_basic.min.js ./Cryptobox/js/
	./node-webkit.app/Contents/MacOS/node-webkit Cryptobox/

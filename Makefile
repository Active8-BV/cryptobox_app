all:
	coffee -c -b ./source/cryptobox.coffee;
	mv ./source/cryptobox.js ./Cryptobox
	./buildcommands.sh cba_main
	cp ../www_cryptobox_nl/source/js/app_basic.min.js ./Cryptobox/js/
	rm -Rf ./build
	mkdir ./build
	cp -r ./node-webkit.app build/Cryptobox.app
	cp Cryptobox/app.icns build/Cryptobox.app/Contents/Resources/nw.icns
	mkdir ./build/Cryptobox.app/Contents/Resources/app.nw/
	cp -r ./Cryptobox/* ./build/Cryptobox.app/Contents/Resources/app.nw/
	hdiutil create /tmp/tmp.dmg -ov -volname "Cryptobox" -fs HFS+ -srcfolder "./build/"
	hdiutil convert /tmp/tmp.dmg -format UDZO -o ./build/Cryptobox.dmg
	rm /tmp/tmp.dmg

app: 
	cp ../www_cryptobox_nl/source/js/app_basic.min.js ./Cryptobox/js/
	rm -Rf ./build
	mkdir ./build
	cp -r ./node-webkit.app build/Cryptobox.app
	cp Cryptobox/app.icns build/Cryptobox.app/Contents/Resources/nw.icns
	mkdir ./build/Cryptobox.app/Contents/Resources/app.nw/
	cp -r ./Cryptobox/* ./build/Cryptobox.app/Contents/Resources/app.nw/

package:
	cp ../www_cryptobox_nl/source/js/app_basic.min.js ./Cryptobox/js/
	rm -Rf ./build
	mkdir ./build
	cp -r ./node-webkit.app build/Cryptobox.app
	cp Cryptobox/app.icns build/Cryptobox.app/Contents/Resources/nw.icns
	mkdir ./build/Cryptobox.app/Contents/Resources/app.nw/
	cp -r ./Cryptobox/* ./build/Cryptobox.app/Contents/Resources/app.nw/
	hdiutil create /tmp/tmp.dmg -ov -volname "Cryptobox" -fs HFS+ -srcfolder "./build/"
	hdiutil convert /tmp/tmp.dmg -format UDZO -o ./build/Cryptobox.dmg
	rm /tmp/tmp.dmg

run:
	cp ../www_cryptobox_nl/source/js/app_basic.min.js ./Cryptobox/js/
	python run_node_webkit_cryptobox.py


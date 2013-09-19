rm app.nw   
mkdir app
cd app 
cp -r ../Cryptobox/ .
cd ..
zip -r app.zip ./app
#rm -Rf ./app
mv app.zip app.nw
#./node-webkit.app/Contents/MacOS/node-webkit app.nw

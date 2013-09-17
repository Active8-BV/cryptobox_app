cd ../../
coffee -c -b ./source/cryptobox.coffee; mv ./source/cryptobox.js ./Cryptobox
./node-webkit.app/Contents/MacOS/node-webkit Cryptobox/ &
cd source/commands  


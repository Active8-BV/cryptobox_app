killall Python
killall python
source ./PYENV/bin/activate
export path_to_sdk=~/Library/Application\ Support/TideSDK/sdk/osx/1.3.1-beta/

# make sure directories exist
rm -Rf "./Cryptobox/packages/osx"
mkdir -p "./Cryptobox/packages/osx/bundle"


# dmg with app package within
python "$path_to_sdk/tidebuilder.py" -p -n -t bundle -d "Cryptobox/packages/osx/bundle" -o "osx" "Cryptobox/"

mv ./Cryptobox/packages/osx/bundle/Cryptobox.dmg ./dist
mv ./Cryptobox/packages/osx/bundle/Cryptobox.app/ ./dist


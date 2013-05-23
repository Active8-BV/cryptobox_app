source ./PYENV/bin/activate
export path_to_sdk=~/Library/Application\ Support/TideSDK/sdk/osx/1.3.1-beta/

# click-to-run
rm -Rf "./Cryptobox/packages/osx/run"
mkdir -p "Cryptobox/packages/osx/run"

python "$path_to_sdk/tidebuilder.py" -r -t bundle -d "Cryptobox/packages/osx/run" -o "osx" "Cryptobox/"

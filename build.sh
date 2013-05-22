
export path_to_sdk=~/Library/Application\ Support/TideSDK/sdk/osx/1.3.1-beta/

# make sure directories exist
#mkdir -p "Cryptobox/packages/osx/network"
#mkdir -p "Cryptobox/packages/osx/bundle"

# dmg with app package within
#/usr/bin/python "$path_to_sdk/tidebuilder.py" -p -n -t network -d "packages/osx/network" -o "osx" "Cryptobox/"
#/usr/bin/python "$path_to_sdk/tidebuilder.py" -p -n -t bundle -d "packages/osx/bundle" -o "osx" "Cryptobox/"

# click-to-run
mkdir -p "Cryptobox/packages/osx/run"
/usr/bin/python "$path_to_sdk/tidebuilder.py" -r -t network -d "Cryptobox/packages/osx/run" -o "osx" "Cryptobox/"

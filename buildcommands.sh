
rm ./build/$1/*.pyz
rm ./dist/$1
rm ./Cryptobox/Resources/$1
echo "building", ./source/commands/$1.py
python ./pyinstaller-2.0/pyinstaller.py --onefile --console --noupx ./source/commands/$1.py
mv $1.spec ./source/commands/specs
mkdir -p ./Cryptobox/commands
cp ./dist/$1 ./Cryptobox/commands
echo ./dist/$1






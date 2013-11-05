if [ ! -d ./dist ]
then
    mkdir ./dist
fi
if [ -f ./build/$1/*.pyz ]
then
    rm ./build/$1/*.pyz
fi
if [ -f ./dist/$1 ]
then
    rm ./dist/$1
fi
if [ -f ./Cryptobox/Resources/$1 ]
then
    rm ./Cryptobox/Resources/$1
fi
echo "building", ./source/commands/$1.py
VERSIONER_PYTHON_PREFER_32_BIT=yes arch -i386 /usr/bin/python ./pyinstaller/pyinstaller.py --onefile --console --noupx ./source/commands/$1.py
mv $1.spec ./source/commands/specs
mkdir -p ./Cryptobox/commands
cp ./dist/$1 ./Cryptobox/commands
echo ./dist/$1






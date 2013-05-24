function compile() {
    rm ./build/$1/*.pyz
    rm ./dist/$1 
    rm ./Cryptobox/Resources/$1
    echo "building", ./source/commands/$1.py
    python2.7.apple ./pyinstaller-2.0/pyinstaller.py --onefile --console --noupx ./source/commands/$1.py
    mv $1.spec ./source/commands/specs
    cp ./dist/$1 ./Cryptobox/Resources/
    rm *final*.log
    echo "done"
    echo ./dist/$1
}

compile pyversion &

wait


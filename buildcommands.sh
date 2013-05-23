function compile() {
    python2.7.apple ./pyinstaller-2.0/pyinstaller.py --onefile --console --noupx ./commands/$1.py
    mv $1.spec ./commands/specs
    mv ./dist/$1 ./Cryptobox/Resources/
}

compile pyversion


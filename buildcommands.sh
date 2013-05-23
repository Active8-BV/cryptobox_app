function compile() {
    rm -Rf ./build
    rm ./commands/*.pyc
    rm ./commands/*.pyc
    rm ./dist/$1 
    rm ./Cryptobox/Resources/$1
    echo "building", ./commands/$1.py
    python2.7.apple ./pyinstaller-2.0/pyinstaller.py --onefile --console --noupx ./commands/$1.py
    mv $1.spec ./commands/specs
    #mv ./dist/$1 ./Cryptobox/Resources/
    ./dist/pyversion
}

compile pyversion &

wait


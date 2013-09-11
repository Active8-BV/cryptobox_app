# coding=utf-8
import os
from subprocess import Popen, PIPE

def main():
    """
    main
    """
    pipe = Popen("./node-webkit.app/Contents/MacOS/node-webkit Cryptobox/", shell=True, stderr=PIPE, stdout=PIPE, cwd="/Users/rabshakeh/workspace/cryptobox/cryptobox_app")
    pipe.wait()

if __name__=="__main__":
    main()

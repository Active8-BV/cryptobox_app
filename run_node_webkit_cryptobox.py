# coding=utf-8
import os
from subprocess import Popen, PIPE

def main():
    """
    main
    """

    proc = Popen("./node-webkit.app/Contents/MacOS/node-webkit Cryptobox/", shell=True, stdout=PIPE, stderr=PIPE, cwd="/Users/rabshakeh/workspace/cryptobox/cryptobox_app")

    while True:

        line = proc.stderr.readline()
        if line != '':
            if "cryptobox.cf" in line:
                ls = line.split("cryptobox.cf:")
                if len(ls) > 0:
                    msg = ls[1].replace("\n", "")
                    smsg = msg.split('", source')
                    if len(smsg) > 0:
                        msg = smsg[0]
                    if "POST /RPC2" not in msg:
                        smsg = msg.split(" ")
                        if len(smsg) > 0:
                            msg = smsg[0] + ">"
                            cnt = 0
                            for s in smsg:
                                if cnt > 0:
                                    msg += " " + s
                                cnt += 1
                        print "\033[93m" + msg + "\033[0m "
        else:
            break

if __name__=="__main__":
    main()

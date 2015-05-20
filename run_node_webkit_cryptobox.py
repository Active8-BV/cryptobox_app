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
            
            
            if "INFO:CONSOLE" in line and not "cryptobox.cf" in line:
                ls = line.split(", source: file")
                if len(ls) > 0:
                    msg = ls[0].replace("\n", "").replace('"', "")
                    if ", source: file" in line:
                        print "\033[33m" + msg + "\033[0m "
                    else:
                        print "\033[91m" + msg + "\033[0m "
            if "at" in line and "file://" in line:
                ls = line.split("(file://")
                if len(ls) > 0:
                    msg = ls[0].replace("\n", "").replace('"', "")
                    print "\033[33m    " + msg + "\033[0m "
            elif "cryptobox.cf" in line:
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
                        print "\033[32m" + msg.replace('"', "") + "\033[0m "
        else:
            break

if __name__=="__main__":
    main()

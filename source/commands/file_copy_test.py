# coding=utf-8
import os

def main():
    stats = os.stat("./gzip")
    open("gzip_copy", "w").write(open("./gzip", "r").read())
    stats2 = os.stat("./gzip_copy")
    print stats
    print stats2

if __name__=="__main__":
    main()

# coding=utf-8
import os
import stat

def main():
    stats = os.stat("./gzip")
    open("gzip_copy2", "w").write(open("./gzip", "r").read())
    stats2 = os.stat("./gzip_copy2")
    #print stats
    #print stats2

    mode = stats.st_mode
    os.chmod("./gzip_copy2", mode)
    uid = stats.st_uid
    gid = stats.st_gid
    #os.chown("./gzip_copy2", uid, gid)
        

    atime = stats[stat.ST_ATIME]
    mtime = stats[stat.ST_MTIME]
    os.utime("./gzip_copy2", (atime, mtime))




    print "----------"
    stats = os.stat("./gzip")
    stats2 = os.stat("./gzip_copy2")
    print stats
    print stats2

    os.system("ls -las gzip*")

if __name__ == "__main__":
    main()

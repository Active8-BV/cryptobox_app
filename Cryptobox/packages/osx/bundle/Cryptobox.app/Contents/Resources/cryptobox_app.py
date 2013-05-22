import sys
import os
pidfile = "cryptobox.pid"

def py_make_pid():
    global pidfile
    pid = str(os.getpid())
    if os.path.isfile(pidfile):
        print "%s already exists, exiting" % pidfile
        return False
    else:
        file(pidfile, 'w').write(pid)
        return True


def py_clean_up_pid():
    global pidfile
    os.remove(pidfile)


def get_version():
    return sys.version


def handle(v):
    return v + v


import sys


def get_version():
    return sys.version.split("\n")[0]


def handle(v): 
    return v + v

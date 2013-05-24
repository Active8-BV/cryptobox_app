#!/usr/bin/python2.7.apple
# coding=utf-8
import sys
from optparse import OptionParser


def warning(s):
    sys.stderr.write("warning: " + s + "\n")


def add_options():
    parser = OptionParser()
    parser.add_option("-d", "--dir", dest="dir",
                      help="index this DIR", metavar="DIR")

    return parser.parse_args()


def main():
    (options, args) = add_options()

    if not options.dir:  
        warning('need a DIR to continue')
        print "-1"
        exit(1)


if __name__ == "__main__":
    main()

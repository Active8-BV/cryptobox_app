#!/usr/bin/python2.7.apple
# coding=utf-8
import os
import sys
from optparse import OptionParser
from Crypto.Hash import SHA512

def warning(*arg):
    sys.stderr.write("\033[91mwarning: " + " ".join([str(s) for s in arg]).strip() + " (-h for help)\033[0m\n")


def log(*arg):
    sys.stderr.write("\033[93m" + " ".join([str(s) for s in arg]).strip() + "\n\033[0m")


def add_options():
    parser = OptionParser()
    parser.add_option("-d", "--dir", dest="dir",
                      help="index this DIR", metavar="DIR")
    parser.add_option("-i", "--index", dest="index",
                      help="filepath for index", metavar="INDEX")

    return parser.parse_args()


def exit_app_warning(*arg):
    warning(*arg)
    print "-1"
    exit(1)


def visit(arg, dirname, names):
    arg[dirname] = names


def main():
    (options, args) = add_options()

    if not options.dir:
        exit_app_warning("Need DIR (-d) to continue")
    if not options.index:
        exit_app_warning("Need INDEX (-i) to continue")
    if not os.path.exists(options.dir):
        exit_app_warning("DIR [", options.dir, "] does not exist")
    if not os.path.isdir(options.dir):
        exit_app_warning("DIR [", options.dir, "] is not a folder")
    log("Indexing", options.dir)
    args = {}
    args["DIR"] = options.dir
    args["INDEX"] = options.index
    os.path.walk(options.dir, visit, args)
    log("done")
    print args.keys()


if __name__ == "__main__":
    main()

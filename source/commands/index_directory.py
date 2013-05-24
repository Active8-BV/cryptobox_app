#!/usr/bin/python2.7.apple
# coding=utf-8
import os
import sys
import cPickle
from optparse import OptionParser
from Crypto.Hash import SHA512


def make_hash(data):
    """ make hash
    @param data:
    """
    sha = SHA512.new(data)
    return sha.hexdigest()


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
    dirname_hash = make_hash(dirname)
    nameshash = make_hash("".join(names))
    folder = {}
    folder["dirname"] = dirname
    folder["dirnamehash"] = dirname_hash
    folder["names"] = names
    folder["nameshash"] = nameshash
    arg["dirname"][dirname] = folder
    arg["dirnamehash"][dirname_hash] = folder


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
    args["dirname"] = {}
    args["dirnamehash"] = {}
    os.path.walk(options.dir, visit, args)
    cPickle.dump(args["dirname"], open("dirname_"+options.index, "w"))
    cPickle.dump(args["dirnamehash"], open("dirnamehash_"+options.index, "w"))
    log("done")


if __name__ == "__main__":
    main()

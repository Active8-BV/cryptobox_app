#!/usr/bin/python2.7.apple
# coding=utf-8
import os
import sys
import cPickle
from optparse import OptionParser
import hashlib


def make_hash(data):
    """ make hash
    @param data:
    """
    sha = hashlib.sha512()
    sha.update(data)
    return sha.hexdigest()


def visit(arg, dirname, names):
    dirname = dirname.replace(os.path.sep, "/")
    filenames = [os.path.basename(x) for x in filter(lambda x: not os.path.isdir(x), [os.path.join(dirname, x) for x in names])]
    dirname_hash = make_hash(dirname)
    nameshash = make_hash("".join(names))
    folder = {}
    folder["dirname"] = dirname
    folder["dirnamehash"] = dirname_hash
    folder["names"] = names
    folder["filenames"] = filenames
    folder["nameshash"] = nameshash
    arg["dirname"][dirname] = folder
    arg["dirnamehash"][dirname_hash] = folder


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
    dirnamepickle = os.path.join(options.dir, "dirname_" + options.index)
    dirnamehashpickle = os.path.join(options.dir, "dirnamehash_" + options.index)
    cPickle.dump(args["dirname"], open(dirnamepickle, "w"))
    cPickle.dump(args["dirnamehash"], open(dirnamehashpickle, "w"))

    numfiles = reduce(lambda x, y: x + y, [len(args["dirnamehash"][x]["filenames"]) for x in args["dirnamehash"]]) + len(args["dirnamehash"])
    log("done, indexed", numfiles, "files")
    print numfiles


if __name__ == "__main__":
    main()

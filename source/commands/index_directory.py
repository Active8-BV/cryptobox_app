#!/usr/bin/python2.7.apple
# coding=utf-8
import os
import sys
import zlib
import cPickle
from optparse import OptionParser
import hashlib


def make_sha1_hash(data):
    """ make hash
    @param data:
    """
    sha = hashlib.sha1()
    sha.update(data)
    return sha.hexdigest()


def save_file_data_as_object(filehash, outpath, fpath, password):
    outfile = os.path.join(outpath, filehash)
    cmd = "openssl enc -aes-256-cbc -in " + fpath + " -pass pass:" + password + " -out " + outfile
    os.system(cmd)


def visit(arg, dirname, names):
    dirname = dirname.replace(os.path.sep, "/")
    filenames = [os.path.basename(x) for x in filter(lambda x: not os.path.isdir(x), [os.path.join(dirname, x) for x in names])]
    dirname_hash = make_sha1_hash(dirname)
    nameshash = make_sha1_hash("".join(names))
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


def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def encrypt_blobstore(arg, dirname, names):
    unencfiles = filter(lambda x: x.endswith(".dec"), names)
    if len(unencfiles) > 0:
        for fname in unencfiles:
            arg.append(os.path.join(dirname, fname))


def ensure_encryption_blobstore(blobdir):
    files_to_encrypt = []
    os.path.walk(blobdir, encrypt_blobstore, files_to_encrypt)
    for unencfile in files_to_encrypt:
        print unencfile


def make_cryptogit_object(fname, fdir, datadir):
    fpath = os.path.join(fdir, fname)
    fcontent = open(fpath, "r").read()
    filehash = make_sha1_hash("blob " + str(len(fcontent)) + "\0" + str(fcontent))
    blobdir = os.path.join(os.path.join(datadir, "blobs"), filehash[:2])
    blobpath = os.path.join(blobdir, filehash)
    if not os.path.exists(blobpath):
        ensure_directory(blobdir)
        fcontent = zlib.compress(fcontent)
        open(blobpath + ".dec", "w").write(fcontent)


def main():
    #Git prefixes the object with "blob ", followed by the length (as a human-readable integer), followed by a NUL character, followed by the contents.
    os.system("/usr/libexec/git-core/git-hash-object openssl")

    #print make_sha1_hash("blob " + str(len(c)) + "\0" + str(c))
    #print make_git_hash("./openssl", c)

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

    datadir = os.path.join(options.dir, ".cryptobox")
    ensure_directory(datadir)
    dirnamepickle = os.path.join(datadir, "dirname_" + options.index)
    dirnamehashpickle = os.path.join(datadir, "dirnamehash_" + options.index)
    dirname = args["dirname"]
    dirnamehash = args["dirnamehash"]
    cPickle.dump(dirname, open(dirnamepickle, "w"))
    cPickle.dump(dirnamehash, open(dirnamehashpickle, "w"))

    numfiles = reduce(lambda x, y: x + y, [len(args["dirnamehash"][x]["filenames"]) for x in args["dirnamehash"]]) + len(args["dirnamehash"])

    log("Comparing", numfiles, "against store")

    for dirhash in dirnamehash:
        #print dirnamehash[dirhash]["dirname"]
        for fname in dirnamehash[dirhash]["filenames"]:
            #print "\t", fname, make_sha1_hash(fname)
            pass
            save_file_data_as_object
    make_cryptogit_object("openssl", ".", datadir)
    ensure_encryption_blobstore(os.path.join(datadir, "blobs"))


if __name__ == "__main__":
    main()

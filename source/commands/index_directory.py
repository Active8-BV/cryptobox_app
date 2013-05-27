#!/usr/bin/python2.7.apple
# coding=utf-8
import os
import sys
import time
import gzip
import shutil
import pipes
import cPickle
import json
from optparse import OptionParser
import hashlib
import multiprocessing


def warning(*arg):
    sys.stderr.write("\033[91mwarning: " + " ".join([str(s) for s in arg]).strip() + " (-h for help)\033[0m\n")


def log(*arg):
    sys.stderr.write("\033[93m" + " ".join([str(s) for s in arg]).strip() + "\n\033[0m")


def add_options():
    parser = OptionParser()
    parser.add_option("-d", "--dir", dest="dir",
                      help="index this DIR", metavar="DIR")
    return parser.parse_args()


def exit_app_warning(*arg):
    warning(*arg)
    print "-1"
    exit(1)


def timestamp_to_string(ts, short=False):
    """Return the current time formatted for logging."""

    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    year, month, day, hh, mm, ss, x, y, z = time.localtime(ts)
    if short:
        year -= 2000
        s = "%d-%d-%d %02d:%02d:%02d" % (day, month, year, hh, mm, ss)

    else:
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (day, monthname[month], year, hh, mm, ss)
    return s


def log_date_time_string():
    return "[" + timestamp_to_string(time.time()) + "]"


def stack_trace(depth=6, line_num_only=False):
    import traceback
    stack = traceback.format_stack()
    stack.reverse()
    space = ""
    cnt = 0
    error = ""
    for line in stack:
        if cnt > 1:
            s = line
            parsed_line = s.strip().replace("\n", ":").split(",")
            error += space
            error += "/".join(parsed_line[0].split("/")[len(parsed_line[0].split("/")) - 2:]).replace('"', '')
            error += ":"
            if line_num_only:
                return error + parsed_line[1].replace("line ", "").strip()
            error += parsed_line[1].replace("line ", "").strip()
            error += parsed_line[2].replace("  ", " ").replace("  ", " ").replace("  ", " ")
            space += "  "
            error += "\n"
        cnt += 1
        if len(space) > len("  " * depth):
            error += ("  " * depth) + "....\n"
            break
    return error


def handle_exception(exc, raise_again=True, return_error=False):
    """
    @param exc:
    @type exc:
    """
    import sys
    import traceback
    if raise_again and return_error:
        raise Exception("handle_exception, raise_again and return_error can't both be true")
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error = "\n\033[95m" + log_date_time_string() + " ---------------------------\n"
    error += "\033[95m" + log_date_time_string() + "   !!! EXCEPTION !!!\n"
    error += "\033[95m" + log_date_time_string() + " ---------------------------\n"
    items = traceback.extract_tb(exc_traceback)
    #items.reverse()
    leni = 0
    error += "\033[93m" + log_date_time_string() + " " + str(exc_type) + "\n"
    error += "\033[93m" + log_date_time_string() + " " + str(exc) + "\n"
    error += "\033[95m" + log_date_time_string() + " ---------------------------\n"
    error += "\033[93m"
    try:
        linenumsize = 0
        for line in items:
            fnamesplit = str(line[0]).split("/")
            fname = "/".join(fnamesplit[len(fnamesplit) - 2:])
            ls = len(fname + ":" + str(line[1]))
            if ls > linenumsize:
                linenumsize = ls
        items.reverse()
        for line in items:
            leni += 1
            tabs = leni * "  "
            fnamesplit = str(line[0]).split("/")
            fname = "/".join(fnamesplit[len(fnamesplit) - 2:])
            fname_number = fname + ":" + str(line[1])
            fname_number += (" " * (linenumsize - len(fname_number)))
            val = ""
            if line[3]:
                val = line[3]
            error += fname_number + " | " + tabs + val + "\n"
        if len(items) < 4:
            error += stack_trace()
    except Exception, e:
        print "\033[93m" + log_date_time_string(), e, '\033[m'
        print "\033[93m" + log_date_time_string(), exc, '\033[m'
    error += "\033[95m" + log_date_time_string() + " ---------------------------\n"
    if return_error:
        return error.replace("\033[95m", "")
    else:
        import sys
        sys.stdout.write(str(error) + '\033[0m')
    if raise_again:
        raise exc
    return "\033[93m" + error


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
    if ".cryptobox" not in dirname.lower():
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


def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def encrypt_blobstore(arg, dirname, names):
    unencfiles = filter(lambda x: x.endswith(".unencrypted"), names)
    if len(unencfiles) > 0:
        for fname in unencfiles:
            arg.append(os.path.join(dirname, fname))


def ensure_encryption_blobstore(datadir):
    blobdir = os.path.join(datadir, "blobs")
    files_to_encrypt = []
    os.path.walk(blobdir, encrypt_blobstore, files_to_encrypt)
    for unencfile in files_to_encrypt:
        print unencfile


def async_make_cryptogit_hash(fpath, datadir):
    try:
        filehash = os.popen("./git-hash-object " + pipes.quote(fpath)).read().strip()

        blobdir = os.path.join(os.path.join(datadir, "blobs"), filehash[:2])
        blobpath_dec = os.path.join(blobdir, filehash + ".unencrypted")
        blobpath_dec_zipped = os.path.join(blobdir, filehash + ".unencryptedzipped")
        blobpath_enc = os.path.join(blobdir, filehash + ".encrypted")

        if not os.path.exists(blobpath_enc) and not os.path.exists(blobpath_dec_zipped):
            ensure_directory(os.path.dirname(blobpath_dec))
            shutil.copy2(fpath, blobpath_dec)
            if os.path.exists(blobpath_dec):
                f_in = open(blobpath_dec, 'rb')
                f_out = gzip.open(blobpath_dec_zipped, 'wb')
                f_out.writelines(f_in)
                f_out.close()
                f_in.close()
                os.remove(blobpath_dec)
            else:
                raise IOError("Cannot find " + str(blobpath_dec))

        else:
            #print "skipping", os.path.basename(fpath)
            pass

    except Exception, e:
        handle_exception(e)


def update_progress(curr, total, msg=""):
    progress = int(float(curr) / (float(total) / 100))
    if progress > 100:
        print "error progress more then 100", progress
        progress = 100
    if len(msg) == 0:
        msg = str(curr) + "/" + str(total)
    sys.stderr.write("\r\033[93m[{0}{1}] {2}% {3}\033[0m".format(progress * "#", (100 - progress) * " ", progress, msg))
    sys.stderr.flush()

    if progress >= 100:
        print


def main():
    (options, args) = add_options()

    if not options.dir:
        exit_app_warning("Need DIR (-d) to continue")
    if not os.path.exists(options.dir):
        exit_app_warning("DIR [", options.dir, "] does not exist")
    log("Building indexing for", options.dir)
    args = {}
    args["DIR"] = options.dir
    args["dirname"] = {}
    args["dirnamehash"] = {}
    os.path.walk(options.dir, visit, args)

    datadir = os.path.join(options.dir, ".cryptobox")
    ensure_directory(datadir)
    cryptobox_index_path = os.path.join(datadir, "cryptobox_index.pickle")
    cryptobox_jsonindex_path = os.path.join(datadir, "cryptobox_index.json")
    cryptobox_index = {"dirname": args["dirname"], "dirnamehash": args["dirnamehash"]}
    cPickle.dump(cryptobox_index, open(cryptobox_index_path, "w"))
    json.dump(cryptobox_index, open(cryptobox_jsonindex_path, "w"))

    numfiles = reduce(lambda x, y: x + y, [len(args["dirnamehash"][x]["filenames"]) for x in args["dirnamehash"]])
    #numdirs = len(args["dirnamehash"])

    log("Comparing", numfiles, "files against the cryptobox vault, using", multiprocessing.cpu_count(), "cores")
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())

    processed_files = 0
    update_progress(processed_files, numfiles, "")
    results = []
    for dirhash in cryptobox_index["dirnamehash"]:
        update_progress(processed_files, numfiles)
        for fname in cryptobox_index["dirnamehash"][dirhash]["filenames"]:
            file_dir = cryptobox_index["dirnamehash"][dirhash]["dirname"]
            file_path = os.path.join(file_dir, fname)

            result = pool.apply_async(async_make_cryptogit_hash, (file_path, datadir))
            results.append(result)

        for result in results:
            if result.ready():
                processed_files += 1
                update_progress(processed_files, numfiles)

                if result.successful():
                    results.remove(result)

    while results:
        time.sleep(0.1)
        for result in results:
            if result.ready():
                processed_files += 1
                update_progress(processed_files, numfiles)

                if not result.successful():
                    result.get()
                results.remove(result)

    pool.close()
    pool.join()


if __name__ == "__main__":
    main()

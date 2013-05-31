#!/usr/bin/python2.7.apple
# coding=utf-8
import sys
reload(sys)
# noinspection PyUnresolvedReferences
sys.setdefaultencoding('utf-8')

import base64
import shutil
import os
import time
import cPickle
import json
import math
import re
from optparse import OptionParser
import multiprocessing
from Crypto import Random
from Crypto.Hash import SHA, SHA512, HMAC
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

g_lock = multiprocessing.Lock()


def warning(*arg):
    sys.stderr.write("\033[91mwarning: " + " ".join([str(s) for s in arg]).strip(" ") + "\033[0m\n")


def log(*arg):
    msg = " ".join([str(s) for s in arg]).strip(" ")
    sys.stderr.write("\033[93m" + msg + "\n\033[0m")


def add_options():
    parser = OptionParser()
    parser.add_option("-f", "--dir", dest="dir",
                      help="index this DIR", metavar="DIR")
    parser.add_option("-e", "--encrypt", dest="encrypt", action='store_true',
                      help="index and possible decrypt files)", metavar="ENCRYPT")
    parser.add_option("-d", "--decrypt", dest="decrypt", action='store_true',
                      help="decrypt and correct the directory", metavar="DECRYPT")
    parser.add_option("-r", "--remove", dest="remove", action='store_true',
                      help="remove the unencrypted files", metavar="DECRYPT")

    return parser.parse_args()


def exit_app_warning(*arg):
    warning(*arg)
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
    sha = SHA.new()
    sha.update(data)
    return sha.hexdigest()


def make_hash(data):
    """ make hash
    @param data:
    """
    sha = SHA512.new(data)
    return sha.hexdigest()


def make_hash_str(data, secret):
    """ make hash
    @param data:
    """
    if isinstance(data, dict):
        sortedkeys = data.keys()
        sortedkeys.sort()
        data2 = {}
        for key in sortedkeys:
            data2[key] = str(data[key])
        data = data2
    elif isinstance(data, list):
        data = data[0]
    if len(data) > 100:
        data = data[:100]
    data = re.sub('[\Waouiae]+', "", str(data).lower())
    hmac = HMAC.new(secret, digestmod=SHA512)
    hmac.update(str(data))
    return hmac.hexdigest()


def pasword_derivation(key, salt, size=32):
    """
    @param key:
    @type key: str
    @param salt:
    @type salt: str
    @return:
    @rtype: str
    """
    return PBKDF2(key, salt, size)


#noinspection PyArgumentEqualDefault
def encrypt(salt, secret, data):
    """
    encrypt data or a list of data with the password (key)
    @param data: data to encrypt
    @type data: list, bytearray
    @return: ecnrypted data dict
    @rtype: dict
    """
    if not data:
        print
        # the block size for the cipher object; must be 16, 24, or 32 for AES
    block_size = 32
    # the character used for padding--with a block cipher such as AES, the value
    # you encrypt must be a multiple of block_size in length.  This character is
    # used to ensure that your value is always a multiple of block_size
    # enhance secret
    Random.atfork()
    initialization_vector = Random.new().read(AES.block_size)
    cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
    # encode the list or string
    data_hash = make_hash_str(data, secret)
    encoded_data = cipher.encrypt(data)

    encoded_hash = make_hash_str(encoded_data, secret)
    encrypted_data_dict = {
        "salt": salt,
        "hash": data_hash,
        "initialization_vector": initialization_vector,
        "encoded_data": encoded_data
    }
    if encoded_hash == data_hash:
        raise Exception("data is not encrypted")
    return encrypted_data_dict


class EncryptionHashMismatch(Exception):
    """
    raised when the hash of the decrypted data doesn't match the hash of the original data
    """
    pass


#noinspection PyArgumentEqualDefault
def decrypt(secret, encrypted_data_dict, hashcheck=True):
    """
    encrypt data or a list of data with the password (key)
    @param encrypted_data_dict: encrypted data
    @type encrypted_data_dict: dict
    @return: the data
    @rtype: list, bytearray
    """
    # the character used for padding--with a block cipher such as AES, the value
    # you encrypt must be a multiple of block_size in length.  This character is
    # used to ensure that your value is always a multiple of block_size
    # one-liners to encrypt/encode and decrypt/decode a str
    # encrypt with AES, encode with base64
    # initialization_vector = Random.new().read(AES.block_size)
    if not isinstance(encrypted_data_dict, dict):
        pass
    if 16 != len(encrypted_data_dict["initialization_vector"]):
        raise Exception("initialization_vector len is not 16")

    cipher = AES.new(secret, AES.MODE_CFB, IV=encrypted_data_dict["initialization_vector"])
    decoded = cipher.decrypt(encrypted_data_dict["encoded_data"])
    data_hash = make_hash_str(decoded, secret)
    if "hash" in encrypted_data_dict and hashcheck:
        if data_hash != encrypted_data_dict["hash"]:
            raise EncryptionHashMismatch("the decryption went wrong, hash didn't match")
    return decoded


def write_file(path, data, a_time, m_time, st_mode, st_uid, st_gid):
    fout = open(path, "wb")
    fout.write(data)
    fout.close()
    os.utime(path, (a_time, m_time))
    os.chmod(path, st_mode)
    os.chown(path, st_uid, st_gid)


def read_file(path):
    data = open(path, "rb").read()
    stats = os.stat(path)
    return data, stats.st_atime, stats.st_mtime, stats.st_mode, stats.st_uid, stats.st_gid


def read_file_to_fdict(path):
    ft = read_file(path)
    file_dict = {}
    file_dict["data"] = ft[0]
    file_dict["st_atime"] = int(ft[1])
    file_dict["st_mtime"] = int(ft[2])
    file_dict["st_mode"] = int(ft[3])
    file_dict["st_uid"] = int(ft[4])
    file_dict["st_gid"] = int(ft[5])
    return file_dict


def write_fdict_to_file(fdict, path):
    write_file(path, fdict["data"], fdict["st_atime"], fdict["st_mtime"], fdict["st_mode"], fdict["st_uid"], fdict["st_gid"])


def get_ignores():
    return [".cryptobox", ".ds_store", "$recycle.bin"]


def ignore_dirname(dirname):
    ignores = get_ignores()
    dirname_igore_finds = map(lambda x: dirname.find(x), ignores)
    filtered_dirname = filter(lambda x: x > 0, dirname_igore_finds)
    if len(filtered_dirname) > 0:
        return True
    return False


def filter_names(names):
    ignores = get_ignores()
    return filter(lambda x: x.lower() not in ignores, names)


def count_files_visit(arg, dirname, names):
    if ignore_dirname(dirname):
        return
    names = filter_names(names)
    arg["cnt"] += len([os.path.basename(x) for x in filter(lambda x: not os.path.isdir(x), [os.path.join(dirname, x) for x in names])])


def update_progress(curr, total, msg=""):
    global g_lock
    g_lock.acquire()
    try:
        if total == 0:
            return
        progress = int(math.ceil(float(curr) / (float(total) / 100)))
        if progress > 100:
            print "error progress more then 100", progress
            progress = 100
        if len(msg) == 0:
            msg = str(curr) + "/" + str(total)
        sys.stderr.write("\r\033[93m[{0}{1}] {2}% {3}\033[0m".format(progress / 2 * "#", (50 - progress / 2) * " ", progress, msg))
        sys.stderr.flush()

    finally:
        g_lock.release()


def index_files_visit(arg, dirname, names):
    if ignore_dirname(dirname):
        return
    names = filter_names(names)

    dirname = dirname.replace(os.path.sep, "/")
    filenames = [os.path.basename(x) for x in filter(lambda x: not os.path.isdir(x), [os.path.join(dirname, x) for x in names])]
    dirname_hash = make_sha1_hash(dirname)
    nameshash = make_sha1_hash("".join(names))
    folder = {}
    folder["dirname"] = dirname
    folder["dirnamehash"] = dirname_hash
    folder["filenames"] = [{'name': x} for x in filenames]
    folder["nameshash"] = nameshash

    arg["folders"]["dirnames"][dirname_hash] = folder
    arg["numfiles"] += len(filenames)
    update_progress(arg["numfiles"], arg["numfiles_cnt"])


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


def make_cryptogit_hash(fpath, datadir):
    file_dict = read_file_to_fdict(fpath)
    filehash = make_sha1_hash("blob " + str(len(file_dict["data"])) + "\0" + str(file_dict["data"]))
    blobdir = os.path.join(os.path.join(datadir, "blobs"), filehash[:2])
    blobpath = os.path.join(blobdir, filehash[2:])
    filedata = {"filehash": filehash, "fpath": fpath, "blobpath": blobpath, "blobdir": blobdir}
    filedata["blob_exists"] = os.path.exists(blobpath)
    return filedata


def read_and_encrypt_file(fpath, blobpath, salt, secret, cryptobox_index):
    try:
        file_dict = read_file_to_fdict(fpath)
        #cryptobox_index["filestats"]
        pickled_file_dict = cPickle.dumps(file_dict, cPickle.HIGHEST_PROTOCOL)
        encrypted_file_dict = encrypt(salt, secret, pickled_file_dict)
        cPickle.dump(encrypted_file_dict, open(blobpath, "wb"), cPickle.HIGHEST_PROTOCOL)

        return None
    except Exception, e:
        handle_exception(e)


def encrypt_new_blobs(salt, secret, new_blobs, cryptobox_index):
    num_cores = multiprocessing.cpu_count()
    progressdata = {}
    progressdata["processed_files"] = 0
    progressdata["numfiles"] = len(new_blobs)

    # noinspection PyUnusedLocal
    def done_encrypting(e):
        progressdata["processed_files"] += 1
        update_progress(progressdata["processed_files"], progressdata["numfiles"])

    pool = multiprocessing.Pool(processes=num_cores)

    counter = 0
    encrypt_results = []
    for fhash in new_blobs:
        counter += 1
        ensure_directory(new_blobs[fhash]["blobdir"])
        result = pool.apply_async(read_and_encrypt_file, (new_blobs[fhash]["fpath"], new_blobs[fhash]["blobpath"], salt, secret, cryptobox_index), callback=done_encrypting)
        encrypt_results.append(result)
    pool.close()
    pool.join()
    for result in encrypt_results:
        if not result.successful():
            result.get()


def index_and_encrypt(options, password):
    datadir = os.path.join(options.dir, ".cryptobox")
    cryptobox_index_path = os.path.join(datadir, "cryptobox_index.pickle")

    if os.path.exists(cryptobox_index_path):
        current_cryptobox_index = cPickle.load(open(cryptobox_index_path, "r"))
        salt = base64.decodestring(current_cryptobox_index["salt_b64"])
        if current_cryptobox_index["locked"] is True:
            exit_app_warning("Current directory is locked")
            return
        else:
            shutil.copy2(cryptobox_index_path, cryptobox_index_path + ".backup")
    else:
        salt = Random.new().read(32)
    secret = pasword_derivation(password, salt)

    log("Start index for", options.dir, "using", multiprocessing.cpu_count(), "cores")

    numfiles = {}
    numfiles["cnt"] = 0
    os.path.walk(options.dir, count_files_visit, numfiles)
    log("Indexing", numfiles["cnt"], "files")
    args = {}
    args["DIR"] = options.dir
    args["folders"] = {"dirnames": {}}
    args["numfiles"] = 0
    args["numfiles_cnt"] = numfiles["cnt"]
    os.path.walk(options.dir, index_files_visit, args)

    #os.system("rm -Rf " + datadir)
    ensure_directory(datadir)
    cryptobox_index = args["folders"]
    numfiles = reduce(lambda x, y: x + y, [len(args["folders"]["dirnames"][x]["filenames"]) for x in args["folders"]["dirnames"]])
    log("\n")
    log("Checking", numfiles, "files")
    new_blobs = {}
    file_cnt = 0
    new_objects = 0
    for dirhash in cryptobox_index["dirnames"]:
        for fname in cryptobox_index["dirnames"][dirhash]["filenames"]:
            file_cnt += 1
            file_dir = cryptobox_index["dirnames"][dirhash]["dirname"]
            file_path = os.path.join(file_dir, fname["name"])
            filedata = make_cryptogit_hash(file_path, datadir)
            fname["hash"] = filedata["filehash"]
            if not filedata["blob_exists"]:
                new_blobs[filedata["filehash"]] = filedata
                new_objects += 1
            if len(new_blobs) > 1500:
                log("\n")
                log("lots of new blobs, doing in between encrypt fase")
                encrypt_new_blobs(salt, secret, new_blobs, cryptobox_index)
                new_blobs = {}
                log("\n")
            update_progress(file_cnt, numfiles)
    if len(new_blobs) > 0:
        log("\n")
        log("Encrypting", len(new_blobs), "blobs")
        if len(new_blobs) > 0:
            encrypt_new_blobs(salt, secret, new_blobs, cryptobox_index)
        sys.stderr.flush()
    log("\n")
    log("writing tree, found", new_objects, "new objects")

    cryptobox_index_path = os.path.join(datadir, "cryptobox_index.pickle")
    cryptobox_jsonindex_path = os.path.join(datadir, "cryptobox_index.json")
    if options.remove:
        cryptobox_index["locked"] = True
    else:
        cryptobox_index["locked"] = False
    cryptobox_index["salt_b64"] = base64.encodestring(salt)
    cPickle.dump(cryptobox_index, open(cryptobox_index_path, "w"))
    json.dump(cryptobox_index, open(cryptobox_jsonindex_path, "w"), sort_keys=True, indent=4, separators=(',', ': '))

    if options.remove:
        for fname in os.listdir(options.dir):
            if fname.lower() not in get_ignores():
                fpath = os.path.join(options.dir, fname)
                if os.path.isdir(fpath):
                    shutil.rmtree(fpath, True)
                else:
                    os.remove(fpath)


def decrypt_blob_to_filepaths(blobdir, cryptobox_index, fhash, secret):
    try:
        fdir = os.path.join(blobdir, fhash[:2])
        blob_enc = cPickle.load(open(os.path.join(fdir, fhash[2:])))
        blob_pickled = decrypt(secret, blob_enc, True)
        file_blob = cPickle.loads(blob_pickled)
        for dirhash in cryptobox_index["dirnames"]:
            for cfile in cryptobox_index["dirnames"][dirhash]["filenames"]:
                if fhash == cfile["hash"]:
                    fpath = os.path.join(cryptobox_index["dirnames"][dirhash]["dirname"], cfile["name"])
                    if not os.path.exists(fpath):
                        write_fdict_to_file(file_blob, fpath)
    except Exception, e:
        handle_exception(e, False)


def decrypt_and_build_filetree(options, password):
    datadir = os.path.join(options.dir, ".cryptobox")
    blobdir = os.path.join(datadir, "blobs")
    cryptobox_index_path = os.path.join(datadir, "cryptobox_index.pickle")
    cryptobox_index = cPickle.load(open(cryptobox_index_path, "rb"))
    hashes = set()
    for dirhash in cryptobox_index["dirnames"]:
        if "dirname" in cryptobox_index["dirnames"][dirhash]:
            if not os.path.exists(cryptobox_index["dirnames"][dirhash]["dirname"]):
                ensure_directory(cryptobox_index["dirnames"][dirhash]["dirname"])
        for cfile in cryptobox_index["dirnames"][dirhash]["filenames"]:
            fpath = os.path.join(cryptobox_index["dirnames"][dirhash]["dirname"], cfile["name"])
            if not os.path.exists(fpath):
                hashes.add(cfile["hash"])

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    progressdata = {}
    progressdata["processed_files"] = 0
    progressdata["numfiles"] = len(hashes)

    # noinspection PyUnusedLocal
    def done_decrypting(e):
        progressdata["processed_files"] += 1
        update_progress(progressdata["processed_files"], progressdata["numfiles"])

    secret = pasword_derivation(password, base64.decodestring(cryptobox_index["salt_b64"]))
    decrypt_results = []
    for fhash in hashes:
        result = pool.apply_async(decrypt_blob_to_filepaths, (blobdir, cryptobox_index, fhash, secret), callback=done_decrypting)
        decrypt_results.append(result)
    pool.close()
    pool.join()
    for result in decrypt_results:
        if not result.successful():
            result.get()
    cryptobox_jsonindex_path = os.path.join(datadir, "cryptobox_index.json")
    cryptobox_index["locked"] = False
    cPickle.dump(cryptobox_index, open(cryptobox_index_path, "w"))
    json.dump(cryptobox_index, open(cryptobox_jsonindex_path, "w"), sort_keys=True, indent=4, separators=(',', ': '))
    log("\n")


def main():
    (options, args) = add_options()

    if not options.dir:
        exit_app_warning("Need DIR (-d) to continue")
    if not os.path.exists(options.dir):
        exit_app_warning("DIR [", options.dir, "] does not exist")
    if not options.encrypt and not options.decrypt:
        exit_app_warning("No encrypt or decrypt directive given (-d or -e)")

    password = "kjhfsd98"

    if options.encrypt:
        index_and_encrypt(options, password)

    if options.decrypt:
        decrypt_and_build_filetree(options, password)


if __name__ == "__main__":
    main()

#!/usr/bin/python2.7.apple
# coding=utf-8
import sys
reload(sys)
# noinspection PyUnresolvedReferences
sys.setdefaultencoding('utf-8')

import re
import base64
import shutil
import os
import time
import cPickle
import json
import math
import requests
import subprocess
import socket
import urllib
from optparse import OptionParser
import multiprocessing
from Crypto import Random
from Crypto.Hash import SHA, SHA512, HMAC
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

g_lock = multiprocessing.Lock()

SERVER = "http://127.0.0.1:8000/"
#SERVER = "https://www.cryptobox.nl/"


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
    parser.add_option("-c", "--clear", dest="clear", action='store_true',
                      help="clear all cryptobox data", metavar="DECRYPT")
    parser.add_option("-u", "--username", dest="username",
                      help="cryptobox username", metavar="USERNAME")
    parser.add_option("-p", "--password", dest="password",
                      help="password used for encryption", metavar="PASSWORD")
    parser.add_option("-b", "--cryptobox", dest="cryptobox",
                      help="cryptobox slug", metavar="CRYPTOBOX")
    parser.add_option("-s", "--sync", dest="sync", action='store_true',
                      help="sync with server", metavar="SYNC")
    parser.add_option("-n", "--numdownloadthreads", dest="numdownloadthreads",
                      help="number if downloadthreads", metavar="NUMDOWNLOADTHREADS")

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
        sys.stderr.write(str(error) + '\033[0m')
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
    # the block size for the cipher object; must be 16, 24, or 32 for AES
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
    if encoded_hash == data_hash and len(data.strip()) > 0:
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
        if len(decoded) > 0:
            if data_hash != encrypted_data_dict["hash"]:
                raise EncryptionHashMismatch("the decryption went wrong, hash didn't match")
    return decoded


def write_file(path, data, a_time, m_time, st_mode, st_uid, st_gid):
    fout = open(path, "wb")
    fout.write(data)
    fout.close()
    os.utime(path, (a_time, m_time))
    if st_mode:
        os.chmod(path, st_mode)
    if st_uid and st_gid:
        os.chown(path, st_uid, st_gid)


def read_file(path):
    data = open(path, "rb").read()
    stats = os.stat(path)
    return data, stats.st_ctime, stats.st_atime, stats.st_mtime, stats.st_mode, stats.st_uid, stats.st_gid


def read_file_to_fdict(path):
    ft = read_file(path)
    file_dict = {}
    file_dict["data"] = ft[0]
    file_dict["st_ctime"] = int(ft[1])
    file_dict["st_atime"] = int(ft[2])
    file_dict["st_mtime"] = int(ft[3])
    file_dict["st_mode"] = int(ft[4])
    file_dict["st_uid"] = int(ft[5])
    file_dict["st_gid"] = int(ft[6])
    return file_dict


def write_fdict_to_file(fdict, path):
    write_file(path, fdict["data"], fdict["st_atime"], fdict["st_mtime"], fdict["st_mode"], fdict["st_uid"], fdict["st_gid"])


last_update_string_len = 0


def update_progress(curr, total, msg):
    global g_lock
    global last_update_string_len
    g_lock.acquire()
    try:
        if total == 0:
            return
        progress = int(math.ceil(float(curr) / (float(total) / 100)))
        msg = msg + " " + str(curr) + "/" + str(total)
        update_string = "\r\033[94m[{0}{1}] {2}% {3}\033[0m".format(progress / 2 * "#", (50 - progress / 2) * " ", progress, msg)
        if len(update_string) < last_update_string_len:
            sys.stderr.write("\r\033[94m{0}\033[0m".format(" " * 100))
        sys.stderr.write(update_string)
        last_update_string_len = len(update_string)
    finally:
        g_lock.release()


def index_files_visit(arg, dirname, names):
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


def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def encrypt_blobstore(arg, dirname, names):
    unencfiles = filter(lambda x: x.endswith(".unencrypted"), names)
    if len(unencfiles) > 0:
        for fname in unencfiles:
            arg.append(os.path.join(dirname, fname))


def make_cryptogit_hash(fpath, datadir, cryptobox_index):
    file_dict = read_file_to_fdict(fpath)
    filehash = make_sha1_hash("blob " + str(len(file_dict["data"])) + "\0" + str(file_dict["data"]))
    blobdir = os.path.join(os.path.join(datadir, "blobs"), filehash[:2])
    blobpath = os.path.join(blobdir, filehash[2:])
    filedata = {"filehash": filehash, "fpath": fpath, "blobpath": blobpath, "blobdir": blobdir}
    filedata["blob_exists"] = os.path.exists(blobpath)
    del file_dict["data"]
    cryptobox_index["filestats"][fpath] = file_dict
    return filedata


def read_and_encrypt_file(fpath, blobpath, salt, secret):
    try:
        file_dict = read_file_to_fdict(fpath)
        encrypted_file_dict = encrypt(salt, secret, file_dict["data"])
        cPickle.dump(encrypted_file_dict, open(blobpath, "wb"), cPickle.HIGHEST_PROTOCOL)
        return None
    except Exception, e:
        handle_exception(e)


def encrypt_new_blobs(salt, secret, new_blobs):
    num_cores = multiprocessing.cpu_count()
    progressdata = {}
    progressdata["processed_files"] = 0
    progressdata["numfiles"] = len(new_blobs)

    # noinspection PyUnusedLocal
    def done_encrypting(e):
        progressdata["processed_files"] += 1
        update_progress(progressdata["processed_files"], progressdata["numfiles"], "encrypting")

    pool = multiprocessing.Pool(processes=num_cores)

    counter = 0
    encrypt_results = []
    for fhash in new_blobs:
        counter += 1
        ensure_directory(new_blobs[fhash]["blobdir"])
        result = pool.apply_async(read_and_encrypt_file, (new_blobs[fhash]["fpath"], new_blobs[fhash]["blobpath"], salt, secret), callback=done_encrypting)
        encrypt_results.append(result)
    pool.close()
    pool.join()
    for result in encrypt_results:
        if not result.successful():
            result.get()
    pool.terminate()


def get_data_dir(options):
    return os.path.join(options.dir, ".cryptobox")


def get_blob_dir(options):
    datadir = get_data_dir(options)
    return os.path.join(datadir, "blobs")


def get_cryptobox_index_path(options):
    datadir = get_data_dir(options)
    return os.path.join(datadir, "cryptobox_index.pickle")


def get_cryptobox_index(options):
    cryptobox_index_path = get_cryptobox_index_path(options)
    if os.path.exists(cryptobox_index_path):
        return cPickle.load(open(cryptobox_index_path, "r"))
    return None


def cryptobox_locked(options):
    current_cryptobox_index = get_cryptobox_index(options)
    if current_cryptobox_index:
        if current_cryptobox_index["locked"] is True:
            return True
    return False


def get_secret(options):
    password = options.password
    current_cryptobox_index = get_cryptobox_index(options)
    if current_cryptobox_index:
        salt = base64.decodestring(current_cryptobox_index["salt_b64"])
    else:
        salt = Random.new().read(32)
    return salt, pasword_derivation(password, salt)


def index_and_encrypt(options):
    password = options.password
    datadir = get_data_dir(options)
    cryptobox_index_path = get_cryptobox_index_path(options)
    current_cryptobox_index = get_cryptobox_index(options)
    if current_cryptobox_index:
        if cryptobox_locked(options):
            warning("cryptobox is locked, nothing can be added now first decrypt (-d)")
            return
        else:
            shutil.copy2(cryptobox_index_path, cryptobox_index_path + ".backup")
    salt, secret = get_secret(options)

    args = {}
    args["DIR"] = options.dir
    args["folders"] = {"dirnames": {}, "filestats": {}}
    args["numfiles"] = 0
    os.path.walk(options.dir, index_files_visit, args)

    json.dump(args, open("indexwalk.json", "w"), sort_keys=True, indent=4, separators=(',', ': '))
    for dirname in args["folders"]["dirnames"].copy():
        if datadir in args["folders"]["dirnames"][dirname]["dirname"]:
            del args["folders"]["dirnames"][dirname]
    json.dump(args, open("indexwalk2.json", "w"), sort_keys=True, indent=4, separators=(',', ': '))

    ensure_directory(datadir)
    cryptobox_index = args["folders"]
    numfiles = reduce(lambda x, y: x + y, [len(args["folders"]["dirnames"][x]["filenames"]) for x in args["folders"]["dirnames"]])
    new_blobs = {}
    file_cnt = 0
    new_objects = 0
    hash_set_on_disk = set()

    for dirhash in cryptobox_index["dirnames"]:
        for fname in cryptobox_index["dirnames"][dirhash]["filenames"]:
            file_cnt += 1
            file_dir = cryptobox_index["dirnames"][dirhash]["dirname"]
            file_path = os.path.join(file_dir, fname["name"])
            filedata = make_cryptogit_hash(file_path, datadir, cryptobox_index)
            fname["hash"] = filedata["filehash"]
            hash_set_on_disk.add(filedata["filehash"])
            if not filedata["blob_exists"]:
                new_blobs[filedata["filehash"]] = filedata
                new_objects += 1
            if len(new_blobs) > 1500:
                encrypt_new_blobs(salt, secret, new_blobs)
                new_blobs = {}
            update_progress(file_cnt, numfiles, "checking")

    if len(new_blobs) > 0:
        if len(new_blobs) > 0:
            encrypt_new_blobs(salt, secret, new_blobs)

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
        ld = os.listdir(options.dir)
        ld.remove(".cryptobox")
        for fname in ld:
            fpath = os.path.join(options.dir, fname)
            if os.path.isdir(fpath):
                shutil.rmtree(fpath, True)
            else:
                os.remove(fpath)

    obsolute_blob_store_entries = set()
    blob_dirs = os.path.join(datadir, "blobs")
    for blob_dir in os.listdir(blob_dirs):
        blob_store = os.path.join(blob_dirs, blob_dir)
        if os.path.isdir(blob_store):
            for blob_file in os.listdir(blob_store):
                found = False
                for fhash in hash_set_on_disk:
                    if fhash == (blob_dir + blob_file):
                        found = True
                if not found:
                    obsolute_blob_store_entries.add(blob_dir + blob_file)

    for f_hash in obsolute_blob_store_entries:
        blob_dir = os.path.join(blob_dirs, f_hash[:2])
        blob_path = os.path.join(blob_dir, f_hash[2:])
        os.remove(blob_path)
        if os.path.isdir(blob_dir):
            blob_entries = [f for f in os.listdir(blob_dir) if not f.startswith('.')]
            if len(blob_entries) == 0:
                shutil.rmtree(blob_dir, True)
    if numfiles > 0:
        print


def decrypt_blob_to_filepaths(blobdir, cryptobox_index, fhash, secret):
    try:
        fdir = os.path.join(blobdir, fhash[:2])
        blob_enc = cPickle.load(open(os.path.join(fdir, fhash[2:])))

        file_blob = {}
        file_blob["data"] = decrypt(secret, blob_enc, True)
        for dirhash in cryptobox_index["dirnames"]:
            for cfile in cryptobox_index["dirnames"][dirhash]["filenames"]:
                if fhash == cfile["hash"]:
                    fpath = os.path.join(cryptobox_index["dirnames"][dirhash]["dirname"], cfile["name"])
                    if not os.path.exists(fpath):
                        ft = cryptobox_index["filestats"][fpath]
                        file_blob["st_atime"] = int(ft["st_atime"])
                        file_blob["st_mtime"] = int(ft["st_mtime"])
                        file_blob["st_mode"] = int(ft["st_mode"])
                        file_blob["st_uid"] = int(ft["st_uid"])
                        file_blob["st_gid"] = int(ft["st_gid"])
                        write_fdict_to_file(file_blob, fpath)

    except Exception, e:
        handle_exception(e, False)


#datadir = get_data_dir(options)

def decrypt_and_build_filetree(options):
    password = options.password
    datadir = get_data_dir(options)
    if not os.path.exists(datadir):
        warning("nothing to decrypt", datadir, "does not exists")
        return
    blobdir = os.path.join(datadir, "blobs")
    cryptobox_index_path = get_cryptobox_index_path(options)
    cryptobox_index = get_cryptobox_index(options)
    if cryptobox_index:
        if not cryptobox_locked(options):
            return
    else:
        cryptobox_index = None
    hashes = set()
    if cryptobox_index:
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
        update_progress(progressdata["processed_files"], progressdata["numfiles"], "decrypting")

    secret = pasword_derivation(password, base64.decodestring(cryptobox_index["salt_b64"]))
    decrypt_results = []
    for fhash in hashes:
        result = pool.apply_async(decrypt_blob_to_filepaths, (blobdir, cryptobox_index, fhash, secret), callback=done_decrypting)
        decrypt_results.append(result)
    pool.close()
    pool.join()
    successfull_decryption = True
    for result in decrypt_results:
        if not result.successful():
            result.get()
            successfull_decryption = False
    if successfull_decryption:
        cryptobox_jsonindex_path = os.path.join(datadir, "cryptobox_index.json")
        cryptobox_index["locked"] = False
        cPickle.dump(cryptobox_index, open(cryptobox_index_path, "w"))
        json.dump(cryptobox_index, open(cryptobox_jsonindex_path, "w"), sort_keys=True, indent=4, separators=(',', ': '))
    if len(hashes) > 0:
        print


class MemoryNoKey(Exception):
    pass


class MemoryExpired(Exception):
    pass


class Memory(object):
    _instance = None
    data = {}
    timestamps = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            # noinspection PyArgumentList
            cls._instance = super(Memory, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def set(self, key, value, timeout_seconds=None, timeout_minute=None):
        self.data[key] = value
        if timeout_minute:
            timeout_seconds = timeout_minute * 60
        if timeout_seconds:
            self.timestamps[key] = (time.time(), timeout_seconds)

    def has(self, key):
        if key in self.timestamps:
            if int(time.time() - self.timestamps[key][0]) > self.timestamps[key][1]:
                timestamp = self.timestamps[key][0]
                timeout = self.timestamps[key][1]
                del self.data[key]
                if key in self.timestamps:
                    del self.timestamps[key]
                raise MemoryExpired(key + ", " + str(int(time.time() - timestamp) - timeout) + " seconds")
        return key in self.data

    def ttl(self, key, show_seconds=False):
        if key in self.timestamps:
            timestamp = self.timestamps[key][0]
            timeout = self.timestamps[key][1]
            seconds = timeout - int(time.time() - timestamp)
            if show_seconds:
                return seconds
            else:
                return int(math.ceil(float(seconds) / 60))
        return None

    def get(self, key):
        if self.has(key):
            if key in self.timestamps:
                self.timestamps[key] = (time.time(), self.timestamps[key][1])
            return self.data[key]
        else:
            raise MemoryNoKey(str(key))

    def delete(self, key):
        if self.has(key):
            del self.data[key]
            if key in self.timestamps:
                del self.timestamps[key]
        else:
            raise MemoryNoKey(str(key))

    def size(self):
        return len(self.data)

    def save(self, datadir):
        if os.path.exists(datadir):
            mempath = os.path.join(datadir, "memory.pickle")
            data = (self.data, self.timestamps)
            cPickle.dump(data, open(mempath, "wb"))

    def load(self, datadir):
        mempath = os.path.join(datadir, "memory.pickle")
        if os.path.exists(mempath):
            data = cPickle.load(open(mempath, "rb"))
            self.data = data[0]
            self.timestamps = data[1]
            for k in self.data.copy():
                try:
                    self.has(k)
                except MemoryExpired:
                    pass


def get_b64mstyle():
    return "data:b64encode/mstyle,"


def b64_decode_mstyle(s):
    if not isinstance(s, str) and not isinstance(s, unicode):
        return s
    b64mstyle = get_b64mstyle()
    if s.find(b64mstyle) != 0:
        return s
    s = s.replace(b64mstyle, "")
    s = base64.decodestring(s.replace("-", "="))
    s = urllib.unquote(s)
    return s


def b64_encode_mstyle(s):
    if not isinstance(s, str) and not isinstance(s, unicode):
        return s
    b64mstyle = get_b64mstyle()
    if s.find(b64mstyle) != -1:
        return s
    s = urllib.quote(s, safe='~()*!.\'')
    s = base64.encodestring(s).replace("=", "-").replace("\n", "")
    s = b64mstyle + s
    return s


def b64_object_mstyle(d):
    if isinstance(d, dict):
        for k in d:
            d[k] = b64_object_mstyle(d[k])
        return d
    if isinstance(d, list):
        cnt = 0
        for k in d:
            d[cnt] = b64_object_mstyle(k)
            cnt += 1
        return d
    d = b64_decode_mstyle(d)
    return d


def object_b64_mstyle(d):
    if isinstance(d, dict):
        for k in d:
            d[k] = object_b64_mstyle(d[k])
        return d
    if isinstance(d, list):
        cnt = 0
        for k in d:
            d[cnt] = object_b64_mstyle(k)
            cnt += 1
        return d
    d = b64_encode_mstyle(d)
    return d


def request_error(result):
    open("error.html", "w").write(result.text)
    subprocess.call(["lynx", "error.html"])
    os.remove("error.html")
    return


def fingerprint():
    fp = str(socket.gethostname())
    fph = make_hash(fp)
    return fph


class ServerForbidden(Exception):
    pass


class ServerError(Exception):
    pass


class NotAuthorized(Exception):
    pass


def parse_http_result(result):
    if result.status_code == 403:
        raise ServerForbidden(result.reason)
    if result.status_code == 500:
        request_error(result)
        raise ServerError(result.reason)
    return result


def on_server(method, cryptobox, payload, session):
    global SERVER
    cookies = dict(c_persist_fingerprint_client_part=fingerprint())
    SERVICE = SERVER + cryptobox + "/" + method + "/" + str(time.time())
    if not session:
        session = requests
    result = session.post(SERVICE, data=json.dumps(payload), cookies=cookies)
    return parse_http_result(result)


def download_server(options, url):
    global SERVER
    cookies = dict(c_persist_fingerprint_client_part=fingerprint())
    url = os.path.normpath(url)
    URL = SERVER + options.cryptobox + "/" + url
    memory = Memory()
    session = memory.get("session")
    result = session.get(URL, cookies=cookies)
    return parse_http_result(result)


def server_time(cryptobox):
    return float(on_server("clock", cryptobox, payload=None, session=None)[0])


class PasswordException(Exception):
    pass


def authorize(username, password, cryptobox):
    session = requests.Session()
    payload = {}
    payload["username"] = username
    payload["password"] = password
    result = on_server("authorize", cryptobox=cryptobox, payload=payload, session=session)
    payload["trust_computer"] = True
    payload["trused_location_name"] = "Cryptobox"
    results = result.json()
    if results[0]:
        results = results[1]
        results["cryptobox"] = cryptobox
        results["payload"] = payload
        return session, results
    else:
        raise PasswordException(username)


def check_otp(session, results):
    if not "otp" in results:
        return True
    else:
        payload = results["payload"]
        cryptobox = results["cryptobox"]
        payload["otp"] = results["otp"]
        results = on_server("checkotp", cryptobox=cryptobox, payload=payload, session=session)
        results = results.json()
        return results


def authorize_user(options):
    try:
        memory = Memory()
        if memory.has("session"):
            return True
        session, results = authorize(options.username, options.password, options.cryptobox)
        memory.set("session", session, timeout_minute=30)
        return check_otp(session, results)
    except PasswordException, p:
        warning(p, "not authorized")
        return False


def authorized(options):
    memory = Memory()
    cryptobox = options.cryptobox
    result = on_server("authorized", cryptobox=cryptobox, payload=None, session=memory.get("session")).json()
    return result[0]


class TreeLoadError(Exception):
    pass


def have_blob(options, blob_hash):
    blobdir = os.path.join(get_blob_dir(options), blob_hash[:2])
    blobpath = os.path.join(blobdir, blob_hash[2:])
    return os.path.exists(blobpath)


def ensure_directory_sync(options, node_path):
    new_dir = os.path.join(options.dir, node_path.lstrip("/"))
    ensure_directory(new_dir)
    return new_dir


def ensure_directories_sync(options, unique_dirs):
    for udir in unique_dirs:
        udir = udir.lstrip("/").strip()
        if len(udir) > 0:
            ensure_directory_sync(options, udir)


def download_blob(options, node):
    try:
        st_mtime = int(node["content_hash_latest_timestamp"][1])
        dirname_of_path = os.path.dirname(node["doc"]["m_path"])
        new_dir = ensure_directory_sync(options, dirname_of_path)
        new_path = os.path.join(new_dir, node["doc"]["m_name"])
        url = "download/" + node["doc"]["m_short_id"]
        result = download_server(options, url)
        write_file(path=new_path, data=result.content, a_time=st_mtime, m_time=st_mtime, st_mode=None, st_uid=None, st_gid=None)
        return url
    except Exception, e:
        handle_exception(e)


def get_unique_content(options, all_unique_nodes):
    unique_nodes_hashes = filter(lambda fhash: not have_blob(options, fhash), all_unique_nodes)
    unique_nodes = [all_unique_nodes[fhash] for fhash in all_unique_nodes if fhash in unique_nodes_hashes]

    pool = multiprocessing.Pool(processes=options.numdownloadthreads)
    downloaded_files = []

    # noinspection PyUnusedLocal
    def done_downloading(e):
        downloaded_files.append(e)
        update_progress(len(downloaded_files), len(unique_nodes), "downloading")

    download_results = []
    for node in unique_nodes:
        result = pool.apply_async(download_blob, (options, node), callback=done_downloading)
        download_results.append(result)
    pool.close()
    pool.join()
    for result in download_results:
        if not result.successful():
            result.get()
    pool.terminate()


def write_blob_to_filepaths(fhash, files_grouped_by_content_hash, options):
    data = None
    for node in files_grouped_by_content_hash[fhash]:
        st_mtime = int(node["content_hash_latest_timestamp"][1])
        dirname_of_path = os.path.dirname(node["doc"]["m_path"])
        new_dir = ensure_directory_sync(options, dirname_of_path)
        new_path = os.path.join(new_dir, node["doc"]["m_name"])
        if not data:
            fdir = os.path.join(get_blob_dir(options), fhash[:2])
            blob_enc = cPickle.load(open(os.path.join(fdir, fhash[2:])))
            salt, secret = get_secret(options)
            data = decrypt(secret, blob_enc, True)
        if data:
            write_file(path=new_path, data=data, a_time=st_mtime, m_time=st_mtime, st_mode=None, st_uid=None, st_gid=None)


def ensure_not_unique_content(options, file_nodes):
    files_grouped_by_content_hash = {}

    for sfile in file_nodes:
        fhash = sfile["content_hash_latest_timestamp"][0]
        if fhash not in files_grouped_by_content_hash:
            files_grouped_by_content_hash[fhash] = []
        files_grouped_by_content_hash[fhash].append(sfile)
    for fhash in files_grouped_by_content_hash:
        write_blob_to_filepaths(fhash, files_grouped_by_content_hash, options)


def sync_server(options):
    if cryptobox_locked(options):
        exit_app_warning("cryptobox is locked, no sync possible, first decrypt (-d)")
        return

    memory = Memory()
    cryptobox = options.cryptobox
    try:
        result = on_server("tree", cryptobox=cryptobox, payload={'listonly': True}, session=memory.get("session")).json()
    except ServerForbidden:
        log("unauthorized try again")
        if memory.has("session"):
            memory.delete("session")
        authorize_user(options)
        result = on_server("tree", cryptobox=cryptobox, payload={'listonly': True}, session=memory.get("session")).json()
    if not result[0]:
        raise TreeLoadError()
    unique_content = {}
    unique_dirs = set()
    files = []
    for node in result[1]:
        dirname_of_path = os.path.dirname(node["doc"]["m_path"])
        unique_dirs.add(dirname_of_path)
        if node["content_hash_latest_timestamp"]:
            unique_content[node["content_hash_latest_timestamp"][0]] = node
            files.append(node)

    get_unique_content(options, unique_content)
    ensure_directories_sync(options, unique_dirs)
    index_and_encrypt(options)
    ensure_not_unique_content(options, files)


def main():
    (options, args) = add_options()
    datadir = os.path.join(options.dir, ".cryptobox")
    memory = Memory()
    memory.load(datadir)

    if not options.numdownloadthreads:
        options.numdownloadthreads = 2
    else:
        options.numdownloadthreads = int(options.numdownloadthreads)
    log(options.numdownloadthreads, "downloadthreads")

    if not options.dir:
        exit_app_warning("Need DIR (-f or --dir) to continue")

    if not os.path.exists(options.dir):
        exit_app_warning("DIR [", options.dir, "] does not exist")

    if not options.encrypt and not options.decrypt:
        warning("No encrypt or decrypt directive given (-d or -e)")

    if not options.password:
        exit_app_warning("No password given (-p or --password)")

    if options.username or options.cryptobox:
        if not options.username:
            exit_app_warning("No username given (-u or --username)")
        if not options.cryptobox:
            exit_app_warning("No cryptobox given (-b or --cryptobox)")

    if options.password and options.username and options.cryptobox:
        if authorize_user(options):
            if options.sync:
                if not options.encrypt:
                    exit_app_warning("A sync step should always be followed by an encrypt step (-e or --encrypt)")
                sync_server(options)

    if options.encrypt:
        index_and_encrypt(options)

    if options.decrypt:
        if not options.clear:
            decrypt_and_build_filetree(options)

    if options.clear:
        if options.encrypt:
            exit_app_warning("clear options cannot be used together with encrypt, possible data loss")
            return
        datadir = get_data_dir(options)
        shutil.rmtree(datadir, True)
        log("cleared all meta data in ", get_data_dir(options))

    memory.save(datadir)


if __name__ == '__main__':
    main()

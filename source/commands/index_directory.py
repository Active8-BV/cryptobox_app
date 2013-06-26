#!/usr/bin/python
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
import uuid
import requests
import subprocess
import socket
import urllib
import uuid as _uu
from optparse import OptionParser
import multiprocessing
from Crypto import Random
from Crypto.Hash import SHA, SHA512, HMAC
from Crypto.Cipher import Blowfish
from Crypto.Protocol.KDF import PBKDF2
from os.path import join, dirname, basename, isdir, exists, sep, walk, normpath

g_lock = multiprocessing.Lock()

SERVER = "http://127.0.0.1:8000/"
#SERVER = "https://www.cryptobox.nl/"
DEBUG = True


def warning(*arg):
    sys.stderr.write("\033[91mwarning: " + " ".join([str(s) for s in arg]).strip(" ") + "\033[0m\n")


def strcmp(s1, s2):
    """
    @type s1: str or unicode
    @type s2: str or unicode
    @return: @rtype: bool
    """
    if not s1 or not s2:
        return False
    s1 = s1.strip()
    s2 = s2.strip()
    return s1 == s2


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
    parser.add_option("-x", "--debug", dest="debug", action='store_true',
                      help="drop to debug repl", metavar="DEBUG")
    parser.add_option("-k", "--fake", dest="fake", action='store_true',
                      help="fake server run", metavar="FAKE")

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
    @param exc: Exception
    @param raise_again: bool
    @param return_error: bool
    @return: @rtype: @raise:
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


def pasword_derivation(key, salt):
    """
    @param key:
    @type key: str or unicode
    @param salt:
    @type salt: str or unicode
    @return:
    @rtype: str or unicode
    """
    size = 32 # 16, 24 or 32 bytes long (for AES-128, AES-196 and AES-256, respectively)
    return PBKDF2(key, salt, size)


#noinspection PyArgumentEqualDefault
def encrypt(salt, secret, data):
    """
    @param salt: str or unicode
    @param secret: str or unicode
    @param data:
    @return: @rtype: @raise:
    """
    Random.atfork()

    initialization_vector = Random.new().read(Blowfish.block_size)
    cipher = Blowfish.new(secret, Blowfish.MODE_CBC, initialization_vector)

    pad = lambda s: s + (8 - len(s) % 8) * "{"
    data_hash = make_hash_str(data, secret)
    encoded_data = cipher.encrypt(pad(data))

    encoded_hash = make_hash_str(encoded_data, secret)
    encrypted_data_dict = {
        "salt": salt,
        "hash": data_hash,
        "initialization_vector": initialization_vector,
        "encoded_data": encoded_data
    }
    if strcmp(encoded_hash, data_hash) and len(data.strip()) > 0:
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
    if not isinstance(encrypted_data_dict, dict):
        pass
    if 8 != len(encrypted_data_dict["initialization_vector"]):
        raise Exception("initialization_vector len is not 16")

    cipher = Blowfish.new(secret, Blowfish.MODE_CBC, encrypted_data_dict["initialization_vector"])
    decoded = cipher.decrypt(encrypted_data_dict["encoded_data"]).rstrip("{")

    data_hash = make_hash_str(decoded, secret)

    if "hash" in encrypted_data_dict and hashcheck:
        if len(decoded) > 0:
            if data_hash != encrypted_data_dict["hash"]:
                raise EncryptionHashMismatch("the decryption went wrong, hash didn't match")
    return decoded


def json_object(path, targetobject):
    """
    @type path: str or unicode
    @type targetobject: object
    """
    global DEBUG
    if DEBUG:
        import jsonpickle
        jsonproxy = json.loads(jsonpickle.encode(targetobject))
        json.dump(jsonproxy, open(path + ".json", "w"), sort_keys=True, indent=4, separators=(',', ': '))


def pickle_object(path, targetobject, json_pickle=False):
    """
    @type path: str or unicode
    @type targetobject: object
    @type json_pickle: bool
    """
    cPickle.dump(targetobject, open(path, "wb"), cPickle.HIGHEST_PROTOCOL)
    if json_pickle:
        if isinstance(targetobject, dict):
            json_object(path, targetobject)
        else:
            json_object(path, targetobject)


def unpickle_object(path):
    """
    @type path: str or unicode
    @return: @rtype:
    """
    return cPickle.load(open(path, "rb"))


def encrypt_object(salt, secret, obj):
    """
    @type salt: str or unicode
    @type secret: str or unicode
    @type obj: str or unicode
    @return: @rtype:
    """
    encrypted_dict = encrypt(salt, secret, cPickle.dumps(obj, cPickle.HIGHEST_PROTOCOL))
    return base64.b64encode(cPickle.dumps(encrypted_dict)).strip()


def decrypt_object(secret, obj_string, key=None, returnsecret_cb=None):
    """
    @type secret: str or unicode
    @type obj_string: str
    @type key: str or unicode
    @type returnsecret_cb: __builtin__.function
    @return: @rtype:
    """
    data = cPickle.loads(base64.b64decode(obj_string))
    if key:
        secret = pasword_derivation(key, data["salt"])
        if returnsecret_cb:
            returnsecret_cb(secret)
    return cPickle.loads(decrypt(secret, data, hashcheck=False))


def write_file(path, data, a_time, m_time, st_mode, st_uid, st_gid):
    """
    @type path: unicode
    @type data: str or unicode
    @type a_time: int
    @type m_time: int
    @type st_mode: __builtin__.NoneType
    @type st_uid: __builtin__.NoneType
    @type st_gid: __builtin__.NoneType
    """
    fout = open(path, "wb")
    fout.write(data)
    fout.close()
    os.utime(path, (a_time, m_time))
    if st_mode:
        os.chmod(path, st_mode)
    if st_uid and st_gid:
        os.chown(path, st_uid, st_gid)


def read_file(path):
    """
    @type path: str or unicode
    @return: @rtype:
    """
    data = open(path, "rb").read()
    stats = os.stat(path)
    return data, stats.st_ctime, stats.st_atime, stats.st_mtime, stats.st_mode, stats.st_uid, stats.st_gid


def read_file_to_fdict(path):
    """
    @type path: str or unicode
    @return: @rtype:
    """
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
    """
    @param fdict: dict
    @param path: str or unicode
    """
    write_file(path, fdict["data"], fdict["st_atime"], fdict["st_mtime"], fdict["st_mode"], fdict["st_uid"], fdict["st_gid"])


last_update_string_len = 0


def update_progress(curr, total, msg):
    """
    @type curr: int
    @type total: int
    @type msg: str or unicode
    @return: @rtype:
    """
    global last_update_string_len
    if total == 0:
        return
    progress = int(math.ceil(float(curr) / (float(total) / 100)))
    if progress > 100:
        progress = 100
    msg = msg + " " + str(curr) + "/" + str(total)
    update_string = "\r\033[94m[{0}{1}] {2}% {3}\033[0m".format(progress / 2 * "#", (50 - progress / 2) * " ", progress, msg)
    if len(update_string) < last_update_string_len:
        sys.stderr.write("\r\033[94m{0}\033[0m".format(" " * 100))
    sys.stderr.write(update_string)
    last_update_string_len = len(update_string)


def ensure_directory(path):
    """
    @type path: str or unicode or unicode
    """
    if not exists(path):
        os.makedirs(path)


def make_cryptogit_hash(fpath, datadir, cryptobox_index):
    """
    @type fpath: str or unicode
    @type datadir: str or unicode
    @type cryptobox_index: dict
    @return: @rtype:
    """
    file_dict = read_file_to_fdict(fpath)
    filehash = make_sha1_hash("blob " + str(len(file_dict["data"])) + "\0" + str(file_dict["data"]))
    blobdir = join(join(datadir, "blobs"), filehash[:2])
    blobpath = join(blobdir, filehash[2:])
    filedata = {"filehash": filehash, "fpath": fpath, "blobpath": blobpath, "blobdir": blobdir}
    filedata["blob_exists"] = exists(blobpath)
    del file_dict["data"]
    cryptobox_index["filestats"][fpath] = file_dict
    return filedata


def read_and_encrypt_file(fpath, blobpath, salt, secret):
    """
    @type fpath: str or unicode
    @type blobpath: str or unicode
    @type salt: str or unicode
    @type secret: str or unicode
    @return: @rtype:
    """
    try:
        file_dict = read_file_to_fdict(fpath)
        encrypted_file_dict = encrypt(salt, secret, file_dict["data"])
        pickle_object(blobpath, encrypted_file_dict, json_pickle=False)
        return None
    except Exception, e:
        handle_exception(e)


def decrypt_file_and_write(fpath, unenc_path, secret):
    """
    @type fpath: str or unicode
    @type unenc_path: str or unicode
    @type secret: str or unicode
    @return: @rtype:
    """
    try:
        encrypted_file_dict = unpickle_object(fpath)
        unencrypted_file_dict = decrypt(secret, encrypted_file_dict)
        open(unenc_path, "wb").write(unencrypted_file_dict)
        return None
    except Exception, e:
        handle_exception(e)


def encrypt_new_blobs(salt, secret, new_blobs):
    """
    @type salt: str or unicode
    @type secret: str or unicode
    @type new_blobs: dict
    """
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
    return join(options.dir, ".cryptobox")


def get_blob_dir(options):
    datadir = get_data_dir(options)
    return join(datadir, "blobs")


class MemoryNoKey(Exception):
    pass


class MemoryExpired(Exception):
    pass


class ListNameClash(Exception):
    pass


class ListDoesNotExist(Exception):
    pass


class MemoryCorruption(Exception):
    pass


class Memory(object):
    _instance = None
    data = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            # noinspection PyArgumentList
            cls._instance = super(Memory, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def set(self, key, value):
        if key in self.data:
            raise MemoryCorruption("overwrite of " + str(key))
        self.data[key] = value

    def get(self, key):
        if self.has(key):
            return self.data[key]
        else:
            raise MemoryNoKey(str(key))

    def delete(self, key):
        if self.has(key):
            del self.data[key]
        else:
            raise MemoryNoKey(str(key))

    def has(self, key):
        return key in self.data

    def replace(self, key, value):
        if self.has(key):
            self.delete(key)
        self.set(key, value)

    def size(self):
        return len(self.data)

    def save(self, datadir):
        if exists(datadir):
            mempath = join(datadir, "memory.pickle")
            pickle_object(mempath, self.data, json_pickle=True)

    def load(self, datadir):
        mempath = join(datadir, "memory.pickle")
        if exists(mempath):
            self.data = unpickle_object(mempath)

            for k in self.data.copy():
                try:
                    self.has(k)
                except MemoryExpired:
                    pass

    def _set_add_value(self, list_name, value):
        if not self.has(list_name):
            self.set(list_name, set())
        collection = self.get(list_name)
        if not isinstance(collection, set):
            raise ListNameClash(collection + " is not a list")
        collection.add(value)

    def _set_have_value(self, list_name, value):
        if not self.has(list_name):
            self.set(list_name, set())
            return False
        collection = self.get(list_name)
        return value in collection

    def _set_delete_value(self, list_name, value):
        if not self.has(list_name):
            return False
        collection = self.get(list_name)
        collection.remove(value)
        return True


def get_cryptobox_index():
    memory = Memory()
    if memory.has("cryptobox_index"):
        return memory.get("cryptobox_index")
    else:
        return dict()


class NoLocalIndex(Exception):
    pass


def get_local_index():
    memory = Memory()
    if not memory.has("localindex"):
        raise NoLocalIndex("there is no localindex yet")
    return memory.get("localindex")


def store_cryptobox_index(index):
    memory = Memory()
    memory.replace("cryptobox_index", index)


def cryptobox_locked():
    current_cryptobox_index = get_cryptobox_index()
    if current_cryptobox_index:
        if current_cryptobox_index["locked"] is True:
            return True
    return False


def get_secret(options):
    password = options.password
    current_cryptobox_index = get_cryptobox_index()
    if current_cryptobox_index:
        salt = base64.decodestring(current_cryptobox_index["salt_b64"])
    else:
        salt = Random.new().read(32)
    return salt, pasword_derivation(password, salt)


def get_uuid(size):
    """
    make a human readable unique identifier
    @param size:
    """
    unique_id = _uu.uuid4().int
    alphabet = "bcdfghjkmnpqrstvwxz"
    alphabet_length = len(alphabet)
    output = ""
    while unique_id > 0:
        digit = unique_id % alphabet_length
        output += alphabet[digit]
        unique_id = int(unique_id / alphabet_length)
    return output[0:size]


def index_files_visit(arg, dir_name, names):
    """
    @type arg: dict
    @type dir_name: str or unicode
    @type names: list
    """
    filenames = [basename(x) for x in filter(lambda x: not isdir(x), [join(dir_name, x.lstrip(sep)) for x in names])]
    dirname_hash = make_sha1_hash(dir_name.replace(arg["DIR"], "").replace(sep, "/"))
    nameshash = make_sha1_hash("".join(names))
    folder = {}
    folder["dirname"] = dir_name
    folder["dirnamehash"] = dirname_hash
    folder["filenames"] = [{'name': x} for x in filenames]
    folder["nameshash"] = nameshash

    arg["folders"]["dirnames"][dirname_hash] = folder
    arg["numfiles"] += len(filenames)


def make_local_index(options):
    datadir = get_data_dir(options)
    args = {}
    args["DIR"] = options.dir
    args["folders"] = {"dirnames": {}, "filestats": {}}
    args["numfiles"] = 0
    walk(options.dir, index_files_visit, args)
    for dir_name in args["folders"]["dirnames"].copy():
        if datadir in args["folders"]["dirnames"][dir_name]["dirname"]:
            del args["folders"]["dirnames"][dir_name]
    cryptobox_index = args["folders"]
    return cryptobox_index


def index_and_encrypt(options):
    datadir = get_data_dir(options)

    if cryptobox_locked():
        warning("cryptobox is locked, nothing can be added now first decrypt (-d)")
        return None, None

    salt, secret = get_secret(options)

    cryptobox_index = get_local_index()

    ensure_directory(datadir)

    if len(cryptobox_index["dirnames"]) > 0:
        numfiles = reduce(lambda x, y: x + y, [len(cryptobox_index["dirnames"][x]["filenames"]) for x in cryptobox_index["dirnames"]])
    else:
        numfiles = 0
    new_blobs = {}
    file_cnt = 0
    new_objects = 0
    hash_set_on_disk = set()

    for dirhash in cryptobox_index["dirnames"]:
        for fname in cryptobox_index["dirnames"][dirhash]["filenames"]:
            file_cnt += 1
            file_dir = cryptobox_index["dirnames"][dirhash]["dirname"]
            file_path = join(file_dir, fname["name"])
            if exists(file_path):
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

    if options.remove:
        cryptobox_index["locked"] = True
    else:
        cryptobox_index["locked"] = False
    cryptobox_index["salt_b64"] = base64.encodestring(salt)

    store_cryptobox_index(cryptobox_index)

    if options.remove:
        ld = os.listdir(options.dir)
        ld.remove(".cryptobox")
        for fname in ld:
            fpath = join(options.dir, fname)
            if isdir(fpath):
                shutil.rmtree(fpath, True)
            else:
                os.remove(fpath)

    obsolute_blob_store_entries = set()
    blob_dirs = join(datadir, "blobs")
    ensure_directory(blob_dirs)
    for blob_dir in os.listdir(blob_dirs):
        blob_store = join(blob_dirs, blob_dir.lstrip(sep))
        if isdir(blob_store):
            for blob_file in os.listdir(blob_store):
                found = False
                for fhash in hash_set_on_disk:
                    if strcmp(fhash, (blob_dir + blob_file)):
                        found = True
                if not found:
                    obsolute_blob_store_entries.add(blob_dir + blob_file)

    for f_hash in obsolute_blob_store_entries:
        blob_dir = join(blob_dirs, f_hash[:2])
        blob_path = join(blob_dir, f_hash[2:])
        os.remove(blob_path)
        if isdir(blob_dir):
            blob_entries = [f for f in os.listdir(blob_dir) if not f.startswith('.')]
            if len(blob_entries) == 0:
                shutil.rmtree(blob_dir, True)
    if numfiles > 0:
        print
    return salt, secret


def decrypt_write_file(cryptobox_index, fdir, fhash, secret):
    """
    @param cryptobox_index: dict
    @param fdir: str or unicode
    @param fhash: str or unicode
    @param secret: str or unicode
    """
    blob_enc = unpickle_object(join(fdir, fhash[2:]))
    file_blob = {}
    file_blob["data"] = decrypt(secret, blob_enc, True)
    for dirhash in cryptobox_index["dirnames"]:
        for cfile in cryptobox_index["dirnames"][dirhash]["filenames"]:
            if strcmp(fhash, cfile["hash"]):
                fpath = join(cryptobox_index["dirnames"][dirhash]["dirname"], cfile["name"])
                if not exists(fpath):
                    ft = cryptobox_index["filestats"][fpath]
                    file_blob["st_atime"] = int(ft["st_atime"])
                    file_blob["st_mtime"] = int(ft["st_mtime"])
                    file_blob["st_mode"] = int(ft["st_mode"])
                    file_blob["st_uid"] = int(ft["st_uid"])
                    file_blob["st_gid"] = int(ft["st_gid"])
                    write_fdict_to_file(file_blob, fpath)


def decrypt_blob_to_filepaths(blobdir, cryptobox_index, fhash, secret):
    """
    @param blobdir: str or unicode
    @param cryptobox_index: dict
    @param fhash: str or unicode
    @param secret: str or unicode
    """
    try:
        fdir = join(blobdir, fhash[:2])
        decrypt_write_file(cryptobox_index, fdir, fhash, secret)

    except Exception, e:
        handle_exception(e, False)


#datadir = get_data_dir(options)

def decrypt_and_build_filetree(options):
    password = options.password
    datadir = get_data_dir(options)
    if not exists(datadir):
        warning("nothing to decrypt", datadir, "does not exists")
        return
    blobdir = join(datadir, "blobs")

    cryptobox_index = get_cryptobox_index()
    if cryptobox_index:
        if not cryptobox_locked():
            return
    else:
        cryptobox_index = None
    hashes = set()
    if cryptobox_index:
        for dirhash in cryptobox_index["dirnames"]:
            if "dirname" in cryptobox_index["dirnames"][dirhash]:
                if not exists(cryptobox_index["dirnames"][dirhash]["dirname"]):
                    ensure_directory(cryptobox_index["dirnames"][dirhash]["dirname"])
            for cfile in cryptobox_index["dirnames"][dirhash]["filenames"]:
                fpath = join(cryptobox_index["dirnames"][dirhash]["dirname"], cfile["name"])
                if not exists(fpath):
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
        cryptobox_index["locked"] = False
    store_cryptobox_index(cryptobox_index)
    if len(hashes) > 0:
        print


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


def on_server(method, cryptobox, payload, session, files=None):
    """
    @type method: str or unicode
    @type cryptobox: str or unicode
    @type payload: dict or None
    @type session: requests.sessions.Session or None
    @return: @rtype:
    """
    global SERVER
    cookies = dict(c_persist_fingerprint_client_part=fingerprint())
    SERVICE = SERVER + cryptobox + "/" + method + "/" + str(time.time())
    print SERVICE
    if not session:
        session = requests
    if not payload:
        result = session.post(SERVICE, cookies=cookies, files=files)
    elif files:
        result = session.post(SERVICE, data=payload, cookies=cookies, files=files)
    else:
        result = session.post(SERVICE, data=json.dumps(payload), cookies=cookies)
    return parse_http_result(result)


def download_server(options, url):
    global SERVER
    cookies = dict(c_persist_fingerprint_client_part=fingerprint())
    url = normpath(url)
    URL = SERVER + options.cryptobox + "/" + url
    #log("download server:", URL)
    memory = Memory()
    session = memory.get("session")
    result = session.get(URL, cookies=cookies)
    return parse_http_result(result)


def server_time(cryptobox):
    return float(on_server("clock", cryptobox, payload=None, session=None)[0])


class PasswordException(Exception):
    pass


def authorize(username, password, cryptobox):
    """
    @type username: str or unicode
    @type password: str or unicode
    @type cryptobox: str or unicode
    @return: @rtype: @raise:
    """
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
    """
    @type session: requests.sessions.Session
    @type results: dict
    @return: @rtype:
    """
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
        memory.set("session", session)
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
    blobdir = join(get_blob_dir(options), blob_hash[:2])
    blobpath = join(blobdir, blob_hash[2:])
    return exists(blobpath)


class NoTimeStamp(Exception):
    pass


def write_blob_to_filepath(node, options, data):
    """
    @type node: dict
    @type options: optparse.Values
    @type data: str or unicode
    """

    if not node["content_hash_latest_timestamp"][1]:
        raise NoTimeStamp(str(node))
    st_mtime = int(node["content_hash_latest_timestamp"][1])
    dirname_of_path = dirname(node["doc"]["m_path"])
    new_path = join(options.dir, join(dirname_of_path.lstrip(sep), node["doc"]["m_name"]))
    add_local_file_history(new_path)
    write_file(path=new_path, data=data, a_time=st_mtime, m_time=st_mtime, st_mode=None, st_uid=None, st_gid=None)


def write_blobs_to_filepaths(options, file_nodes, data, downloaded_fhash):
    """
    @type options: optparse.Values
    @type file_nodes: list
    @type data: str or unicode
    @type downloaded_fhash: unicode
    """
    files_same_hash = []

    for sfile in file_nodes:
        fhash = sfile["content_hash_latest_timestamp"][0]
        if strcmp(fhash, downloaded_fhash):
            files_same_hash.append(sfile)
    for fnode in files_same_hash:
        add_server_file_history(fnode["doc"]["m_path"])
        write_blob_to_filepath(fnode, options, data)


# noinspection PyUnusedLocal
def download_server_stub(options, url):
    class O(object):
        def __init__(self):
            self.url = ""
            self.content = ""

    o = O()
    o.url = url
    o.content = "hello"
    return o


def download_blob(options, node):
    try:
        url = "download/" + node["doc"]["m_short_id"]
        result = download_server(options, url)
        return {"url": result.url, "content_hash": node["content_hash_latest_timestamp"][0], "content": result.content}
    except Exception, e:
        handle_exception(e)


def get_unique_content(options, all_unique_nodes, local_file_paths):
    """
    @type options: optparse.Values
    @type all_unique_nodes: dict
    @type local_file_paths: list
    """
    if len(local_file_paths) == 0:
        return
    unique_nodes_hashes = [fhash for fhash in all_unique_nodes if not have_blob(options, fhash)]
    unique_nodes = [all_unique_nodes[fhash] for fhash in all_unique_nodes if fhash in unique_nodes_hashes]
    pool = multiprocessing.Pool(processes=options.numdownloadthreads)
    downloaded_files = []

    # noinspection PyUnusedLocal
    def done_downloading(result):
        write_blobs_to_filepaths(options, local_file_paths, result["content"], result["content_hash"])
        downloaded_files.append(result["url"])
        update_progress(len(downloaded_files), len(unique_nodes), "downloading")

    download_results = []

    unique_nodes = [node for node in unique_nodes if not exists(join(options.dir, node["doc"]["m_path"].lstrip(sep)))]
    for node in unique_nodes:
        result = pool.apply_async(download_blob, (options, node), callback=done_downloading)
        download_results.append(result)
    pool.close()
    pool.join()
    for result in download_results:
        if not result.successful():
            result.get()
    pool.terminate()


def server_file_history_setup(relative_path_name):
    memory = Memory()
    relative_path_name = relative_path_name.replace(memory.get("cryptobox_folder"), "")
    fnode_path_id = relative_path_name.replace(sep, "/")
    return fnode_path_id, memory


def have_serverhash(fnodehash):
    memory = Memory()
    return memory._set_have_value("serverhash_history", fnodehash)


def in_server_file_history(relative_path_name):
    fnode_path_id, memory = server_file_history_setup(relative_path_name)
    return have_serverhash(fnode_path_id)


def add_server_file_history(relative_path_name):
    fnode_path_id, memory = server_file_history_setup(relative_path_name)
    memory._set_add_value("serverhash_history", fnode_path_id)


def del_serverhash(fnode_hash):
    memory = Memory()
    if memory._set_have_value("serverhash_history", fnode_hash):
        memory._set_delete_value("serverhash_history", fnode_hash)


def del_server_file_history(relative_path_name):
    fnode_path_id, memory = server_file_history_setup(relative_path_name)
    del_serverhash(fnode_path_id)


def add_local_file_history(relative_path_name):
    fnode_hash, memory = server_file_history_setup(relative_path_name)
    memory._set_add_value("localpath_history", fnode_hash)


def in_local_file_history(relative_path_name):
    fnode_hash, memory = server_file_history_setup(relative_path_name)
    return memory._set_have_value("localpath_history", fnode_hash)


def del_local_file_history(relative_path_name):
    fnode_path_id, memory = server_file_history_setup(relative_path_name)
    if memory._set_have_value("localpath_history", fnode_path_id):
        memory._set_delete_value("localpath_history", fnode_path_id)


def sync_directories_with_server(options, serverindex, dirname_hashes_server, unique_dirs):
    fake = options.fake

    localindex = get_local_index()
    local_dirs_not_on_server = []
    for dirhashlocal in localindex["dirnames"]:
        found = False
        for dirhashserver in dirname_hashes_server:
            if strcmp(dirhashserver, localindex["dirnames"][dirhashlocal]["dirnamehash"]):
                found = True
        if not found:
            if localindex["dirnames"][dirhashlocal]["dirname"] != options.dir:
                local_dirs_not_on_server.append(localindex["dirnames"][dirhashlocal])
    dirs_to_make_on_server = []
    dirs_to_remove_locally = []
    for node in local_dirs_not_on_server:
        if float(os.stat(node["dirname"]).st_mtime) >= float(serverindex["tree_timestamp"]):
            dirs_to_make_on_server.append(node)
        elif have_serverhash(node["dirnamehash"]):
            dirs_to_remove_locally.append(node)
        else:
            dirs_to_make_on_server.append(node)
    memory = Memory()
    cryptobox = options.cryptobox
    payload = {}
    payload["foldernames"] = [dir_name["dirname"].replace(options.dir, "") for dir_name in dirs_to_make_on_server]
    for dir_name in payload["foldernames"]:
        log("add server", dir_name)
        if not fake:
            add_server_file_history(dir_name)
    if not fake and len(payload["foldernames"]) > 0:
        on_server("docs/makefolder", cryptobox=cryptobox, payload=payload, session=memory.get("session")).json()
    for node in dirs_to_remove_locally:
        log("remove local", node["dirname"])
        if exists(node["dirname"]):
            if not fake:
                shutil.rmtree(node["dirname"], True)
    on_server_not_local = [np for np in [join(options.dir, np.lstrip("/")) for np in unique_dirs] if not exists(np)]
    dir_names_to_delete_on_server = []
    for dir_name in on_server_not_local:
        dirname_rel = dir_name.replace(options.dir, "")
        if in_server_file_history(dirname_rel):
            dir_names_to_delete_on_server.append(dirname_rel)
        else:
            log("add local:", dir_name)
            if not fake:
                ensure_directory(dir_name)
                add_server_file_history(dirname_rel)
    short_node_ids_to_delete = []
    shortest_paths = set()
    for drl1 in dir_names_to_delete_on_server:
        shortest = ""
        for drl2 in dir_names_to_delete_on_server:
            if drl2 in drl1 or drl1 in drl2:
                if len(drl2) < len(shortest) or len(shortest) == 0:
                    shortest = drl2
        shortest_paths.add(shortest)
    for dir_name_rel in shortest_paths:
        log("remove server:", dir_name_rel)
        if not fake:
            del_serverhash(dir_name_rel)
        short_node_ids_to_delete.extend([node["doc"]["m_short_id"] for node in serverindex["doclist"] if node["doc"]["m_path"] == dir_name_rel])
    if len(short_node_ids_to_delete) > 0:
        payload = {}
        payload["tree_item_list"] = short_node_ids_to_delete
        if not fake:
            on_server("docs/delete", cryptobox=cryptobox, payload=payload, session=memory.get("session")).json()


def upload_file(options, file_object, parent):
    memory = Memory()
    if not memory.has("session"):
        raise NotAuthorized("trying to upload without a session")
    payload = {"uuid": uuid.uuid4().hex, "parent": parent, "path": ""}
    files = {'file': file_object}
    on_server("docs/upload", cryptobox=options.cryptobox, payload=payload, session=memory.get("session"), files=files)


def save_encode_b64(s):
    s = urllib.quote(s)
    s = base64.encodestring(s)
    s = s.replace("=", "-")
    return s


class MultipleGuidsForPath(Exception):
    pass


class NoParentFound(Exception):
    pass


def path_to_server_parent_guid(options, path):
    memory = Memory()
    path = path.replace(options.dir, "")
    path = dirname(path)
    result = [x["doc"]["m_short_id"] for x in memory.get("serverindex")["doclist"] if strcmp(x["doc"]["m_path"], path)]
    if len(result) == 0:
        raise NoParentFound(path)
    elif len(result) == 1:
        return result[0]
    else:
        raise MultipleGuidsForPath(path)


def sync_server(options):
    """
    @type options: optparse.Values
    @return: @rtype: @raise:
    """
    fake = options.fake
    if cryptobox_locked():
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
    serverindex = result[1]
    memory.replace("serverindex", serverindex)
    unique_content = {}
    unique_dirs = set()
    fnodes = []

    checked_dirnames = []
    dirname_hashes_server = {}
    for node in serverindex["doclist"]:
        if node["doc"]["m_nodetype"] == "folder":
            dirname_of_path = node["doc"]["m_path"]
        else:
            dirname_of_path = dirname(node["doc"]["m_path"])
        node["dirname_of_path"] = dirname_of_path
        unique_dirs.add(dirname_of_path)
        if node["content_hash_latest_timestamp"]:
            unique_content[node["content_hash_latest_timestamp"][0]] = node
            fnodes.append(node)

        if dirname_of_path not in checked_dirnames:
            dirname_hash = make_sha1_hash(dirname_of_path.replace(sep, "/"))
            dirname_hashes_server[dirname_hash] = node
        checked_dirnames.append(dirname_of_path)

    sync_directories_with_server(options, serverindex, dirname_hashes_server, unique_dirs)

    localindex = get_local_index()

    local_paths_to_delete_on_server = []
    new_server_files_to_local_paths = []
    for fnode in fnodes:
        server_path_to_local = join(options.dir, fnode["doc"]["m_path"].lstrip(sep))

        if exists(server_path_to_local):
            add_local_file_history(server_path_to_local)
        else:
            if in_local_file_history(server_path_to_local):
                local_paths_to_delete_on_server.append(server_path_to_local)
            else:
                log("new file on server", server_path_to_local)
                new_server_files_to_local_paths.append(fnode)

    local_filenames = [(localindex["dirnames"][d]["dirname"], localindex["dirnames"][d]["filenames"]) for d in localindex["dirnames"] if len(localindex["dirnames"][d]["filenames"]) > 0]
    local_filenames_set = set()
    for ft in local_filenames:
        for fname in ft[1]:
            if not str(fname["name"]).startswith("."):
                local_file = join(ft[0], fname["name"])
                local_filenames_set.add(local_file)
    for local_file_path in local_filenames_set:
        if exists(local_file_path):
            print local_file_path
            if not in_local_file_history(local_file_path):
                parent = path_to_server_parent_guid(options, local_file_path)
                if parent:
                    log("new file on disk", local_file_path, parent)
                    upload_file(options, open(local_file_path, "rb"), parent)

    get_unique_content(options, unique_content, new_server_files_to_local_paths)

    delete_file_guids = []
    for fpath in local_paths_to_delete_on_server:
        relpath = fpath.replace(options.dir, "")
        guids = [x["doc"]["m_short_id"] for x in serverindex["doclist"] if x["doc"]["m_path"] == relpath]

        if len(guids) == 1:
            log("delete file from server", fpath)
            delete_file_guids.append(guids[0])
    if len(delete_file_guids) > 0:
        payload = {}
        payload["tree_item_list"] = delete_file_guids
        if not fake:
            on_server("docs/delete", cryptobox=cryptobox, payload=payload, session=memory.get("session")).json()
    for fpath in local_paths_to_delete_on_server:
        del_server_file_history(fpath)
        del_local_file_history(fpath)


def restore_hidden_config(options):
    hidden_configs = [x for x in os.listdir(options.basedir) if x.endswith(".cryptoboxfolder")]
    hidden_configs_dict = {}
    dsecret = {}

    def return_secret(s):
        dsecret[s] = s

    for config in hidden_configs:
        # noinspection PyBroadException
        try:
            config_file_path = join(options.basedir, config)
            config_stat = os.stat(config_file_path)
            obj = unpickle_object(config_file_path)
            obj = decrypt_object("", key=options.password, obj_string=obj, returnsecret_cb=return_secret)
            hidden_configs_dict[config_stat.st_mtime] = (obj, config)
        except:
            pass
    secret = None
    if len(dsecret) > 0:
        for k in dsecret:
            secret = dsecret[k]
    sorted_keys = sorted(hidden_configs_dict.keys())
    sorted_keys.reverse()
    if len(sorted_keys) > 0:
        hidden_config = hidden_configs_dict[sorted_keys[0]]
        sorted_keys.remove(sorted_keys[0])
        for cf in sorted_keys:
            old_config = hidden_configs_dict[cf]
            guid = old_config[1].split(".")[1]
            if exists(join(options.basedir, old_config[1])):
                os.remove(join(options.basedir, old_config[1]))
            if exists(join(options.basedir, guid)):
                shutil.rmtree(join(options.basedir, guid), True)
        guid = hidden_config[1].split(".")[1]
        if exists(join(options.basedir, guid)):
            os.rename(join(options.basedir, guid), join(options.basedir, hidden_config[0]))
        if exists(join(options.basedir, hidden_config[1])):
            os.remove(join(options.basedir, hidden_config[1]))

    if secret:
        datadir = get_data_dir(options)
        mempath = join(datadir, "memory.pickle")
        if exists(mempath + ".enc"):
            decrypt_file_and_write(mempath + ".enc", mempath, secret=secret)
            os.remove(mempath + ".enc")


def hide_config(options, salt, secret):
    if options.encrypt and options.remove and salt and secret:
        datadir = get_data_dir(options)
        mempath = join(datadir, "memory.pickle")
        read_and_encrypt_file(mempath, mempath + ".enc", salt, secret)
        os.remove(mempath)

        hidden_name = get_uuid(3)
        while hidden_name in os.listdir(options.dir):
            hidden_name = get_uuid(3)
        encrypted_name = encrypt_object(salt, secret, options.cryptobox)
        pickle_object(join(options.basedir, "." + hidden_name + ".cryptoboxfolder"), encrypted_name)
        os.rename(options.dir, join(dirname(options.dir), hidden_name))


def interact():
    import code
    # noinspection PyUnresolvedReferences
    import readline
    myglobals = globals()
    myglobals["m"] = Memory()
    myglobals["md"] = myglobals["m"].data
    code.InteractiveConsole(locals=myglobals).interact()


def main():
    (options, args) = add_options()
    if options.fake:
        log("doing fake server operations")
    if not options.numdownloadthreads:
        options.numdownloadthreads = multiprocessing.cpu_count() * 2
    else:
        options.numdownloadthreads = int(options.numdownloadthreads)

    if not options.dir:
        exit_app_warning("Need DIR (-f or --dir) to continue")
    if not options.cryptobox:
        exit_app_warning("No cryptobox given (-b or --cryptobox)")

    options.basedir = options.dir
    options.dir = join(options.dir, options.cryptobox)

    datadir = get_data_dir(options)

    restore_hidden_config(options)

    memory = Memory()
    memory.load(datadir)
    memory.replace("cryptobox_folder", options.dir)

    if options.debug:
        log("drop to repl")
        interact()
        exit_app_warning("done with repl")

    try:
        if not exists(options.basedir):
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

        if options.sync:
            if not options.username:
                exit_app_warning("No username given (-u or --username)")
            if not options.password:
                exit_app_warning("No password given (-p or --password)")

        if not cryptobox_locked():
            localindex = make_local_index(options)
            memory.replace("localindex", localindex)

        if options.password and options.username and options.cryptobox:
            if authorize_user(options):
                if options.sync:
                    if not options.encrypt:
                        exit_app_warning("A sync step should always be followed by an encrypt step (-e or --encrypt)")

                    if cryptobox_locked():
                        exit_app_warning("cryptobox is locked, nothing can be added now first decrypt (-d)")

                    ensure_directory(options.dir)
                    sync_server(options)

        salt = None
        secret = None
        if options.encrypt:
            salt, secret = index_and_encrypt(options)

        if options.decrypt:
            if options.remove:
                exit_app_warning("option remove (-r) cannot be used together with decrypt (dataloss)")
            if not options.clear:
                decrypt_and_build_filetree(options)

        if options.clear:
            if options.encrypt:
                exit_app_warning("clear options cannot be used together with encrypt, possible data loss")
                return
            datadir = get_data_dir(options)
            shutil.rmtree(datadir, True)
            log("cleared all meta data in ", get_data_dir(options))
    finally:
        memory.save(datadir)

    hide_config(options, salt, secret)


if strcmp(__name__, '__main__'):
    main()

# coding=utf-8
"""
crypto routines for the commandline tool
"""
import re
import os
import json
import base64
import time
import multiprocessing
import cPickle
from cStringIO import StringIO
import jsonpickle
from Crypto import Random
from Crypto.Hash import SHA, SHA512, HMAC
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from cba_utils import run_in_pool, DEBUG


def make_sha1_hash(data):
    """ make hash
    @param data:
    @type data:
    """
    sha = SHA.new()
    sha.update(data)
    return sha.hexdigest()


def make_hash(data):
    """ make hash
    @param data:
    @type data:
    """
    sha = SHA512.new(data)
    return sha.hexdigest()


def make_hash_str(data, secret):
    """ make hash
    @param data: data to hash
    @type data: dict, list, str, unicode
    @param secret: secret used for hmac
    @type secret: dict, list, str, unicode
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


def password_derivation(key, salt):
    """
    @param key:
    @type key: str or unicode
    @param salt:
    @type salt: str or unicode
    @return:
    @rtype: str or unicode
    """

    # 16, 24 or 32 bytes long (for AES-128, AES-196 and AES-256, respectively)
    size = 32
    return PBKDF2(key, salt, size)


class EncryptionHashMismatch(Exception):
    """
    EncryptionHashMismatch
    """
    pass


def decrypt_file(secret, encrypted_data, data_hash, initialization_vector, chunk_sizes, perc_callback=None, perc_callback_freq=0.5):
    """
    @param secret: generated secret pkdf2
    @type secret: str
    @param data_hash: hash of first chunk
    @type data_hash: str
    @param initialization_vector: init vector cipher
    @type initialization_vector: str
    @param chunk_sizes: sizes of the chunks
    @type chunk_sizes: list, dict
    @param encrypted_data: the encrypted data
    @type encrypted_data: file, StringIO
    @param perc_callback: callback progress
    @type perc_callback: function
    @param perc_callback_freq: callback frequency
    @type perc_callback_freq: float
    @return: orignal data temporary file
    @rtype: file
    """
    cnt = 0

    if not secret:
        raise Exception("no secret in decrypt file")

    if 16 != len(initialization_vector):
        raise Exception("initialization_vector len is not 16")

    lc_time = time.time()
    dec_file = StringIO()
    cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)

    while True:
        if cnt >= chunk_sizes["length"]:
            break

        if cnt < chunk_sizes["length"]:
            decrypted_chunk = chunk_sizes["default"][0]
            encrypted_chunk = chunk_sizes["default"][1]
        else:
            decrypted_chunk = chunk_sizes["last"][0]
            encrypted_chunk = chunk_sizes["last"][1]

        chunk = encrypted_data.read(encrypted_chunk)
        dec_data = cipher.decrypt(chunk)
        dec_data = dec_data[0:decrypted_chunk]
        dec_file.write(dec_data)
        if cnt <= 0:
            calculated_hash = make_hash_str(dec_data, secret)

            if data_hash != calculated_hash:
                raise EncryptionHashMismatch("decrypt_file -> the decryption went wrong, hash didn't match")

        cnt += 1

        if perc_callback:
            if time.time() - lc_time > perc_callback_freq:
                perc_callback(cnt / (float(chunk_sizes["length"]) / 100))
                lc_time = time.time()

    dec_file.seek(0)
    if perc_callback:
        perc_callback(100.0)

    return dec_file


#noinspection PyDictCreation,PyPep8Naming
def encrypt_file(secret, fin, total=None, perc_callback=None, perc_callback_freq=0.5):
    """
    @param secret: pkdf2 secre
    @type secret: str
    @param fin: file object
    @type fin: file, FileIO
    @param total: size of the object in bytes
    @type total: int, None
    @param perc_callback: progress callback
    @type perc_callback: function
    @param perc_callback_freq: time between progress calls
    @type perc_callback_freq: float
    @return: salt, hash, init, chunk sizes and encrypted data temp file
    @rtype: tuple
    """
    cnt = 0
    CHUNKSIZE = 1024 * 1024 * 1
    lc_time = time.time()

    if not total:
        fin.seek(0, os.SEEK_END)
        total = fin.tell()
        fin.seek(0)
    Random.atfork()
    total = int(total)
    fin.seek(0)
    enc_file = StringIO()
    data_hash = ""
    initialization_vector = Random.new().read(AES.block_size)
    cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
    chunk_sizes_d = {}
    chunk_sizes_d["length"] = 0
    chunk_sizes_d["default"] = None
    chunk_sizes_d["last"] = None
    enc_data = ""
    chunk = ""

    while True:
        pre_read_chunk = chunk
        chunk = fin.read(CHUNKSIZE)

        if chunk == "":
            chunk_sizes_d["last"] = (len(pre_read_chunk), len(enc_data))
            chunk_sizes_d["length"] = cnt
            break

        enc_data = cipher.encrypt(chunk)

        if cnt <= 0:
            data_hash = make_hash_str(chunk, secret)
            chunk_sizes_d["last"] = chunk_sizes_d["default"] = (len(chunk), len(enc_data))
        enc_file.write(enc_data)
        cnt += 1

        if perc_callback:
            if (time.time() - lc_time) > perc_callback_freq:
                perc = ((cnt * CHUNKSIZE) / (float(total) / 100))
                perc_callback(perc)
                lc_time = time.time()

        if len(chunk) == total:
            chunk_sizes_d["last"] = (len(chunk), len(enc_data))
            chunk_sizes_d["length"] = cnt
            break
    enc_file.seek(0)
    if perc_callback:
        perc_callback(100.0)

    return data_hash, initialization_vector, chunk_sizes_d, enc_file, secret


def progress_file_cryption(p):
    """
    @type p: int
    """
    print "cba_crypto.py:234", p


def encrypt_a_file(secret, perc_callback, chunk):
    """
    encrypt_a_file
    @type secret: str, unicode
    @type perc_callback: function
    @type chunk: unicode, str
    """
    Random.atfork()
    return encrypt_file(secret, StringIO(chunk), perc_callback=perc_callback)


def encrypt_file_smp(secret, fname=None, strobj=None):
    """
    @type secret: str, unicode
    @type fname: str, unicode
    @type strobj: StringIO, None
    """
    if not strobj:
        stats = os.stat(fname)
        datasize = float(stats.st_size)
        fobj = open(fname)
    else:
        datasize = float(strobj.len)
        fobj = strobj

    chunksize = int(datasize / multiprocessing.cpu_count()) + 64
    chunklist = []
    with fobj as infile:
        chunk = infile.read(chunksize)

        while chunk:
            chunklist.append(chunk)
            chunk = infile.read(chunksize)

    encrypted_file_chunks = run_in_pool(chunklist, encrypt_a_file, base_params=(secret, progress_file_cryption))
    return encrypted_file_chunks


def decrypt_file_smp(secret, enc_file_chunks):
    """
    @type secret: str, unicode
    @type enc_file_chunks: list
    """
    dec_file = StringIO()

    chunks_param_sorted = [(secret, chunk[3], chunk[0], chunk[1], chunk[2], progress_file_cryption) for chunk in enc_file_chunks]
    dec_file_chunks = run_in_pool(chunks_param_sorted, decrypt_file)

    for chunk_dec_file in dec_file_chunks:
        dec_file.write(chunk_dec_file.read())
    dec_file.seek(0)
    return dec_file


def json_object(path, targetobject):
    """
    @type path: str or unicode
    @type targetobject: object
    """
    if DEBUG:
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


def encrypt_object(secret, obj):
    """
    @type secret: str or unicode
    @type obj: str or unicode
    @return: @rtype:
    """
    encrypted_dict = encrypt_file_smp(secret, strobj=cPickle.dump(obj, cPickle.HIGHEST_PROTOCOL))
    return base64.b64encode(cPickle.dumps(encrypted_dict)).strip()


def decrypt_object(secret, obj_string, key=None, give_secret_cb=None):
    """
    @type secret: str or unicode
    @type obj_string: str
    @type key: str or unicode
    @type give_secret_cb: __builtin__.function
    @return: @rtype:
    """
    data = cPickle.loads(base64.b64decode(obj_string))

    if key:
        secret = password_derivation(key, data["salt"])

        if give_secret_cb:
            give_secret_cb(secret)

    return cPickle.load(decrypt_file_smp(secret, data).read())

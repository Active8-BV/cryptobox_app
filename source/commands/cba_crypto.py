# coding=utf-8
"""
crypto routines for the commandline tool
"""
import os
import base64
import time
import cPickle
import zlib
from cStringIO import StringIO
from Crypto import Random
from Crypto.Hash import SHA, SHA512
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from cba_utils import smp_all_cpu_apply, update_item_progress


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


def make_checksum(data):
    """
    @type data: str, unicode
    @rtype: str, unicode
    """

    try:
        crc = base64.encodestring(str(zlib.adler32(data)))
        return crc.strip().rstrip("=")
    except OverflowError:
        return base64.encodestring(str(SHA.new(data).hexdigest())).strip().rstrip("=")


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


def encrypt_file_for_smp(secret, fin, total=None, perc_callback=None, perc_callback_freq=2):
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
    chunksize = 1024 * 1024 * 1
    lc_time = time.time()

    if not total:
        fin.seek(0, os.SEEK_END)
        total = fin.tell()
        fin.seek(0)
    Random.atfork()
    total = int(total)
    fin.seek(0)
    total_enc_data = ""
    data_hash = ""
    initialization_vector = Random.new().read(AES.block_size)
    cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
    chunk_sizes_d = {"length": 0, "default": None, "last": None}
    enc_data = ""
    chunk = ""

    while True:
        pre_read_chunk = chunk
        chunk = fin.read(chunksize)

        if chunk == "":
            chunk_sizes_d["last"] = (len(pre_read_chunk), len(enc_data))
            chunk_sizes_d["length"] = cnt
            break

        enc_data = cipher.encrypt(chunk)

        if cnt <= 0:
            data_hash = make_checksum(chunk)
            chunk_sizes_d["last"] = chunk_sizes_d["default"] = (len(chunk), len(enc_data))

        total_enc_data += enc_data
        cnt += 1

        if perc_callback:
            if (time.time() - lc_time) > perc_callback_freq:
                perc = (float(cnt * chunksize) / (float(total) / 100))
                perc_callback(perc)
                lc_time = time.time()

        if len(chunk) == total:
            chunk_sizes_d["last"] = (len(chunk), len(enc_data))
            chunk_sizes_d["length"] = cnt
            break

    if perc_callback:
        perc_callback(100.0)

    return data_hash, initialization_vector, chunk_sizes_d, total_enc_data


def decrypt_file_for_smp(secret, encrypted_data, data_hash, initialization_vector, chunk_sizes, perc_callback=None, perc_callback_freq=2):
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
    encrypted_data = StringIO(encrypted_data)

    if not secret:
        raise Exception("no secret in decrypt file")

    if 16 != len(initialization_vector):
        raise Exception("initialization_vector len is not 16")

    lc_time = time.time()
    dec_file = StringIO()
    cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
    total_data_size = (chunk_sizes["default"][0] * chunk_sizes["length"] - 1) + chunk_sizes["last"][0]
    current_data_read = 0

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
        current_data_read += encrypted_chunk
        dec_data = cipher.decrypt(chunk)
        dec_data = dec_data[0:decrypted_chunk]
        dec_file.write(dec_data)
        if cnt <= 0:
            calculated_hash = make_checksum(dec_data)

            if data_hash != calculated_hash:
                raise EncryptionHashMismatch("decrypt_file -> the decryption went wrong, hash didn't match")

        cnt += 1

        if perc_callback:
            if time.time() - lc_time > perc_callback_freq:
                perc_callback(float(current_data_read) / (float(total_data_size) / 100))
                lc_time = time.time()

    dec_file.seek(0)
    if perc_callback:
        perc_callback(100.0)

    return dec_file.read()


def progress_file_cryption(p):
    """
    @type p: int
    """
    update_item_progress(p, True)


def encrypt_a_file(secret, perc_callback, chunk):
    """
    encrypt_a_file
    @type secret: str, unicode
    @type perc_callback: function
    @type chunk: unicode, str
    """
    Random.atfork()
    return encrypt_file_for_smp(secret, StringIO(chunk), perc_callback=perc_callback)


def encrypt_file_smp(secret, fname=None, strobj=None, progress_callback=progress_file_cryption):
    """
    @type secret: str, unicode
    @type fname: str, unicode
    @type strobj: StringIO, None
    @type progress_callback: function
    """
    if not strobj:
        fobj = open(fname)
    else:
        fobj = strobj

    two_mb = (2 * (2 ** 20))

    #if datasize < max_single_cpu_size:
    #    chunksize = int(datasize) + 1
    #else:
    #    chunksize = int(datasize / cpu_count()) + 64
    chunklist = []
    chunk = fobj.read(two_mb)

    while chunk:
        chunklist.append(chunk)
        chunk = fobj.read(two_mb)

    encrypted_file_chunks = smp_all_cpu_apply(encrypt_a_file, chunklist, base_params=(secret, progress_callback))
    progress_file_cryption(0)
    return encrypted_file_chunks


def decrypt_file_smp(secret, enc_file_chunks, progress_callback=progress_file_cryption):
    """
    @type secret: str, unicode
    @type enc_file_chunks: list
    @type progress_callback: function
    """
    dec_file = StringIO()

    chunks_param_sorted = [(secret, chunk[3], chunk[0], chunk[1], chunk[2], progress_callback) for chunk in enc_file_chunks]
    dec_file_chunks = smp_all_cpu_apply(decrypt_file_for_smp, chunks_param_sorted)

    for chunk_dec_file in dec_file_chunks:
        dec_file.write(chunk_dec_file)
    dec_file.seek(0)
    progress_file_cryption(0)
    return dec_file


def encrypt_object(secret, obj):
    """
    @type secret: str or unicode
    @type obj: str or unicode
    @return: @rtype:
    """
    pickle_data = cPickle.dumps(obj, cPickle.HIGHEST_PROTOCOL)
    encrypted_dict = encrypt_file_smp(secret, strobj=StringIO(pickle_data))
    return base64.b64encode(cPickle.dumps(encrypted_dict)).strip()


def decrypt_object(secret, obj_string, key=None, salt=None):
    """
    @type secret: str or unicode
    @type obj_string: str
    @type key: str or unicode
    @type salt: str
    @return: @rtype: object, str
    """
    data = cPickle.loads(base64.b64decode(obj_string))

    if key:
        if not salt:
            raise Exception("no salt")

        secret = password_derivation(key, salt)
    return cPickle.load(decrypt_file_smp(secret, data)), secret

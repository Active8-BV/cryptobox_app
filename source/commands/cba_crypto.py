# coding=utf-8
"""
crypto routines for the commandline tool
"""
import os
import tempfile
import base64
import cPickle
import zlib
from cStringIO import StringIO
from Crypto import Random
from Crypto.Hash import SHA, SHA512
from Crypto.Cipher import AES, XOR
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


def make_sha1_hash_file(prefix, strio=None, fpi=None, fpath=None):
    """ make hash
    @type prefix: str
    @type fpath: str, None
    @type strio: str, None
    @type fpi: file, None, FileIO
    """
    sha = SHA.new()
    sha.update(prefix)
    if not fpi:
        fp = StringIO(strio)
    else:
        fp = fpi

    if fpath:
        fp = open(fpath)
    fp.seek(0)
    one_mb = (1 * (2 ** 20))
    chunksize = one_mb / 2
    chunk = fp.read(chunksize)
    crc = base64.encodestring(str(zlib.adler32(chunk))).strip().rstrip("=")
    sha.update(crc)

    while chunk:
        crc = base64.encodestring(str(zlib.adler32(chunk))).strip().rstrip("=")
        sha.update(crc)
        chunk = fp.read(chunksize)

    return sha.hexdigest()


def make_hash(data):
    """ make hash
    @param data:
    @type data:
    """
    sha = SHA512.new(data)
    return sha.hexdigest()


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

def encrypt_file_for_smp(secret, chunk, bucket_name, name, cnt):
    """
    @param secret: pkdf2 secre
    @type secret: str
    @type chunk: str
    @type cnt: int
    """
    Random.atfork()
    initialization_vector = Random.new().read(AES.block_size)

    #cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
    from Crypto.Cipher import XOR
    cipher = XOR.new(secret)
    data_hash = make_checksum(chunk)
    enc_data = cipher.encrypt(chunk)
    data = {"initialization_vector": initialization_vector,
            "enc_data": enc_data,
            "data_hash": data_hash}

    pdata = cPickle.dumps(data)
    write_to_gcloud(bucket_name, name + "_" + str(cnt), pdata)
    return True


def make_chunklist(fobj):
    """
    @type fobj: file
    """
    chunksize = (20 * (2 ** 20))

    #noinspection PyBroadException
    try:
        import multiprocessing
        numcores = multiprocessing.cpu_count()
        fobj.seek(0, os.SEEK_END)
        fsize = fobj.tell()

        if (numcores * chunksize) > fsize:
            chunksize = fsize / numcores
    except:
        pass

    fobj.seek(0)
    chunklist = []
    chunk = fobj.read(chunksize)

    while chunk:
        tf = tempfile.TemporaryFile()
        tf.write(chunk)
        chunklist.append(tf)
        chunk = fobj.read(chunksize)

    return chunklist


def encrypt_file_smp(secret, fname, bucket_name=None, name=None, progress_callback=None):
    """
    @type secret: str, unicode
    @type fname: str, unicode
    @type progress_callback: function
    """
    store_in_cloud = True

    if not bucket_name or not name:

        # use the cloud as a temp buffer
        bucket_name = "tmp"
        name = str(uuid.uuid4().hex)
        store_in_cloud = False

    if isinstance(fname, str) or isinstance(fname, unicode):
        fobj = open(fname)
    else:
        fobj = fname

    chunklist = make_chunklist(fobj)
    chunklist = [(secret, chunk_fp, bucket_name, name, cnt) for cnt, chunk_fp in enumerate(chunklist)]
    encrypted_file_chunks = smp_all_cpu_apply(encrypt_file_for_smp, chunklist, progress_callback)

    if store_in_cloud:
        return len(encrypted_file_chunks)
    else:
        encrypted_file_chunks_data = []

        for i in range(0, len(encrypted_file_chunks)):
            encrypted_file_chunks_data.append(read_from_gcloud(bucket_name, name + "_" + str(i)).read())
            delete_from_gcloud(bucket_name, name + "_" + str(i))
        return encrypted_file_chunks_data


def decrypt_chunk(secret, chunk):
    """
    @type secret: str
    @type chunk: dict, str
    """
    if isinstance(chunk, str):
        chunk = cPickle.loads(chunk)

    initialization_vector = chunk["initialization_vector"]
    encrypted_data = chunk["enc_data"]
    data_hash = chunk["data_hash"]
    if 16 != len(initialization_vector):
        raise Exception("initialization_vector len is not 16")

    #cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
    from Crypto.Cipher import XOR
    cipher = XOR.new(secret)
    tf = tempfile.NamedTemporaryFile(delete=False)
    dec_data = cipher.decrypt(encrypted_data)
    tf.write(dec_data)
    calculated_hash = make_checksum(dec_data)
    if data_hash != calculated_hash:
        raise EncryptionHashMismatch("decrypt_file -> the decryption went wrong, hash didn't match")

    return tf.name


def decrypt_file_smp(secret, enc_file_chunks, progress_callback=None):
    """
    @type secret: str, unicode
    @type enc_file_chunks: list
    @type progress_callback: function
    """
    chunks_param_sorted = [(secret, chunk) for chunk in enc_file_chunks]
    dec_file_chunks = smp_all_cpu_apply(decrypt_chunk, chunks_param_sorted, progress_callback)
    dec_file = tempfile.TemporaryFile()

    for chunk_dec_file in dec_file_chunks:
        chunk_path = chunk_dec_file.read()
        dec_file.write(open(chunk_path).read())
        os.remove(chunk_path)
    dec_file.seek(0)
    return dec_file


def encrypt_object(secret, obj):
    """
    @type secret: str or unicode
    @type obj: str or unicode
    @return: @rtype:
    """
    pickle_data = cPickle.dumps(obj, cPickle.HIGHEST_PROTOCOL)
    encrypted_dict = encrypt_file_smp(secret, StringIO(pickle_data), update_item_progress)
    return base64.b64encode(cPickle.dumps(encrypted_dict)).strip()


def decrypt_object(secret, obj_string, key=None, salt=None, progress_callback=update_item_progress):
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
    return cPickle.load(decrypt_file_smp(secret, data, progress_callback)), secret

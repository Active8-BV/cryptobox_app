# coding=utf-8
"""
crypto routines for the commandline tool
"""
import base64
import cPickle
import zlib
from cStringIO import StringIO
from Crypto import Random
from Crypto.Hash import SHA, \
    SHA512
from Crypto.Cipher import AES, \
    Blowfish
from Crypto.Protocol.KDF import PBKDF2
from cba_utils import smp_all_cpu_apply, \
    update_item_progress
from struct import pack


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


def encrypt_file_for_smp(secret, chunk):
    """
    @param secret: pkdf2 secre
    @type secret: str
    @param chunk: file object
    @type chunk: unicode, str
    @return: salt, hash, init, chunk sizes and encrypted data temp file
    @rtype: tuple
    """
    Random.atfork()
    fin = StringIO(chunk)
    bs = Blowfish.block_size

    #initialization_vector = Random.new().read(AES.block_size)
    #cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
    initialization_vector = Random.new().read(Blowfish.block_size)
    cipher = Blowfish.new(secret, Blowfish.MODE_CBC, initialization_vector)
    chunk = fin.read()
    plen = bs - divmod(len(chunk), bs)[1]
    padding = [plen] * plen
    padding = pack('b' * plen, *padding)
    enc_data = cipher.encrypt(chunk+padding)
    data_hash = make_checksum(chunk)
    return {"initialization_vector": initialization_vector,
            "enc_data": enc_data,
            "data_hash": data_hash}


def progress_file_cryption(p):
    """
    @type p: int
    """
    update_item_progress(p)


def encrypt_file_smp(secret, fname, progress_callback):
    """
    @type secret: str, unicode
    @type fname: str, unicode
    @type progress_callback: function
    """
    if isinstance(fname, str) or isinstance(fname, unicode):
        fobj = open(fname)
    else:
        fobj = fname

    two_mb = (2 * (2 ** 20))
    chunklist = []
    chunk = fobj.read(two_mb)

    while chunk:
        chunklist.append(chunk)
        chunk = fobj.read(two_mb)

    chunklist = [(secret, chunk) for chunk in chunklist]
    encrypted_file_chunks = smp_all_cpu_apply(encrypt_file_for_smp, chunklist, progress_callback)
    return encrypted_file_chunks


def decrypt_file_for_smp(secret, encrypted_data, data_hash, initialization_vector):
    """
    @param secret: generated secret pkdf2
    @type secret: str
    @param data_hash: hash of first chunk
    @type data_hash: str
    @param initialization_vector: init vector cipher
    @type initialization_vector: str
    @param encrypted_data: the encrypted data
    @type encrypted_data: file, StringIO
    @return: orignal data temporary file
    @rtype: file
    """
    if not secret:
        raise Exception("no secret in decrypt file")

    if 8 != len(initialization_vector):
        raise Exception("initialization_vector len is not 16")

    cipher = Blowfish.new(secret, Blowfish.MODE_CBC, initialization_vector)

    #cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
    dec_data = cipher.decrypt(encrypted_data).strip("\b")
    calculated_hash = make_checksum(dec_data)
    if data_hash != calculated_hash:
        raise EncryptionHashMismatch("decrypt_file -> the decryption went wrong, hash didn't match")

    return dec_data


def decrypt_file_smp(secret, enc_file_chunks, progress_callback):
    """
    @type secret: str, unicode
    @type enc_file_chunks: list
    @type progress_callback: function
    """
    dec_file = StringIO()
    chunks_param_sorted = [(secret, chunk["enc_data"], chunk["data_hash"], chunk["initialization_vector"]) for chunk in enc_file_chunks]
    dec_file_chunks = smp_all_cpu_apply(decrypt_file_for_smp, chunks_param_sorted, progress_callback)

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

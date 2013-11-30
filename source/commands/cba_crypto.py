# coding=utf-8
"""
crypto routines for the commandline tool
"""
import os
import math
import time
import tempfile
import base64
import cPickle
import zlib
import uuid
from cStringIO import StringIO
from Crypto import Random
from Crypto.Hash import SHA, SHA512
from Crypto.Cipher import AES, XOR
from Crypto.Protocol.KDF import PBKDF2
from cba_utils import update_item_progress, log_json


def get_named_temporary_file(auto_delete):
    ntf = tempfile.NamedTemporaryFile(delete=auto_delete)

    if not auto_delete:
        fname = "tempfile_" + str(uuid.uuid4().hex) + ".cba"
        fpath = os.path.join(os.getcwd(), fname)
        logf = open(fpath, "w")
        logf.write(cPickle.dumps({"file_path": ntf.name}))
        logf.close()

    return ntf


def cleanup_tempfiles():
    for fp in os.listdir(os.getcwd()):
        if str(fp).startswith("tempfile_") and str(fp).endswith(".cba"):
            data = cPickle.load(open(fp))

            if os.path.exists(data["file_path"]):
                if time.time() - os.stat(data["file_path"]).st_mtime > 30:
                    log_json("removing " + data["file_path"])
                    os.remove(data["file_path"])
                    os.remove(fp)
            else:
                os.remove(fp)


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


def make_sha1_hash_file(prefix=None, fpath=None, data=None, fpi=None):
    """ make hash
    @type prefix: str
    @type fpath: str, None
    @type data: str, None
    @type fpi: file, None, FileIO
    """
    sha = SHA.new()

    if prefix:
        sha.update(prefix)

    if data:
        fp = StringIO(data)

    if fpath:
        fp = open(fpath)
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


def encrypt_file_for_smp(secret, fpath, chunksize):
    """
    @param secret: pkdf2 secre
    @type secret: str
    @type fpath: str
    @type chunksize: tuple
    """
    try:
        Random.atfork()
        initialization_vector = Random.new().read(AES.block_size)

        #cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
        f = open(fpath)
        f.seek(chunksize[0])
        chunk = f.read(chunksize[1])
        cipher = XOR.new(secret)
        data_hash = make_checksum(chunk)
        enc_data = cipher.encrypt(chunk)
        ntf = get_named_temporary_file(auto_delete=False)
        ntf.write(str(len(initialization_vector)) + "\n")
        ntf.write(initialization_vector)
        ntf.write(str(len(data_hash)) + "\n")
        ntf.write(data_hash)
        ntf.write(str(len(enc_data)) + "\n")
        ntf.write(enc_data)
        return ntf.name
    except Exception, e:
        raise e


class ChunkListException(Exception):
    pass


def make_chunklist(fpath):
    """
    @type fpath: str
    """
    fsize = os.stat(fpath).st_size
    chunksize = (20 * (2 ** 20))

    #noinspection PyBroadException
    try:
        import multiprocessing
        numcores = multiprocessing.cpu_count()

        if (numcores * chunksize) > fsize:
            chunksize = int(math.ceil(float(fsize) / numcores))
    except:
        pass

    if chunksize == 0:
        pass

    num_chunks = fsize / chunksize
    chunk_remainder = fsize % chunksize
    chunklist = [chunksize for x in range(0, num_chunks)]
    chunklist.append(chunk_remainder)
    chunklist_abs = []
    val = 0

    for i in chunklist:
        chunklist_abs.append((val, i))
        val += i

    if chunk_remainder != 0:
        last = chunklist_abs.pop()
        second_last = chunklist_abs.pop()
        chunklist_abs.append((second_last[0], second_last[1] + last[1]))

    return chunklist_abs


def encrypt_file_smp(secret, fname, progress_callback=None, single_file=False):
    """
    @type secret: str, unicode
    @type fname: str, unicode
    @type progress_callback: function
    """
    try:
        chunklist = make_chunklist(fname)
        chunklist = [(secret, fname, chunk_size) for chunk_size in chunklist]
        enc_files = smp_all_cpu_apply(encrypt_file_for_smp, chunklist, progress_callback)

        if single_file:
            enc_file = tempfile.SpooledTemporaryFile(max_size=524288000)

            for efpath in enc_files:
                enc_file.write(str(os.stat(efpath).st_size) + "\n")
                enc_file.write(open(efpath).read())
                os.remove(efpath)
            enc_file.seek(0)
            return enc_file
        else:
            return enc_files
    finally:
        cleanup_tempfiles()


def decrypt_chunk(secret, fpath):
    """
    @type secret: str
    @type fpath: str
    """
    chunk_file = open(fpath)
    initialization_vector_len = int(chunk_file.readline())
    initialization_vector = chunk_file.read(initialization_vector_len)
    data_hash_len = int(chunk_file.readline())
    data_hash = chunk_file.read(data_hash_len)
    enc_data_len = int(chunk_file.readline())
    enc_data = chunk_file.read(enc_data_len)
    if 16 != len(initialization_vector):
        raise Exception("initialization_vector len is not 16")

    #cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
    from Crypto.Cipher import XOR
    cipher = XOR.new(secret)
    ntf = get_named_temporary_file(False)
    dec_data = cipher.decrypt(enc_data)
    ntf.write(dec_data)
    calculated_hash = make_checksum(dec_data)
    if data_hash != calculated_hash:
        raise EncryptionHashMismatch("decrypt_file -> the decryption went wrong, hash didn't match")

    return ntf.name


def decrypt_file_smp(secret, enc_file=None, enc_files=[], progress_callback=None):
    """
    @type secret: str, unicode
    @type enc_file: file, None
    @type enc_files: list
    @type progress_callback: function
    """
    try:
        if enc_file:
            enc_files = []
            enc_file.seek(0)
            chunk_size = int(enc_file.readline())

            while chunk_size:
                nef = get_named_temporary_file(auto_delete=False)
                nef.write(enc_file.read(chunk_size))
                nef.close()
                enc_files.append(nef.name)
                chunk_line = enc_file.readline()

                if not chunk_line:
                    chunk_size = None
                else:
                    chunk_size = int(chunk_line)
            enc_file.close()

        if not enc_files:
            raise Exception("nothing to decrypt")

        chunks_param_sorted = [(secret, file_path) for file_path in enc_files]
        dec_files = smp_all_cpu_apply(decrypt_chunk, chunks_param_sorted, progress_callback)
        del chunks_param_sorted
        dec_file = tempfile.SpooledTemporaryFile(max_size=524288000)

        for dfp in dec_files:
            dec_file.write(open(dfp).read())
            os.remove(dfp)
        dec_file.seek(0)

        for efp in enc_files:
            if os.path.exists(efp):
                os.remove(efp)

        return dec_file
    finally:
        cleanup_tempfiles()


def encrypt_object(secret, obj):
    """
    @type secret: str or unicode
    @type obj: str or unicode or object
    @return: @rtype:
    """
    temp_file = get_named_temporary_file(auto_delete=True)
    pickle_data = cPickle.dumps(obj)
    temp_file.write(pickle_data)
    temp_file.seek(0)
    encrypted_file = encrypt_file_smp(secret, temp_file.name, single_file=True)
    return base64.b64encode(encrypted_file.read())


def decrypt_object(secret, obj_string, key=None, salt=None):
    """
    @type secret: str or unicode
    @type obj_string: str
    @type key: str or unicode
    @type salt: str
    @return: @rtype: object, str
    """
    if key:
        if not salt:
            raise Exception("no salt")

        secret = password_derivation(key, salt)

    tf = get_named_temporary_file(auto_delete=True)
    obj_string = base64.decodestring(obj_string)
    tf.write(obj_string)
    tf.seek(0)
    data = decrypt_file_smp(secret, enc_file=tf)
    obj = cPickle.loads(data.read())
    return obj, secret


def smp_all_cpu_apply(method, items, progress_callback=None, dummy=False):
    """
    @type method: function
    @type items: list
    @type progress_callback: function
    """
    last_update = [time.time()]
    results_cnt = [0]

    def progress_callback_wrapper(result_func):
        """
        progress_callback
        @type result_func: object
        """
        if progress_callback:
            now = time.time()
            results_cnt[0] += 1

            try:
                perc = float(results_cnt[0]) / (float(len(items)) / 100)
            except ZeroDivisionError:
                perc = 0

            if results_cnt[0] == 1 and perc == 100:
                pass

            else:
                if now - last_update[0] > 0.1:
                    if perc > 100:
                        perc = 100
                    progress_callback(perc)
                    last_update[0] = now

        return result_func
    try:
        from multiprocessing import cpu_count
        num_procs = cpu_count()
    except Exception, e:
        log_json(str(e))
        num_procs = 8

    num_procs *= 2

    if dummy:
        from multiprocessing.dummy import Pool
        pool = Pool(processes=num_procs)
    else:
        from multiprocessing import Pool
        pool = Pool(processes=num_procs)

    calculation_result = []

    for item in items:
        base_params_list = []

        if isinstance(item, tuple):
            for i in item:
                if hasattr(i, "seek"):
                    i.seek(0)
                    data = i.read()
                    i.close()
                    base_params_list.append(data)
                else:
                    base_params_list.append(i)

        elif isinstance(item, file):
            item.seek(0)
            base_params_list.append(item.read())
        else:
            base_params_list.append(item)

        params = tuple(base_params_list)

        #result = apply(method, params)
        result = pool.apply_async(method, params, callback=progress_callback_wrapper)
        calculation_result.append(result)
    pool.close()
    pool.join()
    if progress_callback:
        progress_callback(100)

    try:
        return [x.get() for x in calculation_result]
    except Exception, e:
        print "cba_crypto.py:432", "DEBUG MODE", e
        return [x for x in calculation_result]

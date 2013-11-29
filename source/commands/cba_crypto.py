# coding=utf-8
"""
crypto routines for the commandline tool
"""
import os
import time
import tempfile
import base64
import cPickle
import zlib
import uuid
from cStringIO import StringIO
from Crypto import Random
from Crypto.Hash import SHA, SHA512
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from cba_utils import update_item_progress, log_json


def get_named_temporary_file():
    ntf = tempfile.NamedTemporaryFile(delete=False)
    logf = open(os.path.join(os.getcwd(), "tempfile_" + str(uuid.uuid4().hex)))
    logf.write(cPickle.dumps({"timestamp": time.time(), "file_path": ntf.name}))
    logf.close()
    return ntf


def cleanup_tempfiles():
    for fp in os.listdir(os.getcwd()):
        if str(fp).startswith("tempfile_"):
            data = cPickle.load(open(fp))

            if os.path.exists(data["file_path"]):
                if time.time() - data["timestamp"] > 60:
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


def make_sha1_hash_file(prefix=None, data=None, fpi=None, fpath=None):
    """ make hash
    @type prefix: str
    @type fpath: str, None
    @type data: str, None
    @type fpi: file, None, FileIO
    """
    sha = SHA.new()

    if prefix:
        sha.update(prefix)

    if not fpi:
        fp = StringIO(data)
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


def encrypt_file_for_smp(secret, chunk):
    """
    @param secret: pkdf2 secre
    @type secret: str
    @type chunk: str
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
    ntf = get_named_temporary_file()
    ntf.write(pdata)
    return {"file_path": ntf.name}


class ChunkListException(Exception):
    pass


def make_chunklist(fobj, offsets=None):
    """
    @type fobj: file
    @type offsets: list
    """
    offsetcnt = 0
    chunk_hash = ""

    if not offsets:
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

    else:
        chunksize = offsets[offsetcnt][0]
        chunk_hash = offsets[offsetcnt][1]
        offsetcnt += 1
    fobj.seek(0)
    chunklist = []
    chunk = fobj.read(chunksize)

    while chunk:
        if offsets:
            if chunk_hash != make_sha1_hash_file(data=chunk):
                raise ChunkListException("make_chunklist, hash does not match")

        tf = tempfile.SpooledTemporaryFile(max_size=100 * (2 ** 20))
        tf.write(chunk)
        chunklist.append(tf)
        if offsets:
            if offsetcnt >= len(offsets):
                break

            chunksize = offsets[offsetcnt][0]
            offsetcnt += 1

        chunk = fobj.read(chunksize)

    return chunklist


def encrypt_file_smp(secret, fname, progress_callback=None):
    """
    @type secret: str, unicode
    @type fname: str, unicode
    @type progress_callback: function
    """
    if isinstance(fname, str) or isinstance(fname, unicode):
        fobj = open(fname)
    else:
        fobj = fname

    try:
        chunklist = make_chunklist(fobj)
        chunklist = [(secret, chunk_fp) for chunk_fp in chunklist]
        return smp_all_cpu_apply(encrypt_file_for_smp, chunklist, progress_callback)
    finally:
        cleanup_tempfiles()


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
    ntf = get_named_temporary_file()
    dec_data = cipher.decrypt(encrypted_data)
    ntf.write(dec_data)
    calculated_hash = make_checksum(dec_data)
    if data_hash != calculated_hash:
        raise EncryptionHashMismatch("decrypt_file -> the decryption went wrong, hash didn't match")

    return {"file_path": ntf.name}


def decrypt_file_smp(secret, enc_file, offsets, progress_callback=None):
    """
    @type secret: str, unicode
    @type enc_file: tempfile.SpooledTemporarFile, tempfile.TemporarFile
    @type offsets: list
    @type progress_callback: function
    """

    try:
        chunklist = make_chunklist(enc_file, offsets)
        chunks_param_sorted = [(secret, chunk) for chunk in chunklist]
        dec_file = smp_all_cpu_apply(decrypt_chunk, chunks_param_sorted, progress_callback)
        return dec_file[0]
    finally:
        cleanup_tempfiles()


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


def smp_all_cpu_apply(method, items, progress_callback=None, numprocs=None, dummy=False):
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

    if numprocs:
        num_procs = numprocs
    else:
        try:
            from multiprocessing import cpu_count
            num_procs = cpu_count()
        except Exception, e:
            log_json(str(e))
            num_procs = 16

    if dummy:
        from multiprocessing.dummy import Pool
        pool = Pool(processes=num_procs)
    else:
        from multiprocessing import Pool
        pool = Pool(processes=num_procs)

    calculation_result = []
    calculation_result_values = []

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
    progress_callback(100)
    stf = None
    offsets = []

    for result in calculation_result:
        if not result.successful():
            result.get()
        else:
            res = result.get()

            if isinstance(res, dict):
                if not stf:
                    stf = tempfile.SpooledTemporaryFile(max_size=100 * (2 ** 20))

                if "file_path" in res:
                    data = open(res["file_path"]).read()
                    offsets.append((len(data), make_sha1_hash_file(data=data)))
                    stf.write(data)
                    os.remove(res["file_path"])
                else:
                    raise Exception("smp_all_cpu_apply, received dict, don't know what to do now.")

            else:
                calculation_result_values.append(str(res))

    pool.terminate()
    if stf:
        stf.seek(0)
        return stf, offsets
    else:
        return calculation_result_values, None

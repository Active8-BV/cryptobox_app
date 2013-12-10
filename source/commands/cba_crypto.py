# coding=utf-8
"""
crypto routines for the commandline tool
"""
import os
import glob
import math
import time
import tempfile
import base64
import cPickle
import zlib
import uuid
import multiprocessing
from cStringIO import StringIO
from Crypto import Random
from Crypto.Hash import SHA, SHA512
from Crypto.Cipher import AES, XOR
from Crypto.Protocol.KDF import PBKDF2
from cba_utils import log_json


def stack_trace(line_num_only=0, ret_list=False):
    """
    @param line_num_only:
    @type line_num_only:
    @type ret_list: bool
    @return: @rtype:
    """
    import traceback
    import tempfile
    stack = tempfile.TemporaryFile()
    traceback.print_stack(file=stack)
    stack.seek(0)
    stack = stack.read()

    if ret_list and (line_num_only > 0):
        raise Exception("ret_list or line_num_only both true")

    stackl = []
    stack = stack.split("\n")
    stack.reverse()
    cnt = 0

    for i in stack:
        stackl.append(i)
        if line_num_only > 0:
            if "line" in i and "File" in i:
                if cnt > line_num_only - 1:
                    for j in i.split("line"):
                        for k in j.split(","):
                            #noinspection PyBroadException
                            try:
                                ln = int(k)
                                fs = i.replace('"', "").split(",")[0].split(os.sep)
                                return str("/".join(fs[len(fs) - 2:])) + ":" + str(ln)
                            except:
                                pass

                cnt += 1

    if line_num_only > 0:
        return str("?")

    if ret_list:
        return stackl
    return "\n".join(stackl)


def get_named_temporary_file(auto_delete):
    """
    get_named_temporary_file
    """
    ntf = tempfile.NamedTemporaryFile(delete=auto_delete)

    if not auto_delete:
        fname = "tempfile_" + str(uuid.uuid4().hex) + ".cba"
        fpath = os.path.join(os.getcwd(), fname)
        logf = open(fpath, "w")
        logf.write(ntf.name)
        logf.write("\n\n")
        logf.write(stack_trace())
        logf.close()

    return ntf


def cleanup_tempfiles():
    """
    cleanup_tempfiles
    """
    for fp in glob.glob("tempfile_*.cba"):
        if str(fp).startswith("tempfile_") and str(fp).endswith(".cba"):
            if os.path.exists(os.path.join(os.getcwd(), fp)):
                #noinspection PyBroadException
                try:
                    data = open(fp).readline().strip()

                    if os.path.exists(data):
                        if time.time() - os.stat(data).st_mtime > 300:
                            os.remove(data)
                            os.remove(os.path.join(os.getcwd(), fp))
                    else:
                        os.remove(os.path.join(os.getcwd(), fp))
                except:
                    pass


def make_checksum(data):
    """
    @type data: str, unicode
    @rtype: str, unicode
    """
    try:
        return str(zlib.adler32(data))
    except OverflowError:
        log_json("overflow make_checksum")
        return base64.encodestring(str(SHA.new(data).hexdigest())).strip().rstrip("=")


def make_checksum_tuple(t):
    """
    @type t: tuple
    """
    sha = SHA.new()

    for i in t:
        c = make_checksum(i)
        sha.update(c)

    return sha.hexdigest()


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

    if data is not None:
        fp = StringIO(data)
    elif fpath:
        fp = open(fpath)
    else:
        fp = fpi
        fp.seek(0)

    one_mb = (1 * (2 ** 20))
    chunksize = one_mb / 2
    chunk = fp.read(chunksize)
    cnt = 1

    while chunk:
        crc = base64.encodestring(str(zlib.adler32(chunk))).strip().rstrip("=")
        sha.update(crc)
        fp.seek(cnt * chunksize)
        cnt += 1
        chunk = fp.read(10)

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


def encrypt_chunk(secret, fpath, chunksize, initialization_vector):
    """
    @param secret: pkdf2 secre
    @type secret: str
    @type fpath: str
    @type chunksize: tuple
    """
    try:
        f = open(fpath)
        f.seek(chunksize[0])
        chunk = f.read(chunksize[1])

        #cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
        cipher = XOR.new(secret)
        data_hash = make_checksum(chunk)
        enc_data = cipher.encrypt(chunk)
        ntf = get_named_temporary_file(auto_delete=False)
        chunk_seek = str(chunksize[0])
        ntf.write(str(len(chunk_seek)) + "\n")
        ntf.write(chunk_seek)
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
    if not os.path.exists(fpath):
        raise Exception("make_chunklist: file does not exist")

    fstats = os.stat(fpath)
    fsize = fstats.st_size
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
        chunksize = 1

    num_chunks = fsize / chunksize
    chunk_remainder = fsize % chunksize
    chunklist = [chunksize] * num_chunks
    chunklist.append(chunk_remainder)
    chunklist_abs = []
    val = 0

    for i in chunklist:
        chunklist_abs.append((val, i))
        val += i

    if chunk_remainder != 0:
        last = chunklist_abs.pop()
        chunklist_abs.append((last[0], last[1] + chunk_remainder))

    if chunklist_abs[len(chunklist_abs) - 1][1] == 0:
        chunklist_abs.pop()

    return chunklist_abs


def encrypt_file_smp(secret, fname, progress_callback=None, single_file=False):
    """
    @type secret: str, unicode
    @type fname: str, unicode
    @type progress_callback: function
    """
    cleanup_tempfiles()
    initialization_vector = Random.new().read(AES.block_size)
    chunklist = make_chunklist(fname)
    chunklist = [(secret, fname, chunk_size, initialization_vector) for chunk_size in chunklist]
    enc_files = smp_all_cpu_apply(encrypt_chunk, chunklist, progress_callback)

    if single_file:
        enc_file = tempfile.SpooledTemporaryFile(max_size=524288000)

        for efpath in enc_files:
            enc_file.write(str(os.stat(efpath).st_size) + "\n")
            fdata = open(efpath).read()
            enc_file.write(fdata)
            os.remove(efpath)
        enc_file.seek(0)
        return enc_file
    else:
        return enc_files


def listener_file_writer(fn, q):
    """listens for messages on the q, writes to file. """
    f = open(fn, 'wb')

    while 1:
        m = q.get()

        if m == 'kill':
            break
        f.seek(m[0])
        f.write(m[1])
        f.flush()
    f.close()


def decrypt_chunk(secret, fpath, queue):
    """
    @type secret: str
    @type fpath: str
    @type queue: multiprocessing.Queue
    """
    chunk_file = open(fpath.strip())
    chunk_pos_len = int(chunk_file.readline())
    chunk_pos = int(chunk_file.read(chunk_pos_len))
    initialization_vector_len = int(chunk_file.readline())
    initialization_vector = chunk_file.read(initialization_vector_len)
    data_hash_len = int(chunk_file.readline())
    data_hash = chunk_file.read(data_hash_len)
    enc_data_len = int(chunk_file.readline())
    enc_data = chunk_file.read(enc_data_len)
    if 16 != len(initialization_vector):
        raise Exception("initialization_vector len is not 16")

    #cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector)
    cipher = XOR.new(secret)
    dec_data = cipher.decrypt(enc_data)
    calculated_hash = make_checksum(dec_data)
    if data_hash != calculated_hash:
        raise EncryptionHashMismatch("decrypt_file -> the decryption went wrong, hash didn't match")

    if queue.qsize() > 20:
        time.sleep(0.5)
    queue.put((chunk_pos, dec_data))
    return True


def decrypt_file_smp(secret, enc_file=None, enc_files=tuple(), progress_callback=None, delete_enc_files=False):
    """
    @type secret: str, unicode
    @type enc_file: file, None
    @type enc_files: tuple
    @type progress_callback: function
    @type delete_enc_files: bool
    """
    try:
        if enc_file:
            enc_files = []
            enc_file.seek(0)
            chunk_size = int(enc_file.readline())

            while chunk_size:
                delete_enc_files = True
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

        dec_file = get_named_temporary_file(auto_delete=True)
        chunks_param_sorted = [(secret, file_path) for file_path in enc_files]
        smp_all_cpu_apply(decrypt_chunk, chunks_param_sorted, progress_callback, listener=listener_file_writer, listener_param=tuple([dec_file.name]))
        dec_file.seek(0)
        return dec_file
    finally:
        if delete_enc_files:
            for efp in enc_files:
                if os.path.exists(efp):
                    os.remove(efp)

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


def decrypt_object(secret, obj_string):
    """
    @type secret: str or unicode
    @type obj_string: str
    @return: @rtype: object, str
    """
    if len(secret) == 0:
        secret = None

    if not secret:
        raise Exception("decrypt_object, no secret")

    tf = get_named_temporary_file(auto_delete=True)
    obj_string = base64.decodestring(obj_string)
    tf.write(obj_string)
    tf.seek(0)
    data = decrypt_file_smp(secret, enc_file=tf)
    pdata = data.read()
    obj = cPickle.loads(pdata)
    return obj, secret


def smp_all_cpu_apply(method, items, progress_callback=None, dummy_pool=False, listener=None, listener_param=tuple(), num_procs_param=None):
    """
    @type method: function
    @type items: list
    @type progress_callback: function
    @type dummy_pool: bool
    @type listener: function
    @type listener_param: tuple
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

    num_procs = 8

    if num_procs_param:
        num_procs = num_procs_param
    else:
        try:
            from multiprocessing import cpu_count
            num_procs = cpu_count()
        except Exception, e:
            log_json(str(e))

    if listener:
        num_procs += 1

    manager = multiprocessing.Manager()

    if dummy_pool:
        from multiprocessing.dummy import Pool
        pool = Pool(processes=num_procs)
    else:
        pool = multiprocessing.Pool(processes=num_procs)

    calculation_result = []

    if listener:
        queue = manager.Queue()
    else:
        queue = None

    watcher = None

    if listener:
        if listener_param:
            listener_param = list(listener_param)
            listener_param.append(queue)
        else:
            listener_param = (queue,)

        watcher = pool.apply_async(listener, tuple(listener_param))

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

        if queue:
            base_params_list.append(queue)

        params = tuple(base_params_list)
        result = pool.apply_async(method, params, callback=progress_callback_wrapper)
        calculation_result.append(result)

    [result.wait() for result in calculation_result]
    if queue:
        queue.put("kill")

    if watcher:
        watcher.get()
    pool.close()
    pool.join()
    return [x.get() for x in calculation_result]

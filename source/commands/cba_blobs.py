# coding=utf-8
"""
blob routines, loosely based on git
"""
import os
import multiprocessing
from cba_utils import handle_exception, strcmp, update_progress
from cba_file import read_and_encrypt_file, ensure_directory, decrypt_write_file, write_file
from cba_memory import add_local_file_history, add_server_file_history


def get_data_dir(options):
    """
    get_data_dir
    @type options: optparse.Values, instance
    """
    return os.path.join(options.dir, ".cryptobox")


def get_blob_dir(options):
    """
    get_blob_dir
    @type options: optparse.Values, instance
    """
    datadir = get_data_dir(options)
    return os.path.join(datadir, "blobs")


def encrypt_new_blobs(salt, secret, new_blobs):
    """
    @type salt: str or unicode
    @type secret: str or unicode
    @type new_blobs: dict
    """
    num_cores = multiprocessing.cpu_count()
    progressdata = {"processed_files": 0, "numfiles": len(new_blobs)}

    #noinspection PyUnusedLocal
    def done_encrypting(e):
        """
        @param e: event
        @type e:
        """
        progressdata["processed_files"] += 1
        update_progress(progressdata["processed_files"], progressdata["numfiles"], "encrypting")

    pool = multiprocessing.dummy.Pool(processes=num_cores)
    counter = 0
    encrypt_results = []

    for fhash in new_blobs:
        counter += 1
        ensure_directory(new_blobs[fhash]["blobdir"])
        result = pool.apply_async(read_and_encrypt_file,
                                  (new_blobs[fhash]["fpath"], new_blobs[fhash]["blobpath"], salt, secret),
                                  callback=done_encrypting)

        encrypt_results.append(result)

    pool.close()
    pool.join()

    for result in encrypt_results:
        if not result.successful():
            result.get()

    pool.terminate()


def decrypt_blob_to_filepaths(blobdir, cryptobox_index, fhash, secret):
    """
    @param blobdir: str or unicode
    @type blobdir:
    @param cryptobox_index: dict
    @type cryptobox_index:
    @param fhash: str or unicode
    @type fhash:
    @param secret: str or unicode
    @type secret:
    """

    try:
        fdir = os.path.join(blobdir, fhash[:2])
        return decrypt_write_file(cryptobox_index, fdir, fhash, secret)
    except Exception, e:
        handle_exception(e, False)


def have_blob(options, blob_hash):
    """
    have_blob
    @type options: optparse.Values, instance
    @type blob_hash: str, unicode
    """
    blobdir = os.path.join(get_blob_dir(options), blob_hash[:2])
    blobpath = os.path.join(blobdir, blob_hash[2:])
    return os.path.exists(blobpath)


class NoTimeStamp(Exception):
    """
    NoTimeStamp
    """
    pass


def write_blob_to_filepath(memory, node, options, data):
    """
    @type memory: Memory
    @type node: dict
    @type options: optparse.Values, instance
    @type data: str or unicode
    """
    if not node["content_hash_latest_timestamp"][1]:
        raise NoTimeStamp(str(node))

    st_mtime = int(node["content_hash_latest_timestamp"][1])
    dirname_of_path = os.path.dirname(node["doc"]["m_path"])
    new_path = os.path.join(options.dir, os.path.join(dirname_of_path.lstrip(os.path.sep), node["doc"]["m_name"]))
    memory = add_local_file_history(memory, new_path)
    write_file(path=new_path, data=data, a_time=st_mtime, m_time=st_mtime, st_mode=None, st_uid=None, st_gid=None)
    return memory


def write_blobs_to_filepaths(memory, options, file_nodes, data, downloaded_fhash):
    """
    @type memory: Memory
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
        memory = add_server_file_history(memory, fnode["doc"]["m_path"])
        write_blob_to_filepath(memory, fnode, options, data)

    return memory

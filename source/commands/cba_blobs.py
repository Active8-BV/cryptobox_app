# coding=utf-8
"""
blob routines, loosely based on git
"""
import os
from cba_utils import handle_exception, strcmp, update_progress, output_json
from cba_file import read_and_encrypt_file, ensure_directory, decrypt_write_file, write_file, add_local_path_history, add_server_path_history


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


def encrypt_new_blobs(secret, new_blobs):
    """
    @type secret: str or unicode
    @type new_blobs: dict
    """
    processed_files = 0
    numfiles = len(new_blobs)

    for fhash in new_blobs:
        ensure_directory(new_blobs[fhash]["blobdir"])
        update_progress(processed_files, numfiles, "encrypting: " + os.path.basename(new_blobs[fhash]["fpath"]))
        read_and_encrypt_file(new_blobs[fhash]["fpath"], new_blobs[fhash]["blobpath"], secret)
        processed_files += 1


def decrypt_blob_to_filepaths(blobdir, localindex, fhash, secret):
    """
    @param blobdir: str or unicode
    @type blobdir:
    @param localindex: dict
    @type localindex:
    @param fhash: str or unicode
    @type fhash:
    @param secret: str or unicode
    @type secret:
    """

    #noinspection PyBroadException
    try:
        fdir = os.path.join(blobdir, fhash[:2])
        return decrypt_write_file(localindex, fdir, fhash, secret)
    except Exception:
        handle_exception(False)


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


def write_blob_to_filepath(memory, node, options, data, content_path):
    """
    @type memory: Memory
    @type node: dict
    @type options: optparse.Values, instance
    @type data: str or unicode
    @type content_path: str or unicode
    """
    if not node["content_hash_latest_timestamp"][1]:
        raise NoTimeStamp(str(node))

    st_mtime = int(node["content_hash_latest_timestamp"][1])
    dirname_of_path = os.path.dirname(node["doc"]["m_path_p64s"])
    new_path = os.path.join(options.dir, os.path.join(dirname_of_path.lstrip(os.path.sep), node["doc"]["m_name"]))
    memory = add_local_path_history(memory, new_path)
    output_json({"msg": new_path})
    write_file(path=new_path, data=data, content_path=content_path, a_time=st_mtime, m_time=st_mtime, st_mode=None, st_uid=None, st_gid=None)
    return memory


def write_blobs_to_filepaths(memory, options, file_nodes, data, downloaded_fhash, content_path):
    """
    @type memory: Memory
    @type options: optparse.Values
    @type file_nodes: tuple
    @type data: str or unicode or None
    @type downloaded_fhash: unicode
    @type content_path: str or unicode
    """
    files_same_hash = []
    file_nodes_copy = list(file_nodes)

    for sfile in file_nodes:
        fhash = sfile["content_hash_latest_timestamp"][0]

        if strcmp(fhash, downloaded_fhash):
            files_same_hash.append(sfile)

    for fnode in files_same_hash:
        memory = add_server_path_history(memory, fnode["doc"]["m_path_p64s"])
        write_blob_to_filepath(memory, fnode, options, data, content_path)
        file_nodes_copy.remove(fnode)

    return memory, file_nodes_copy

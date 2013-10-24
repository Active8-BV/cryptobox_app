# coding=utf-8
"""
file operations
"""
import os
from cba_utils import strcmp, pickle_object, unpickle_object, update_item_progress
from cba_crypto import make_sha1_hash, decrypt_file_smp, encrypt_file_smp


def ensure_directory(path):
    """
    @type path: str or unicode or unicode
    """
    if not os.path.exists(path):
        os.makedirs(path)


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
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    fout = open(path, "wb")
    fout.write(data)
    fout.close()
    os.utime(path, (a_time, m_time))
    if st_mode:
        os.chmod(path, st_mode)

    if st_uid and st_gid:
        os.chown(path, st_uid, st_gid)


def read_file(path, read_data=False):
    """
    @type path: str or unicode
    @type read_data: bool
    @return: @rtype:
    """
    if read_data:
        data = open(path, "rb").read()
    else:
        data = None

    stats = os.stat(path)
    return stats.st_ctime, stats.st_atime, stats.st_mtime, stats.st_mode, stats.st_uid, stats.st_gid, stats.st_size, data


def read_file_to_fdict(path, read_data=False):
    """
    @type path: str or unicode
    @type read_data: bool
    @return: @rtype:
    """
    ft = read_file(path, read_data)
    file_dict = {"st_ctime": int(ft[0]), "st_atime": int(ft[1]), "st_mtime": int(ft[2]), "st_mode": int(ft[3]), "st_uid": int(ft[4]), "st_gid": int(ft[5]), "st_size": int(ft[6])}

    if read_data:
        file_dict["data"] = ft[7]

    return file_dict


def write_fdict_to_file(fdict, path):
    """
    @param fdict: dict
    @type fdict:
    @param path: str or unicode
    @type path:
    """
    write_file(path, fdict["data"], fdict["st_atime"], fdict["st_mtime"], fdict["st_mode"], fdict["st_uid"], fdict["st_gid"])


def read_and_encrypt_file(fpath, blobpath, secret):
    """
    @type fpath: str or unicode
    @type blobpath: str or unicode
    @type secret: str or unicode
    @return: @rtype:
    """
    enc_file_struct = encrypt_file_smp(secret, fpath, progress_callback=update_item_progress)
    pickle_object(blobpath, enc_file_struct)
    return True


def decrypt_file_and_write(fpath, unenc_path, secret):
    """
    @type fpath: str or unicode
    @type unenc_path: str or unicode
    @type secret: str or unicode
    @return: @rtype:
    """
    enc_file_struct = unpickle_object(fpath)
    dec_file = decrypt_file_smp(secret, enc_file_struct, progress_callback=update_item_progress)
    open(unenc_path, "wb").write(dec_file.read())
    return True


def decrypt_write_file(localindex, fdir, fhash, secret):
    """
    @param localindex: dict
    @type localindex:
    @param fdir: str or unicode
    @type fdir:
    @param fhash: str or unicode
    @type fhash:
    @param secret: str or unicode
    @type secret:
    """
    blob_enc = unpickle_object(os.path.join(fdir, fhash[2:]))
    file_blob = {"data": decrypt_file_smp(secret, blob_enc, update_item_progress).read()}
    paths = []

    for dirhash in localindex["dirnames"]:
        for cfile in localindex["dirnames"][dirhash]["filenames"]:
            if strcmp(fhash, cfile["hash"]):
                fpath = os.path.join(localindex["dirnames"][dirhash]["dirname"], cfile["name"])

                if not os.path.exists(fpath):
                    ft = localindex["filestats"][fpath]
                    file_blob["st_atime"] = int(ft["st_atime"])
                    file_blob["st_mtime"] = int(ft["st_mtime"])
                    file_blob["st_mode"] = int(ft["st_mode"])
                    file_blob["st_uid"] = int(ft["st_uid"])
                    file_blob["st_gid"] = int(ft["st_gid"])
                    write_fdict_to_file(file_blob, fpath)
                    paths.append(fpath)

    return paths


def make_cryptogit_hash(fpath, datadir, localindex):
    """
    @type fpath: str or unicode
    @type datadir: str or unicode
    @type localindex: dict
    @return: @rtype:
    """
    file_dict = read_file_to_fdict(fpath, read_data=True)
    filehash = make_sha1_hash("blob " + str(file_dict["st_size"]) + "\0" + str(file_dict["data"]))
    blobdir = os.path.join(os.path.join(datadir, "blobs"), filehash[:2])
    blobpath = os.path.join(blobdir, filehash[2:])
    filedata = {"filehash": filehash, "fpath": fpath, "blobpath": blobpath, "blobdir": blobdir, "blob_exists": os.path.exists(blobpath)}
    del file_dict["data"]
    localindex["filestats"][fpath] = file_dict
    return filedata, localindex

# coding=utf-8
"""
file operations
"""
import os
from cba_utils import handle_exception, strcmp
from cba_crypto import encrypt, decrypt, pickle_object, unpickle_object


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
    fout = open(path, "wb")
    fout.write(data)
    fout.close()
    os.utime(path, (a_time, m_time))
    if st_mode:
        os.chmod(path, st_mode)

    if st_uid and st_gid:
        os.chown(path, st_uid, st_gid)


def read_file(path):
    """
    @type path: str or unicode
    @return: @rtype:
    """
    data = open(path, "rb").read()
    stats = os.stat(path)
    return data, stats.st_ctime, stats.st_atime, stats.st_mtime, stats.st_mode, stats.st_uid, stats.st_gid


def read_file_to_fdict(path):
    """
    @type path: str or unicode
    @return: @rtype:
    """
    ft = read_file(path)
    file_dict = {"data": ft[0],

                 "st_ctime": int(ft[1]),
                 "st_atime": int(ft[2]),
                 "st_mtime": int(ft[3]),
                 "st_mode": int(ft[4]),
                 "st_uid": int(ft[5]),
                 "st_gid": int(ft[6])}

    return file_dict


def write_fdict_to_file(fdict, path):
    """
    @param fdict: dict
    @type fdict:
    @param path: str or unicode
    @type path:
    """
    write_file(path, fdict["data"], fdict["st_atime"], fdict["st_mtime"], fdict["st_mode"], fdict["st_uid"], fdict["st_gid"])


def read_and_encrypt_file(fpath, blobpath, salt, secret):
    """
    @type fpath: str or unicode
    @type blobpath: str or unicode
    @type salt: str or unicode
    @type secret: str or unicode
    @return: @rtype:
    """

    try:
        file_dict = read_file_to_fdict(fpath)
        encrypted_file_dict = encrypt(salt, secret, file_dict["data"])
        pickle_object(blobpath, encrypted_file_dict)
        return None
    except Exception, e:
        handle_exception(e)


def decrypt_file_and_write(fpath, unenc_path, secret):
    """
    @type fpath: str or unicode
    @type unenc_path: str or unicode
    @type secret: str or unicode
    @return: @rtype:
    """

    try:
        encrypted_file_dict = unpickle_object(fpath)
        unencrypted_file_dict = decrypt(secret, encrypted_file_dict)
        open(unenc_path, "wb").write(unencrypted_file_dict)
        return None
    except Exception, e:
        handle_exception(e)


def decrypt_write_file(cryptobox_index, fdir, fhash, secret):
    """
    @param cryptobox_index: dict
    @type cryptobox_index:
    @param fdir: str or unicode
    @type fdir:
    @param fhash: str or unicode
    @type fhash:
    @param secret: str or unicode
    @type secret:
    """
    blob_enc = unpickle_object(os.path.join(fdir, fhash[2:]))
    file_blob = {"data": decrypt(secret, blob_enc)}

    for dirhash in cryptobox_index["dirnames"]:
        for cfile in cryptobox_index["dirnames"][dirhash]["filenames"]:
            if strcmp(fhash, cfile["hash"]):
                fpath = os.path.join(cryptobox_index["dirnames"][dirhash]["dirname"], cfile["name"])

                if not os.path.exists(fpath):
                    ft = cryptobox_index["filestats"][fpath]
                    file_blob["st_atime"] = int(ft["st_atime"])
                    file_blob["st_mtime"] = int(ft["st_mtime"])
                    file_blob["st_mode"] = int(ft["st_mode"])
                    file_blob["st_uid"] = int(ft["st_uid"])
                    file_blob["st_gid"] = int(ft["st_gid"])
                    write_fdict_to_file(file_blob, fpath)


def make_cryptogit_hash(fpath, datadir, cryptobox_index):
    """
    @type fpath: str or unicode
    @type datadir: str or unicode
    @type cryptobox_index: dict
    @return: @rtype:
    """
    file_dict = read_file_to_fdict(fpath)
    filehash = make_sha1_hash("blob " + str(len(file_dict["data"])) + "\0" + str(file_dict["data"]))
    blobdir = os.path.join(os.path.join(datadir, "blobs"), filehash[:2])
    blobpath = os.path.join(blobdir, filehash[2:])
    filedata = {"filehash": filehash,
                "fpath": fpath,
                "blobpath": blobpath,
                "blobdir": blobdir,
                "blob_exists": os.path.exists(blobpath)}

    del file_dict["data"]
    cryptobox_index["filestats"][fpath] = file_dict
    return filedata

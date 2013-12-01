# coding=utf-8
"""
file operations
"""
import os
from cba_utils import strcmp, unpickle_object, update_item_progress, output_json
from cba_crypto import make_sha1_hash, make_sha1_hash_file, decrypt_file_smp, encrypt_file_smp


def ensure_directory(path):
    """
    @type path: str or unicode or unicode
    """
    if not os.path.exists(path):
        os.makedirs(path)


def write_file(path, data, a_time, m_time, st_mode, st_uid, st_gid):
    """
    @type path: str
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
    file_dict = {"st_ctime": int(ft[0]),
                 "st_atime": int(ft[1]),
                 "st_mtime": int(ft[2]),
                 "st_mode": int(ft[3]),
                 "st_uid": int(ft[4]),
                 "st_gid": int(ft[5]),
                 "st_size": int(ft[6])}

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
    output_json({"msg": "write: " + path})
    write_file(path, fdict["data"], fdict["st_atime"], fdict["st_mtime"], fdict["st_mode"], fdict["st_uid"], fdict["st_gid"])


def read_and_encrypt_file(fpath, blobpath, secret):
    """
    @type fpath: str or unicode
    @type blobpath: str or unicode
    @type secret: str or unicode
    @return: @rtype:
    """
    enc_file_paths = encrypt_file_smp(secret, fpath, progress_callback=update_item_progress)
    enc_file_paths = [x for x in enumerate(enc_file_paths)]
    with open(blobpath, "w") as configfp:
        for chunk_path in enc_file_paths:
            path = blobpath + "_" + str(chunk_path[0])
            os.rename(chunk_path[1], path)
            configfp.write(path + "\n")

    return True


def decrypt_file_and_write(enc_path, unenc_path, secret):
    """
    @type enc_path: str or unicode
    @type unenc_path: str or unicode
    @type secret: str or unicode
    @return: @rtype:
    """
    enc_file_chunks = []
    with open(enc_path) as enc_fp:
        enc_file_chunk_path = enc_fp.readline()

        while enc_file_chunk_path:
            enc_file_chunks.append(enc_file_chunk_path.strip())
            enc_file_chunk_path = enc_fp.readline()

    dec_file = decrypt_file_smp(secret, enc_files=enc_file_chunks, progress_callback=update_item_progress)
    open(unenc_path, "wb").write(dec_file.read())
    os.remove(enc_path)
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
    data = decrypt_file_smp(secret, blob_enc, update_item_progress).read()
    file_blob = {"data": data}
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
    file_dict = read_file_to_fdict(fpath)
    filehash = make_sha1_hash_file("blob " + str(file_dict["st_size"]) + "\0", fpath)
    blobdir = os.path.join(os.path.join(datadir, "blobs"), filehash[:2])
    blobpath = os.path.join(blobdir, filehash[2:])
    filedata = {"filehash": filehash,
                "fpath": fpath,
                "blobpath": blobpath,
                "blobdir": blobdir,
                "blob_exists": os.path.exists(blobpath)}

    localindex["filestats"][fpath] = file_dict
    return filedata, localindex


def get_mtime_and_content_hash(fpath):
    """
    @type fpath: str or unicode
    """
    if not os.path.exists(fpath):
        return None, None

    if os.path.isdir(fpath):
        return None, None

    file_dict = read_file_to_fdict(fpath, read_data=True)
    filehash = make_sha1_hash("blob " + str(file_dict["st_size"]) + "\0" + str(file_dict["data"]))
    return file_dict["st_mtime"], filehash


def path_to_relative_path_unix_style(memory, relative_path_name):
    """
    path_to_relative_path_unix_style
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_name = relative_path_name.replace(memory.get("cryptobox_folder"), "")
    relative_path_unix_style = relative_path_name.replace(os.path.sep, "/")
    return relative_path_unix_style


def have_serverhash(memory, node_path):
    """
    have_serverhash
    @type memory: Memory
    @type node_path: str, unicode
    """
    node_path_relative = path_to_relative_path_unix_style(memory, node_path)
    return memory.set_have_value("serverpath_history", (node_path_relative, make_sha1_hash(node_path_relative))), memory


def in_server_path_history(memory, relative_path_name):
    """
    in_server_path_history
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style = path_to_relative_path_unix_style(memory, relative_path_name)
    has_server_hash, memory = have_serverhash(memory, relative_path_unix_style)
    return has_server_hash, memory


def add_server_path_history(memory, relative_path_name):
    """
    add_server_path_history
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style = path_to_relative_path_unix_style(memory, relative_path_name)
    memory.set_add_value("serverpath_history", (relative_path_unix_style, make_sha1_hash(relative_path_unix_style)))
    return memory


def del_serverhash(memory, relative_path_name):
    """
    del_serverhash
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style = path_to_relative_path_unix_style(memory, relative_path_name)

    if memory.set_have_value("serverpath_history", (relative_path_unix_style, make_sha1_hash(relative_path_unix_style))):
        memory.set_delete_value("serverpath_history", (relative_path_unix_style, make_sha1_hash(relative_path_unix_style)))
    return memory


def del_server_path_history(memory, relative_path_name):
    """
    @type memory: Memory
    del_server_path_history
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style = path_to_relative_path_unix_style(memory, relative_path_name)
    memory = del_serverhash(memory, relative_path_unix_style)
    return memory


def add_local_path_history(memory, fpath):
    """
    @type memory: Memory
    add_local_path_history
    @type fpath: str, unicode
    """
    relative_path = path_to_relative_path_unix_style(memory, fpath)
    memory.set_add_value("localpath_history", (relative_path, fpath, get_mtime_and_content_hash(fpath)))
    return memory


def in_local_path_history(memory, fpath):
    """
    @type memory: Memory
    in_local_path_history
    @type fpath: str, unicode
    """
    relative_path = path_to_relative_path_unix_style(memory, fpath)
    inpath = False

    if memory.has("localpath_history"):
        collection = memory.get("localpath_history")

        for v in collection:
            if relative_path == v[0]:
                inpath = True
                break

    return inpath, memory


def del_local_path_history(memory, fpath):
    """
    @type memory: Memory
    del_local_path_history
    """
    relative_path = path_to_relative_path_unix_style(memory, fpath)

    if memory.has("localpath_history"):
        collection = memory.get("localpath_history")
        new_collection = []

        for v in collection:
            delete = False

            if relative_path == v[0]:
                delete = True
            elif fpath == v[1]:
                delete = True
            elif str(v[0]).startswith(relative_path):
                delete = True

            if not delete:
                new_collection.append(v)
        memory.replace("localpath_history", set(new_collection))

    return memory

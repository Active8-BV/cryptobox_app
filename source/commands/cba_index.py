# coding=utf-8
"""
indexing routines
"""
import os
import shutil
import base64
from Crypto import Random
from cba_utils import log, strcmp, get_uuid, update_progress, unpickle_object, Memory, pickle_object
from cba_crypto import password_derivation, make_sha1_hash, encrypt_object, decrypt_object
from cba_blobs import encrypt_new_blobs, get_data_dir, decrypt_blob_to_filepaths
from cba_file import ensure_directory, decrypt_file_and_write, read_and_encrypt_file, make_cryptogit_hash


class TreeLoadError(Exception):
    """
    TreeLoadError
    """
    pass


def get_cryptobox_index(memory):
    """
    @type memory: Memory
    get_cryptobox_index
    """
    if memory.has("cryptobox_index"):
        return memory.get("cryptobox_index")
    else:
        return dict()


class NoLocalIndex(Exception):
    """
    NoLocalIndex
    """
    pass


def store_cryptobox_index(memory, index):
    """
    store_cryptobox_index
    @type memory: Memory
    @type index: dict
    """
    memory.replace("cryptobox_index", index)
    return memory


def cryptobox_locked(memory):
    """
    cryptobox_locked
    @type memory: Memory
    """
    locked = True
    current_cryptobox_index = get_cryptobox_index(memory)

    if not "dirnames" in current_cryptobox_index:
        locked = False
    else:
        for dirname in current_cryptobox_index["dirnames"]:
            if not strcmp(current_cryptobox_index["dirnames"][dirname]["dirname"], memory.get("cryptobox_folder")):
                if os.path.exists(current_cryptobox_index["dirnames"][dirname]["dirname"]):
                    locked = False
    if locked:
        try:

            mempath = os.path.join(os.path.join(memory.get("cryptobox_folder"), ".cryptobox", "memory.pickle"))
            unpickle_object(mempath)
            locked = False
        except Exception, e:
            log(str(e))

    return locked


def get_secret(memory, options):
    """
    get_secret
    @type memory: Memory
    @type options: optparse.Values, instance
    """
    password = options.password
    current_cryptobox_index = get_cryptobox_index(memory)

    if current_cryptobox_index:
        salt = base64.decodestring(current_cryptobox_index["salt_b64"])
    else:
        salt = Random.new().read(32)

    return salt, password_derivation(password, salt)


def index_files_visit(arg, dir_name, names):
    """
    @type arg: dict
    @type dir_name: str or unicode
    @type names: list
    """
    filenames = [os.path.basename(x) for x in filter(lambda fpath: not os.path.os.path.isdir(fpath), [os.path.join(dir_name, x.lstrip(os.path.sep)) for x in names])]
    dirname_hash = make_sha1_hash(dir_name.replace(arg["DIR"], "").replace(os.path.sep, "/"))
    nameshash = make_sha1_hash("".join(names))

    folder = {"dirname": dir_name, "dirnamehash": dirname_hash, "filenames": [{'name': x} for x in filenames], "nameshash": nameshash}
    arg["folders"]["dirnames"][dirname_hash] = folder
    arg["numfiles"] += len(filenames)


def make_local_index(options):
    """
    make_local_index
    @type options: optparse.Values, instance
    """
    datadir = get_data_dir(options)
    args = {"DIR": options.dir, "folders": {"dirnames": {}, "filestats": {}}, "numfiles": 0}
    os.path.walk(options.dir, index_files_visit, args)

    for dir_name in args["folders"]["dirnames"].copy():
        if datadir in args["folders"]["dirnames"][dir_name]["dirname"]:
            del args["folders"]["dirnames"][dir_name]

    cryptobox_index = args["folders"]
    return cryptobox_index


def index_and_encrypt(memory, options, localindex_param):
    """
    index_and_encrypt
    @type memory: Memory
    @type options: optparse.Values, instance
    @type localindex_param: dict
    @rtype salt, secret, memory, localindex: str, str, Memory, dict
    """
    localindex = localindex_param
    datadir = get_data_dir(options)

    if cryptobox_locked(memory):
        log("cba_index.py:140", "cryptobox is locked, nothing can be added now first decrypt (-d)")
        return None, None, memory, localindex

    salt, secret = get_secret(memory, options)
    ensure_directory(datadir)

    new_blobs = {}
    file_cnt = 0
    new_objects = 0
    hash_set_on_disk = set()

    for dirhash in localindex["dirnames"]:
        for fname in localindex["dirnames"][dirhash]["filenames"]:
            file_cnt += 1
            file_dir = localindex["dirnames"][dirhash]["dirname"]
            file_path = os.path.join(file_dir, fname["name"])

            if os.path.exists(file_path):
                filedata, localindex = make_cryptogit_hash(file_path, datadir, localindex)
                fname["hash"] = filedata["filehash"]
                hash_set_on_disk.add(filedata["filehash"])
                if not filedata["blob_exists"]:
                    new_blobs[filedata["filehash"]] = filedata
                    new_objects += 1

                if len(new_blobs) > 1500:
                    encrypt_new_blobs(secret, new_blobs)
                    new_blobs = {}

    if len(new_blobs) > 0:
        if len(new_blobs) > 0:
            encrypt_new_blobs(secret, new_blobs)

    localindex["salt_b64"] = base64.encodestring(salt)
    memory = store_cryptobox_index(memory, localindex)

    if options.remove:
        ld = os.listdir(options.dir)
        ld.remove(".cryptobox")

        for fname in ld:
            fpath = os.path.join(options.dir, fname)
            log("delete", fpath)
            if os.path.isdir(fpath):
                shutil.rmtree(fpath, True)
            else:
                os.remove(fpath)

    obsolute_blob_store_entries = set()
    blob_dirs = os.path.join(datadir, "blobs")
    ensure_directory(blob_dirs)

    for blob_dir in os.listdir(blob_dirs):
        blob_store = os.path.join(blob_dirs, blob_dir.lstrip(os.path.sep))

        if os.path.isdir(blob_store):
            for blob_file in os.listdir(blob_store):
                found = False

                for fhash in hash_set_on_disk:
                    if strcmp(fhash, (blob_dir + blob_file)):
                        found = True

                if not found:
                    obsolute_blob_store_entries.add(blob_dir + blob_file)

    for f_hash in obsolute_blob_store_entries:
        blob_dir = os.path.join(blob_dirs, f_hash[:2])
        blob_path = os.path.join(blob_dir, f_hash[2:])
        os.remove(blob_path)
        if os.path.isdir(blob_dir):
            blob_entries = [f for f in os.listdir(blob_dir) if not f.startswith('.')]

            if len(blob_entries) == 0:
                shutil.rmtree(blob_dir, True)

    return salt, secret, memory, localindex


def get_hidden_configs(options):
    dirs_base_folder = os.listdir(options.basedir)
    hidden_configs = []
    for base_folder in dirs_base_folder:
        dirpath = os.path.join(options.basedir, base_folder)
        if os.path.isdir(dirpath):
            for fpath in os.listdir(dirpath):
                if fpath.endswith(".cryptoboxfolder"):
                    hidden_configs.append((base_folder, fpath))

    return hidden_configs


def restore_hidden_config(options):
    """
    @param options:
    @type options:
    """
    hidden_configs = get_hidden_configs(options)

    for config in hidden_configs:
        config_file_path = os.path.join(options.basedir, config[0])
        config_file_path = os.path.join(config_file_path, config[1])

        cryptoboxname = unpickle_object(config_file_path)
        cryptoboxname, secret = decrypt_object("", key=options.password, obj_string=cryptoboxname["encrypted_name"], salt=cryptoboxname["salt"])

        if strcmp(cryptoboxname, options.cryptobox):
            if os.path.exists(config_file_path):
                os.remove(config_file_path)

            p1 = os.path.dirname(config_file_path)
            p2 = os.path.join(options.basedir, cryptoboxname)
            os.rename(p1, p2)

            if secret:
                datadir = get_data_dir(options)
                mempath = os.path.join(datadir, "memory.pickle")

                if os.path.exists(mempath + ".enc"):
                    decrypt_file_and_write(mempath + ".enc", mempath, secret=secret)
                    os.remove(mempath + ".enc")
            return


def hide_config(options, salt, secret):
    """
    @param options:
    @type options:
    @param salt:
    @type salt:
    @param secret:
    @type secret:
    """
    if options.encrypt and options.remove and salt and secret:
        datadir = get_data_dir(options)
        mempath = os.path.join(datadir, "memory.pickle")

        if os.path.exists(mempath):
            read_and_encrypt_file(mempath, mempath + ".enc", secret)

            os.remove(mempath)
            hidden_name = "." + get_uuid(3)

            while hidden_name in os.listdir(options.dir):
                hidden_name = "." + get_uuid(3)

            encrypted_name = encrypt_object(secret, options.cryptobox)
            pickle_object(os.path.join(options.dir, hidden_name + ".cryptoboxfolder"), {"encrypted_name": encrypted_name, "salt": salt})
            os.rename(options.dir, os.path.join(os.path.dirname(options.dir), hidden_name))


def check_and_clean_dir(options):
    """
    check_and_clean_dir
    @type options: instance
    """
    if not hasattr(options, "clear") or not hasattr(options, "encrypt"):
        log("check_and_clean_dir needs clear and encrypt option")
        return

    if options.clear == "1":
        if options.encrypt:
            log("clear options cannot be used together with encrypt, possible data loss")
            return

        datadir = get_data_dir(options)
        shutil.rmtree(datadir, True)


def decrypt_and_build_filetree(memory, options):
    """
    decrypt_and_build_filetree
    @type memory: Memory
    @type options: optparse.Values, instance
    """
    password = options.password
    datadir = get_data_dir(options)

    if not os.path.exists(datadir):
        log("nothing to decrypt", datadir, "does not exists")
        return memory

    blobdir = os.path.join(datadir, "blobs")
    cryptobox_index = get_cryptobox_index(memory)

    if cryptobox_index:
        cb_locked = cryptobox_locked(memory)

        if not cb_locked:
            return memory
    else:
        cryptobox_index = None

    hashes = set()

    if cryptobox_index:
        for dirhash in cryptobox_index["dirnames"]:
            if "dirname" in cryptobox_index["dirnames"][dirhash]:
                if not os.path.exists(cryptobox_index["dirnames"][dirhash]["dirname"]):
                    ensure_directory(cryptobox_index["dirnames"][dirhash]["dirname"])

            for cfile in cryptobox_index["dirnames"][dirhash]["filenames"]:
                fpath = os.path.join(cryptobox_index["dirnames"][dirhash]["dirname"], cfile["name"])

                if not os.path.exists(fpath):
                    hashes.add(cfile["hash"])

    processed_files = 0
    numfiles = len(hashes)
    secret = password_derivation(password, base64.decodestring(cryptobox_index["salt_b64"]))

    for fhash in hashes:
        paths = decrypt_blob_to_filepaths(blobdir, cryptobox_index, fhash, secret)
        processed_files += 1
        update_progress(processed_files, numfiles, "decrypting " + "\n\t"+"\n\t".join(paths))

    memory = store_cryptobox_index(memory, cryptobox_index)
    return memory

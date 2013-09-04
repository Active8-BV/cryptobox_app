# coding=utf-8
"""
indexing routines
"""
import os
import shutil
import base64
from Crypto import Random
from cba_utils import cba_warning, strcmp, get_uuid
from cba_memory import Memory
from cba_crypto import password_derivation, make_sha1_hash, unpickle_object, encrypt_object, pickle_object, decrypt_object
from cba_blobs import encrypt_new_blobs, get_data_dir
from cba_file import ensure_directory, decrypt_file_and_write, read_and_encrypt_file, make_cryptogit_hash
from cba_feedback import update_progress


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
    current_cryptobox_index = get_cryptobox_index(memory)

    if current_cryptobox_index:
        if current_cryptobox_index["locked"] is True:
            return True
    return False


def get_secret(memory, options):
    """
    get_secret
    @type memory: Memory
    @type options: instance
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
    filenames = [os.path.basename(x) for x in filter(lambda x: not os.path.os.path.isdir(x), [os.path.join(dir_name, x.lstrip(os.path.sep)) for x in names])]
    dirname_hash = make_sha1_hash(dir_name.replace(arg["DIR"], "").replace(os.path.sep, "/"))
    nameshash = make_sha1_hash("".join(names))

    folder = {"dirname": dir_name, "dirnamehash": dirname_hash, "filenames": [{'name': x} for x in filenames], "nameshash": nameshash}
    arg["folders"]["dirnames"][dirname_hash] = folder
    arg["numfiles"] += len(filenames)


def make_local_index(options):
    """
    make_local_index
    @type options: instance
    """
    datadir = get_data_dir(options)
    args = {"DIR": options.dir, "folders": {"dirnames": {}, "filestats": {}}, "numfiles": 0}
    os.path.walk(options.dir, index_files_visit, args)

    for dir_name in args["folders"]["dirnames"].copy():
        if datadir in args["folders"]["dirnames"][dir_name]["dirname"]:
            del args["folders"]["dirnames"][dir_name]

    cryptobox_index = args["folders"]
    return cryptobox_index


def index_and_encrypt(memory, options, localindex):
    """
    index_and_encrypt
    @type memory: Memory
    @type options: instance
    @type localindex: dict
    """
    datadir = get_data_dir(options)

    if cryptobox_locked(memory):
        cba_warning("cba_index.py:140", "cryptobox is locked, nothing can be added now first decrypt (-d)")
        return None, None

    salt, secret = get_secret(memory, options)

    ensure_directory(datadir)

    if len(localindex["dirnames"]) > 0:
        numfiles = reduce(lambda x, y: x + y, [len(localindex["dirnames"][x]["filenames"]) for x in localindex["dirnames"]])
    else:
        numfiles = 0

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
                    encrypt_new_blobs(salt, secret, new_blobs)
                    new_blobs = {}

            update_progress(file_cnt, numfiles, "checking")

    if len(new_blobs) > 0:
        if len(new_blobs) > 0:
            encrypt_new_blobs(salt, secret, new_blobs)

    if options.remove:
        localindex["locked"] = True
    else:
        localindex["locked"] = False
    localindex["salt_b64"] = base64.encodestring(salt)
    memory = store_cryptobox_index(memory, localindex)

    if options.remove:
        ld = os.listdir(options.dir)
        ld.remove(".cryptobox")

        for fname in ld:
            fpath = os.path.join(options.dir, fname)

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

    return salt, secret, memory


def restore_hidden_config(options):
    """
    @param options:
    @type options:
    """
    hidden_configs = [x for x in os.listdir(options.basedir) if x.endswith(".cryptoboxfolder")]
    hidden_configs_dict = {}
    dsecret = {}
    def return_secret(s):
        """
        @param s:
        @type s:
        """
        dsecret[s] = s

    for config in hidden_configs:
        #noinspection PyBroadException
        try:
            config_file_path = os.path.join(options.basedir, config)
            config_stat = os.stat(config_file_path)
            obj = unpickle_object(config_file_path)
            obj = decrypt_object("", key=options.password, obj_string=obj, give_secret_cb=return_secret)
            hidden_configs_dict[config_stat.st_mtime] = (obj, config)
        except:
            pass

    secret = None

    if len(dsecret) > 0:
        for k in dsecret:
            secret = dsecret[k]

    sorted_keys = sorted(hidden_configs_dict.keys())
    sorted_keys.reverse()

    if len(sorted_keys) > 0:
        hidden_config = hidden_configs_dict[sorted_keys[0]]
        sorted_keys.remove(sorted_keys[0])

        for cf in sorted_keys:
            old_config = hidden_configs_dict[cf]
            guid = old_config[1].split(".")[1]

            if os.path.exists(os.path.join(options.basedir, old_config[1])):
                os.remove(os.path.join(options.basedir, old_config[1]))

            if os.path.exists(os.path.join(options.basedir, guid)):
                shutil.rmtree(os.path.join(options.basedir, guid), True)

        guid = hidden_config[1].split(".")[1]

        if os.path.exists(os.path.join(options.basedir, guid)):
            os.rename(os.path.join(options.basedir, guid), os.path.join(options.basedir, hidden_config[0]))

        if os.path.exists(os.path.join(options.basedir, hidden_config[1])):
            os.remove(os.path.join(options.basedir, hidden_config[1]))

    if secret:
        datadir = get_data_dir(options)
        mempath = os.path.join(datadir, "memory.pickle")

        if os.path.exists(mempath + ".enc"):
            decrypt_file_and_write(mempath + ".enc", mempath, secret=secret)
            os.remove(mempath + ".enc")


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
        read_and_encrypt_file(mempath, mempath + ".enc", salt, secret)
        os.remove(mempath)
        hidden_name = get_uuid(3)

        while hidden_name in os.listdir(options.dir):
            hidden_name = get_uuid(3)

        encrypted_name = encrypt_object(salt, secret, options.cryptobox)
        pickle_object(os.path.join(options.basedir, "." + hidden_name + ".cryptoboxfolder"), encrypted_name)
        os.rename(options.dir, os.path.join(os.path.dirname(options.dir), hidden_name))

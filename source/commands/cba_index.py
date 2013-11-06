# coding=utf-8
"""
indexing routines
"""
import os
import shutil
import base64
from Crypto import Random
from cba_utils import strcmp, get_uuid, update_progress, unpickle_object, Memory, pickle_object, output_json
from cba_crypto import password_derivation, make_sha1_hash, encrypt_object, decrypt_object
from cba_blobs import encrypt_new_blobs, get_data_dir, decrypt_blob_to_filepaths
from cba_file import ensure_directory, decrypt_file_and_write, read_and_encrypt_file, make_cryptogit_hash


class TreeLoadError(Exception):
    """
    TreeLoadError
    """
    pass


def get_localindex(memory):
    """
    @type memory: Memory
    get_localindex
    """
    if memory.has("localindex"):
        return memory.get("localindex")
    else:
        return dict()


class NoLocalIndex(Exception):
    """
    NoLocalIndex
    """
    pass


def store_localindex(memory, index):
    """
    store_localindex
    @type memory: Memory
    @type index: dict
    """
    memory.replace("localindex", index)
    return memory


def get_hidden_configs(options):
    """
    :param options:
    :return: :rtype:
    """
    hidden_configs = []

    if os.path.exists(options.basedir):
        dirs_base_folder = os.listdir(options.basedir)

        for base_folder in dirs_base_folder:
            dirpath = os.path.join(options.basedir, base_folder)

            if os.path.isdir(dirpath):
                for fpath in os.listdir(dirpath):
                    if fpath.endswith(".cryptoboxfolder"):
                        hidden_configs.append((base_folder, fpath))

    return hidden_configs


def restore_config(config_file_path, cryptoboxname, options, secret):
    """
    @type config_file_path: str, unicode
    @type cryptoboxname: str, unicode
    @type options: optparse.Values, instance
    @type secret: str, unicode
    """
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


def get_encrypted_configs(options, name_stop=None):
    """
    @type options: optparse.Values, instance
    @param name_stop: stop looking if this name is matched
    @type name_stop:bool
    """
    hidden_configs = get_hidden_configs(options)
    encrypted_configs = []

    for config in hidden_configs:
        config_file_path = os.path.join(options.basedir, config[0])
        config_file_path = os.path.join(config_file_path, config[1])
        cryptoboxname = unpickle_object(config_file_path)
        cryptoboxname, secret = decrypt_object("", key=options.password, obj_string=cryptoboxname["encrypted_name"], salt=cryptoboxname["salt"], progress_callback=None)
        encrypted_configs.append({"cryptoboxname": cryptoboxname, "secret": secret, "config_file_path": config_file_path})
        if name_stop == cryptoboxname:
            return encrypted_configs
    return encrypted_configs


def restore_hidden_config(options):
    """
    @type options: optparse.Values, instance
    """
    encrypted_configs = get_encrypted_configs(options, name_stop=options.cryptobox)

    for encrypted_config in encrypted_configs:
        if strcmp(encrypted_config["cryptoboxname"], options.cryptobox):
            restore_config(encrypted_config["config_file_path"], encrypted_config["cryptoboxname"], options, encrypted_config["secret"])


def hide_config(options, salt, secret):
    """
    @type options: optparse.Values, instance
    @param salt:
    @type salt:
    @param secret:
    @type secret:
    """
    if salt and secret:
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


def quick_lock_check(options):
    """
    quick_lock_check
    @type options: optparse.Values, instance
    """

    #noinspection PyBroadException
    if not os.path.exists(options.dir):
        encrypted_configs = get_encrypted_configs(options, name_stop=options.cryptobox)

        if len(encrypted_configs) > 0:
            return True
    return False


def index_files_visit(arg, dir_name, names):
    """
    @type arg: dict
    @type dir_name: str or unicode
    @type names: list
    """
    filenames = [os.path.basename(x) for x in filter(lambda fpath: not os.path.os.path.isdir(fpath), [os.path.join(dir_name, x.lstrip(os.path.sep)) for x in names])]
    dirname_hash = make_sha1_hash(dir_name.replace(arg["DIR"], "").replace(os.path.sep, "/"))
    nameshash = make_sha1_hash("".join(names))
    folder = {"dirname": dir_name, "dirnamehash": dirname_hash,

              "filenames": [{'name': x} for x in filenames],
                             "nameshash": nameshash}

    arg["folders"]["dirnames"][dirname_hash] = folder
    arg["numfiles"] += len(filenames)


def make_local_index(options):
    """
    make_local_index
    @type options: optparse.Values, instance
    """
    datadir = get_data_dir(options)
    args = {"DIR": options.dir,
            "folders": {"dirnames": {},
            "filestats": {}},
            "numfiles": 0}
    os.path.walk(options.dir, index_files_visit, args)

    for dir_name in args["folders"]["dirnames"].copy():
        if datadir in args["folders"]["dirnames"][dir_name]["dirname"]:
            del args["folders"]["dirnames"][dir_name]

    localindex = args["folders"]
    return localindex


def index_and_encrypt(memory, options):
    """
    index_and_encrypt
    @type memory: Memory
    @type options: optparse.Values, instance
    @rtype salt, secret, memory, localindex: str, str, Memory, dict
    """
    localindex = make_local_index(options)
    datadir = get_data_dir(options)

    if quick_lock_check(options):
        print "cba_index.py:213", "cryptobox is locked, nothing can be added now first decrypt (-d)"
        return None, None, memory, localindex

    salt = None

    if memory.has("salt_b64"):
        salt = base64.decodestring(memory.get("salt_b64"))

    if not salt:
        salt = Random.new().read(32)
        memory.set("salt_b64", base64.encodestring(salt))

    output_json({"msg": "preparing encrypt"})
    secret = password_derivation(options.password, salt)
    ensure_directory(datadir)
    new_blobs = {}
    file_cnt = 0
    new_objects = 0
    hash_set_on_disk = set()
    processed_files = 0
    numfiles = 0

    for dirhash in localindex["dirnames"]:
        numfiles += len(localindex["dirnames"][dirhash]["filenames"])

    for dirhash in localindex["dirnames"]:
        for fname in localindex["dirnames"][dirhash]["filenames"]:
            file_cnt += 1
            file_dir = localindex["dirnames"][dirhash]["dirname"]
            file_path = os.path.join(file_dir, fname["name"])

            if os.path.exists(file_path):
                update_progress(processed_files, numfiles, "indexing " + os.path.basename(file_path))
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

    memory = store_localindex(memory, localindex)

    if options.remove:
        ld = os.listdir(options.dir)
        ld.remove(".cryptobox")
        processed_files = 0
        numfiles = len(ld)

        for fname in ld:
            fpath = os.path.join(options.dir, fname)
            processed_files += 1
            update_progress(processed_files, numfiles, "delete "+os.path.basename(fpath))
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


def reset_cryptobox_local(options):
    """
    check_and_clean_dir
    @type options: optparse.Values, instance
    """
    if not hasattr(options, "clear") or not hasattr(options, "encrypt"):
        print "cba_index.py:315", "check_and_clean_dir needs clear and encrypt option"
        return

    if options.clear == "1":
        if options.encrypt:
            print "cba_index.py:320", "clear options cannot be used together with encrypt, possible data loss"
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
        print "cba_index.py:337", "nothing to decrypt", datadir, "does not exists"
        return memory

    output_json({"msg": "preparing decrypt"})
    blobdir = os.path.join(datadir, "blobs")
    localindex = get_localindex(memory)
    hashes = set()

    if localindex:
        for dirhash in localindex["dirnames"]:
            if "dirname" in localindex["dirnames"][dirhash]:
                if not os.path.exists(localindex["dirnames"][dirhash]["dirname"]):
                    ensure_directory(localindex["dirnames"][dirhash]["dirname"])

            for cfile in localindex["dirnames"][dirhash]["filenames"]:
                fpath = os.path.join(localindex["dirnames"][dirhash]["dirname"], cfile["name"])

                if not os.path.exists(fpath):
                    hashes.add((cfile["hash"], cfile["name"]))

    processed_files = 0
    numfiles = len(hashes)
    secret = password_derivation(password, base64.decodestring(memory.get("salt_b64")))

    for cfile in hashes:
        processed_files += 1
        update_progress(processed_files, numfiles, cfile[1])

        #noinspection PyUnusedLocal
        paths = decrypt_blob_to_filepaths(blobdir, localindex, cfile[0], secret)

    memory = store_localindex(memory, localindex)
    return memory

# coding=utf-8
"""
directory indexing and tree building
"""
import os
import base64
import multiprocessing
from cba_utils import cba_warning
from cba_index import get_cryptobox_index, cryptobox_locked, store_cryptobox_index
from cba_file import ensure_directory
from cba_feedback import update_progress
from cba_crypto import password_derivation
from cba_blobs import decrypt_blob_to_filepaths, get_data_dir


def decrypt_and_build_filetree(memory, options):
    """
    decrypt_and_build_filetree
    @type memory: Memory
    @type options: optparse.Values, instance
    """
    password = options.password
    datadir = get_data_dir(options)

    if not os.path.exists(datadir):
        cba_warning("nothing to decrypt", datadir, "does not exists")
        return

    blobdir = os.path.join(datadir, "blobs")
    cryptobox_index = get_cryptobox_index(memory)

    if cryptobox_index:
        cb_locked = cryptobox_locked(memory)

        if not cb_locked:
            return
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

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    progressdata = {"processed_files": 0,
                    "numfiles": len(hashes)}

    #noinspection PyUnusedLocal

    def done_decrypting(e):
        """
        @param e: event
        @type e:
        """
        progressdata["processed_files"] += 1
        update_progress(progressdata["processed_files"], progressdata["numfiles"], "decrypting")

    secret = password_derivation(password, base64.decodestring(cryptobox_index["salt_b64"]))
    decrypt_results = []

    for fhash in hashes:
        result = pool.apply_async(decrypt_blob_to_filepaths, (blobdir, cryptobox_index, fhash, secret), callback=done_decrypting)
        decrypt_results.append(result)

    pool.close()
    pool.join()
    successfull_decryption = True

    for result in decrypt_results:
        if not result.successful():
            result.get()
            successfull_decryption = False

    if successfull_decryption:
        cryptobox_index["locked"] = False

    memory = store_cryptobox_index(memory, cryptobox_index)

    if len(hashes) > 0:
        print "cba_tree.py:92"
    return memory

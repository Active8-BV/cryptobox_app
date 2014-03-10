# coding=utf-8
"""
unit test for app commands
"""
__author__ = 'rabshakeh'
import unittest
import random
import os
import time
import cPickle
import base64
import sys
from subprocess import Popen, PIPE
from cba_main import cryptobox_command
from cba_utils import get_files_dir, Memory, Dict2Obj
from cba_index import make_local_index, index_and_encrypt, reset_cryptobox_local, hide_config, restore_hidden_config, decrypt_and_build_filetree
from cba_blobs import get_blob_dir, get_data_dir
from cba_sync import instruct_server_to_rename_path, get_server_index, parse_serverindex, instruct_server_to_delete_folders, dirs_on_local, path_to_server_shortid, wait_for_tasks, sync_server, get_sync_changes, short_id_to_server_path, NoSyncDirFound
from cba_file import ensure_directory, make_cryptogit_hash, make_sha1_hash_file, read_file_to_fdict
from cba_crypto import encrypt_file_smp, decrypt_file_smp, smp_apply, cleanup_tempfiles, encrypt_object, decrypt_object
from cba_network import authorize_user, new_mandate, NotAuthorized, get_mandate
sys.path.append("/Users/rabshakeh/workspace/cryptobox")

#noinspection PyUnresolvedReferences
from couchdb_api import MemcachedServer, CouchDBServer, sync_all_views

#noinspection PyUnresolvedReferences
import crypto_api


def delete_progress_file(fname):
    """
    @type fname: str, unicode
    """
    p = os.path.join(os.getcwd(), fname)

    if os.path.exists(p):
        os.remove(p)


def add(a, b):
    """
    @type a: int
    @type b: int
    """
    return a + b


def pc(p):
    """
    @type p: int
    """
    print "tests.py:53", p


def count_files_dir(fpath):
    """
    count_files_dir
    @type fpath: str, unicode
    """
    return len(get_files_dir(fpath))


def print_progress(p):
    """
    :param p: percentage
    """
    print "tests.py:68", "progress", p


class CryptoboxAppTest(unittest.TestCase):
    """
    CryptoboTestCase
    """
    @staticmethod
    def make_testfile(name, sizemb):
        fname = "1MB.zip"
        fpath = os.path.join(os.getcwd(), "testdata")
        fpath = os.path.join(fpath, fname)
        fp_in = open(fpath)
        fpatho = os.path.join(os.getcwd(), "testdata")
        fpatho = os.path.join(fpatho, name)
        fp_out = open(fpatho, "w")

        for i in range(0, sizemb):
            fp_in.seek(0)
            fp_out.write(fp_in.read())

            #fp_out.write("hello")
        print "tests.py:90", "made", name

    def setUp(self):
        """
        setUp
        """
        cleanup_tempfiles()
        os.system("rm -Rf testdata/test")
        self.db_name = "rabshakeh"
        server = "http://127.0.01:8000/"
        self.options_d = {"basedir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata",
                          "dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/test",
                          "encrypt": True,
                          "remove": False,
                          "username": "rabshakeh",
                          "password": "kjhfsd98",
                          "cryptobox": self.db_name,
                          "clear": False,
                          "sync": False,
                          "server": server,
                          "numdownloadthreads": 12}

        self.cboptions = Dict2Obj(self.options_d)
        mc = RedisServer("mutex")
        mc.flush_all()
        self.cbmemory = Memory()
        self.cbmemory.set("cryptobox_folder", self.cboptions.dir)

        #    self.reset_cb_db_clean()
        #    self.cbmemory = authorize_user(self.cbmemory, self.cboptions, force=True)
        self.do_wait_for_tasks = True
        self.testfile_sizes = ["2MB.zip", "200MB.zip", "100MB.zip", "20MB.zip", "5MB.zip", "50MB.zip"]

        for tfn in self.testfile_sizes:
            if not os.path.exists(os.path.join("testdata", tfn)):
                self.make_testfile(tfn, int(tfn.replace("MB.zip", "")))

        self.remove_temp_files = False

    #noinspection PyPep8Naming
    def clear_tempfiles(self):
        if self.remove_temp_files:
            for tfn in self.testfile_sizes:
                if os.path.exists(os.path.join("testdata", tfn)):
                    os.remove(os.path.join("testdata", tfn))

    def tearDown(self):
        """
        tearDown
        """
        if self.do_wait_for_tasks:
            wait_for_tasks(self.cbmemory, self.cboptions)
        self.cbmemory.save(get_data_dir(self.cboptions))
        if os.path.exists('stdout.txt'):
            os.remove('stdout.txt')

        if os.path.exists('stderr.txt'):
            os.remove('stderr.txt')
        delete_progress_file("progress")
        delete_progress_file("item_progress")
        if self.remove_temp_files:
            self.clear_tempfiles()

    def unzip_testfiles_clean(self):
        """
        unzip_testfiles_clean
        """
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))
        os.system("cd testdata; cp testmap_clean.zip test.zip")
        os.system("cd testdata; unzip -o test.zip > /dev/null")
        os.system("rm testdata/test.zip")

    def unzip_testfiles_synced(self):
        """
        unzip_testfiles_synced
        """
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))
        os.system("cd testdata; cp testmap_synced.zip test.zip")
        os.system("cd testdata; unzip -o test.zip > /dev/null")
        os.system("rm testdata/test.zip")
        self.cbmemory.load(get_data_dir(self.cboptions))

    def unzip_testfiles_configonly(self):
        """
        unzip_testfiles_configonly
        """
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))
        os.system("cd testdata; cp testmap_config.zip test.zip")
        os.system("cd testdata; unzip -o test.zip > /dev/null")
        os.system("rm testdata/test.zip")
        self.cbmemory.load(get_data_dir(self.cboptions))

    def reset_cb_db(self):
        """
        reset_cb_db_clean
        """
        server = "http://127.0.0.1:5984/"
        os.system("rm -Rf testdata/test")
        os.system("cp testdata/rabshakeh.dump /Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl")
        self.pipe = Popen("nohup python server/manage.py load -c rabshakeh", shell=True, stderr=PIPE, stdout=PIPE, cwd="/Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl")
        self.pipe.wait()
        dbase = CouchDBServer(self.db_name, [server])
        sync_all_views(dbase, ["couchdb_api", "crypto_api"])
        time.sleep(0.5)

    def reset_cb_db_clean(self):
        """
        reset_cb_db_clean
        """
        os.system("cp testdata/rabshakeh_clean.dump testdata/rabshakeh.dump")
        self.reset_cb_db()
        os.system("rm testdata/rabshakeh.dump")
        os.system("rm -Rf /Users/rabshakeh/workspace/cloudfiles/couchdb_test_crypto_docs")

    def reset_cb_db_synced(self):
        """
        reset_cb_db_synced
        """
        os.system("cp testdata/rabshakeh_synced.dump testdata/rabshakeh.dump")
        self.reset_cb_db()
        os.system("cp testdata/couchdb_test_crypto_docs.zip /Users/rabshakeh/workspace/cloudfiles/")
        os.system("cd /Users/rabshakeh/workspace/cloudfiles; unzip -o couchdb_test_crypto_docs.zip > /dev/null; rm couchdb_test_crypto_docs.zip")

    def reset_cb_dir(self):
        """
        complete_reset
        """
        os.system("rm -Rf testdata/test")
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))

    def test_reset_all(self):
        """
        test_reset_all
        """
        self.do_wait_for_tasks = False
        self.reset_cb_dir()
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()

    def test_smp_apply(self):
        self.do_wait_for_tasks = False
        items = [(x, x + random.randint(1, 10)) for x in range(0, 10)]
        res_items = [x[0] + x[1] for x in items]
        res_items2 = smp_apply(add, items)
        self.assertEquals(res_items, res_items2)

    def test_encrypt_file_smp(self):
        """
        test_encrypt_file
        """
        self.do_wait_for_tasks = False

        #self.make_testfile("1000MB.zip", 1000)
        fname = "testdata/200MB.zip"
        secret = '\xeb>M\x04\xc22\x96!\xce\xed\xbb.\xe1u\xc7\xe4\x07h<.\x87\xc9H\x89\x8aj\xb4\xb2b5}\x95'
        enc_files = encrypt_file_smp(secret, fname, print_progress)
        dec_file = decrypt_file_smp(secret, enc_files=enc_files, progress_callback=print_progress, delete_enc_files=True)
        h1 = make_sha1_hash_file(fpi=dec_file)
        h2 = make_sha1_hash_file(fpi=open(fname))
        self.assertEqual(h1, h2)

    def test_encrypt_file_smp_single_file(self):
        """
        test_encrypt_file
        """
        self.do_wait_for_tasks = False
        fname = "testdata/200MB.zip"
        secret = '\xeb>M\x04\xc22\x96!\xce\xed\xbb.\xe1u\xc7\xe4\x07h<.\x87\xc9H\x89\x8aj\xb4\xb2b5}\x95'
        enc_file = encrypt_file_smp(secret, fname, print_progress, single_file=True)
        dec_file = decrypt_file_smp(secret, enc_file=enc_file, progress_callback=print_progress)
        self.assertEqual(make_sha1_hash_file(fpi=dec_file), make_sha1_hash_file(fpi=open(fname)))

    def test_object_encryption(self):
        """
        test_object_encryption
        """
        self.do_wait_for_tasks = False
        mydict = {"hello": "world"}
        encrypted_obj = encrypt_object("kjhfsd98", mydict)
        mydict2, secret = decrypt_object("kjhfsd98", encrypted_obj)
        self.assertEqual(mydict, mydict2)

    def test_index_no_box_given(self):
        """
        test_index
        """
        self.do_wait_for_tasks = False
        self.no_box_given = self.options_d.copy()
        self.no_box_given = Dict2Obj(self.no_box_given)
        del self.no_box_given["cryptobox"]

        #with self.assertRaisesRegexp(ExitAppWarning, "No cryptobox given -b or --cryptobox"):
        self.assertFalse(cryptobox_command(self.no_box_given))

    def test_index_directory(self):
        """
        test_index
        """
        self.do_wait_for_tasks = False
        os.system("rm -Rf testdata/test")
        self.unzip_testfiles_clean()
        self.cboptions.sync = False
        localindex_check = cPickle.load(open("testdata/localindex_test.pickle"))
        localindex = make_local_index(self.cboptions)

        #cPickle.dump(localindex, open("testdata/localindex_test.pickle", "w"))
        self.assertTrue(localindex_check == localindex)

    def test_index_and_encrypt(self):
        """
        test_index_and_encrypt
        """
        self.reset_cb_dir()
        self.unzip_testfiles_synced()
        self.do_wait_for_tasks = False
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 38)

        # add a new file
        open(os.path.join(self.cboptions.dir, "hello world.txt"), "w").write("hello world 123 Dit is random data")
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 46)

        # same content, blob count should not rise
        open(os.path.join(self.cboptions.dir, "hello world2.txt"), "w").write("hello world 123 Dit is random data")
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 46)

    @staticmethod
    def delete_hidden_configs():
        """
        delete_hidden_configs
        """
        for i in os.listdir("testdata"):
            p = os.path.join(os.path.join(os.getcwd(), "testdata"), i)

            if os.path.isdir(p):
                if i.startswith("."):
                    import shutil
                    shutil.rmtree(p)

    def test_hide_config(self):
        """
        test_hide_config
        """
        self.delete_hidden_configs()
        self.do_wait_for_tasks = False
        self.unzip_testfiles_configonly()
        p = os.path.join(os.path.join(os.getcwd(), "testdata"), "test")
        org_files = get_files_dir(p)
        org_files = [x for x in org_files if "memory.pickle.json" not in x]
        salt = "123"
        secret = base64.decodestring('Ea9fxt0JExxPqkbbIAFggRz0DIsFumuXX/xnuARPOTw=\n')
        hide_config(self.cboptions, salt, secret)
        restore_hidden_config(self.cboptions)
        org_files2 = get_files_dir(p)
        self.assertEqual(set(org_files), set(org_files2))

    def test_encrypt_hide_decrypt(self):
        """
        encrypt_hide_decrypt
        """
        self.do_wait_for_tasks = False
        encrypt = 1
        decrypt = 1
        self.reset_cb_dir()
        self.unzip_testfiles_synced()
        p = os.path.join(os.path.join(os.getcwd(), "testdata"), "test")
        org_files = get_files_dir(p, ignore_hidden=True)
        org_files = [x for x in org_files if "memory.pickle.json" not in x]

        #decrypt_and_build_filetree, hide_config
        if encrypt:
            self.delete_hidden_configs()
            self.do_wait_for_tasks = False
            self.cboptions.remove = True
            salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
            datadir = get_data_dir(self.cboptions)
            self.cbmemory.save(datadir)
            hide_config(self.cboptions, salt, secret)
            self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 0)

        if decrypt:
            os.system("rm -Rf testdata/test")
            if not encrypt:
                os.system("cd testdata; unzip -o hidden_config.zip > /dev/null")

            options = self.cboptions
            options.encrypt = False
            options.decrypt = True
            options.remove = False
            secret = restore_hidden_config(options)
            datadir = get_data_dir(self.cboptions)
            memory = Memory()
            memory.load(datadir)
            decrypt_and_build_filetree(memory, options, secret)

        org_files2 = get_files_dir(p, ignore_hidden=True)
        self.assertEqual(set(org_files), set(org_files2))

    def test_index_clear(self):
        self.do_wait_for_tasks = False
        self.unzip_testfiles_clean()
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.cboptions.clear = True
        self.cboptions.encrypt = False
        self.cboptions.clear = "1"
        reset_cryptobox_local(self.cboptions)
        dd = get_data_dir(self.cboptions)
        self.assertEquals(os.path.exists(dd), False)

    def directories_synced(self):
        """
        directories_synced
        """
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        localindex = make_local_index(self.cboptions)
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        dir_make_server, dir_del_local = dirs_on_local(self.cbmemory, self.cboptions, localindex, dirname_hashes_server, serverindex)
        return (len(dir_make_server) == 0) and (len(dir_del_local) == 0)

    def test_compare_server_tree_with_local_tree_method_folders(self):
        """
        test_compare_server_tree_with_local_tree_method_folders
        """
        self.reset_cb_dir()
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.directories_synced())

        # delete on server
        dir_del_server = tuple(['/map1'])
        self.cbmemory = instruct_server_to_delete_folders(self.cbmemory, self.cboptions, serverindex, dir_del_server)

        # sync dirs again
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.directories_synced())

        # delete local
        os.system("rm -Rf testdata/test/map2")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.directories_synced())

    def test_sync_clean_tree(self):
        """
        test_sync_clean_tree
        """
        self.do_wait_for_tasks = False
        self.reset_cb_dir()
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()

        # build directories locally and on server
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.directories_synced())
        self.assertTrue(self.files_synced())

    def files_synced(self):
        """
        files_synced
        """
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, file_rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()

        for l in [file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, file_rename_server, folder_rename_server, rename_local_folders]:
            if len(l) != 0:
                return False
        return True

    def test_sync_synced_tree_mutations_local(self):
        """
        test_sync_synced_tree_mutations_local
        """
        self.reset_cb_db_synced()
        self.unzip_testfiles_synced()
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("date > testdata/test/all_types/date.txt")
        os.system("mkdir testdata/test/map3")
        os.system("rm -Rf testdata/test/all_types/document.pdf")
        os.system("rm -Rf testdata/test/smalltest")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(file_del_server), 1)
        self.assertEqual(len(file_downloads), 0)
        self.assertEqual(len(file_uploads), 1)
        self.assertEqual(len(dir_del_server), 1)
        self.assertEqual(len(dir_make_local), 0)
        self.assertEqual(len(dir_make_server), 1)
        self.assertEqual(len(dir_del_local), 0)
        self.assertEqual(len(file_del_local), 0)

    def test_sync_method_clean_tree(self):
        """
        test_sync_method_clean_tree
        """
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.files_synced())

    def get_sync_changes(self):
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory, self.cboptions, fdels, fds, fups, dirdels, dirmakelo, dirmakes, ddelloc, fdelloc, spn, uc, rens, renfolderserver, rename_local_folders = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)
        return ddelloc, dirdels, dirmakelo, dirmakes, fdelloc, fdels, fds, fups, rens, renfolderserver, rename_local_folders

    def all_changes_asserted_zero(self):
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(file_del_server), 0)
        self.assertEqual(len(file_del_local), 0)
        self.assertEqual(len(file_downloads), 0)
        self.assertEqual(len(file_uploads), 0)
        self.assertEqual(len(dir_del_server), 0)
        self.assertEqual(len(dir_make_local), 0)
        self.assertEqual(len(dir_make_server), 0)
        self.assertEqual(len(dir_del_local), 0)
        return True

    @staticmethod
    def test_memory_lock():
        """
        test_memory_lock
        """
        memory = Memory()
        memory.lock()
        memory.unlock()

    def test_sync_new_file(self):
        """
        test_sync_new_file
        """
        self.reset_cb_db_synced()
        self.unzip_testfiles_synced()
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        os.system("ls > testdata/test/all_types/listing.txt")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.all_changes_asserted_zero()

    def test_sync_changed_file(self):
        """
        test_sync_changed_file
        """
        self.reset_cb_db_clean()
        ensure_directory(self.cboptions.dir)
        os.system("echo 'hello' > testdata/test/hello.txt")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("echo 'hello world' > testdata/test/hello.txt")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(file_uploads), 1)

    def test_find_short_ids(self):
        """
        test_find_short_ids
        """
        self.reset_cb_db_synced()
        self.unzip_testfiles_synced()
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        map1 = '/smalltest'
        map1_short_id = path_to_server_shortid(self.cboptions, serverindex, '/smalltest')
        map1_2, self.cbmemory = short_id_to_server_path(self.cbmemory, serverindex, map1_short_id)
        self.assertEqual(map1, map1_2)

    def test_mutation_history(self):
        """
        test_sync_delete_local_folder
        """
        self.reset_cb_dir()
        self.reset_cb_db_clean()
        ensure_directory(self.cboptions.dir)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.mkdir("testdata/test/foo")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("rm -Rf testdata/test/foo")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertEqual(self.directories_synced(), True)
        self.all_changes_asserted_zero()
        os.mkdir("testdata/test/foo")
        self.assertEqual(os.path.exists("testdata/test/foo"), True)
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(dir_make_server), 1)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.mkdir("testdata/test/foo2")
        os.system("ls > testdata/test/foo2/test.txt")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("rm -Rf testdata/test/foo2/test.txt")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(file_del_server), 1)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("ls > testdata/test/foo2/test.txt")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(file_uploads), 1)

    def test_mutation_history_file(self):
        """
        test_sync_delete_local_folder
        """
        self.reset_cb_dir()
        self.reset_cb_db_clean()
        ensure_directory(self.cboptions.dir)
        os.mkdir("testdata/test/foo")
        os.system("ls > testdata/test/foo/test.txt")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("rm -Rf testdata/test/foo/test.txt")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(file_del_server), 1)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("ls > testdata/test/foo/test.txt")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(file_uploads), 1)

    def test_sync_delete_local_folder(self):
        """
        test_sync_delete_local_folder
        """
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        os.mkdir("testdata/test/all_types/foo")
        os.mkdir("testdata/test/all_types/foo2")
        os.mkdir("testdata/test/all_types/foo2/bar")
        os.system("ls > testdata/test/all_types/foo/test.txt")
        os.system("ls > testdata/test/all_types/foo2/test2.txt")
        os.system("ls > testdata/test/all_types/foo2/bar/test3.txt")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("rm -Rf testdata/test/all_types")
        self.assertTrue(os.path.exists("testdata/test"))
        self.assertFalse(os.path.exists("testdata/test/all_types"))
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        cbmemory, cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_path_nodes, unique_content, rename_paths, dir_renames, dir_renames_local = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)
        self.assertEqual(len(dir_del_server), 4)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.unzip_testfiles_clean()
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(file_uploads), 3)

    def test_sync_delete_server_folder(self):
        """
        test_sync_delete_server_folder
        """
        self.reset_cb_db_clean()

        #self.unzip_testfiles_clean()
        os.makedirs("testdata/test/foo")
        os.makedirs("testdata/test/bar")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        dir_del_server = tuple(['/foo'])
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory = instruct_server_to_delete_folders(self.cbmemory, self.cboptions, serverindex, dir_del_server)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        cbmemory, cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_path_nodes, unique_content, rename_paths, dir_renames, dir_local_renames = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)
        self.assertEqual(len(dir_del_local), 1)

    def test_sync_method_clean_tree_remove_local_folder(self):
        """
        test_sync_method_clean_tree_remove_local_folder
        """
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        os.system("rm -Rf testdata/test/")
        with self.assertRaisesRegexp(NoSyncDirFound, "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/test"):
            localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)

    def test_set_dir_to_non_empty_syncfolder(self):
        """
        test_set_dir_to_non_empty_syncfolder
        """
        self.do_wait_for_tasks = False
        self.reset_cb_dir()
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        os.system("rm -Rf testdata/test/.cryptobox")
        os.system("mkdir testdata/test/legedir")

        #noinspection PyUnusedLocal
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(dir_make_server), 1)
        self.assertEqual(len(file_uploads), 5)

    def test_subdirs(self):
        """
        test_subdirs
        """
        self.do_wait_for_tasks = False
        self.reset_cb_dir()
        self.reset_cb_db_clean()
        os.system("mkdir -p testdata/test/foo/bar/hello")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("rmdir testdata/test/foo/bar/hello")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(dir_del_server), 1)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("rm -Rf testdata/test/foo/bar")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(dir_del_server), 1)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)

    def test_remove_directory(self):
        """
        test_remove_directory
        """
        self.do_wait_for_tasks = False
        self.reset_cb_dir()
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("rm -Rf testdata/test/smalltest")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(dir_del_server), 1)
        self.assertEqual(len(file_del_server), 0)

    def test_hash(self):
        """
        test_hash
        """
        fpath = "testdata/1MB.zip"
        localindex = {"filestats": {}}
        fd, localindex = make_cryptogit_hash(fpath, self.cboptions.dir, localindex)
        self.assertEqual(fd["filehash"], '0c1d7e2e3283b3ee3f319533ea6aa6372982922f')

    def test_rename_file_local(self):
        """
        test_rename_local
        """
        self.do_wait_for_tasks = False
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        os.system("rm testdata/test/all_types/*")
        os.system("rm -Rf testdata/test/smalltest/test.java")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.files_synced())
        os.system("mv testdata/test/smalltest/test.cpp testdata/test/all_types/test2.cpp")
        os.system("ls > testdata/test/smalltest/test3.txt")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(file_uploads), 1)
        self.assertEqual(len(rename_server), 1)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.files_synced())

    def test_hash_rename(self):
        """
        test_hash_rename
        """
        self.unzip_testfiles_clean()
        fpath = "testdata/test/smalltest/test.cpp"
        file_dict = read_file_to_fdict(fpath)
        filehash = make_sha1_hash_file("blob " + str(file_dict["st_size"]) + "\0", fpath)
        os.system("mv testdata/test/smalltest/test.cpp testdata/test/smalltest/test2.cpp")
        fpath = "testdata/test/smalltest/test2.cpp"
        file_dict = read_file_to_fdict(fpath)
        filehash2 = make_sha1_hash_file("blob " + str(file_dict["st_size"]) + "\0", fpath)
        self.assertEqual(filehash, filehash2)

    def test_rename_server(self):
        """
        test_rename_server
        """
        self.do_wait_for_tasks = False
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        os.system("rm -Rf testdata/test/all_types")
        os.system("rm -Rf testdata/test/smalltest/test.java")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.assertTrue(self.files_synced())
        self.cbmemory = authorize_user(self.cbmemory, self.cboptions, force=True)
        instruct_server_to_rename_path(self.cbmemory, self.cboptions, "/smalltest/test.cpp", "/smalltest/test2.cpp")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.files_synced())

    def test_rename_folder_local(self):
        """
        test_rename_folder_local
        """
        self.do_wait_for_tasks = False
        self.reset_cb_db_synced()
        self.unzip_testfiles_synced()
        os.system("cp -r testdata/test/all_types testdata/test/smalltest")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("mv testdata/test/smalltest testdata/test/smalltest2")
        os.system("mv testdata/test/all_types/bmptest.png testdata/test/all_types/bmptest2.png")

        #noinspection PyUnusedLocal
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, file_rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(dir_del_server), 0)
        self.assertEqual(len(file_uploads), 0)
        self.assertEqual(len(folder_rename_server), 1)
        self.assertEqual(len(file_rename_server), 1)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.files_synced())

    def test_rename_on_server(self):
        """
        test_rename_on_server
        """
        self.do_wait_for_tasks = True
        self.reset_cb_db_synced()
        self.unzip_testfiles_synced()
        self.cbmemory = authorize_user(self.cbmemory, self.cboptions, force=True)
        instruct_server_to_rename_path(self.cbmemory, self.cboptions, "/all_types", "/smalltest/all_types2")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads, file_rename_server, folder_rename_server, rename_local_folders = self.get_sync_changes()
        self.assertEqual(len(rename_local_folders), 1)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.files_synced())

    def test_symlink(self):
        """
        test_symlink
        """
        self.do_wait_for_tasks = True
        self.reset_cb_db_synced()
        self.unzip_testfiles_synced()
        os.system("ln -s testdata/test/all_types testdata/test/smalltest/")
        os.system("ln -s testdata/test/smalltest/test.java testdata/test/all_types/")
        index = make_local_index(self.cboptions)
        self.assertEqual(len(index["messages"]), 2)
        self.assertEqual("symbolic link" in index["messages"][0], True)

    def test_super_large_file(self):
        """
        test_super_large_file
        """
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        self.make_testfile("3000MB.txt", 3000)
        os.system("rm testdata/test/all_types/*")
        os.system("rm -Rf testdata/test/smalltest")
        os.system("cp testdata/3000MB.txt testdata/test/all_types/")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.files_synced())
        datadir = get_data_dir(self.cboptions)
        self.cbmemory.save(datadir)
        p = os.path.join(os.path.join(os.getcwd(), "testdata"), "test")
        org_files = get_files_dir(p, ignore_hidden=True)
        org_files = [x for x in org_files if "memory.pickle.json" not in x]
        org_files1 = [make_sha1_hash_file(fpath=x) for x in org_files]
        self.delete_hidden_configs()
        self.do_wait_for_tasks = False
        self.cboptions.remove = True
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        datadir = get_data_dir(self.cboptions)
        self.cbmemory.save(datadir)
        hide_config(self.cboptions, salt, secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 0)
        options = self.cboptions
        options.encrypt = False
        options.decrypt = True
        options.remove = False
        secret = restore_hidden_config(options)
        datadir = get_data_dir(self.cboptions)
        memory = Memory()
        memory.load(datadir)
        decrypt_and_build_filetree(memory, options, secret)
        org_files2 = get_files_dir(p, ignore_hidden=True)
        org_files3 = [make_sha1_hash_file(fpath=x) for x in org_files2]
        self.assertEqual(set(org_files1), set(org_files3))
        os.system("rm -Rf testdata/test")
        os.system("rm testdata/3000MB.txt")

    def test_client_mandate(self):
        """
        test_client_mandate
        """
        self.reset_cb_db_clean()
        mandate_key = "test_from_app"

        with self.assertRaisesRegexp(NotAuthorized, "new_mandate"):
            new_mandate(self.cbmemory, self.cboptions, mandate_key)

        self.cbmemory = authorize_user(self.cbmemory, self.cboptions, force=True)
        mandate1 = new_mandate(self.cbmemory, self.cboptions, mandate_key)
        with self.assertRaisesRegexp(NotAuthorized, "mandate_denied"):
            new_mandate(self.cbmemory, self.cboptions, mandate_key)
        self.assertIsNotNone(mandate1)

        # try to login with a mandate
        # noinspection PyUnusedLocal
        mandate_name, mandate_private_key = get_mandate(self.cbmemory, self.cboptions, mandate1)
        pass


if __name__ == '__main__':
    unittest.main()

# coding=utf-8
"""
unit test for app commands
"""
__author__ = 'rabshakeh'
import os
import cPickle
import unittest
import random
from subprocess import Popen, PIPE
import sys
from cba_main import cryptobox_command
from cba_utils import Dict2Obj, smp_all_cpu_apply, Memory
from cba_index import make_local_index, index_and_encrypt, check_and_clean_dir, decrypt_and_build_filetree, hide_config
from cba_blobs import get_blob_dir, get_data_dir
from cba_network import authorize_user, authorized
from cba_sync import get_server_index, parse_serverindex, instruct_server_to_delete_folders, dirs_on_local, path_to_server_shortid, wait_for_tasks, sync_server, get_sync_changes, short_id_to_server_path, NoSyncDirFound
from cba_file import ensure_directory
from cba_crypto import make_checksum, encrypt_file_smp, decrypt_file_smp
sys.path.append("/Users/rabshakeh/workspace/cryptobox")

#noinspection PyUnresolvedReferences
from couchdb_api import MemcachedServer


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
    print "tests.py:38", p


def count_files_dir(fpath):
    """
    count_files_dir
    @type fpath: str, unicode
    """
    s = set()

    for path, dirs, files in os.walk(fpath):
        for f in files:
            s.add(f)

    return len(s)

#noinspection PyPep8Naming


class CryptoboxAppTest(unittest.TestCase):
    """
    CryptoboTestCase
    """

    def setUp(self):
        """
        setUp
        """

        #SERVER = "https://www.cryptobox.nl/"
        #os.system("cd testdata; unzip -o testmap.zip > /dev/null")
        #server = "https://www.cryptobox.nl/"
        mc = MemcachedServer(["127.0.0.1:11211"], "mutex")
        mc.flush_all()
        server = "http://127.0.01:8000/"
        self.options_d = {"dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/testmap", "encrypt": True, "remove": False, "username": "rabshakeh", "password": "kjhfsd98", "cryptobox": "test", "clear": False, "sync": False, "server": server, "numdownloadthreads": 12}
        self.cboptions = Dict2Obj(self.options_d)
        self.cbmemory = Memory()
        self.cbmemory.set("cryptobox_folder", self.cboptions.dir)
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))
        self.do_wait_for_tasks = True
        testfile_sizes = ["1MB.zip", "200MB.zip", "100MB.zip", "20MB.zip", "5MB.zip", "1GB.zip", "50MB.zip"]

        for tfn in testfile_sizes:
            if not os.path.exists(os.path.join("testdata", tfn)):
                os.system("cd testdata; nohup wget http://download.thinkbroadband.com/" + tfn)

                #sys.stdout = open('stdout.txt', 'w')
                #sys.stderr = open('stderr.txt', 'w')

                #noinspection PyPep8Naming

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

    @staticmethod
    def unzip_testfiles_clean():
        """
        unzip_testfiles_clean
        """
        os.system("cd testdata; cp testmap_clean.zip testmap.zip")
        os.system("cd testdata; unzip -o testmap.zip > /dev/null")
        os.system("rm testdata/testmap.zip")

    @staticmethod
    def unzip_testfiles_synced():
        """
        unzip_testfiles_synced
        """
        os.system("cd testdata; cp testmap_synced.zip testmap.zip")
        os.system("cd testdata; unzip -o testmap.zip > /dev/null")
        os.system("rm testdata/testmap.zip")

    def reset_cb_db(self):
        """
        reset_cb_db_clean
        """
        os.system("rm -Rf testdata/testmap")
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))
        os.system("wget -q -O '/dev/null' --retry-connrefused http://127.0.0.1:8000/")
        os.system("cp testdata/test.dump /Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl")
        self.pipe = Popen("nohup python server/manage.py load -c test", shell=True, stderr=PIPE, stdout=PIPE, cwd="/Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl")
        self.pipe.wait()

    def reset_cb_db_clean(self):
        """
        reset_cb_db_clean
        """
        os.system("cp testdata/test_clean.dump testdata/test.dump")
        self.reset_cb_db()
        os.system("rm testdata/test.dump")

    def reset_cb_db_synced(self):
        """
        reset_cb_db_synced
        """
        os.system("cp testdata/test_synced.dump testdata/test.dump")
        os.system("cd testdata; unzip -o crypto_docs.zip > /dev/null; cd crypto_docs; cp * /Users/rabshakeh/workspace/cloudfiles/crypto_docs; cd ..; rm -Rf crypto_docs")
        self.reset_cb_db()

    def complete_reset(self):
        """
        complete_reset
        """
        os.system("rm -Rf testdata/testmap")
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))

    def test_reset_all(self):
        """
        test_reset_all
        """
        self.do_wait_for_tasks = False
        self.complete_reset()
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()

    def test_smp_all_cpu_apply(self):
        self.do_wait_for_tasks = False

        items = [(x, x + random.randint(1, 10)) for x in range(0, 10)]
        res_items = [x[0] + x[1] for x in items]
        res_items2 = smp_all_cpu_apply(add, items)
        self.assertEquals(res_items, res_items2)

    def test_encrypt_file_smp(self):
        """
        test_encrypt_file
        """
        self.do_wait_for_tasks = False
        fname = "testdata/1MB.zip"
        secret = '\xeb>M\x04\xc22\x96!\xce\xed\xbb.\xe1u\xc7\xe4\x07h<.\x87\xc9H\x89\x8aj\xb4\xb2b5}\x95'
        enc_file_struct = encrypt_file_smp(secret, fname)
        dec_file = decrypt_file_smp(secret, enc_file_struct)
        dec_file.seek(0)
        dec_data = dec_file.read()
        org_data = (open(fname).read())
        self.assertEqual(make_checksum(dec_data), make_checksum(org_data))
        fname = "testdata/20MB.zip"
        enc_file_struct = encrypt_file_smp(secret, fname)
        dec_file = decrypt_file_smp(secret, enc_file_struct)
        dec_file.seek(0)
        dec_data = dec_file.read()
        org_data = (open(fname).read())
        self.assertEqual(make_checksum(dec_data), make_checksum(org_data))

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
        os.system("rm -Rf testdata/testmap")
        self.unzip_testfiles_clean()
        self.cboptions.sync = False
        localindex_check = cPickle.load(open("testdata/localindex_test.pickle"))
        localindex = make_local_index(self.cboptions)

        #pickle.dump(localindex, open("testdata/localindex_test.pickle", "w"))
        self.assertTrue(localindex_check == localindex)

    def test_index_and_encrypt(self):
        """
        test_index_and_encrypt
        """
        self.complete_reset()
        self.unzip_testfiles_synced()
        self.do_wait_for_tasks = False
        localindex = make_local_index(self.cboptions)
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 8)

        # add a new file
        open(os.path.join(self.cboptions.dir, "hello world.txt"), "w").write("hello world 123 Dit is random data")
        localindex = make_local_index(self.cboptions)
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 9)

        # same content, blob count should not rise
        open(os.path.join(self.cboptions.dir, "hello world2.txt"), "w").write("hello world 123 Dit is random data")
        localindex = make_local_index(self.cboptions)
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 9)

    def itest_index_encrypt_decrypt_clean(self):
        """
        test_index_encrypt_decrypt_clean
        """
        self.do_wait_for_tasks = False
        self.complete_reset()
        self.unzip_testfiles_clean()
        os.system("rm -Rf " + get_blob_dir(self.cboptions))
        localindex1 = make_local_index(self.cboptions)
        self.cboptions.remove = True
        salt, secret, self.cbmemory, localindex1 = index_and_encrypt(self.cbmemory, self.cboptions)
        datadir = get_data_dir(self.cboptions)
        self.cbmemory.save(datadir)
        hide_config(self.cboptions, salt, secret)
        self.assertEqual(count_files_dir(self.cboptions.dir), 7)
        self.cbmemory = decrypt_and_build_filetree(self.cbmemory, self.cboptions)
        os.system("rm -Rf " + get_blob_dir(self.cboptions))
        localindex2 = make_local_index(self.cboptions)
        salt, secret, self.cbmemory, localindex2 = index_and_encrypt(self.cbmemory, self.cboptions)
        self.max_diff = None

        def remove_atime(index):
            """
            remove_atime
            @type index: dict
            """

            def del_atime(ix, k):
                """
                del_atime
                @type ix: dict
                @type k: dict
                """
                del ix[k]["st_atime"]
                del ix[k]["st_ctime"]
                return ix

            filestats = [del_atime(index["filestats"], x) for x in index["filestats"]]
            index["filestats"] = filestats[0]
            return index

        localindex1 = remove_atime(localindex1)
        localindex2 = remove_atime(localindex2)
        self.assertEquals(localindex1["filestats"], localindex2["filestats"])

    def test_index_clear(self):
        self.do_wait_for_tasks = False
        self.unzip_testfiles_clean()
        localindex = make_local_index(self.cboptions)
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.cboptions.clear = True
        self.cboptions.encrypt = False
        self.cboptions.clear = "1"
        check_and_clean_dir(self.cboptions)
        dd = get_data_dir(self.cboptions)
        self.assertEquals(os.path.exists(dd), False)

    def directories_synced(self):
        """
        directories_synced
        """
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        localindex = make_local_index(self.cboptions)
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        dir_make_server, dir_del_local = dirs_on_local(self.cboptions, localindex, dirname_hashes_server, serverindex)
        return (len(dir_make_server) == 0) and (len(dir_del_local) == 0)

    def test_connection(self):
        """
        test_connection
        """
        self.cbmemory = authorized(self.cbmemory, self.cboptions)
        self.assertFalse(self.cbmemory.get("authorized"))
        self.cbmemory = authorize_user(self.cbmemory, self.cboptions)
        self.assertTrue(self.cbmemory.get("authorized"))
        self.cbmemory = authorized(self.cbmemory, self.cboptions)
        self.assertTrue(self.cbmemory.get("authorized"))

    def test_compare_server_tree_with_local_tree_method_folders(self):
        """
        test_compare_server_tree_with_local_tree_method_folders
        """
        self.complete_reset()
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.directories_synced())

        # delete on server
        dir_del_server = ['/map1']
        self.cbmemory = instruct_server_to_delete_folders(self.cbmemory, self.cboptions, serverindex, dir_del_server)

        # sync dirs again
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.directories_synced())

        # delete local
        os.system("rm -Rf testdata/testmap/map2")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.directories_synced())

    def test_sync_clean_tree(self):
        """
        test_sync_clean_tree
        """
        self.complete_reset()
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
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads = self.get_sync_changes()

        for l in [file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local]:
            if len(l) != 0:
                return False
        return True

    def test_sync_synced_tree_mutations_local(self):
        """
        test_sync_synced_tree_mutations_local
        """
        self.reset_cb_db_synced()
        self.unzip_testfiles_clean()
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("date > testdata/testmap/all_types/date.txt")
        os.system("mkdir testdata/testmap/map3")
        os.system("rm -Rf testdata/testmap/all_types/document.pdf")
        os.system("rm -Rf testdata/testmap/smalltest")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads = self.get_sync_changes()
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
        os.system("ls > testdata/testmap/all_types/test.txt")
        self.assertFalse(self.files_synced())

    def get_sync_changes(self):
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)
        return dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads

    def all_changes_asserted_zero(self):
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads = self.get_sync_changes()
        self.assertEqual(len(file_del_server), 0)
        self.assertEqual(len(file_del_local), 0)
        self.assertEqual(len(file_downloads), 0)
        self.assertEqual(len(file_uploads), 0)
        self.assertEqual(len(dir_del_server), 0)
        self.assertEqual(len(dir_make_local), 0)
        self.assertEqual(len(dir_make_server), 0)
        self.assertEqual(len(dir_del_local), 0)
        return True

    def test_memory_lock(self):
        """
        test_memory_lock
        """
        memory = Memory()
        memory.lock()
        memory.unlock()

    def test_sync_new_file(self):
        """
        remove a folder on server and add same folder locally
        """
        self.reset_cb_db_synced()
        self.unzip_testfiles_synced()
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        os.system("ls > testdata/testmap/all_types/listing.txt")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.all_changes_asserted_zero()

    def test_find_short_ids(self):
        """
        test_find_short_ids
        """
        self.reset_cb_db_synced()
        self.unzip_testfiles_synced()
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        map1 = '/smalltest'
        map1_short_id, self.cbmemory = path_to_server_shortid(self.cbmemory, self.cboptions, serverindex, '/smalltest')
        map1_2, self.cbmemory = short_id_to_server_path(self.cbmemory, serverindex, map1_short_id)
        self.assertEqual(map1, map1_2)

    def test_mutation_history(self):
        """
        test_sync_delete_local_folder
        """
        self.complete_reset()
        self.reset_cb_db_clean()
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.mkdir("testdata/testmap/foo")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("rm -Rf testdata/testmap/foo")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertEqual(self.directories_synced(), True)
        self.all_changes_asserted_zero()
        os.mkdir("testdata/testmap/foo")
        self.assertEqual(os.path.exists("testdata/testmap/foo"), True)
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads = self.get_sync_changes()
        self.assertEqual(len(dir_make_server), 1)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.mkdir("testdata/testmap/foo2")
        os.system("ls > testdata/testmap/foo2/test.txt")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("rm -Rf testdata/testmap/foo2/test.txt")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads = self.get_sync_changes()
        self.assertEqual(len(file_del_server), 1)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("ls > testdata/testmap/foo2/test.txt")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads = self.get_sync_changes()
        self.assertEqual(len(file_uploads), 1)

    def test_sync_delete_local_folder(self):
        """
        test_sync_delete_local_folder
        """
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        os.mkdir("testdata/testmap/all_types/foo")
        os.mkdir("testdata/testmap/all_types/foo2")
        os.mkdir("testdata/testmap/all_types/foo2/bar")
        os.system("ls > testdata/testmap/all_types/foo/test.txt")
        os.system("ls > testdata/testmap/all_types/foo2/test2.txt")
        os.system("ls > testdata/testmap/all_types/foo2/bar/test3.txt")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("rm -Rf testdata/testmap/all_types")
        self.assertTrue(os.path.exists("testdata/testmap"))
        self.assertFalse(os.path.exists("testdata/testmap/all_types"))
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        cbmemory, cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)
        self.assertEqual(len(dir_del_server), 4)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.unzip_testfiles_clean()
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads = self.get_sync_changes()
        self.assertEqual(len(file_uploads), 3)

    def test_sync_method_clean_tree_remove_local_folder(self):
        """
        test_sync_method_clean_tree_remove_local_folder
        """
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        os.system("rm -Rf testdata/testmap/")
        with self.assertRaisesRegexp(NoSyncDirFound, "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/testmap"):
            localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)

    def test_set_dir_to_non_empty_syncfolder(self):
        """
        test_set_dir_to_non_empty_syncfolder
        """
        self.complete_reset()
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        os.system("rm -Rf testdata/testmap/.cryptobox")
        os.system("mkdir testdata/testmap/legedir")

        #noinspection PyUnusedLocal
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads = self.get_sync_changes()
        self.assertEqual(len(dir_make_server), 1)
        self.assertEqual(len(file_uploads), 5)


if __name__ == '__main__':
    unittest.main()

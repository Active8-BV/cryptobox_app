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
from cba_main import cryptobox_command
from cba_utils import Dict2Obj, smp_all_cpu_apply, Memory
from cba_index import make_local_index, index_and_encrypt, check_and_clean_dir, decrypt_and_build_filetree, hide_config
from cba_blobs import get_blob_dir, get_data_dir
from cba_network import authorize_user, authorized
from cba_sync import get_server_index, parse_serverindex, instruct_server_to_delete_folders, dirs_on_local, path_to_server_shortid, wait_for_tasks, sync_server, get_sync_changes, short_id_to_server_path
from cba_file import ensure_directory
from cba_crypto import make_checksum, encrypt_file_smp, decrypt_file_smp


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
    print "tests.py:33", p


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
        os.system("echo 'flush_all' | nc localhost 11211")
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
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions, localindex)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 8)

        # add a new file
        open(os.path.join(self.cboptions.dir, "hello world.txt"), "w").write("hello world 123 Dit is random data")
        localindex = make_local_index(self.cboptions)
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions, localindex)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 9)

        # same content, blob count should not rise
        open(os.path.join(self.cboptions.dir, "hello world2.txt"), "w").write("hello world 123 Dit is random data")
        localindex = make_local_index(self.cboptions)
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions, localindex)
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
        salt, secret, self.cbmemory, localindex1 = index_and_encrypt(self.cbmemory, self.cboptions, localindex1)
        datadir = get_data_dir(self.cboptions)
        self.cbmemory.save(datadir)
        hide_config(self.cboptions, salt, secret)
        self.assertEqual(count_files_dir(self.cboptions.dir), 7)
        self.cbmemory = decrypt_and_build_filetree(self.cbmemory, self.cboptions)
        os.system("rm -Rf " + get_blob_dir(self.cboptions))
        localindex2 = make_local_index(self.cboptions)
        salt, secret, self.cbmemory, localindex2 = index_and_encrypt(self.cbmemory, self.cboptions, localindex2)
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
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions, localindex)
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
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        # build directories locally and on server
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
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

    def test_sync_delete_local_folder_diff(self):
        """
        test_sync_delete_local_folder_diff
        """
        import base64
        options_d = {"dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/testmap", "encrypt": True, "remove": False, "username": "rabshakeh", "password": "kjhfsd98", "cryptobox": "test", "clear": False, "sync": False, "server": "http://127.0.0.1:8000", "numdownloadthreads": 12}
        cboptions = Dict2Obj(options_d)

        memory = cPickle.loads(base64.decodestring(
            "Y2NvcHlfcmVnCl9yZWNvbnN0cnVjdG9yCnAxCihjY2JhX3V0aWxzCk1lbW9yeQpwMgpjX19idWlsdGluX18Kb2JqZWN0CnAzCk50UnA0CihkcDUKUydkYXRhJwpwNgooZHA3ClMnbG9jYWxwYXRoX2hpc3RvcnknCnA4CmNfX2J1aWx0aW5fXwpzZXQKcDkKKChscDEwCihTJy9hbGxfdHlwZXMvZG9jdW1lbnQucGRmJwpTJ2U3YmRlOTU1MGQ5NjRmMDg4NTVkYjZjYTUzMDliNGFhMTQ4YzJiNmUnCnRwMTEKYShTJy9hbGxfdHlwZXMvYm1wdGVzdC5wbmcnClMnNGJkZGU5YWEwZTc0Zjg0ZWE2MGZjODU1MzQ1Yjg0ODA2ODU3M2JhNCcKdHAxMgphKFMnL2FsbF90eXBlcy9mb28vdGVzdC50eHQnClMnYTQzNjMwNTdhN2I1NDdhMWU3MmI4ZDY5Yzg2MzY1ZjgwYTczZDIzNicKdHAxMwphKFMnL3NtYWxsdGVzdC90ZXN0LmNwcCcKUydiYWYyODljNGE1MTE5ZGM1NzYzNjNhNmFiOWM5NTE1YTkwNmQ1ODU2Jwp0cDE0CmEoUycvYWxsX3R5cGVzL2ZvbzIvYmFyL3Rlc3QzLnR4dCcKUydkOTc2YjRjMGRjZmE4NDYxOGI5NWJhMDQ1OWY3NGE0ZDQyNDE0MTBjJwp0cDE1CmEoUycvc21hbGx0ZXN0L3Rlc3QuamF2YScKUyc1YTVhYzc3MDNmZmViYjE4YjcxMDlkNTg5YTc1ZmExYWQzNTljNGFjJwp0cDE2CmEoUycvYWxsX3R5cGVzL2ZvbzIvdGVzdDIudHh0JwpTJzJlM2Q4MGU2ZTJjMDNhZDA0OGMxMDk0ODhmZjUxN2FhZDY5NDIwNWMnCnRwMTcKYShTJy9hbGxfdHlwZXMvd29yZC5kb2N4JwpTJzdkNzJkMzk2OTMzOWJlZWRkNDg4YzMzNGZlYjQ4ZTA4M2E1MDY2ZGInCnRwMTgKYXRScDE5CnNTJ2NyeXB0b2JveF9mb2xkZXInCnAyMApTJy9Vc2Vycy9yYWJzaGFrZWgvd29ya3NwYWNlL2NyeXB0b2JveC9jcnlwdG9ib3hfYXBwL3NvdXJjZS9jb21tYW5kcy90ZXN0ZGF0YS90ZXN0bWFwJwpwMjEKc1Mnc2VydmVyaW5kZXgnCnAyMgooZHAyMwpWZG9jbGlzdApwMjQKKGxwMjUKKGRwMjYKVmNvbnRlbnRfaGFzaF9sYXRlc3RfdGltZXN0YW1wCnAyNwpOc1Zkb2MKcDI4CihkcDI5ClZtX3BhcmVudApwMzAKVgpzVm1fZGF0YV9pZApwMzEKVgpzVm1fcGF0aApwMzIKVi8Kc1ZtX2RhdGVfaHVtYW4KcDMzClYwOC8xMC8xMyAxMzo0NgpwMzQKc1ZtX2NyZWF0aW9uX3RpbWUKcDM1CkYxMzgxMjMyNzY1Ljk4CnNWbV9zbHVnCnAzNgpWZG9jdW1lbnRlbgpwMzcKc1Z0aW1lc3RhbXAKcDM4CkYxMzgxMjMyNzY1Ljk4CnNWbV9kYXRlX3RpbWUKcDM5CkYxMzgxMjMyNzY1OTgwCnNWbV9zaG9ydF9pZApwNDAKVnp6ZGgKcDQxCnNWbV9kYXRlCnA0MgpGMTM4MTIzMjc2NS45OApzVm1fc2l6ZQpwNDMKSTEzCnNWbV9zbHVncGF0aApwNDQKVi8Kc1ZtX29yZGVyCnA0NQpJMApzVm1fbm9kZXR5cGUKcDQ2ClZmb2xkZXIKcDQ3CnNWbV9taW1lCnA0OApWZm9sZGVyCnA0OQpzVm1fbmFtZQpwNTAKVmRvY3VtZW50ZW4KcDUxCnNzVnJvb3RwYXJlbnQKcDUyCk5zVl9pZApwNTMKVnp6ZGgKcDU0CnNWcGFyZW50CnA1NQpOc2EoZHA1NgpnMjcKTnNnMjgKKGRwNTcKZzMwClZ6emRoCnA1OApzZzMxClYKc2czMgpWL3NtYWxsdGVzdApwNTkKc2czMwpWMDkvMTAvMTMgMDg6MjEKcDYwCnNnMzUKRjEzODEyOTk2ODEuMzE1MjM0OQpzZzM2ClZzbWFsbHRlc3QKcDYxCnNnMzgKRjEzODEyOTk2ODEuMzE1MTUKc2czOQpGMTM4MTI5OTY4MTMxNS4xNDk5CnNnNDAKVmRqanYKcDYyCnNnNDIKRjEzODEyOTk2ODEuMzE1MTUKc2c0MwpJMTMKc2c0NApWL3NtYWxsdGVzdApwNjMKc2c0NQpJMQpzZzQ2ClZmb2xkZXIKcDY0CnNnNDgKVmZvbGRlcgpwNjUKc2c1MApWc21hbGx0ZXN0CnA2Ngpzc2c1MgpWZGpqdgpwNjcKc2c1MwpWZGpqdgpwNjgKc2c1NQpWenpkaApwNjkKc2EoZHA3MApnMjcKKGxwNzEKVmM2NzMxZDhmNDZlMTg1M2Q0YjA2ZTZmYWYwNTVkZmQ0MDMzMmQzZjMKcDcyCmFGMTM4MTI5OTY4Mi42ODkxNjUxCmFzZzI4CihkcDczCmczMApWZGpqdgpwNzQKc2czMQpWY3J5cHRvX2RvY19jNDY4NjFlNTc5YTE0NzdjYTM3ZGI1MjY5NDhjZjk4YwpwNzUKc2czMgpWL3NtYWxsdGVzdC90ZXN0LmphdmEKcDc2CnNnMzMKVjA5LzEwLzEzIDA4OjIxCnA3NwpzZzM1CkYxMzgxMjk5NjgxLjMxNTc0ODkKc2czNgpWdGVzdGphdmEKcDc4CnNnMzgKRjEzODEyOTk2ODIuNjg5MTY1MQpzZzM5CkYxMzgxMjk5NjgxMzE1LjY3OTkKc2c0MApWa3NieApwNzkKc2c0MgpGMTM4MTI5OTY4MS4zMTU2OApzZzQzCkk5CnNnNDQKVi9zbWFsbHRlc3QvdGVzdGphdmEKcDgwCnNnNDUKSTAKc2c0NgpWZmlsZQpwODEKc2c0OApWdGV4dC94LWphdmEtc291cmNlCnA4MgpzZzUwClZ0ZXN0LmphdmEKcDgzCnNzZzUyClZkamp2CnA4NApzZzUzClZrc2J4CnA4NQpzZzU1ClZkamp2CnA4NgpzYShkcDg3CmcyNwoobHA4OApWMzBkNzRkMjU4NDQyYzdjNjU1MTJlYWZhYjQ3NDU2OGRkNzA2YzQzMApwODkKYUYxMzgxMjk5NjkxLjYyMzkzNjkKYXNnMjgKKGRwOTAKZzMwClZkamp2CnA5MQpzZzMxClZjcnlwdG9fZG9jXzZmYjVhZTU3ZDA1MjRjMzJiOTM4NTc0YmM5ZDI0YjFiCnA5MgpzZzMyClYvc21hbGx0ZXN0L3Rlc3QuY3BwCnA5MwpzZzMzClYwOS8xMC8xMyAwODoyMQpwOTQKc2czNQpGMTM4MTI5OTY5MC41NTM2NTQKc2czNgpWdGVzdGNwcApwOTUKc2czOApGMTM4MTI5OTY5MS42MjM5MzY5CnNnMzkKRjEzODEyOTk2OTA1NTMuNTY2OQpzZzQwClZzdG14CnA5NgpzZzQyCkYxMzgxMjk5NjkwLjU1MzU2NjkKc2c0MwpJNApzZzQ0ClYvc21hbGx0ZXN0L3Rlc3RjcHAKcDk3CnNnNDUKSTEKc2c0NgpWZmlsZQpwOTgKc2c0OApWdGV4dC94LWMKcDk5CnNnNTAKVnRlc3QuY3BwCnAxMDAKc3NnNTIKVmRqanYKcDEwMQpzZzUzClZzdG14CnAxMDIKc2c1NQpWZGpqdgpwMTAzCnNhc1MnZGlybGlzdCcKcDEwNAoobHAxMDUKVi9zbWFsbHRlc3QKcDEwNgphVi8KYXNWdHJlZV90aW1lc3RhbXAKcDEwNwpGMTM4MTI5OTY5NC41ODA5MTMxCnNzUydzZXNzaW9uJwpwMTA4CmcxCihjcmVxdWVzdHMuc2Vzc2lvbnMKU2Vzc2lvbgpwMTA5CmczCk50UnAxMTAKKGRwMTExClMnY29va2llcycKcDExMgpnMQooY3JlcXVlc3RzLmNvb2tpZXMKUmVxdWVzdHNDb29raWVKYXIKcDExMwpnMwpOdFJwMTE0CihkcDExNQpTJ19ub3cnCnAxMTYKSTEzODEyOTk3MDAKc1MnX3BvbGljeScKcDExNwooaWNvb2tpZWxpYgpEZWZhdWx0Q29va2llUG9saWN5CnAxMTgKKGRwMTE5ClMnc3RyaWN0X3JmYzI5NjVfdW52ZXJpZmlhYmxlJwpwMTIwCkkwMQpzUydzdHJpY3RfbnNfZG9tYWluJwpwMTIxCkkwCnNTJ19hbGxvd2VkX2RvbWFpbnMnCnAxMjIKTnNTJ3JmYzIxMDlfYXNfbmV0c2NhcGUnCnAxMjMKTnNTJ3JmYzI5NjUnCnAxMjQKSTAwCnNTJ3N0cmljdF9kb21haW4nCnAxMjUKSTAwCnNnMTE2CkkxMzgxMjk5NzAwCnNTJ3N0cmljdF9uc19zZXRfcGF0aCcKcDEyNgpJMDAKc1Mnc3RyaWN0X25zX3VudmVyaWZpYWJsZScKcDEyNwpJMDAKc1Mnc3RyaWN0X25zX3NldF9pbml0aWFsX2RvbGxhcicKcDEyOApJMDAKc1MnaGlkZV9jb29raWUyJwpwMTI5CkkwMApzUydfYmxvY2tlZF9kb21haW5zJwpwMTMwCih0c1MnbmV0c2NhcGUnCnAxMzEKSTAxCnNic1MnX2Nvb2tpZXMnCnAxMzIKKGRwMTMzClMnMTI3LjAuMDEnCnAxMzQKKGRwMTM1ClMnLycKKGRwMTM2ClMnY190b2tlbicKcDEzNwooaWNvb2tpZWxpYgpDb29raWUKcDEzOAooZHAxMzkKUydjb21tZW50JwpwMTQwCk5zUydkb21haW4nCnAxNDEKZzEzNApzUyduYW1lJwpwMTQyCmcxMzcKc1MnZG9tYWluX2luaXRpYWxfZG90JwpwMTQzCkkwMApzUydleHBpcmVzJwpwMTQ0Ck5zUyd2YWx1ZScKcDE0NQpTJyIuZUp4dFZUZlA3QW9SdlR3UWhaX2dOOXdTeVFKN25ZMUU0Ylc5VHV0c3IwTno1Wnh6dG9SRWlmalZmTy1La21uUGFPYUU0dnpybDM5T3ZfdUwtLXM0VjN1MFpqLWE3SnAtY2Y3engyX2ZfdnJiUEhsQjByNWJOdlBkc0tRUDRfRGZGVDc0aVFDcUpQRkRJVDBaUm1FWmsyZVdqQnN3S1BjenFtYWhhM2x4RjdUQ3VpNlNfUHVPOHVRQzJ3cmRpV1FQZGZuajNta05QRnIyanRSUWVJRmxWeVJ0WHBPSUVia1JYMkd6aU1MM2xOcVIzWldkelE3QnVCUmFhdTZEQUpkcjlENHB4QlJ0RUhoZXRxY2swWHpBM1YwSWh3bEwtRHVCMUFxOTBvY2t4S3Mxc3ExY3c5ZlpZeXRZZEZTWXUyaDQ0ejdwMzBMV1d4WGdSZkJLTjRWVlozeGlHMEplRVV0TVMtLURhX1NBV2xnYlVkdTlvcUw0amNWQ05VbWNxVHdLLVVhUUp5bFdLNk1fQVJ3bVl6SXh5bHItMGx0M2syanRLN2VJc1JkTUxYb1JWZDhyR0VHbFhxMldKMDJoNWxKOURMR3ljV0xWbi1MTENvQjdjUnNRT210ZDctLTd6clJub2VWT3pxMzE3SlZCWDFreV9qRjFVLUlZazNreXc1ZlpULXQ2eUtxWmFzbnd1cFVJY0gzYnlhRlAyS3hzWU1lMGZrVTBUcUllOFJCN3BOaHRsOGVLY05sQ3R0VVpjSE1Hd1dzTm1uamJkYW5BSUdNV0N6QjRkR1VseC1xLXB0S1BFVlJ5Tl9HZTdtVmwxbXEzOTN5bldTUXNuRGlHVXRyR3RKSXduT09jSWJHUDdIWWROUmxnVXZIQXRuVklJaU9tUXI0Q1BWMVV6NGZtb0hKZU5RS0taSUhYMzgzSHBaWVZZcTJ5NVp6ZEpYc2xZZ3k4ai1VUFlKVzlGMHJDWTAydkFJR1FtNUZva3BBejVkNkRHUElSbW16WklwQURBWktNVTQ3Vi1JajhUZVJzbjRFdk1MNWVCUUNCSk94Sy1sZUdZOW4xN2t4a2laNlVnYlFvS20wOUF2TEdJaHhIaU1QVDkxU2YxQ1c0M2IxSTFYWmlfVjUxZ3dLWXlHcVdvT2JyRGM5c0JCNWFjeHE4TzViVERncWRHcTgxbTFFZ01RTTl3S3dmcGUxNXQxYVZnaFhyUm1RTUdwa016T042NEkzamdIeEJGd3FUZXpDWmNuMC1PNFo4V2dyeW1lSWdfRFNWWnlsQm9vVlRQZTVSaHVCRGJ5ZnVTMXdSQ0VDUGJQeUFoVkc3NHNEM0I2YmFYckVWVWhjZVJwdmMyOTN4VkYtYXpFYVhzUUYzdTZrX3RQYUtsNS1NcVluX0FIMFNGNVpXU3VKay1EczJ2WHNMeDJsWTBqWG1VejlNeVlOZ2pWSVVzVXVRWXlmeU1MU2JLMUs1Y3hUVmNjdWdxUVE4OFNPN3FBOEpuQk1xRlRhbHNDXzd4cW1zeENyejZ1eUlmRXhFelVlNUJfYnI0cXpIVjZMNGRabVNDRTZFOGVNTmNMbjF6QW15YWtyVW05czd5V3VQRFlZLVBPZG5jNG5oVEdyemZjcV9VV2FRbGJFZlpVYmx1T2VGaFpvVDE0MC1BS0k3dHhZYkNjYjdyRU52MEU1TTBUUFVVcnpmSG1ieUZZckF0YWlGMWxrOVY0UmFFM1MxSlVtLWZUTG9yc19veW9GREZSOXdFMDRPVkNZa3NodUlGRW9RUlVQSHZscEM2dUxjWk9mMk85eFg2bEJPT0NoN3k3U3d4NlJJN0JRZFNmQUVCSjFmYWNNamxUY0plc3hZRDY4UGY1dktzM2lLejRRQnhhdnBvS3pLYWpRZGxEcHdCU1lqTDN1QTFLZU52MEw5ZFFMdVdpR0I4TVpCT3V0dHJHT2lzRUI0YktrZjd2QUt2SmNEUTM0OXZMWGhtcmEtZG82WGlhamRnUEJ0UmFVS0xERVB3QXlDTkdRS2M5SmZ6QWtwVmF3YVpzalNhOVNBLVRxTjFSR1dkc1lNcDYteDJuRzVzdU05aXNGZVhfSm5SdDU0aGdONzdZYk1JRERCWEl6ZTJTOFUzWkM5dm5rV3VwQU5XRXdOUXF3dTJqWmpCNV9aOWdJUjJMYUVRVnRnYjFoOHIwb0JXSmpoYTQzR2d5NUNlMjIzSEhHcjJYNXp5WFlaYUlXUEdKVkY0WlhWWlkxV190SXdTVE5BcFZOTzRRQmpjVllQQUlORXAyTHZXdDZoOHkxdl9OQzFHNFdQTi15aHQ5WHNHUG0wcjU2THRTZUo4eFpKUkJyal9nUDRXU204eHYzZnFuSF92TTdic3Y1SWhtN2MxbXllZnY5djkwOUx0aXpWMFA5WWh5YnJwel80cjJfZnZzV2RmQkp2ckdEWG5KQ05JbTJIb3ZyZnhvOE1lZUI0a3FZSlJSTVlUbVVVSE1kMGhGTXhsWkZVbk5CX242TjRLYU1tSzdlX19SZnBPRlY3OjFWVG45NTpUZnlkcnQzNWp2RFJJMDVvTXJfazNUTmNSRGsiJwpwMTQ2CnNTJ2RvbWFpbl9zcGVjaWZpZWQnCnAxNDcKSTAwCnNTJ19yZXN0JwpwMTQ4CihkcDE0OQpTJ2h0dHBvbmx5JwpwMTUwCk5zc1MndmVyc2lvbicKcDE1MQpJMApzUydwb3J0X3NwZWNpZmllZCcKcDE1MgpJMDAKc1MncmZjMjEwOScKcDE1MwpJMDAKc1MnZGlzY2FyZCcKcDE1NApJMDEKc1MncGF0aF9zcGVjaWZpZWQnCnAxNTUKSTAxCnNTJ3BhdGgnCnAxNTYKUycvJwpzUydwb3J0JwpwMTU3Ck5zUydjb21tZW50X3VybCcKcDE1OApOc1Mnc2VjdXJlJwpwMTU5CkkwMApzYnNzc3Nic1Mnc3RyZWFtJwpwMTYwCkkwMApzUydob29rcycKcDE2MQooZHAxNjIKUydyZXNwb25zZScKcDE2MwoobHAxNjQKc3NTJ2F1dGgnCnAxNjUKTnNTJ3RydXN0X2VudicKcDE2NgpJMDEKc1MnaGVhZGVycycKcDE2NwpnMQooY3JlcXVlc3RzLnN0cnVjdHVyZXMKQ2FzZUluc2Vuc2l0aXZlRGljdApwMTY4CmczCk50UnAxNjkKKGRwMTcwClMnX3N0b3JlJwpwMTcxCihkcDE3MgpTJ2FjY2VwdC1lbmNvZGluZycKcDE3MwooUydBY2NlcHQtRW5jb2RpbmcnCnAxNzQKUydnemlwLCBkZWZsYXRlLCBjb21wcmVzcycKdHAxNzUKc1MnYWNjZXB0JwpwMTc2CihTJ0FjY2VwdCcKcDE3NwpTJyovKicKcDE3OAp0cDE3OQpzUyd1c2VyLWFnZW50JwpwMTgwCihTJ1VzZXItQWdlbnQnCnAxODEKUydweXRob24tcmVxdWVzdHMvMi4wLjAgQ1B5dGhvbi8yLjcuNSBEYXJ3aW4vMTMuMC4wJwp0cDE4Mgpzc2JzUydjZXJ0JwpwMTgzCk5zUydwYXJhbXMnCnAxODQKKGRwMTg1CnNTJ3ByZWZldGNoJwpwMTg2Ck5zUyd0aW1lb3V0JwpwMTg3Ck5zUyd2ZXJpZnknCnAxODgKSTAxCnNTJ3Byb3hpZXMnCnAxODkKKGRwMTkwCnNTJ2FkYXB0ZXJzJwpwMTkxCmNyZXF1ZXN0cy5wYWNrYWdlcy51cmxsaWIzLnBhY2thZ2VzLm9yZGVyZWRfZGljdApPcmRlcmVkRGljdApwMTkyCigobHAxOTMKKGxwMTk0ClMnaHR0cHM6Ly8nCnAxOTUKYWcxCihjcmVxdWVzdHMuYWRhcHRlcnMKSFRUUEFkYXB0ZXIKcDE5NgpnMwpOdFJwMTk3CihkcDE5OApTJ19wb29sX2Jsb2NrJwpwMTk5CkkwMApzUydfcG9vbF9tYXhzaXplJwpwMjAwCkkxMApzUydtYXhfcmV0cmllcycKcDIwMQpJMApzUydjb25maWcnCnAyMDIKKGRwMjAzCnNTJ19wb29sX2Nvbm5lY3Rpb25zJwpwMjA0CkkxMApzYmFhKGxwMjA1ClMnaHR0cDovLycKcDIwNgphZzEKKGcxOTYKZzMKTnRScDIwNwooZHAyMDgKZzE5OQpJMDAKc2cyMDAKSTEwCnNnMjAxCkkwCnNnMjAyCihkcDIwOQpzZzIwNApJMTAKc2JhYXRScDIxMApzUydtYXhfcmVkaXJlY3RzJwpwMjExCkkzMApzYnNTJ2F1dGhvcml6ZWQnCnAyMTIKSTAxCnNTJ3NlcnZlcnBhdGhfaGlzdG9yeScKcDIxMwpnOQooKGxwMjE0CihTJy9zbWFsbHRlc3QnClMnMjFkOGVhYjQyZjFjYzJlMjhkNTY4Y2MwOTc1MGFkYTU5MDQwMDk4OScKdHAyMTUKYXRScDIxNgpzc2Iu"))
        localindex = cPickle.loads(base64.decodestring(
            "KGRwMQpTJ2ZpbGVzdGF0cycKcDIKKGRwMwpzUydkaXJuYW1lcycKcDQKKGRwNQpTJ2RjNDAwOTQ0YjA5OWU4YjNjYTFkNDIxZTQ4MjY2MzM4MmNjODgzYzknCnA2CihkcDcKUyduYW1lc2hhc2gnCnA4ClMnODFjMjUyNWNlYTZmY2VkYWRjYWRmZGY1YTU1NTI2ZjkyY2MyMDY5OCcKcDkKc1MnZGlybmFtZScKcDEwClMnL1VzZXJzL3JhYnNoYWtlaC93b3Jrc3BhY2UvY3J5cHRvYm94L2NyeXB0b2JveF9hcHAvc291cmNlL2NvbW1hbmRzL3Rlc3RkYXRhL3Rlc3RtYXAvYWxsX3R5cGVzJwpwMTEKc1MnZmlsZW5hbWVzJwpwMTIKKGxwMTMKKGRwMTQKUyduYW1lJwpwMTUKUycuRFNfU3RvcmUnCnAxNgpzYShkcDE3CmcxNQpTJ2JtcHRlc3QucG5nJwpwMTgKc2EoZHAxOQpnMTUKUydkb2N1bWVudC5wZGYnCnAyMApzYShkcDIxCmcxNQpTJ3dvcmQuZG9jeCcKcDIyCnNhc1MnZGlybmFtZWhhc2gnCnAyMwpnNgpzc1MnZGEzOWEzZWU1ZTZiNGIwZDMyNTViZmVmOTU2MDE4OTBhZmQ4MDcwOScKcDI0CihkcDI1Cmc4ClMnMWY0ZjUyZTE0YTI5NzEyMmJhMGEyM2QyNjg5NDIzZTFhYWIxMDY0OCcKcDI2CnNnMTAKUycvVXNlcnMvcmFic2hha2VoL3dvcmtzcGFjZS9jcnlwdG9ib3gvY3J5cHRvYm94X2FwcC9zb3VyY2UvY29tbWFuZHMvdGVzdGRhdGEvdGVzdG1hcCcKcDI3CnNnMTIKKGxwMjgKKGRwMjkKZzE1ClMnLkRTX1N0b3JlJwpwMzAKc2FzZzIzCmcyNApzc1MnMjFkOGVhYjQyZjFjYzJlMjhkNTY4Y2MwOTc1MGFkYTU5MDQwMDk4OScKcDMxCihkcDMyCmc4ClMnODE0MDZiMWM0Y2MyM2NlMTM1M2ZjZGM2MDJhY2EwOGI4OTE0ZGNkYicKcDMzCnNnMTAKUycvVXNlcnMvcmFic2hha2VoL3dvcmtzcGFjZS9jcnlwdG9ib3gvY3J5cHRvYm94X2FwcC9zb3VyY2UvY29tbWFuZHMvdGVzdGRhdGEvdGVzdG1hcC9zbWFsbHRlc3QnCnAzNApzZzEyCihscDM1CihkcDM2CmcxNQpTJy5EU19TdG9yZScKcDM3CnNhKGRwMzgKZzE1ClMndGVzdC5jcHAnCnAzOQpzYShkcDQwCmcxNQpTJ3Rlc3QuamF2YScKcDQxCnNhc2cyMwpnMzEKc3NzLg=="))
        serverindex = cPickle.loads(base64.decodestring(
            "KGRwMQpWZG9jbGlzdApwMgoobHAzCihkcDQKVmNvbnRlbnRfaGFzaF9sYXRlc3RfdGltZXN0YW1wCnA1Ck5zVmRvYwpwNgooZHA3ClZtX3BhcmVudApwOApWCnNWbV9kYXRhX2lkCnA5ClYKc1ZtX3BhdGgKcDEwClYvCnNWbV9kYXRlX2h1bWFuCnAxMQpWMDgvMTAvMTMgMTM6NDYKcDEyCnNWbV9jcmVhdGlvbl90aW1lCnAxMwpGMTM4MTIzMjc2NS45OApzVm1fc2x1ZwpwMTQKVmRvY3VtZW50ZW4KcDE1CnNWdGltZXN0YW1wCnAxNgpGMTM4MTIzMjc2NS45OApzVm1fZGF0ZV90aW1lCnAxNwpGMTM4MTIzMjc2NTk4MApzVm1fc2hvcnRfaWQKcDE4ClZ6emRoCnAxOQpzVm1fZGF0ZQpwMjAKRjEzODEyMzI3NjUuOTgKc1ZtX3NpemUKcDIxCkkxMwpzVm1fc2x1Z3BhdGgKcDIyClYvCnNWbV9vcmRlcgpwMjMKSTAKc1ZtX25vZGV0eXBlCnAyNApWZm9sZGVyCnAyNQpzVm1fbWltZQpwMjYKVmZvbGRlcgpwMjcKc1ZtX25hbWUKcDI4ClZkb2N1bWVudGVuCnAyOQpzc1Zyb290cGFyZW50CnAzMApOc1ZfaWQKcDMxClZ6emRoCnAzMgpzVnBhcmVudApwMzMKTnNhKGRwMzQKZzUKTnNnNgooZHAzNQpnOApWenpkaApwMzYKc2c5ClYKc2cxMApWL3NtYWxsdGVzdApwMzcKc2cxMQpWMDkvMTAvMTMgMDg6MjEKcDM4CnNnMTMKRjEzODEyOTk2ODEuMzE1MjM0OQpzZzE0ClZzbWFsbHRlc3QKcDM5CnNnMTYKRjEzODEyOTk2ODEuMzE1MTUKc2cxNwpGMTM4MTI5OTY4MTMxNS4xNDk5CnNnMTgKVmRqanYKcDQwCnNnMjAKRjEzODEyOTk2ODEuMzE1MTUKc2cyMQpJMTMKc2cyMgpWL3NtYWxsdGVzdApwNDEKc2cyMwpJMQpzZzI0ClZmb2xkZXIKcDQyCnNnMjYKVmZvbGRlcgpwNDMKc2cyOApWc21hbGx0ZXN0CnA0NApzc2czMApWZGpqdgpwNDUKc2czMQpWZGpqdgpwNDYKc2czMwpWenpkaApwNDcKc2EoZHA0OApnNQoobHA0OQpWYzY3MzFkOGY0NmUxODUzZDRiMDZlNmZhZjA1NWRmZDQwMzMyZDNmMwpwNTAKYUYxMzgxMjk5NjgyLjY4OTE2NTEKYXNnNgooZHA1MQpnOApWZGpqdgpwNTIKc2c5ClZjcnlwdG9fZG9jX2M0Njg2MWU1NzlhMTQ3N2NhMzdkYjUyNjk0OGNmOThjCnA1MwpzZzEwClYvc21hbGx0ZXN0L3Rlc3QuamF2YQpwNTQKc2cxMQpWMDkvMTAvMTMgMDg6MjEKcDU1CnNnMTMKRjEzODEyOTk2ODEuMzE1NzQ4OQpzZzE0ClZ0ZXN0amF2YQpwNTYKc2cxNgpGMTM4MTI5OTY4Mi42ODkxNjUxCnNnMTcKRjEzODEyOTk2ODEzMTUuNjc5OQpzZzE4ClZrc2J4CnA1NwpzZzIwCkYxMzgxMjk5NjgxLjMxNTY4CnNnMjEKSTkKc2cyMgpWL3NtYWxsdGVzdC90ZXN0amF2YQpwNTgKc2cyMwpJMApzZzI0ClZmaWxlCnA1OQpzZzI2ClZ0ZXh0L3gtamF2YS1zb3VyY2UKcDYwCnNnMjgKVnRlc3QuamF2YQpwNjEKc3NnMzAKVmRqanYKcDYyCnNnMzEKVmtzYngKcDYzCnNnMzMKVmRqanYKcDY0CnNhKGRwNjUKZzUKKGxwNjYKVjMwZDc0ZDI1ODQ0MmM3YzY1NTEyZWFmYWI0NzQ1NjhkZDcwNmM0MzAKcDY3CmFGMTM4MTI5OTY5MS42MjM5MzY5CmFzZzYKKGRwNjgKZzgKVmRqanYKcDY5CnNnOQpWY3J5cHRvX2RvY182ZmI1YWU1N2QwNTI0YzMyYjkzODU3NGJjOWQyNGIxYgpwNzAKc2cxMApWL3NtYWxsdGVzdC90ZXN0LmNwcApwNzEKc2cxMQpWMDkvMTAvMTMgMDg6MjEKcDcyCnNnMTMKRjEzODEyOTk2OTAuNTUzNjU0CnNnMTQKVnRlc3RjcHAKcDczCnNnMTYKRjEzODEyOTk2OTEuNjIzOTM2OQpzZzE3CkYxMzgxMjk5NjkwNTUzLjU2NjkKc2cxOApWc3RteApwNzQKc2cyMApGMTM4MTI5OTY5MC41NTM1NjY5CnNnMjEKSTQKc2cyMgpWL3NtYWxsdGVzdC90ZXN0Y3BwCnA3NQpzZzIzCkkxCnNnMjQKVmZpbGUKcDc2CnNnMjYKVnRleHQveC1jCnA3NwpzZzI4ClZ0ZXN0LmNwcApwNzgKc3NnMzAKVmRqanYKcDc5CnNnMzEKVnN0bXgKcDgwCnNnMzMKVmRqanYKcDgxCnNhc1MnZGlybGlzdCcKcDgyCihscDgzClYvc21hbGx0ZXN0CnA4NAphVi8KYXNWdHJlZV90aW1lc3RhbXAKcDg1CkYxMzgxMjk5Njk0LjU4MDkxMzEKcy4="))
        cbmemory, cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(memory, cboptions, localindex, serverindex)
        self.assertEqual(len(file_uploads), 3)

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
        os.mkdir("testdata/testmap/foo")
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
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        self.assertTrue(self.files_synced())
        os.system("rm -Rf testdata/testmap/")
        self.cbmemory = Memory()
        self.cbmemory.set("cryptobox_folder", self.cboptions.dir)
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads = self.get_sync_changes()
        self.assertEqual(len(dir_del_server), 0)
        self.assertEqual(len(dir_make_local), 3)
        self.assertEqual(len(file_downloads), 5)


if __name__ == '__main__':
    unittest.main()

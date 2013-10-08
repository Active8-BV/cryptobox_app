# coding=utf-8
"""
unit test for app commands
"""
__author__ = 'rabshakeh'
import os
import pickle
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
                os.system("cd testdata; nohup wget http://download.thinkbroadband.com/" + tfn + " &")

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
        localindex_check = pickle.load(open("testdata/localindex_test.pickle"))
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
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)

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
        if not self.cbmemory.has("session"):
            self.cbmemory = authorize_user(self.cbmemory, self.cboptions)

        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)
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

    def all_changes_asserted_zero(self):
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)
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

    #noinspection PyMethodMayBeStatic
    def test_sync_delete_local_folder_diff(self):
        """
        test_sync_delete_local_folder_diff
        """
        import base64
        options_d = {"dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/testmap", "encrypt": True, "remove": False, "username": "rabshakeh", "password": "kjhfsd98", "cryptobox": "test", "clear": False, "sync": False, "server": "http://127.0.0.1:8000", "numdownloadthreads": 12}
        cboptions = Dict2Obj(options_d)
        memory = pickle.loads(base64.decodestring("Y2NvcHlfcmVnCl9yZWNvbnN0cnVjdG9yCnAwCihjY2JhX3V0aWxzCk1lbW9yeQpwMQpjX19idWlsdGluX18Kb2JqZWN0CnAyCk50cDMKUnA0CihkcDUKUydkYXRhJwpwNgooZHA3ClMnbG9jYWxwYXRoX2hpc3RvcnknCnA4CmNfX2J1aWx0aW5fXwpzZXQKcDkKKChscDEwCihTJy9hbGxfdHlwZXMvZG9jdW1lbnQucGRmJwpwMTEKUydlN2JkZTk1NTBkOTY0ZjA4ODU1ZGI2Y2E1MzA5YjRhYTE0OGMyYjZlJwpwMTIKdHAxMwphKFMnL2FsbF90eXBlcy9ibXB0ZXN0LnBuZycKcDE0ClMnNGJkZGU5YWEwZTc0Zjg0ZWE2MGZjODU1MzQ1Yjg0ODA2ODU3M2JhNCcKcDE1CnRwMTYKYShTJy9hbGxfdHlwZXMvZm9vL3Rlc3QudHh0JwpwMTcKUydhNDM2MzA1N2E3YjU0N2ExZTcyYjhkNjljODYzNjVmODBhNzNkMjM2JwpwMTgKdHAxOQphKFMnL3NtYWxsdGVzdC90ZXN0LmNwcCcKcDIwClMnYmFmMjg5YzRhNTExOWRjNTc2MzYzYTZhYjljOTUxNWE5MDZkNTg1NicKcDIxCnRwMjIKYShTJy9hbGxfdHlwZXMvZm9vMi9iYXIvdGVzdDMudHh0JwpwMjMKUydkOTc2YjRjMGRjZmE4NDYxOGI5NWJhMDQ1OWY3NGE0ZDQyNDE0MTBjJwpwMjQKdHAyNQphKFMnL3NtYWxsdGVzdC90ZXN0LmphdmEnCnAyNgpTJzVhNWFjNzcwM2ZmZWJiMThiNzEwOWQ1ODlhNzVmYTFhZDM1OWM0YWMnCnAyNwp0cDI4CmEoUycvYWxsX3R5cGVzL2ZvbzIvdGVzdDIudHh0JwpwMjkKUycyZTNkODBlNmUyYzAzYWQwNDhjMTA5NDg4ZmY1MTdhYWQ2OTQyMDVjJwpwMzAKdHAzMQphKFMnL2FsbF90eXBlcy93b3JkLmRvY3gnCnAzMgpTJzdkNzJkMzk2OTMzOWJlZWRkNDg4YzMzNGZlYjQ4ZTA4M2E1MDY2ZGInCnAzMwp0cDM0CmF0cDM1ClJwMzYKc1MnY3J5cHRvYm94X2ZvbGRlcicKcDM3ClMnL1VzZXJzL3JhYnNoYWtlaC93b3Jrc3BhY2UvY3J5cHRvYm94L2NyeXB0b2JveF9hcHAvc291cmNlL2NvbW1hbmRzL3Rlc3RkYXRhL3Rlc3RtYXAnCnAzOApzUydzZXJ2ZXJpbmRleCcKcDM5CihkcDQwClZkb2NsaXN0CnA0MQoobHA0MgooZHA0MwpWY29udGVudF9oYXNoX2xhdGVzdF90aW1lc3RhbXAKcDQ0Ck5zVmRvYwpwNDUKKGRwNDYKVm1fcGFyZW50CnA0NwpWCnA0OApzVm1fZGF0YV9pZApwNDkKZzQ4CnNWbV9wYXRoCnA1MApWLwpwNTEKc1ZtX2RhdGVfaHVtYW4KcDUyClYwOC8xMC8xMyAxMzo0NgpwNTMKc1ZtX2NyZWF0aW9uX3RpbWUKcDU0CkYxMzgxMjMyNzY1Ljk4CnNWbV9zbHVnCnA1NQpWZG9jdW1lbnRlbgpwNTYKc1Z0aW1lc3RhbXAKcDU3CkYxMzgxMjMyNzY1Ljk4CnNWbV9kYXRlX3RpbWUKcDU4CkYxMzgxMjMyNzY1OTgwLjAKc1ZtX3Nob3J0X2lkCnA1OQpWenpkaApwNjAKc1ZtX2RhdGUKcDYxCkYxMzgxMjMyNzY1Ljk4CnNWbV9zaXplCnA2MgpJMTk1NTE1CnNWbV9zbHVncGF0aApwNjMKZzUxCnNWbV9vcmRlcgpwNjQKSTAKc1ZtX25vZGV0eXBlCnA2NQpWZm9sZGVyCnA2NgpzVm1fbWltZQpwNjcKVmZvbGRlcgpwNjgKc1ZtX25hbWUKcDY5ClZkb2N1bWVudGVuCnA3MApzc1Zyb290cGFyZW50CnA3MQpOc1ZfaWQKcDcyClZ6emRoCnA3MwpzVnBhcmVudApwNzQKTnNhKGRwNzUKZzQ0Ck5zZzQ1CihkcDc2Cmc0NwpWenpkaApwNzcKc2c0OQpnNDgKc2c1MApWL2FsbF90eXBlcwpwNzgKc2c1MgpWMDgvMTAvMTMgMTg6NTUKcDc5CnNnNTQKRjEzODEyNTEzMjguNTYwNDY0CnNnNTUKVmFsbF90eXBlcwpwODAKc2c1NwpGMTM4MTI1MTMyOC41NjAzMjkKc2c1OApGMTM4MTI1MTMyODU2MC4zMjg5CnNnNTkKVm53amoKcDgxCnNnNjEKRjEzODEyNTEzMjguNTYwMzI5CnNnNjIKSTE5NTUwMgpzZzYzClYvYWxsX3R5cGVzCnA4MgpzZzY0CkkwCnNnNjUKVmZvbGRlcgpwODMKc2c2NwpWZm9sZGVyCnA4NApzZzY5ClZhbGxfdHlwZXMKcDg1CnNzZzcxClZud2pqCnA4NgpzZzcyClZud2pqCnA4NwpzZzc0ClZ6emRoCnA4OApzYShkcDg5Cmc0NApOc2c0NQooZHA5MApnNDcKVm53amoKcDkxCnNnNDkKZzQ4CnNnNTAKVi9hbGxfdHlwZXMvZm9vMgpwOTIKc2c1MgpWMDgvMTAvMTMgMTg6NTUKcDkzCnNnNTQKRjEzODEyNTEzMjguNTg1MDE2CnNnNTUKVmZvbzIKcDk0CnNnNTcKRjEzODEyNTEzMjguNTg0OTIxCnNnNTgKRjEzODEyNTEzMjg1ODQuOTIxCnNnNTkKVmhrdm4KcDk1CnNnNjEKRjEzODEyNTEzMjguNTg0OTIxCnNnNjIKSTEwOTIKc2c2MwpWL2FsbF90eXBlcy9mb28yCnA5NgpzZzY0CkkwCnNnNjUKVmZvbGRlcgpwOTcKc2c2NwpWZm9sZGVyCnA5OApzZzY5ClZmb28yCnA5OQpzc2c3MQpWbndqagpwMTAwCnNnNzIKVmhrdm4KcDEwMQpzZzc0ClZud2pqCnAxMDIKc2EoZHAxMDMKZzQ0Ck5zZzQ1CihkcDEwNApnNDcKVmhrdm4KcDEwNQpzZzQ5Cmc0OApzZzUwClYvYWxsX3R5cGVzL2ZvbzIvYmFyCnAxMDYKc2c1MgpWMDgvMTAvMTMgMTg6NTUKcDEwNwpzZzU0CkYxMzgxMjUxMzI4LjU4NTQxNgpzZzU1ClZiYXIKcDEwOApzZzU3CkYxMzgxMjUxMzI4LjU4NTM0NgpzZzU4CkYxMzgxMjUxMzI4NTg1LjM0NgpzZzU5ClZjZ3pqCnAxMDkKc2c2MQpGMTM4MTI1MTMyOC41ODUzNDYKc2c2MgpJNTQ2CnNnNjMKVi9hbGxfdHlwZXMvZm9vMi9iYXIKcDExMApzZzY0CkkwCnNnNjUKVmZvbGRlcgpwMTExCnNnNjcKVmZvbGRlcgpwMTEyCnNnNjkKVmJhcgpwMTEzCnNzZzcxClZud2pqCnAxMTQKc2c3MgpWY2d6agpwMTE1CnNnNzQKVmhrdm4KcDExNgpzYShkcDExNwpnNDQKKGxwMTE4ClYxY2EyNGQyM2FjZDM0MGU1ZWY5YzhiZjFmNjVjYWE0Y2MxOTdkOTA0CnAxMTkKYUYxMzgxMjUxMzM5LjIxNjYxMwphc2c0NQooZHAxMjAKZzQ3ClZjZ3pqCnAxMjEKc2c0OQpWY3J5cHRvX2RvY19jODM3MTE3Y2JjNDg0NDAxYjFlZGE2MDI4ZWM3MzRmZQpwMTIyCnNnNTAKVi9hbGxfdHlwZXMvZm9vMi9iYXIvdGVzdDMudHh0CnAxMjMKc2c1MgpWMDgvMTAvMTMgMTg6NTUKcDEyNApzZzU0CkYxMzgxMjUxMzM4LjE2NTgxOApzZzU1ClZ0ZXN0M3R4dApwMTI1CnNnNTcKRjEzODEyNTEzMzkuMjE2NjEzCnNnNTgKRjEzODEyNTEzMzgxNjUuNzI5CnNnNTkKVnJtcmgKcDEyNgpzZzYxCkYxMzgxMjUxMzM4LjE2NTcyOQpzZzYyCkk1NDYKc2c2MwpWL2FsbF90eXBlcy9mb28yL2Jhci90ZXN0M3R4dApwMTI3CnNnNjQKSTAKc2c2NQpWZmlsZQpwMTI4CnNnNjcKVnRleHQvcGxhaW4KcDEyOQpzZzY5ClZ0ZXN0My50eHQKcDEzMApzc2c3MQpWbndqagpwMTMxCnNnNzIKVnJtcmgKcDEzMgpzZzc0ClZjZ3pqCnAxMzMKc2EoZHAxMzQKZzQ0CihscDEzNQpWMWNhMjRkMjNhY2QzNDBlNWVmOWM4YmYxZjY1Y2FhNGNjMTk3ZDkwNApwMTM2CmFGMTM4MTI1MTMzNi43NzU3OTEKYXNnNDUKKGRwMTM3Cmc0NwpWaGt2bgpwMTM4CnNnNDkKVmNyeXB0b19kb2NfOWVlYTdkOWU0ZjM1NGQ1ZWE3YjU3NTcyZmVmM2MyMjQKcDEzOQpzZzUwClYvYWxsX3R5cGVzL2ZvbzIvdGVzdDIudHh0CnAxNDAKc2c1MgpWMDgvMTAvMTMgMTg6NTUKcDE0MQpzZzU0CkYxMzgxMjUxMzM1LjQ3OTg2OQpzZzU1ClZ0ZXN0MnR4dApwMTQyCnNnNTcKRjEzODEyNTEzMzYuNzc1NzkxCnNnNTgKRjEzODEyNTEzMzU0NzkuNjgwMgpzZzU5ClZ2d2R2CnAxNDMKc2c2MQpGMTM4MTI1MTMzNS40Nzk2OApzZzYyCkk1NDYKc2c2MwpWL2FsbF90eXBlcy9mb28yL3Rlc3QydHh0CnAxNDQKc2c2NApJMQpzZzY1ClZmaWxlCnAxNDUKc2c2NwpWdGV4dC9wbGFpbgpwMTQ2CnNnNjkKVnRlc3QyLnR4dApwMTQ3CnNzZzcxClZud2pqCnAxNDgKc2c3MgpWdndkdgpwMTQ5CnNnNzQKVmhrdm4KcDE1MApzYShkcDE1MQpnNDQKTnNnNDUKKGRwMTUyCmc0NwpWbndqagpwMTUzCnNnNDkKZzQ4CnNnNTAKVi9hbGxfdHlwZXMvZm9vCnAxNTQKc2c1MgpWMDgvMTAvMTMgMTg6NTUKcDE1NQpzZzU0CkYxMzgxMjUxMzI4LjYzNDI1NgpzZzU1ClZmb28KcDE1NgpzZzU3CkYxMzgxMjUxMzI4LjYzNDE0OApzZzU4CkYxMzgxMjUxMzI4NjM0LjE0OApzZzU5ClZic3B0CnAxNTcKc2c2MQpGMTM4MTI1MTMyOC42MzQxNDgKc2c2MgpJNTQ2CnNnNjMKVi9hbGxfdHlwZXMvZm9vCnAxNTgKc2c2NApJMQpzZzY1ClZmb2xkZXIKcDE1OQpzZzY3ClZmb2xkZXIKcDE2MApzZzY5ClZmb28KcDE2MQpzc2c3MQpWbndqagpwMTYyCnNnNzIKVmJzcHQKcDE2MwpzZzc0ClZud2pqCnAxNjQKc2EoZHAxNjUKZzQ0CihscDE2NgpWMWNhMjRkMjNhY2QzNDBlNWVmOWM4YmYxZjY1Y2FhNGNjMTk3ZDkwNApwMTY3CmFGMTM4MTI1MTMzMS45MzkyMDQKYXNnNDUKKGRwMTY4Cmc0NwpWYnNwdApwMTY5CnNnNDkKVmNyeXB0b19kb2NfOTNjMmE4ZDUwMjYzNGQ3N2I1NzdiNjQzMjgyMGExM2IKcDE3MApzZzUwClYvYWxsX3R5cGVzL2Zvby90ZXN0LnR4dApwMTcxCnNnNTIKVjA4LzEwLzEzIDE4OjU1CnAxNzIKc2c1NApGMTM4MTI1MTMzMS4xMDI1OApzZzU1ClZ0ZXN0dHh0CnAxNzMKc2c1NwpGMTM4MTI1MTMzMS45MzkyMDQKc2c1OApGMTM4MTI1MTMzMTEwMi40OTMyCnNnNTkKVmJxcnIKcDE3NApzZzYxCkYxMzgxMjUxMzMxLjEwMjQ5MwpzZzYyCkk1NDYKc2c2MwpWL2FsbF90eXBlcy9mb28vdGVzdHR4dApwMTc1CnNnNjQKSTAKc2c2NQpWZmlsZQpwMTc2CnNnNjcKVnRleHQvcGxhaW4KcDE3NwpzZzY5ClZ0ZXN0LnR4dApwMTc4CnNzZzcxClZud2pqCnAxNzkKc2c3MgpWYnFycgpwMTgwCnNnNzQKVmJzcHQKcDE4MQpzYShkcDE4MgpnNDQKKGxwMTgzClY5N2VjZjIxODQzODQyMTE5NzYxOTVhZWE3NjFhNmJmOTM3NGRmN2RkCnAxODQKYUYxMzgxMjUxMzMzLjA1NDcxNwphc2c0NQooZHAxODUKZzQ3ClZud2pqCnAxODYKc2c0OQpWY3J5cHRvX2RvY19jYTk2Y2FiZTFlODk0Y2U4YWU0NzY4ZmNhNGJiNzYxZQpwMTg3CnNnNTAKVi9hbGxfdHlwZXMvZG9jdW1lbnQucGRmCnAxODgKc2c1MgpWMDgvMTAvMTMgMTg6NTUKcDE4OQpzZzU0CkYxMzgxMjUxMzMxLjk5NDUwOQpzZzU1ClZkb2N1bWVudHBkZgpwMTkwCnNnNTcKRjEzODEyNTEzMzMuMDU0NzE3CnNnNTgKRjEzODEyNTEzMzE5OTQuMzk2CnNnNTkKVmRwZmQKcDE5MQpzZzYxCkYxMzgxMjUxMzMxLjk5NDM5NgpzZzYyCkk0ODM4OQpzZzYzClYvYWxsX3R5cGVzL2RvY3VtZW50cGRmCnAxOTIKc2c2NApJMgpzZzY1ClZmaWxlCnAxOTMKc2c2NwpWYXBwbGljYXRpb24vcGRmCnAxOTQKc2c2OQpWZG9jdW1lbnQucGRmCnAxOTUKc3NnNzEKVm53amoKcDE5NgpzZzcyClZkcGZkCnAxOTcKc2c3NApWbndqagpwMTk4CnNhKGRwMTk5Cmc0NAoobHAyMDAKVjRiZGZkN2Y1NjY4MTMxNjU5ZmZiMjM1ODczMmEyZGJiYzhiYzYxMzAKcDIwMQphRjEzODEyNTEzMzQuMjg0MzE4CmFzZzQ1CihkcDIwMgpnNDcKVm53amoKcDIwMwpzZzQ5ClZjcnlwdG9fZG9jX2EzYTQzODA0YjZmMjRmNGU5ZjI5NTk0NDRlZjBmOTlmCnAyMDQKc2c1MApWL2FsbF90eXBlcy9ibXB0ZXN0LnBuZwpwMjA1CnNnNTIKVjA4LzEwLzEzIDE4OjU1CnAyMDYKc2c1NApGMTM4MTI1MTMzMy4xMTgzMgpzZzU1ClZibXB0ZXN0cG5nCnAyMDcKc2c1NwpGMTM4MTI1MTMzNC4yODQzMTgKc2c1OApGMTM4MTI1MTMzMzExOC4xMjYKc2c1OQpWa2hrcwpwMjA4CnNnNjEKRjEzODEyNTEzMzMuMTE4MTI2CnNnNjIKSTExOTI0MwpzZzYzClYvYWxsX3R5cGVzL2JtcHRlc3RwbmcKcDIwOQpzZzY0CkkzCnNnNjUKVmZpbGUKcDIxMApzZzY3ClZpbWFnZS9wbmcKcDIxMQpzZzY5ClZibXB0ZXN0LnBuZwpwMjEyCnNzZzcxClZud2pqCnAyMTMKc2c3MgpWa2hrcwpwMjE0CnNnNzQKVm53amoKcDIxNQpzYShkcDIxNgpnNDQKKGxwMjE3ClY1Y2ZiNDkyODI4YzE5ZWEzZDJkNjQyZDg1MWI1Y2U2NzE5NzliMDdlCnAyMTgKYUYxMzgxMjUxMzM1LjQ2NjQ3OQphc2c0NQooZHAyMTkKZzQ3ClZud2pqCnAyMjAKc2c0OQpWY3J5cHRvX2RvY18zNjcxOWVmZjRkYTM0ZmM4YjIyN2I1ZWYwMGQyMjNiYgpwMjIxCnNnNTAKVi9hbGxfdHlwZXMvd29yZC5kb2N4CnAyMjIKc2c1MgpWMDgvMTAvMTMgMTg6NTUKcDIyMwpzZzU0CkYxMzgxMjUxMzM0LjMyMzE3MgpzZzU1ClZ3b3JkZG9jeApwMjI0CnNnNTcKRjEzODEyNTEzMzUuNDY2NDc5CnNnNTgKRjEzODEyNTEzMzQzMjMuMDIyCnNnNTkKVnNjZ2oKcDIyNQpzZzYxCkYxMzgxMjUxMzM0LjMyMzAyMgpzZzYyCkkyNjIzMgpzZzYzClYvYWxsX3R5cGVzL3dvcmRkb2N4CnAyMjYKc2c2NApJNApzZzY1ClZmaWxlCnAyMjcKc2c2NwpWYXBwbGljYXRpb24vdm5kLm9wZW54bWxmb3JtYXRzLW9mZmljZWRvY3VtZW50LndvcmRwcm9jZXNzaW5nbWwuZG9jdW1lbnQKcDIyOApzZzY5ClZ3b3JkLmRvY3gKcDIyOQpzc2c3MQpWbndqagpwMjMwCnNnNzIKVnNjZ2oKcDIzMQpzZzc0ClZud2pqCnAyMzIKc2EoZHAyMzMKZzQ0Ck5zZzQ1CihkcDIzNApnNDcKVnp6ZGgKcDIzNQpzZzQ5Cmc0OApzZzUwClYvc21hbGx0ZXN0CnAyMzYKc2c1MgpWMDgvMTAvMTMgMTg6NTUKcDIzNwpzZzU0CkYxMzgxMjUxMzI5LjU4MDA2NQpzZzU1ClZzbWFsbHRlc3QKcDIzOApzZzU3CkYxMzgxMjUxMzI5LjU3OTk3MwpzZzU4CkYxMzgxMjUxMzI5NTc5Ljk3MwpzZzU5ClZocG1iCnAyMzkKc2c2MQpGMTM4MTI1MTMyOS41Nzk5NzMKc2c2MgpJMTMKc2c2MwpWL3NtYWxsdGVzdApwMjQwCnNnNjQKSTEKc2c2NQpWZm9sZGVyCnAyNDEKc2c2NwpWZm9sZGVyCnAyNDIKc2c2OQpWc21hbGx0ZXN0CnAyNDMKc3NnNzEKVmhwbWIKcDI0NApzZzcyClZocG1iCnAyNDUKc2c3NApWenpkaApwMjQ2CnNhKGRwMjQ3Cmc0NAoobHAyNDgKVmM2NzMxZDhmNDZlMTg1M2Q0YjA2ZTZmYWYwNTVkZmQ0MDMzMmQzZjMKcDI0OQphRjEzODEyNTEzMzAuNjA4CmFzZzQ1CihkcDI1MApnNDcKVmhwbWIKcDI1MQpzZzQ5ClZjcnlwdG9fZG9jXzFiZDZmNjhjMDQxZDRkMDk5MTc5YTBkODdjZGZjZjMyCnAyNTIKc2c1MApWL3NtYWxsdGVzdC90ZXN0LmphdmEKcDI1MwpzZzUyClYwOC8xMC8xMyAxODo1NQpwMjU0CnNnNTQKRjEzODEyNTEzMjkuNTgwNjA5CnNnNTUKVnRlc3RqYXZhCnAyNTUKc2c1NwpGMTM4MTI1MTMzMC42MDgKc2c1OApGMTM4MTI1MTMyOTU4MC41MzgKc2c1OQpWem16cQpwMjU2CnNnNjEKRjEzODEyNTEzMjkuNTgwNTM4CnNnNjIKSTkKc2c2MwpWL3NtYWxsdGVzdC90ZXN0amF2YQpwMjU3CnNnNjQKSTAKc2c2NQpWZmlsZQpwMjU4CnNnNjcKVnRleHQveC1qYXZhLXNvdXJjZQpwMjU5CnNnNjkKVnRlc3QuamF2YQpwMjYwCnNzZzcxClZocG1iCnAyNjEKc2c3MgpWem16cQpwMjYyCnNnNzQKVmhwbWIKcDI2MwpzYShkcDI2NApnNDQKKGxwMjY1ClYzMGQ3NGQyNTg0NDJjN2M2NTUxMmVhZmFiNDc0NTY4ZGQ3MDZjNDMwCnAyNjYKYUYxMzgxMjUxMzM4LjMyNzkzOAphc2c0NQooZHAyNjcKZzQ3ClZocG1iCnAyNjgKc2c0OQpWY3J5cHRvX2RvY18xZWZhNGVkMTIzMGE0OTAyYTViM2JmMTg2ZGM4MmZlMApwMjY5CnNnNTAKVi9zbWFsbHRlc3QvdGVzdC5jcHAKcDI3MApzZzUyClYwOC8xMC8xMyAxODo1NQpwMjcxCnNnNTQKRjEzODEyNTEzMzcuMjg3MTM2CnNnNTUKVnRlc3RjcHAKcDI3MgpzZzU3CkYxMzgxMjUxMzM4LjMyNzkzOApzZzU4CkYxMzgxMjUxMzM3Mjg3LjA0NgpzZzU5ClZ6dGRrCnAyNzMKc2c2MQpGMTM4MTI1MTMzNy4yODcwNDYKc2c2MgpJNApzZzYzClYvc21hbGx0ZXN0L3Rlc3RjcHAKcDI3NApzZzY0CkkxCnNnNjUKVmZpbGUKcDI3NQpzZzY3ClZ0ZXh0L3gtYwpwMjc2CnNnNjkKVnRlc3QuY3BwCnAyNzcKc3NnNzEKVmhwbWIKcDI3OApzZzcyClZ6dGRrCnAyNzkKc2c3NApWaHBtYgpwMjgwCnNhc1MnZGlybGlzdCcKcDI4MQoobHAyODIKZzUxCmFWL2FsbF90eXBlcy9mb28yCnAyODMKYVYvYWxsX3R5cGVzCnAyODQKYVYvYWxsX3R5cGVzL2ZvbwpwMjg1CmFWL3NtYWxsdGVzdApwMjg2CmFWL2FsbF90eXBlcy9mb28yL2JhcgpwMjg3CmFzVnRyZWVfdGltZXN0YW1wCnAyODgKRjEzODEyNTEzMzkuMzY4MTkzCnNzUydzZXNzaW9uJwpwMjg5CmcwCihjcmVxdWVzdHMuc2Vzc2lvbnMKU2Vzc2lvbgpwMjkwCmcyCk50cDI5MQpScDI5MgooZHAyOTMKUydjb29raWVzJwpwMjk0CmcwCihjcmVxdWVzdHMuY29va2llcwpSZXF1ZXN0c0Nvb2tpZUphcgpwMjk1CmcyCk50cDI5NgpScDI5NwooZHAyOTgKUydfbm93JwpwMjk5CkkxMzgxMjUxMzQyCnNTJ19wb2xpY3knCnAzMDAKKGljb29raWVsaWIKRGVmYXVsdENvb2tpZVBvbGljeQpwMzAxCihkcDMwMgpTJ3N0cmljdF9yZmMyOTY1X3VudmVyaWZpYWJsZScKcDMwMwpJMDEKc1Mnc3RyaWN0X25zX2RvbWFpbicKcDMwNApJMApzUydfYWxsb3dlZF9kb21haW5zJwpwMzA1Ck5zUydyZmMyMTA5X2FzX25ldHNjYXBlJwpwMzA2Ck5zUydyZmMyOTY1JwpwMzA3CkkwMApzUydzdHJpY3RfZG9tYWluJwpwMzA4CkkwMApzZzI5OQpJMTM4MTI1MTM0MgpzUydzdHJpY3RfbnNfc2V0X3BhdGgnCnAzMDkKSTAwCnNTJ3N0cmljdF9uc191bnZlcmlmaWFibGUnCnAzMTAKSTAwCnNTJ3N0cmljdF9uc19zZXRfaW5pdGlhbF9kb2xsYXInCnAzMTEKSTAwCnNTJ2hpZGVfY29va2llMicKcDMxMgpJMDAKc1MnX2Jsb2NrZWRfZG9tYWlucycKcDMxMwoodHNTJ25ldHNjYXBlJwpwMzE0CkkwMQpzYnNTJ19jb29raWVzJwpwMzE1CihkcDMxNgpTJzEyNy4wLjAxJwpwMzE3CihkcDMxOApTJy8nCnAzMTkKKGRwMzIwClMnY190b2tlbicKcDMyMQooaWNvb2tpZWxpYgpDb29raWUKcDMyMgooZHAzMjMKUydjb21tZW50JwpwMzI0Ck5zUydkb21haW4nCnAzMjUKZzMxNwpzUyduYW1lJwpwMzI2CmczMjEKc1MnZG9tYWluX2luaXRpYWxfZG90JwpwMzI3CkkwMApzUydleHBpcmVzJwpwMzI4Ck5zUyd2YWx1ZScKcDMyOQpTJyIuZUp4dFZVZlA1QW9SWEI2SWc1X2dOLXdSeVFMbmhNVEJNX1k0amJNOURwZVZjODdaRWhKSHhLX21leXVPOUtta2JuVlhWeDNxWDdfOGNfcmRYOXhmeDduYW96WDcwV1RYOUl2em56OS0tX2JYMy1yQkM1TDIzYkxaNzRZbGZWaUhfNjd3d2M4T29Fb1NQeFRTZzJXVkoydnk3Skp4QXc3bGZrYlhULWhhWHR3RnJiQ3VpeFRfdnFNOHVjQzJ3bll5MlVOZF9yaDNXZ05JLTd3ak5SUmVZTmtWU1p2WEZHcEVic1JYLUN4aThEMmxkbVIzWldjX2gyQmNDaTAxOTBHQXl6VjZuelJxaWpZSVBDN2JVNUpvUHVEdUxvVERoQ1hpblVCcWhWMHBJZ254YW8zUFZxN2g2LXp4RlN3Nk9zeGRMTHdKbl9KdklldXRDdkFpZUdXYXdxb3pQckVOSWFfSUpXYWs5OEUxZWtBdlR4dFYyNzJpb19pTngwSTFTWnlwSUlWOG8taURFcXVWMVI4QUFWTXhsUmhsTFhfOVczZVRhTzBydDRpeEYwd3RkcEZWM3lzNFNhZGVyWlluUTJQbVVuME1zYklKY3RVZjRzc0tnSHR4R3hBNmExM3Y3N3ZPdEVlaDVVN09yZlhzbFVGZldUTHhNWFZUNGxpVGZiRERsOWdQNjBKazFVeTFaSGpkU2dTNHZ1M2swQ2RzMW1kZ3g0eC1SUXhCWVI2SmlEMWE3TGJMNDBXNGJPR3oxVmx3Y3diQmF3MkdmTnQxcWNBZ2F4WUxNSGhNWlNYSDZyNm0wbzlSVEhJMzhaN3VaV1hYYXJmM2ZHZWVhRmc0Y1F5bGpJMXJKV2s0eHpsRFloX1o3VHBxTXNDbTRvRnY2NUJFUmt5SGZBVjZ1cWllaU9aZ2NsNDFBb1ptZ2RmZnpjZWxseFY2V21YTE9idEw5VXJFR2tRZnl4X0FLbnN2bEFSa1RhOEFoZENibFJpS2xEUGwzb01ZOGxHR2FwOUZJQWNDSkJtbkhLdnhFZm1ieU5rLUMxOWdmTDBLQUFJcDJKWDBMd19Ic3V2ZG1jd1NQU2tEYVZGVXhrSUM2c1lqZ2tESnc5UDNWSl9VSmJqZHZValZkbnI2dmVvR0JUQlIxU3hCemRjWm50MUlJclRtTkhoM1QwNDdhR3hxdk5ac1JvSENEZXdBczM2VXRzZmRXbFVLVms4M29tTFF5R1JnSHRlRGFCd0g1QXVtVU5qY2c2bVU2X1BaTWVUVFV0RFBGQWZocDZrOFN3a1NMWnpxY1k4eWxCaDZPM0ZmNG9wQ0FIWms0d2Nzak5vVkI3NF9jTlgyaXEyUXV2QXcydVRlN282bi05SmtONmFNRGJqYlRSM1IyaXRlZmpLbUpfNEQ5RWxjV0ZvcGlaUGg3X2owN2kyQ1lHQkoxOWhQalppU0I4RWFyU2hpbDZESFR1WmhhRGRYcEhMbktLcmpsa0ZUQ1hqaVIzWXhIeEk0SjFRcWZFcGhYX2FOVTFuSlZlYlYyUkg1bUl5YWozSVB6Ni1Oc3g1ZmllTFhaVXFoQkJuR3lCdmdjdXVSazFUVmxKZzN0M2VTMTk0ekdQcnduQl9OSllZenBjMzNLZjlHbVVWWDFrYktqTTRKendzTE5TZXZHME1Bc2p1M0ZoOUoxdnVzUTI4d1Rrd3pNOVRTdk44ZVp2Smxpc0MxbUlYVldUMVhwRnFUVExVbFNiNTlNdWl1ei1qS2dVTVZFYmdKSndjcUV3cmREVlFLSllobW9HTmZMU0YxQ1c2eWNfc2Q3aXQ5S0NjY2xMMWxXamd5S2RKemlvNGtlQUNDenEtTTRWSEttd0k5ZHF5SDE0ZV9UZVZSUE1SSHdvTGkxWFJRVm1VMWxnNUtIYmdDbTFHWFBVRHF3eVplb2Y0NkFYZXQwRUI0RXlDVDlUYmVzVkZZb0R5LTFJZzd2QUx2NWNDUVh3OXZiYmltcmEtZDQyV2lhamVnZkZ2UnFRSkxMQUtZUVpDR2JHRk8tb3M5SWFXS1ZjTU1uOHdhTldDLVRtTjFoS1dkc2NQcGEwX3R1RnpaOFpCaXNOZVhfSm5STjVFUndGNjdJVHNJYkRBWG8zZjJDODAwVks5dm5vVXRWQU1XVTRPU3E0dTF6ZGpCWjdhOVFCUzJMV0hRRnRnYkZ0LXJVZ0FXWnZoYW9fRmdpdEJlMnkxSDNXcTIzMXl5WFFaV0VTTk9aMUY0WlhWWlk1V19OR3pTREZEcGxGTTR3SGljMVFQQW90R3AyTHVXZDloOHl4c19kTzFHRS1NTmU5aHROVHRPUGV5cjUyTHRRUkc4UlpHUnhycl9BSDVHQ3E5eF96ZHEzRC12ODdhc1A1S2hHN2MxbTZmZl85djkwNUl0U3pYMFA5YWh5ZnJwRF83cjI3ZHYtdDRUTkZnRWFTQnYtNWNzN1ZCVV81djRnYUE0bGRJSUhaSHhGX29DVkk1bkdJSWlERU1sVVl6OGZZN2lwWXlhck56LTlsX2FrRlREOjFWVGFaOToyYjIzZ0E2U2NUTzE4d2JaT2pPeW0wV1ZWNU0iJwpwMzMwCnNTJ2RvbWFpbl9zcGVjaWZpZWQnCnAzMzEKSTAwCnNTJ19yZXN0JwpwMzMyCihkcDMzMwpTJ2h0dHBvbmx5JwpwMzM0Ck5zc1MndmVyc2lvbicKcDMzNQpJMApzUydwb3J0X3NwZWNpZmllZCcKcDMzNgpJMDAKc1MncmZjMjEwOScKcDMzNwpJMDAKc1MnZGlzY2FyZCcKcDMzOApJMDEKc1MncGF0aF9zcGVjaWZpZWQnCnAzMzkKSTAxCnNTJ3BhdGgnCnAzNDAKZzMxOQpzUydwb3J0JwpwMzQxCk5zUydjb21tZW50X3VybCcKcDM0MgpOc1Mnc2VjdXJlJwpwMzQzCkkwMApzYnNzc3Nic1Mnc3RyZWFtJwpwMzQ0CkkwMApzUydob29rcycKcDM0NQooZHAzNDYKUydyZXNwb25zZScKcDM0NwoobHAzNDgKc3NTJ2F1dGgnCnAzNDkKTnNTJ3RydXN0X2VudicKcDM1MApJMDEKc1MnaGVhZGVycycKcDM1MQpnMAooY3JlcXVlc3RzLnN0cnVjdHVyZXMKQ2FzZUluc2Vuc2l0aXZlRGljdApwMzUyCmcyCk50cDM1MwpScDM1NAooZHAzNTUKUydfc3RvcmUnCnAzNTYKKGRwMzU3ClMnYWNjZXB0LWVuY29kaW5nJwpwMzU4CihTJ0FjY2VwdC1FbmNvZGluZycKcDM1OQpTJ2d6aXAsIGRlZmxhdGUsIGNvbXByZXNzJwpwMzYwCnRwMzYxCnNTJ2FjY2VwdCcKcDM2MgooUydBY2NlcHQnCnAzNjMKUycqLyonCnAzNjQKdHAzNjUKc1MndXNlci1hZ2VudCcKcDM2NgooUydVc2VyLUFnZW50JwpwMzY3ClMncHl0aG9uLXJlcXVlc3RzLzIuMC4wIENQeXRob24vMi43LjUgRGFyd2luLzEzLjAuMCcKcDM2OAp0cDM2OQpzc2JzUydjZXJ0JwpwMzcwCk5zUydwYXJhbXMnCnAzNzEKKGRwMzcyCnNTJ3ByZWZldGNoJwpwMzczCk5zUyd0aW1lb3V0JwpwMzc0Ck5zUyd2ZXJpZnknCnAzNzUKSTAxCnNTJ3Byb3hpZXMnCnAzNzYKKGRwMzc3CnNTJ2FkYXB0ZXJzJwpwMzc4CmNyZXF1ZXN0cy5wYWNrYWdlcy51cmxsaWIzLnBhY2thZ2VzLm9yZGVyZWRfZGljdApPcmRlcmVkRGljdApwMzc5CigobHAzODAKKGxwMzgxClMnaHR0cHM6Ly8nCnAzODIKYWcwCihjcmVxdWVzdHMuYWRhcHRlcnMKSFRUUEFkYXB0ZXIKcDM4MwpnMgpOdHAzODQKUnAzODUKKGRwMzg2ClMnX3Bvb2xfYmxvY2snCnAzODcKSTAwCnNTJ19wb29sX21heHNpemUnCnAzODgKSTEwCnNTJ21heF9yZXRyaWVzJwpwMzg5CkkwCnNTJ2NvbmZpZycKcDM5MAooZHAzOTEKc1MnX3Bvb2xfY29ubmVjdGlvbnMnCnAzOTIKSTEwCnNiYWEobHAzOTMKUydodHRwOi8vJwpwMzk0CmFnMAooZzM4MwpnMgpOdHAzOTUKUnAzOTYKKGRwMzk3CmczODcKSTAwCnNnMzg4CkkxMApzZzM4OQpJMApzZzM5MAooZHAzOTgKc2czOTIKSTEwCnNiYWF0cDM5OQpScDQwMApzUydtYXhfcmVkaXJlY3RzJwpwNDAxCkkzMApzYnNTJ2F1dGhvcml6ZWQnCnA0MDIKSTAxCnNTJ3NlcnZlcnBhdGhfaGlzdG9yeScKcDQwMwpnOQooKGxwNDA0CihTJy9zbWFsbHRlc3QnCnA0MDUKUycyMWQ4ZWFiNDJmMWNjMmUyOGQ1NjhjYzA5NzUwYWRhNTkwNDAwOTg5JwpwNDA2CnRwNDA3CmEoUycvYWxsX3R5cGVzL2ZvbzIvYmFyJwpwNDA4ClMnYWE3NjNmNWEyMDRhZmQ1ZWRjMTBhNzI0MzMwNDBkOWUyYzI5MGYyYycKcDQwOQp0cDQxMAphKFMnL2FsbF90eXBlcy9mb28yJwpwNDExClMnNTQxNTVhMjQ1YWIwZDViMjg3MmJkNjA3ZDUzM2ViZTg4ODI4ZTNmMCcKcDQxMgp0cDQxMwphKFMnL2FsbF90eXBlcycKcDQxNApTJ2RjNDAwOTQ0YjA5OWU4YjNjYTFkNDIxZTQ4MjY2MzM4MmNjODgzYzknCnA0MTUKdHA0MTYKYShTJy9hbGxfdHlwZXMvZm9vJwpwNDE3ClMnNDc1MGQ4Y2Q5Mjc3YzIyODZhOTNkMTQ4Mzc1Y2QzNDQwYTg2ZjhhNicKcDQxOAp0cDQxOQphdHA0MjAKUnA0MjEKc3NiLg=="))
        localindex = pickle.loads(base64.decodestring("KGRwMApTJ2ZpbGVzdGF0cycKcDEKKGRwMgpzUydkaXJuYW1lcycKcDMKKGRwNApTJ2RhMzlhM2VlNWU2YjRiMGQzMjU1YmZlZjk1NjAxODkwYWZkODA3MDknCnA1CihkcDYKUyduYW1lc2hhc2gnCnA3ClMnZTFkYmE3NDQzMGQ1MGE0N2IyNTI1ZDI5ZTdjODBlMGY0NDExNTBmMycKcDgKc1MnZGlybmFtZScKcDkKUycvVXNlcnMvcmFic2hha2VoL3dvcmtzcGFjZS9jcnlwdG9ib3gvY3J5cHRvYm94X2FwcC9zb3VyY2UvY29tbWFuZHMvdGVzdGRhdGEvdGVzdG1hcCcKcDEwCnNTJ2ZpbGVuYW1lcycKcDExCihscDEyCihkcDEzClMnbmFtZScKcDE0ClMnLkRTX1N0b3JlJwpwMTUKc2FzUydkaXJuYW1laGFzaCcKcDE2Cmc1CnNzUycyMWQ4ZWFiNDJmMWNjMmUyOGQ1NjhjYzA5NzUwYWRhNTkwNDAwOTg5JwpwMTcKKGRwMTgKZzcKUyc4MTQwNmIxYzRjYzIzY2UxMzUzZmNkYzYwMmFjYTA4Yjg5MTRkY2RiJwpwMTkKc2c5ClMnL1VzZXJzL3JhYnNoYWtlaC93b3Jrc3BhY2UvY3J5cHRvYm94L2NyeXB0b2JveF9hcHAvc291cmNlL2NvbW1hbmRzL3Rlc3RkYXRhL3Rlc3RtYXAvc21hbGx0ZXN0JwpwMjAKc2cxMQoobHAyMQooZHAyMgpnMTQKUycuRFNfU3RvcmUnCnAyMwpzYShkcDI0CmcxNApTJ3Rlc3QuY3BwJwpwMjUKc2EoZHAyNgpnMTQKUyd0ZXN0LmphdmEnCnAyNwpzYXNnMTYKZzE3CnNzcy4="))
        serverindex = pickle.loads(base64.decodestring("KGRwMApWZG9jbGlzdApwMQoobHAyCihkcDMKVmNvbnRlbnRfaGFzaF9sYXRlc3RfdGltZXN0YW1wCnA0Ck5zVmRvYwpwNQooZHA2ClZtX3BhcmVudApwNwpWCnA4CnNWbV9kYXRhX2lkCnA5Cmc4CnNWbV9wYXRoCnAxMApWLwpwMTEKc1ZtX2RhdGVfaHVtYW4KcDEyClYwOC8xMC8xMyAxMzo0NgpwMTMKc1ZtX2NyZWF0aW9uX3RpbWUKcDE0CkYxMzgxMjMyNzY1Ljk4CnNWbV9zbHVnCnAxNQpWZG9jdW1lbnRlbgpwMTYKc1Z0aW1lc3RhbXAKcDE3CkYxMzgxMjMyNzY1Ljk4CnNWbV9kYXRlX3RpbWUKcDE4CkYxMzgxMjMyNzY1OTgwLjAKc1ZtX3Nob3J0X2lkCnAxOQpWenpkaApwMjAKc1ZtX2RhdGUKcDIxCkYxMzgxMjMyNzY1Ljk4CnNWbV9zaXplCnAyMgpJMTk1NTE1CnNWbV9zbHVncGF0aApwMjMKZzExCnNWbV9vcmRlcgpwMjQKSTAKc1ZtX25vZGV0eXBlCnAyNQpWZm9sZGVyCnAyNgpzVm1fbWltZQpwMjcKVmZvbGRlcgpwMjgKc1ZtX25hbWUKcDI5ClZkb2N1bWVudGVuCnAzMApzc1Zyb290cGFyZW50CnAzMQpOc1ZfaWQKcDMyClZ6emRoCnAzMwpzVnBhcmVudApwMzQKTnNhKGRwMzUKZzQKTnNnNQooZHAzNgpnNwpWenpkaApwMzcKc2c5Cmc4CnNnMTAKVi9hbGxfdHlwZXMKcDM4CnNnMTIKVjA4LzEwLzEzIDE4OjU1CnAzOQpzZzE0CkYxMzgxMjUxMzI4LjU2MDQ2NApzZzE1ClZhbGxfdHlwZXMKcDQwCnNnMTcKRjEzODEyNTEzMjguNTYwMzI5CnNnMTgKRjEzODEyNTEzMjg1NjAuMzI4OQpzZzE5ClZud2pqCnA0MQpzZzIxCkYxMzgxMjUxMzI4LjU2MDMyOQpzZzIyCkkxOTU1MDIKc2cyMwpWL2FsbF90eXBlcwpwNDIKc2cyNApJMApzZzI1ClZmb2xkZXIKcDQzCnNnMjcKVmZvbGRlcgpwNDQKc2cyOQpWYWxsX3R5cGVzCnA0NQpzc2czMQpWbndqagpwNDYKc2czMgpWbndqagpwNDcKc2czNApWenpkaApwNDgKc2EoZHA0OQpnNApOc2c1CihkcDUwCmc3ClZud2pqCnA1MQpzZzkKZzgKc2cxMApWL2FsbF90eXBlcy9mb28yCnA1MgpzZzEyClYwOC8xMC8xMyAxODo1NQpwNTMKc2cxNApGMTM4MTI1MTMyOC41ODUwMTYKc2cxNQpWZm9vMgpwNTQKc2cxNwpGMTM4MTI1MTMyOC41ODQ5MjEKc2cxOApGMTM4MTI1MTMyODU4NC45MjEKc2cxOQpWaGt2bgpwNTUKc2cyMQpGMTM4MTI1MTMyOC41ODQ5MjEKc2cyMgpJMTA5MgpzZzIzClYvYWxsX3R5cGVzL2ZvbzIKcDU2CnNnMjQKSTAKc2cyNQpWZm9sZGVyCnA1NwpzZzI3ClZmb2xkZXIKcDU4CnNnMjkKVmZvbzIKcDU5CnNzZzMxClZud2pqCnA2MApzZzMyClZoa3ZuCnA2MQpzZzM0ClZud2pqCnA2MgpzYShkcDYzCmc0Ck5zZzUKKGRwNjQKZzcKVmhrdm4KcDY1CnNnOQpnOApzZzEwClYvYWxsX3R5cGVzL2ZvbzIvYmFyCnA2NgpzZzEyClYwOC8xMC8xMyAxODo1NQpwNjcKc2cxNApGMTM4MTI1MTMyOC41ODU0MTYKc2cxNQpWYmFyCnA2OApzZzE3CkYxMzgxMjUxMzI4LjU4NTM0NgpzZzE4CkYxMzgxMjUxMzI4NTg1LjM0NgpzZzE5ClZjZ3pqCnA2OQpzZzIxCkYxMzgxMjUxMzI4LjU4NTM0NgpzZzIyCkk1NDYKc2cyMwpWL2FsbF90eXBlcy9mb28yL2JhcgpwNzAKc2cyNApJMApzZzI1ClZmb2xkZXIKcDcxCnNnMjcKVmZvbGRlcgpwNzIKc2cyOQpWYmFyCnA3Mwpzc2czMQpWbndqagpwNzQKc2czMgpWY2d6agpwNzUKc2czNApWaGt2bgpwNzYKc2EoZHA3NwpnNAoobHA3OApWMWNhMjRkMjNhY2QzNDBlNWVmOWM4YmYxZjY1Y2FhNGNjMTk3ZDkwNApwNzkKYUYxMzgxMjUxMzM5LjIxNjYxMwphc2c1CihkcDgwCmc3ClZjZ3pqCnA4MQpzZzkKVmNyeXB0b19kb2NfYzgzNzExN2NiYzQ4NDQwMWIxZWRhNjAyOGVjNzM0ZmUKcDgyCnNnMTAKVi9hbGxfdHlwZXMvZm9vMi9iYXIvdGVzdDMudHh0CnA4MwpzZzEyClYwOC8xMC8xMyAxODo1NQpwODQKc2cxNApGMTM4MTI1MTMzOC4xNjU4MTgKc2cxNQpWdGVzdDN0eHQKcDg1CnNnMTcKRjEzODEyNTEzMzkuMjE2NjEzCnNnMTgKRjEzODEyNTEzMzgxNjUuNzI5CnNnMTkKVnJtcmgKcDg2CnNnMjEKRjEzODEyNTEzMzguMTY1NzI5CnNnMjIKSTU0NgpzZzIzClYvYWxsX3R5cGVzL2ZvbzIvYmFyL3Rlc3QzdHh0CnA4NwpzZzI0CkkwCnNnMjUKVmZpbGUKcDg4CnNnMjcKVnRleHQvcGxhaW4KcDg5CnNnMjkKVnRlc3QzLnR4dApwOTAKc3NnMzEKVm53amoKcDkxCnNnMzIKVnJtcmgKcDkyCnNnMzQKVmNnemoKcDkzCnNhKGRwOTQKZzQKKGxwOTUKVjFjYTI0ZDIzYWNkMzQwZTVlZjljOGJmMWY2NWNhYTRjYzE5N2Q5MDQKcDk2CmFGMTM4MTI1MTMzNi43NzU3OTEKYXNnNQooZHA5NwpnNwpWaGt2bgpwOTgKc2c5ClZjcnlwdG9fZG9jXzllZWE3ZDllNGYzNTRkNWVhN2I1NzU3MmZlZjNjMjI0CnA5OQpzZzEwClYvYWxsX3R5cGVzL2ZvbzIvdGVzdDIudHh0CnAxMDAKc2cxMgpWMDgvMTAvMTMgMTg6NTUKcDEwMQpzZzE0CkYxMzgxMjUxMzM1LjQ3OTg2OQpzZzE1ClZ0ZXN0MnR4dApwMTAyCnNnMTcKRjEzODEyNTEzMzYuNzc1NzkxCnNnMTgKRjEzODEyNTEzMzU0NzkuNjgwMgpzZzE5ClZ2d2R2CnAxMDMKc2cyMQpGMTM4MTI1MTMzNS40Nzk2OApzZzIyCkk1NDYKc2cyMwpWL2FsbF90eXBlcy9mb28yL3Rlc3QydHh0CnAxMDQKc2cyNApJMQpzZzI1ClZmaWxlCnAxMDUKc2cyNwpWdGV4dC9wbGFpbgpwMTA2CnNnMjkKVnRlc3QyLnR4dApwMTA3CnNzZzMxClZud2pqCnAxMDgKc2czMgpWdndkdgpwMTA5CnNnMzQKVmhrdm4KcDExMApzYShkcDExMQpnNApOc2c1CihkcDExMgpnNwpWbndqagpwMTEzCnNnOQpnOApzZzEwClYvYWxsX3R5cGVzL2ZvbwpwMTE0CnNnMTIKVjA4LzEwLzEzIDE4OjU1CnAxMTUKc2cxNApGMTM4MTI1MTMyOC42MzQyNTYKc2cxNQpWZm9vCnAxMTYKc2cxNwpGMTM4MTI1MTMyOC42MzQxNDgKc2cxOApGMTM4MTI1MTMyODYzNC4xNDgKc2cxOQpWYnNwdApwMTE3CnNnMjEKRjEzODEyNTEzMjguNjM0MTQ4CnNnMjIKSTU0NgpzZzIzClYvYWxsX3R5cGVzL2ZvbwpwMTE4CnNnMjQKSTEKc2cyNQpWZm9sZGVyCnAxMTkKc2cyNwpWZm9sZGVyCnAxMjAKc2cyOQpWZm9vCnAxMjEKc3NnMzEKVm53amoKcDEyMgpzZzMyClZic3B0CnAxMjMKc2czNApWbndqagpwMTI0CnNhKGRwMTI1Cmc0CihscDEyNgpWMWNhMjRkMjNhY2QzNDBlNWVmOWM4YmYxZjY1Y2FhNGNjMTk3ZDkwNApwMTI3CmFGMTM4MTI1MTMzMS45MzkyMDQKYXNnNQooZHAxMjgKZzcKVmJzcHQKcDEyOQpzZzkKVmNyeXB0b19kb2NfOTNjMmE4ZDUwMjYzNGQ3N2I1NzdiNjQzMjgyMGExM2IKcDEzMApzZzEwClYvYWxsX3R5cGVzL2Zvby90ZXN0LnR4dApwMTMxCnNnMTIKVjA4LzEwLzEzIDE4OjU1CnAxMzIKc2cxNApGMTM4MTI1MTMzMS4xMDI1OApzZzE1ClZ0ZXN0dHh0CnAxMzMKc2cxNwpGMTM4MTI1MTMzMS45MzkyMDQKc2cxOApGMTM4MTI1MTMzMTEwMi40OTMyCnNnMTkKVmJxcnIKcDEzNApzZzIxCkYxMzgxMjUxMzMxLjEwMjQ5MwpzZzIyCkk1NDYKc2cyMwpWL2FsbF90eXBlcy9mb28vdGVzdHR4dApwMTM1CnNnMjQKSTAKc2cyNQpWZmlsZQpwMTM2CnNnMjcKVnRleHQvcGxhaW4KcDEzNwpzZzI5ClZ0ZXN0LnR4dApwMTM4CnNzZzMxClZud2pqCnAxMzkKc2czMgpWYnFycgpwMTQwCnNnMzQKVmJzcHQKcDE0MQpzYShkcDE0MgpnNAoobHAxNDMKVjk3ZWNmMjE4NDM4NDIxMTk3NjE5NWFlYTc2MWE2YmY5Mzc0ZGY3ZGQKcDE0NAphRjEzODEyNTEzMzMuMDU0NzE3CmFzZzUKKGRwMTQ1Cmc3ClZud2pqCnAxNDYKc2c5ClZjcnlwdG9fZG9jX2NhOTZjYWJlMWU4OTRjZThhZTQ3NjhmY2E0YmI3NjFlCnAxNDcKc2cxMApWL2FsbF90eXBlcy9kb2N1bWVudC5wZGYKcDE0OApzZzEyClYwOC8xMC8xMyAxODo1NQpwMTQ5CnNnMTQKRjEzODEyNTEzMzEuOTk0NTA5CnNnMTUKVmRvY3VtZW50cGRmCnAxNTAKc2cxNwpGMTM4MTI1MTMzMy4wNTQ3MTcKc2cxOApGMTM4MTI1MTMzMTk5NC4zOTYKc2cxOQpWZHBmZApwMTUxCnNnMjEKRjEzODEyNTEzMzEuOTk0Mzk2CnNnMjIKSTQ4Mzg5CnNnMjMKVi9hbGxfdHlwZXMvZG9jdW1lbnRwZGYKcDE1MgpzZzI0CkkyCnNnMjUKVmZpbGUKcDE1MwpzZzI3ClZhcHBsaWNhdGlvbi9wZGYKcDE1NApzZzI5ClZkb2N1bWVudC5wZGYKcDE1NQpzc2czMQpWbndqagpwMTU2CnNnMzIKVmRwZmQKcDE1NwpzZzM0ClZud2pqCnAxNTgKc2EoZHAxNTkKZzQKKGxwMTYwClY0YmRmZDdmNTY2ODEzMTY1OWZmYjIzNTg3MzJhMmRiYmM4YmM2MTMwCnAxNjEKYUYxMzgxMjUxMzM0LjI4NDMxOAphc2c1CihkcDE2MgpnNwpWbndqagpwMTYzCnNnOQpWY3J5cHRvX2RvY19hM2E0MzgwNGI2ZjI0ZjRlOWYyOTU5NDQ0ZWYwZjk5ZgpwMTY0CnNnMTAKVi9hbGxfdHlwZXMvYm1wdGVzdC5wbmcKcDE2NQpzZzEyClYwOC8xMC8xMyAxODo1NQpwMTY2CnNnMTQKRjEzODEyNTEzMzMuMTE4MzIKc2cxNQpWYm1wdGVzdHBuZwpwMTY3CnNnMTcKRjEzODEyNTEzMzQuMjg0MzE4CnNnMTgKRjEzODEyNTEzMzMxMTguMTI2CnNnMTkKVmtoa3MKcDE2OApzZzIxCkYxMzgxMjUxMzMzLjExODEyNgpzZzIyCkkxMTkyNDMKc2cyMwpWL2FsbF90eXBlcy9ibXB0ZXN0cG5nCnAxNjkKc2cyNApJMwpzZzI1ClZmaWxlCnAxNzAKc2cyNwpWaW1hZ2UvcG5nCnAxNzEKc2cyOQpWYm1wdGVzdC5wbmcKcDE3Mgpzc2czMQpWbndqagpwMTczCnNnMzIKVmtoa3MKcDE3NApzZzM0ClZud2pqCnAxNzUKc2EoZHAxNzYKZzQKKGxwMTc3ClY1Y2ZiNDkyODI4YzE5ZWEzZDJkNjQyZDg1MWI1Y2U2NzE5NzliMDdlCnAxNzgKYUYxMzgxMjUxMzM1LjQ2NjQ3OQphc2c1CihkcDE3OQpnNwpWbndqagpwMTgwCnNnOQpWY3J5cHRvX2RvY18zNjcxOWVmZjRkYTM0ZmM4YjIyN2I1ZWYwMGQyMjNiYgpwMTgxCnNnMTAKVi9hbGxfdHlwZXMvd29yZC5kb2N4CnAxODIKc2cxMgpWMDgvMTAvMTMgMTg6NTUKcDE4MwpzZzE0CkYxMzgxMjUxMzM0LjMyMzE3MgpzZzE1ClZ3b3JkZG9jeApwMTg0CnNnMTcKRjEzODEyNTEzMzUuNDY2NDc5CnNnMTgKRjEzODEyNTEzMzQzMjMuMDIyCnNnMTkKVnNjZ2oKcDE4NQpzZzIxCkYxMzgxMjUxMzM0LjMyMzAyMgpzZzIyCkkyNjIzMgpzZzIzClYvYWxsX3R5cGVzL3dvcmRkb2N4CnAxODYKc2cyNApJNApzZzI1ClZmaWxlCnAxODcKc2cyNwpWYXBwbGljYXRpb24vdm5kLm9wZW54bWxmb3JtYXRzLW9mZmljZWRvY3VtZW50LndvcmRwcm9jZXNzaW5nbWwuZG9jdW1lbnQKcDE4OApzZzI5ClZ3b3JkLmRvY3gKcDE4OQpzc2czMQpWbndqagpwMTkwCnNnMzIKVnNjZ2oKcDE5MQpzZzM0ClZud2pqCnAxOTIKc2EoZHAxOTMKZzQKTnNnNQooZHAxOTQKZzcKVnp6ZGgKcDE5NQpzZzkKZzgKc2cxMApWL3NtYWxsdGVzdApwMTk2CnNnMTIKVjA4LzEwLzEzIDE4OjU1CnAxOTcKc2cxNApGMTM4MTI1MTMyOS41ODAwNjUKc2cxNQpWc21hbGx0ZXN0CnAxOTgKc2cxNwpGMTM4MTI1MTMyOS41Nzk5NzMKc2cxOApGMTM4MTI1MTMyOTU3OS45NzMKc2cxOQpWaHBtYgpwMTk5CnNnMjEKRjEzODEyNTEzMjkuNTc5OTczCnNnMjIKSTEzCnNnMjMKVi9zbWFsbHRlc3QKcDIwMApzZzI0CkkxCnNnMjUKVmZvbGRlcgpwMjAxCnNnMjcKVmZvbGRlcgpwMjAyCnNnMjkKVnNtYWxsdGVzdApwMjAzCnNzZzMxClZocG1iCnAyMDQKc2czMgpWaHBtYgpwMjA1CnNnMzQKVnp6ZGgKcDIwNgpzYShkcDIwNwpnNAoobHAyMDgKVmM2NzMxZDhmNDZlMTg1M2Q0YjA2ZTZmYWYwNTVkZmQ0MDMzMmQzZjMKcDIwOQphRjEzODEyNTEzMzAuNjA4CmFzZzUKKGRwMjEwCmc3ClZocG1iCnAyMTEKc2c5ClZjcnlwdG9fZG9jXzFiZDZmNjhjMDQxZDRkMDk5MTc5YTBkODdjZGZjZjMyCnAyMTIKc2cxMApWL3NtYWxsdGVzdC90ZXN0LmphdmEKcDIxMwpzZzEyClYwOC8xMC8xMyAxODo1NQpwMjE0CnNnMTQKRjEzODEyNTEzMjkuNTgwNjA5CnNnMTUKVnRlc3RqYXZhCnAyMTUKc2cxNwpGMTM4MTI1MTMzMC42MDgKc2cxOApGMTM4MTI1MTMyOTU4MC41MzgKc2cxOQpWem16cQpwMjE2CnNnMjEKRjEzODEyNTEzMjkuNTgwNTM4CnNnMjIKSTkKc2cyMwpWL3NtYWxsdGVzdC90ZXN0amF2YQpwMjE3CnNnMjQKSTAKc2cyNQpWZmlsZQpwMjE4CnNnMjcKVnRleHQveC1qYXZhLXNvdXJjZQpwMjE5CnNnMjkKVnRlc3QuamF2YQpwMjIwCnNzZzMxClZocG1iCnAyMjEKc2czMgpWem16cQpwMjIyCnNnMzQKVmhwbWIKcDIyMwpzYShkcDIyNApnNAoobHAyMjUKVjMwZDc0ZDI1ODQ0MmM3YzY1NTEyZWFmYWI0NzQ1NjhkZDcwNmM0MzAKcDIyNgphRjEzODEyNTEzMzguMzI3OTM4CmFzZzUKKGRwMjI3Cmc3ClZocG1iCnAyMjgKc2c5ClZjcnlwdG9fZG9jXzFlZmE0ZWQxMjMwYTQ5MDJhNWIzYmYxODZkYzgyZmUwCnAyMjkKc2cxMApWL3NtYWxsdGVzdC90ZXN0LmNwcApwMjMwCnNnMTIKVjA4LzEwLzEzIDE4OjU1CnAyMzEKc2cxNApGMTM4MTI1MTMzNy4yODcxMzYKc2cxNQpWdGVzdGNwcApwMjMyCnNnMTcKRjEzODEyNTEzMzguMzI3OTM4CnNnMTgKRjEzODEyNTEzMzcyODcuMDQ2CnNnMTkKVnp0ZGsKcDIzMwpzZzIxCkYxMzgxMjUxMzM3LjI4NzA0NgpzZzIyCkk0CnNnMjMKVi9zbWFsbHRlc3QvdGVzdGNwcApwMjM0CnNnMjQKSTEKc2cyNQpWZmlsZQpwMjM1CnNnMjcKVnRleHQveC1jCnAyMzYKc2cyOQpWdGVzdC5jcHAKcDIzNwpzc2czMQpWaHBtYgpwMjM4CnNnMzIKVnp0ZGsKcDIzOQpzZzM0ClZocG1iCnAyNDAKc2FzUydkaXJsaXN0JwpwMjQxCihscDI0MgpnMTEKYVYvYWxsX3R5cGVzL2ZvbzIKcDI0MwphVi9hbGxfdHlwZXMKcDI0NAphVi9hbGxfdHlwZXMvZm9vCnAyNDUKYVYvc21hbGx0ZXN0CnAyNDYKYVYvYWxsX3R5cGVzL2ZvbzIvYmFyCnAyNDcKYXNWdHJlZV90aW1lc3RhbXAKcDI0OApGMTM4MTI1MTMzOS4zNjgxOTMKcy4="))

        cbmemory, cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(memory, cboptions, localindex, serverindex)
        self.assertEqual(len(file_uploads), 3)

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

        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)

        self.unzip_testfiles_clean()
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)
        self.assertEqual(len(file_uploads), 3)
        self.assertEqual(len(dir_del_local), 0)
        self.assertEqual(len(dir_make_server), 1)

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
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)
        self.assertEqual(len(dir_del_server), 0)
        self.assertEqual(len(dir_make_local), 3)
        self.assertEqual(len(file_downloads), 5)


if __name__ == '__main__':
    unittest.main()

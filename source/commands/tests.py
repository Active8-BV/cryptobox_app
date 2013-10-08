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

        memory = cPickle.loads(base64.decodestring(
            "Y2NvcHlfcmVnCl9yZWNvbnN0cnVjdG9yCnAxCihjY2JhX3V0aWxzCk1lbW9yeQpwMgpjX19idWlsdGluX18Kb2JqZWN0CnAzCk50UnA0CihkcDUKUydkYXRhJwpwNgooZHA3ClMnbG9jYWxwYXRoX2hpc3RvcnknCnA4CmNfX2J1aWx0aW5fXwpzZXQKcDkKKChscDEwCihTJy9hbGxfdHlwZXMvZG9jdW1lbnQucGRmJwpTJ2U3YmRlOTU1MGQ5NjRmMDg4NTVkYjZjYTUzMDliNGFhMTQ4YzJiNmUnCnRwMTEKYShTJy9hbGxfdHlwZXMvYm1wdGVzdC5wbmcnClMnNGJkZGU5YWEwZTc0Zjg0ZWE2MGZjODU1MzQ1Yjg0ODA2ODU3M2JhNCcKdHAxMgphKFMnL2FsbF90eXBlcy9mb28vdGVzdC50eHQnClMnYTQzNjMwNTdhN2I1NDdhMWU3MmI4ZDY5Yzg2MzY1ZjgwYTczZDIzNicKdHAxMwphKFMnL3NtYWxsdGVzdC90ZXN0LmNwcCcKUydiYWYyODljNGE1MTE5ZGM1NzYzNjNhNmFiOWM5NTE1YTkwNmQ1ODU2Jwp0cDE0CmEoUycvYWxsX3R5cGVzL2ZvbzIvYmFyL3Rlc3QzLnR4dCcKUydkOTc2YjRjMGRjZmE4NDYxOGI5NWJhMDQ1OWY3NGE0ZDQyNDE0MTBjJwp0cDE1CmEoUycvc21hbGx0ZXN0L3Rlc3QuamF2YScKUyc1YTVhYzc3MDNmZmViYjE4YjcxMDlkNTg5YTc1ZmExYWQzNTljNGFjJwp0cDE2CmEoUycvYWxsX3R5cGVzL2ZvbzIvdGVzdDIudHh0JwpTJzJlM2Q4MGU2ZTJjMDNhZDA0OGMxMDk0ODhmZjUxN2FhZDY5NDIwNWMnCnRwMTcKYShTJy9hbGxfdHlwZXMvd29yZC5kb2N4JwpTJzdkNzJkMzk2OTMzOWJlZWRkNDg4YzMzNGZlYjQ4ZTA4M2E1MDY2ZGInCnRwMTgKYXRScDE5CnNTJ2NyeXB0b2JveF9mb2xkZXInCnAyMApTJy9Vc2Vycy9yYWJzaGFrZWgvd29ya3NwYWNlL2NyeXB0b2JveC9jcnlwdG9ib3hfYXBwL3NvdXJjZS9jb21tYW5kcy90ZXN0ZGF0YS90ZXN0bWFwJwpwMjEKc1Mnc2VydmVyaW5kZXgnCnAyMgooZHAyMwpWZG9jbGlzdApwMjQKKGxwMjUKKGRwMjYKVmNvbnRlbnRfaGFzaF9sYXRlc3RfdGltZXN0YW1wCnAyNwpOc1Zkb2MKcDI4CihkcDI5ClZtX3BhcmVudApwMzAKVgpzVm1fZGF0YV9pZApwMzEKVgpzVm1fcGF0aApwMzIKVi8Kc1ZtX2RhdGVfaHVtYW4KcDMzClYwOC8xMC8xMyAxMzo0NgpwMzQKc1ZtX2NyZWF0aW9uX3RpbWUKcDM1CkYxMzgxMjMyNzY1Ljk4CnNWbV9zbHVnCnAzNgpWZG9jdW1lbnRlbgpwMzcKc1Z0aW1lc3RhbXAKcDM4CkYxMzgxMjMyNzY1Ljk4CnNWbV9kYXRlX3RpbWUKcDM5CkYxMzgxMjMyNzY1OTgwCnNWbV9zaG9ydF9pZApwNDAKVnp6ZGgKcDQxCnNWbV9kYXRlCnA0MgpGMTM4MTIzMjc2NS45OApzVm1fc2l6ZQpwNDMKSTE5NTUxNQpzVm1fc2x1Z3BhdGgKcDQ0ClYvCnNWbV9vcmRlcgpwNDUKSTAKc1ZtX25vZGV0eXBlCnA0NgpWZm9sZGVyCnA0NwpzVm1fbWltZQpwNDgKVmZvbGRlcgpwNDkKc1ZtX25hbWUKcDUwClZkb2N1bWVudGVuCnA1MQpzc1Zyb290cGFyZW50CnA1MgpOc1ZfaWQKcDUzClZ6emRoCnA1NApzVnBhcmVudApwNTUKTnNhKGRwNTYKZzI3Ck5zZzI4CihkcDU3CmczMApWenpkaApwNTgKc2czMQpWCnNnMzIKVi9hbGxfdHlwZXMKcDU5CnNnMzMKVjA4LzEwLzEzIDE5OjE2CnA2MApzZzM1CkYxMzgxMjUyNTgxLjMzNzg4OQpzZzM2ClZhbGxfdHlwZXMKcDYxCnNnMzgKRjEzODEyNTI1ODEuMzM3ODAyOQpzZzM5CkYxMzgxMjUyNTgxMzM3LjgwMwpzZzQwClZia3R6CnA2MgpzZzQyCkYxMzgxMjUyNTgxLjMzNzgwMjkKc2c0MwpJMTk1NTAyCnNnNDQKVi9hbGxfdHlwZXMKcDYzCnNnNDUKSTAKc2c0NgpWZm9sZGVyCnA2NApzZzQ4ClZmb2xkZXIKcDY1CnNnNTAKVmFsbF90eXBlcwpwNjYKc3NnNTIKVmJrdHoKcDY3CnNnNTMKVmJrdHoKcDY4CnNnNTUKVnp6ZGgKcDY5CnNhKGRwNzAKZzI3Ck5zZzI4CihkcDcxCmczMApWYmt0egpwNzIKc2czMQpWCnNnMzIKVi9hbGxfdHlwZXMvZm9vMgpwNzMKc2czMwpWMDgvMTAvMTMgMTk6MTYKcDc0CnNnMzUKRjEzODEyNTI1ODEuMzY3MDA2MQpzZzM2ClZmb28yCnA3NQpzZzM4CkYxMzgxMjUyNTgxLjM2NjkwNApzZzM5CkYxMzgxMjUyNTgxMzY2LjkwNDEKc2c0MApWZnNyYwpwNzYKc2c0MgpGMTM4MTI1MjU4MS4zNjY5MDQKc2c0MwpJMTA5MgpzZzQ0ClYvYWxsX3R5cGVzL2ZvbzIKcDc3CnNnNDUKSTAKc2c0NgpWZm9sZGVyCnA3OApzZzQ4ClZmb2xkZXIKcDc5CnNnNTAKVmZvbzIKcDgwCnNzZzUyClZia3R6CnA4MQpzZzUzClZmc3JjCnA4MgpzZzU1ClZia3R6CnA4MwpzYShkcDg0CmcyNwpOc2cyOAooZHA4NQpnMzAKVmZzcmMKcDg2CnNnMzEKVgpzZzMyClYvYWxsX3R5cGVzL2ZvbzIvYmFyCnA4NwpzZzMzClYwOC8xMC8xMyAxOToxNgpwODgKc2czNQpGMTM4MTI1MjU4MS4zNjc2NDEKc2czNgpWYmFyCnA4OQpzZzM4CkYxMzgxMjUyNTgxLjM2NzUxNTEKc2czOQpGMTM4MTI1MjU4MTM2Ny41MTUxCnNnNDAKVmJ6cHAKcDkwCnNnNDIKRjEzODEyNTI1ODEuMzY3NTE1MQpzZzQzCkk1NDYKc2c0NApWL2FsbF90eXBlcy9mb28yL2JhcgpwOTEKc2c0NQpJMApzZzQ2ClZmb2xkZXIKcDkyCnNnNDgKVmZvbGRlcgpwOTMKc2c1MApWYmFyCnA5NApzc2c1MgpWYmt0egpwOTUKc2c1MwpWYnpwcApwOTYKc2c1NQpWZnNyYwpwOTcKc2EoZHA5OApnMjcKKGxwOTkKVjFjYTI0ZDIzYWNkMzQwZTVlZjljOGJmMWY2NWNhYTRjYzE5N2Q5MDQKcDEwMAphRjEzODEyNTI1OTMuOTA0NTgzCmFzZzI4CihkcDEwMQpnMzAKVmJ6cHAKcDEwMgpzZzMxClZjcnlwdG9fZG9jX2UzYjg1NzJjNDUyMjRjY2Y4NWYwOGZmM2U1Mjg3M2Y3CnAxMDMKc2czMgpWL2FsbF90eXBlcy9mb28yL2Jhci90ZXN0My50eHQKcDEwNApzZzMzClYwOC8xMC8xMyAxOToxNgpwMTA1CnNnMzUKRjEzODEyNTI1OTMuMDMxNTA4CnNnMzYKVnRlc3QzdHh0CnAxMDYKc2czOApGMTM4MTI1MjU5My45MDQ1ODMKc2czOQpGMTM4MTI1MjU5MzAzMS40MTMxCnNnNDAKVnRxcGIKcDEwNwpzZzQyCkYxMzgxMjUyNTkzLjAzMTQxMzEKc2c0MwpJNTQ2CnNnNDQKVi9hbGxfdHlwZXMvZm9vMi9iYXIvdGVzdDN0eHQKcDEwOApzZzQ1CkkwCnNnNDYKVmZpbGUKcDEwOQpzZzQ4ClZ0ZXh0L3BsYWluCnAxMTAKc2c1MApWdGVzdDMudHh0CnAxMTEKc3NnNTIKVmJrdHoKcDExMgpzZzUzClZ0cXBiCnAxMTMKc2c1NQpWYnpwcApwMTE0CnNhKGRwMTE1CmcyNwoobHAxMTYKVjFjYTI0ZDIzYWNkMzQwZTVlZjljOGJmMWY2NWNhYTRjYzE5N2Q5MDQKcDExNwphRjEzODEyNTI1OTAuMTg4NzYxCmFzZzI4CihkcDExOApnMzAKVmZzcmMKcDExOQpzZzMxClZjcnlwdG9fZG9jXzA3MTVlM2RiYTNkNDRmNzBhN2M3ZTJhNWExOWNjNTE5CnAxMjAKc2czMgpWL2FsbF90eXBlcy9mb28yL3Rlc3QyLnR4dApwMTIxCnNnMzMKVjA4LzEwLzEzIDE5OjE2CnAxMjIKc2czNQpGMTM4MTI1MjU4OS4wNDY3MTYKc2czNgpWdGVzdDJ0eHQKcDEyMwpzZzM4CkYxMzgxMjUyNTkwLjE4ODc2MQpzZzM5CkYxMzgxMjUyNTg5MDQ2LjYyNzkKc2c0MApWcG5tcApwMTI0CnNnNDIKRjEzODEyNTI1ODkuMDQ2NjI4CnNnNDMKSTU0NgpzZzQ0ClYvYWxsX3R5cGVzL2ZvbzIvdGVzdDJ0eHQKcDEyNQpzZzQ1CkkxCnNnNDYKVmZpbGUKcDEyNgpzZzQ4ClZ0ZXh0L3BsYWluCnAxMjcKc2c1MApWdGVzdDIudHh0CnAxMjgKc3NnNTIKVmJrdHoKcDEyOQpzZzUzClZwbm1wCnAxMzAKc2c1NQpWZnNyYwpwMTMxCnNhKGRwMTMyCmcyNwpOc2cyOAooZHAxMzMKZzMwClZia3R6CnAxMzQKc2czMQpWCnNnMzIKVi9hbGxfdHlwZXMvZm9vCnAxMzUKc2czMwpWMDgvMTAvMTMgMTk6MTYKcDEzNgpzZzM1CkYxMzgxMjUyNTgxLjQyMjY2MzkKc2czNgpWZm9vCnAxMzcKc2czOApGMTM4MTI1MjU4MS40MjI1NjMxCnNnMzkKRjEzODEyNTI1ODE0MjIuNTYzCnNnNDAKVnFqeGgKcDEzOApzZzQyCkYxMzgxMjUyNTgxLjQyMjU2MzEKc2c0MwpJNTQ2CnNnNDQKVi9hbGxfdHlwZXMvZm9vCnAxMzkKc2c0NQpJMQpzZzQ2ClZmb2xkZXIKcDE0MApzZzQ4ClZmb2xkZXIKcDE0MQpzZzUwClZmb28KcDE0Mgpzc2c1MgpWYmt0egpwMTQzCnNnNTMKVnFqeGgKcDE0NApzZzU1ClZia3R6CnAxNDUKc2EoZHAxNDYKZzI3CihscDE0NwpWMWNhMjRkMjNhY2QzNDBlNWVmOWM4YmYxZjY1Y2FhNGNjMTk3ZDkwNApwMTQ4CmFGMTM4MTI1MjU4NS42MjY2Mjc5CmFzZzI4CihkcDE0OQpnMzAKVnFqeGgKcDE1MApzZzMxClZjcnlwdG9fZG9jX2Y1MjFiNDY4YzJhYjQxOGJiY2IxNjA0MzFlODc5YzIxCnAxNTEKc2czMgpWL2FsbF90eXBlcy9mb28vdGVzdC50eHQKcDE1MgpzZzMzClYwOC8xMC8xMyAxOToxNgpwMTUzCnNnMzUKRjEzODEyNTI1ODMuNTgzODAyCnNnMzYKVnRlc3R0eHQKcDE1NApzZzM4CkYxMzgxMjUyNTg1LjYyNjYyNzkKc2czOQpGMTM4MTI1MjU4MzU4My42NjQ4CnNnNDAKVmpua3IKcDE1NQpzZzQyCkYxMzgxMjUyNTgzLjU4MzY2NDkKc2c0MwpJNTQ2CnNnNDQKVi9hbGxfdHlwZXMvZm9vL3Rlc3R0eHQKcDE1NgpzZzQ1CkkwCnNnNDYKVmZpbGUKcDE1NwpzZzQ4ClZ0ZXh0L3BsYWluCnAxNTgKc2c1MApWdGVzdC50eHQKcDE1OQpzc2c1MgpWYmt0egpwMTYwCnNnNTMKVmpua3IKcDE2MQpzZzU1ClZxanhoCnAxNjIKc2EoZHAxNjMKZzI3CihscDE2NApWOTdlY2YyMTg0Mzg0MjExOTc2MTk1YWVhNzYxYTZiZjkzNzRkZjdkZApwMTY1CmFGMTM4MTI1MjU4NS44NTg5Mjg5CmFzZzI4CihkcDE2NgpnMzAKVmJrdHoKcDE2NwpzZzMxClZjcnlwdG9fZG9jXzgwY2JiZDllMzE3NDQyNDg4ZWMzYWI0NWQzNGNkZDU4CnAxNjgKc2czMgpWL2FsbF90eXBlcy9kb2N1bWVudC5wZGYKcDE2OQpzZzMzClYwOC8xMC8xMyAxOToxNgpwMTcwCnNnMzUKRjEzODEyNTI1ODQuODA1NjMzMQpzZzM2ClZkb2N1bWVudHBkZgpwMTcxCnNnMzgKRjEzODEyNTI1ODUuODU4OTI4OQpzZzM5CkYxMzgxMjUyNTg0ODA1LjU0MgpzZzQwClZnc3JmCnAxNzIKc2c0MgpGMTM4MTI1MjU4NC44MDU1NDIKc2c0MwpJNDgzODkKc2c0NApWL2FsbF90eXBlcy9kb2N1bWVudHBkZgpwMTczCnNnNDUKSTIKc2c0NgpWZmlsZQpwMTc0CnNnNDgKVmFwcGxpY2F0aW9uL3BkZgpwMTc1CnNnNTAKVmRvY3VtZW50LnBkZgpwMTc2CnNzZzUyClZia3R6CnAxNzcKc2c1MwpWZ3NyZgpwMTc4CnNnNTUKVmJrdHoKcDE3OQpzYShkcDE4MApnMjcKKGxwMTgxClY0YmRmZDdmNTY2ODEzMTY1OWZmYjIzNTg3MzJhMmRiYmM4YmM2MTMwCnAxODIKYUYxMzgxMjUyNTg3LjU5NjAyMzEKYXNnMjgKKGRwMTgzCmczMApWYmt0egpwMTg0CnNnMzEKVmNyeXB0b19kb2NfZTk2ZDUxMTI1NmFhNGRhYzkyZTdkMWU1MmUyZjVlMmYKcDE4NQpzZzMyClYvYWxsX3R5cGVzL2JtcHRlc3QucG5nCnAxODYKc2czMwpWMDgvMTAvMTMgMTk6MTYKcDE4NwpzZzM1CkYxMzgxMjUyNTg2LjYwNDY2NjkKc2czNgpWYm1wdGVzdHBuZwpwMTg4CnNnMzgKRjEzODEyNTI1ODcuNTk2MDIzMQpzZzM5CkYxMzgxMjUyNTg2NjA0LjU0NzEKc2c0MApWbXd6YgpwMTg5CnNnNDIKRjEzODEyNTI1ODYuNjA0NTQ3CnNnNDMKSTExOTI0MwpzZzQ0ClYvYWxsX3R5cGVzL2JtcHRlc3RwbmcKcDE5MApzZzQ1CkkzCnNnNDYKVmZpbGUKcDE5MQpzZzQ4ClZpbWFnZS9wbmcKcDE5MgpzZzUwClZibXB0ZXN0LnBuZwpwMTkzCnNzZzUyClZia3R6CnAxOTQKc2c1MwpWbXd6YgpwMTk1CnNnNTUKVmJrdHoKcDE5NgpzYShkcDE5NwpnMjcKKGxwMTk4ClY1Y2ZiNDkyODI4YzE5ZWEzZDJkNjQyZDg1MWI1Y2U2NzE5NzliMDdlCnAxOTkKYUYxMzgxMjUyNTg5Ljc0ODU3NzEKYXNnMjgKKGRwMjAwCmczMApWYmt0egpwMjAxCnNnMzEKVmNyeXB0b19kb2NfM2IwM2M5NGI0YTAyNDVkZGI3NmViMjU0NThhZTc2YzUKcDIwMgpzZzMyClYvYWxsX3R5cGVzL3dvcmQuZG9jeApwMjAzCnNnMzMKVjA4LzEwLzEzIDE5OjE2CnAyMDQKc2czNQpGMTM4MTI1MjU4OC4wODEyMjgKc2czNgpWd29yZGRvY3gKcDIwNQpzZzM4CkYxMzgxMjUyNTg5Ljc0ODU3NzEKc2czOQpGMTM4MTI1MjU4ODA4MS4wMzIKc2c0MApWa2JtegpwMjA2CnNnNDIKRjEzODEyNTI1ODguMDgxMDMyCnNnNDMKSTI2MjMyCnNnNDQKVi9hbGxfdHlwZXMvd29yZGRvY3gKcDIwNwpzZzQ1Ckk0CnNnNDYKVmZpbGUKcDIwOApzZzQ4ClZhcHBsaWNhdGlvbi92bmQub3BlbnhtbGZvcm1hdHMtb2ZmaWNlZG9jdW1lbnQud29yZHByb2Nlc3NpbmdtbC5kb2N1bWVudApwMjA5CnNnNTAKVndvcmQuZG9jeApwMjEwCnNzZzUyClZia3R6CnAyMTEKc2c1MwpWa2JtegpwMjEyCnNnNTUKVmJrdHoKcDIxMwpzYShkcDIxNApnMjcKTnNnMjgKKGRwMjE1CmczMApWenpkaApwMjE2CnNnMzEKVgpzZzMyClYvc21hbGx0ZXN0CnAyMTcKc2czMwpWMDgvMTAvMTMgMTk6MTYKcDIxOApzZzM1CkYxMzgxMjUyNTgyLjQxMjI4NwpzZzM2ClZzbWFsbHRlc3QKcDIxOQpzZzM4CkYxMzgxMjUyNTgyLjQxMjIwMDkKc2czOQpGMTM4MTI1MjU4MjQxMi4yMDA5CnNnNDAKVm5uZHoKcDIyMApzZzQyCkYxMzgxMjUyNTgyLjQxMjIwMDkKc2c0MwpJMTMKc2c0NApWL3NtYWxsdGVzdApwMjIxCnNnNDUKSTEKc2c0NgpWZm9sZGVyCnAyMjIKc2c0OApWZm9sZGVyCnAyMjMKc2c1MApWc21hbGx0ZXN0CnAyMjQKc3NnNTIKVm5uZHoKcDIyNQpzZzUzClZubmR6CnAyMjYKc2c1NQpWenpkaApwMjI3CnNhKGRwMjI4CmcyNwoobHAyMjkKVmM2NzMxZDhmNDZlMTg1M2Q0YjA2ZTZmYWYwNTVkZmQ0MDMzMmQzZjMKcDIzMAphRjEzODEyNTI1ODMuNzIzMTcKYXNnMjgKKGRwMjMxCmczMApWbm5kegpwMjMyCnNnMzEKVmNyeXB0b19kb2NfMGI4YjM1YTRjZjdkNDg0ZTlkNDY5YmQ3NmUzMWQ0YTMKcDIzMwpzZzMyClYvc21hbGx0ZXN0L3Rlc3QuamF2YQpwMjM0CnNnMzMKVjA4LzEwLzEzIDE5OjE2CnAyMzUKc2czNQpGMTM4MTI1MjU4Mi40MTI4MDc5CnNnMzYKVnRlc3RqYXZhCnAyMzYKc2czOApGMTM4MTI1MjU4My43MjMxNwpzZzM5CkYxMzgxMjUyNTgyNDEyLjczOQpzZzQwClZ3bXJuCnAyMzcKc2c0MgpGMTM4MTI1MjU4Mi40MTI3MzkKc2c0MwpJOQpzZzQ0ClYvc21hbGx0ZXN0L3Rlc3RqYXZhCnAyMzgKc2c0NQpJMApzZzQ2ClZmaWxlCnAyMzkKc2c0OApWdGV4dC94LWphdmEtc291cmNlCnAyNDAKc2c1MApWdGVzdC5qYXZhCnAyNDEKc3NnNTIKVm5uZHoKcDI0MgpzZzUzClZ3bXJuCnAyNDMKc2c1NQpWbm5kegpwMjQ0CnNhKGRwMjQ1CmcyNwoobHAyNDYKVjMwZDc0ZDI1ODQ0MmM3YzY1NTEyZWFmYWI0NzQ1NjhkZDcwNmM0MzAKcDI0NwphRjEzODEyNTI1OTEuNjQ1OTE2OQphc2cyOAooZHAyNDgKZzMwClZubmR6CnAyNDkKc2czMQpWY3J5cHRvX2RvY183Y2U5ODc5ZGE3Y2Q0MzE1OGJkODk0ZDAwMGU1YTNhMwpwMjUwCnNnMzIKVi9zbWFsbHRlc3QvdGVzdC5jcHAKcDI1MQpzZzMzClYwOC8xMC8xMyAxOToxNgpwMjUyCnNnMzUKRjEzODEyNTI1OTAuNjQ0NTM5MQpzZzM2ClZ0ZXN0Y3BwCnAyNTMKc2czOApGMTM4MTI1MjU5MS42NDU5MTY5CnNnMzkKRjEzODEyNTI1OTA2NDQuMzQwMQpzZzQwClZ4cmtmCnAyNTQKc2c0MgpGMTM4MTI1MjU5MC42NDQzNApzZzQzCkk0CnNnNDQKVi9zbWFsbHRlc3QvdGVzdGNwcApwMjU1CnNnNDUKSTEKc2c0NgpWZmlsZQpwMjU2CnNnNDgKVnRleHQveC1jCnAyNTcKc2c1MApWdGVzdC5jcHAKcDI1OApzc2c1MgpWbm5kegpwMjU5CnNnNTMKVnhya2YKcDI2MApzZzU1ClZubmR6CnAyNjEKc2FzUydkaXJsaXN0JwpwMjYyCihscDI2MwpWLwphVi9hbGxfdHlwZXMvZm9vMgpwMjY0CmFWL2FsbF90eXBlcwpwMjY1CmFWL2FsbF90eXBlcy9mb28KcDI2NgphVi9zbWFsbHRlc3QKcDI2NwphVi9hbGxfdHlwZXMvZm9vMi9iYXIKcDI2OAphc1Z0cmVlX3RpbWVzdGFtcApwMjY5CkYxMzgxMjUyNTk0LjA5NDcwODkKc3NTJ3Nlc3Npb24nCnAyNzAKZzEKKGNyZXF1ZXN0cy5zZXNzaW9ucwpTZXNzaW9uCnAyNzEKZzMKTnRScDI3MgooZHAyNzMKUydjb29raWVzJwpwMjc0CmcxCihjcmVxdWVzdHMuY29va2llcwpSZXF1ZXN0c0Nvb2tpZUphcgpwMjc1CmczCk50UnAyNzYKKGRwMjc3ClMnX25vdycKcDI3OApJMTM4MTI1MjU5NApzUydfcG9saWN5JwpwMjc5CihpY29va2llbGliCkRlZmF1bHRDb29raWVQb2xpY3kKcDI4MAooZHAyODEKUydzdHJpY3RfcmZjMjk2NV91bnZlcmlmaWFibGUnCnAyODIKSTAxCnNTJ3N0cmljdF9uc19kb21haW4nCnAyODMKSTAKc1MnX2FsbG93ZWRfZG9tYWlucycKcDI4NApOc1MncmZjMjEwOV9hc19uZXRzY2FwZScKcDI4NQpOc1MncmZjMjk2NScKcDI4NgpJMDAKc1Mnc3RyaWN0X2RvbWFpbicKcDI4NwpJMDAKc2cyNzgKSTEzODEyNTI1OTQKc1Mnc3RyaWN0X25zX3NldF9wYXRoJwpwMjg4CkkwMApzUydzdHJpY3RfbnNfdW52ZXJpZmlhYmxlJwpwMjg5CkkwMApzUydzdHJpY3RfbnNfc2V0X2luaXRpYWxfZG9sbGFyJwpwMjkwCkkwMApzUydoaWRlX2Nvb2tpZTInCnAyOTEKSTAwCnNTJ19ibG9ja2VkX2RvbWFpbnMnCnAyOTIKKHRzUyduZXRzY2FwZScKcDI5MwpJMDEKc2JzUydfY29va2llcycKcDI5NAooZHAyOTUKUycxMjcuMC4wMScKcDI5NgooZHAyOTcKUycvJwooZHAyOTgKUydjX3Rva2VuJwpwMjk5CihpY29va2llbGliCkNvb2tpZQpwMzAwCihkcDMwMQpTJ2NvbW1lbnQnCnAzMDIKTnNTJ2RvbWFpbicKcDMwMwpnMjk2CnNTJ25hbWUnCnAzMDQKZzI5OQpzUydkb21haW5faW5pdGlhbF9kb3QnCnAzMDUKSTAwCnNTJ2V4cGlyZXMnCnAzMDYKTnNTJ3ZhbHVlJwpwMzA3ClMnIi5lSnh0VlRmUDdBb1J2VHdRaFpfZ045d1N5UUxuaEVSaDczcWQxdGxlaC1iS09lZHNDWWtTOGF2NTNoVWwwNTdSekFuRi1kY3ZfNXgtOXhmMzEzR3U5bWpOZmpUWk5mM2lfT2VQMzc3OTliZmhlRUhTdmxzMi05MndwQV9yOE44VlB2aUpBS29rOFVNaGNTeXJQRmlUWjVmc09lQlE3bWQwX1lDdTVmVzhvQlhXZFpIaTMzZVVKeGZZVnRoT0pudW95eF8zVG1zQWFSOTNwSWJDQ3l5N0ltbnpta0tOeUkzNENwOUZETDZuMUk3c3J1enN4eENNUzZHbDVqNEljTGxHNzVOR1RkRUdBZTZ5UFNXSjVnUHU3a0k0VEZnaTNnbWtWdGlWSXBJUXI5YjRhT1VhdnM0ZVg4R2lvOFBjeGNLYjhDbl9GckxlcWdBdmdsZW1LYXc2NHhQYkVQS0tYR0pHZWhfUFJnX281V0dqYXJ0WGRCU184VmlvSnVscEtrZ2gzeWpLVVdLMXNqb0hFREFWVTRsUjF2S1gzcnFiUkd0Zm40c1llOEhVWWhkWjliMkNrM1RxMVdwNU1qUm1MdFhIRUN1YklGZWRFMTlXQU55TDI0RFFXZXQ2Zjk5MXBuR0ZsanY1YzYxbnJ3ejZ5cEtKajZtYjBwTTFXWTRkdnN6bXJBdVJWVFBWa3VGMUt4SGctcmFUUTUtd1dSLUJIVFA2RlRFRWhYa2tJdlpvc2RzdWp4Zmhzb1dQVm1mQnpSa0VyelVZOG0zWHBRS0RyRmtzd09BeGxaVWNxX3VhU2o5R01jbmR4SHU2bDVWZHE5M2U4NTE1b0dIaHhER1VNamF1bGFUaEhPY01pWDFrdC11b3lRQ2JpZ2UtclVNU0dURWQ4aFhvNmFKNklwcUR5WG5WQ0JpYUJWNV9OeC1YWGxib1laWHQwOWxkcWxjaTFpRDZXUDRBVnRsN29TUWdhM29GS0lUZXJNUlFwSndwOXg3RWtJOHlWUHNvQWprUUlNazQ1VmlOajhqZnhLZnRzX0FGeHRlckFDQ1FnbDFKXzhwd0xMdmVuY2tzMFpNeWtCWkZaU3drb0c0OElnaVVQRHg5VF9WSlhZTGIzWXRVYmFlSDM2dHVVQUFUVmMwUzFIeTk0ZG1OSkVKclRvTjM5M2hxQjQxTmpkZWF6U2hRdUlFZFlOYVAwc2JkclZXbFlQVndJeW9HalV3RzVuRTlpTVp4UUw1Z0NvWE5QWmhLbjMwLU80WjhXZ3I2bWVJZ19EU1ZaeWxCb29WVFBlNVJoaEpEYnlmdVMxeFJDTUNPYlB5QWhWRzc0c0QzQjY3YVhyRVZVaGNlUnB2YzI5M3hkRi1hN01hVXNRRjN1NmtqV252RnkwX0c5TVJfZ0Q2SkMwc3JKWEV5X0IyZjNyMUZFQXdzNlJyN3FSRlQ4aUJZb3hWRjdCTDAyTWs4RE8zbWl0VG5PWXJxdUdYUVZBS2UtSkZkekllRXB4TXFGVDZsc0NfN3hxbXM1Q3J6NnV5SWZFeEd6VWU1aDhmWHhWbVByMFR4NnpLbFVJSU1ZLVFOUEhPTHkwbXFha3JNbTlzN3lXdnZFUXg5ZU01Y2M0bmhUR256ZmNxX1VXYlJsYldSTXFOend2UENRczNKNjhZUWdPek9yY1ZIa3ZVLTY5QWJqQlBUekF5MU5PLTNoNWw4aFNJOFc4ekM2cXllSzFLdFNhYmFraVRmUGhsMDEyZDA1Y0NoaWdqY2hKTURsUW1GN2dZcWhSSkVNOUN4cjVhUXVzUnpzblA3SGU0cmZTZ25ISlM5WlZvNE1pblNZNHFPSk9BQVFlZFh4dkFvNVUyQkhqdld3LXZEMzZiQ0ZaeklKU3dvWGswSFpWVldZLW1nMUlFcnNCbDEyUU9rY2pieEN2WFhDYmhyaFFiQ213Q1pyTGZ4am8zQ0F1WHhwVWJjNFJWNEx3ZUdfSHA0YThNMWJYM3RIQzhUVmJzQjVkdUtUaFZZWWhIQURJSTBaQXR6MGxfc0NTbFZyQnBtLUdEV3FBSHpkUnFySXl6dGpCMU9YM3RveC1YS2pvY1VnNzItNU0tTXZvbU1BUGJhRGRsQllJTzVHTDJ6WDJpbW9YcDk4eXhzb1Jxd21CcVVYRjJzYmNZT1ByUHRCYUt3YlFtRHRzRGVzUGhlbFFLd01NUFhHbzBIVTRUMjJtNDU2bGF6X1g0bTIyVmdGVEhpZEJhRlYxYVhOVmI1UzhNbXpRQ1ZUam1GQTR6SFdUMEFMQnFkaXIxcmVZZk50N3p4UTlkdU5ESGVzSWZkVnJQakZHZGZfVFBXT0lyZ0xZcU1OTmI5Ql9DelVuanQtWC1yeHYzek9tX0wtaU1adW5GYnMzbjZfYl9kUHkzWnNsUkRfMk1kbXF5Zl91Q192bjM3dGppLWN3Z2xGLU4yNUNDVjNRNUY5Yi1OSHhTT1lUQ0Y1UWhEb2poRE1qUkZVRG1lNVFpV3dsUVU0My1mbzNncG95WXJ0N185RjhMNlZGUToxVlRhdFE6NWFVbEctLXB4dFEyaDdSYjN5bWNsVlBVQjBjIicKcDMwOApzUydkb21haW5fc3BlY2lmaWVkJwpwMzA5CkkwMApzUydfcmVzdCcKcDMxMAooZHAzMTEKUydodHRwb25seScKcDMxMgpOc3NTJ3ZlcnNpb24nCnAzMTMKSTAKc1MncG9ydF9zcGVjaWZpZWQnCnAzMTQKSTAwCnNTJ3JmYzIxMDknCnAzMTUKSTAwCnNTJ2Rpc2NhcmQnCnAzMTYKSTAxCnNTJ3BhdGhfc3BlY2lmaWVkJwpwMzE3CkkwMQpzUydwYXRoJwpwMzE4ClMnLycKc1MncG9ydCcKcDMxOQpOc1MnY29tbWVudF91cmwnCnAzMjAKTnNTJ3NlY3VyZScKcDMyMQpJMDAKc2Jzc3NzYnNTJ3N0cmVhbScKcDMyMgpJMDAKc1MnaG9va3MnCnAzMjMKKGRwMzI0ClMncmVzcG9uc2UnCnAzMjUKKGxwMzI2CnNzUydhdXRoJwpwMzI3Ck5zUyd0cnVzdF9lbnYnCnAzMjgKSTAxCnNTJ2hlYWRlcnMnCnAzMjkKZzEKKGNyZXF1ZXN0cy5zdHJ1Y3R1cmVzCkNhc2VJbnNlbnNpdGl2ZURpY3QKcDMzMApnMwpOdFJwMzMxCihkcDMzMgpTJ19zdG9yZScKcDMzMwooZHAzMzQKUydhY2NlcHQtZW5jb2RpbmcnCnAzMzUKKFMnQWNjZXB0LUVuY29kaW5nJwpwMzM2ClMnZ3ppcCwgZGVmbGF0ZSwgY29tcHJlc3MnCnRwMzM3CnNTJ2FjY2VwdCcKcDMzOAooUydBY2NlcHQnCnAzMzkKUycqLyonCnAzNDAKdHAzNDEKc1MndXNlci1hZ2VudCcKcDM0MgooUydVc2VyLUFnZW50JwpwMzQzClMncHl0aG9uLXJlcXVlc3RzLzIuMC4wIENQeXRob24vMi43LjUgRGFyd2luLzEzLjAuMCcKdHAzNDQKc3Nic1MnY2VydCcKcDM0NQpOc1MncGFyYW1zJwpwMzQ2CihkcDM0NwpzUydwcmVmZXRjaCcKcDM0OApOc1MndGltZW91dCcKcDM0OQpOc1MndmVyaWZ5JwpwMzUwCkkwMQpzUydwcm94aWVzJwpwMzUxCihkcDM1MgpzUydhZGFwdGVycycKcDM1MwpjcmVxdWVzdHMucGFja2FnZXMudXJsbGliMy5wYWNrYWdlcy5vcmRlcmVkX2RpY3QKT3JkZXJlZERpY3QKcDM1NAooKGxwMzU1CihscDM1NgpTJ2h0dHBzOi8vJwpwMzU3CmFnMQooY3JlcXVlc3RzLmFkYXB0ZXJzCkhUVFBBZGFwdGVyCnAzNTgKZzMKTnRScDM1OQooZHAzNjAKUydfcG9vbF9ibG9jaycKcDM2MQpJMDAKc1MnX3Bvb2xfbWF4c2l6ZScKcDM2MgpJMTAKc1MnbWF4X3JldHJpZXMnCnAzNjMKSTAKc1MnY29uZmlnJwpwMzY0CihkcDM2NQpzUydfcG9vbF9jb25uZWN0aW9ucycKcDM2NgpJMTAKc2JhYShscDM2NwpTJ2h0dHA6Ly8nCnAzNjgKYWcxCihnMzU4CmczCk50UnAzNjkKKGRwMzcwCmczNjEKSTAwCnNnMzYyCkkxMApzZzM2MwpJMApzZzM2NAooZHAzNzEKc2czNjYKSTEwCnNiYWF0UnAzNzIKc1MnbWF4X3JlZGlyZWN0cycKcDM3MwpJMzAKc2JzUydhdXRob3JpemVkJwpwMzc0CkkwMQpzUydzZXJ2ZXJwYXRoX2hpc3RvcnknCnAzNzUKZzkKKChscDM3NgooUycvc21hbGx0ZXN0JwpTJzIxZDhlYWI0MmYxY2MyZTI4ZDU2OGNjMDk3NTBhZGE1OTA0MDA5ODknCnRwMzc3CmEoUycvYWxsX3R5cGVzL2ZvbzIvYmFyJwpTJ2FhNzYzZjVhMjA0YWZkNWVkYzEwYTcyNDMzMDQwZDllMmMyOTBmMmMnCnRwMzc4CmEoUycvYWxsX3R5cGVzL2ZvbzInClMnNTQxNTVhMjQ1YWIwZDViMjg3MmJkNjA3ZDUzM2ViZTg4ODI4ZTNmMCcKdHAzNzkKYShTJy9hbGxfdHlwZXMnClMnZGM0MDA5NDRiMDk5ZThiM2NhMWQ0MjFlNDgyNjYzMzgyY2M4ODNjOScKdHAzODAKYShTJy9hbGxfdHlwZXMvZm9vJwpTJzQ3NTBkOGNkOTI3N2MyMjg2YTkzZDE0ODM3NWNkMzQ0MGE4NmY4YTYnCnRwMzgxCmF0UnAzODIKc3NiLg=="))
        localindex = cPickle.loads(base64.decodestring(
            "KGRwMQpTJ2ZpbGVzdGF0cycKcDIKKGRwMwpzUydkaXJuYW1lcycKcDQKKGRwNQpTJ2RhMzlhM2VlNWU2YjRiMGQzMjU1YmZlZjk1NjAxODkwYWZkODA3MDknCnA2CihkcDcKUyduYW1lc2hhc2gnCnA4ClMnZTFkYmE3NDQzMGQ1MGE0N2IyNTI1ZDI5ZTdjODBlMGY0NDExNTBmMycKcDkKc1MnZGlybmFtZScKcDEwClMnL1VzZXJzL3JhYnNoYWtlaC93b3Jrc3BhY2UvY3J5cHRvYm94L2NyeXB0b2JveF9hcHAvc291cmNlL2NvbW1hbmRzL3Rlc3RkYXRhL3Rlc3RtYXAnCnAxMQpzUydmaWxlbmFtZXMnCnAxMgoobHAxMwooZHAxNApTJ25hbWUnCnAxNQpTJy5EU19TdG9yZScKcDE2CnNhc1MnZGlybmFtZWhhc2gnCnAxNwpnNgpzc1MnMjFkOGVhYjQyZjFjYzJlMjhkNTY4Y2MwOTc1MGFkYTU5MDQwMDk4OScKcDE4CihkcDE5Cmc4ClMnODE0MDZiMWM0Y2MyM2NlMTM1M2ZjZGM2MDJhY2EwOGI4OTE0ZGNkYicKcDIwCnNnMTAKUycvVXNlcnMvcmFic2hha2VoL3dvcmtzcGFjZS9jcnlwdG9ib3gvY3J5cHRvYm94X2FwcC9zb3VyY2UvY29tbWFuZHMvdGVzdGRhdGEvdGVzdG1hcC9zbWFsbHRlc3QnCnAyMQpzZzEyCihscDIyCihkcDIzCmcxNQpTJy5EU19TdG9yZScKcDI0CnNhKGRwMjUKZzE1ClMndGVzdC5jcHAnCnAyNgpzYShkcDI3CmcxNQpTJ3Rlc3QuamF2YScKcDI4CnNhc2cxNwpnMTgKc3NzLg=="))
        serverindex = cPickle.loads(base64.decodestring(
            "KGRwMQpWZG9jbGlzdApwMgoobHAzCihkcDQKVmNvbnRlbnRfaGFzaF9sYXRlc3RfdGltZXN0YW1wCnA1Ck5zVmRvYwpwNgooZHA3ClZtX3BhcmVudApwOApWCnNWbV9kYXRhX2lkCnA5ClYKc1ZtX3BhdGgKcDEwClYvCnNWbV9kYXRlX2h1bWFuCnAxMQpWMDgvMTAvMTMgMTM6NDYKcDEyCnNWbV9jcmVhdGlvbl90aW1lCnAxMwpGMTM4MTIzMjc2NS45OApzVm1fc2x1ZwpwMTQKVmRvY3VtZW50ZW4KcDE1CnNWdGltZXN0YW1wCnAxNgpGMTM4MTIzMjc2NS45OApzVm1fZGF0ZV90aW1lCnAxNwpGMTM4MTIzMjc2NTk4MApzVm1fc2hvcnRfaWQKcDE4ClZ6emRoCnAxOQpzVm1fZGF0ZQpwMjAKRjEzODEyMzI3NjUuOTgKc1ZtX3NpemUKcDIxCkkxOTU1MTUKc1ZtX3NsdWdwYXRoCnAyMgpWLwpzVm1fb3JkZXIKcDIzCkkwCnNWbV9ub2RldHlwZQpwMjQKVmZvbGRlcgpwMjUKc1ZtX21pbWUKcDI2ClZmb2xkZXIKcDI3CnNWbV9uYW1lCnAyOApWZG9jdW1lbnRlbgpwMjkKc3NWcm9vdHBhcmVudApwMzAKTnNWX2lkCnAzMQpWenpkaApwMzIKc1ZwYXJlbnQKcDMzCk5zYShkcDM0Cmc1Ck5zZzYKKGRwMzUKZzgKVnp6ZGgKcDM2CnNnOQpWCnNnMTAKVi9hbGxfdHlwZXMKcDM3CnNnMTEKVjA4LzEwLzEzIDE5OjE2CnAzOApzZzEzCkYxMzgxMjUyNTgxLjMzNzg4OQpzZzE0ClZhbGxfdHlwZXMKcDM5CnNnMTYKRjEzODEyNTI1ODEuMzM3ODAyOQpzZzE3CkYxMzgxMjUyNTgxMzM3LjgwMwpzZzE4ClZia3R6CnA0MApzZzIwCkYxMzgxMjUyNTgxLjMzNzgwMjkKc2cyMQpJMTk1NTAyCnNnMjIKVi9hbGxfdHlwZXMKcDQxCnNnMjMKSTAKc2cyNApWZm9sZGVyCnA0MgpzZzI2ClZmb2xkZXIKcDQzCnNnMjgKVmFsbF90eXBlcwpwNDQKc3NnMzAKVmJrdHoKcDQ1CnNnMzEKVmJrdHoKcDQ2CnNnMzMKVnp6ZGgKcDQ3CnNhKGRwNDgKZzUKTnNnNgooZHA0OQpnOApWYmt0egpwNTAKc2c5ClYKc2cxMApWL2FsbF90eXBlcy9mb28yCnA1MQpzZzExClYwOC8xMC8xMyAxOToxNgpwNTIKc2cxMwpGMTM4MTI1MjU4MS4zNjcwMDYxCnNnMTQKVmZvbzIKcDUzCnNnMTYKRjEzODEyNTI1ODEuMzY2OTA0CnNnMTcKRjEzODEyNTI1ODEzNjYuOTA0MQpzZzE4ClZmc3JjCnA1NApzZzIwCkYxMzgxMjUyNTgxLjM2NjkwNApzZzIxCkkxMDkyCnNnMjIKVi9hbGxfdHlwZXMvZm9vMgpwNTUKc2cyMwpJMApzZzI0ClZmb2xkZXIKcDU2CnNnMjYKVmZvbGRlcgpwNTcKc2cyOApWZm9vMgpwNTgKc3NnMzAKVmJrdHoKcDU5CnNnMzEKVmZzcmMKcDYwCnNnMzMKVmJrdHoKcDYxCnNhKGRwNjIKZzUKTnNnNgooZHA2MwpnOApWZnNyYwpwNjQKc2c5ClYKc2cxMApWL2FsbF90eXBlcy9mb28yL2JhcgpwNjUKc2cxMQpWMDgvMTAvMTMgMTk6MTYKcDY2CnNnMTMKRjEzODEyNTI1ODEuMzY3NjQxCnNnMTQKVmJhcgpwNjcKc2cxNgpGMTM4MTI1MjU4MS4zNjc1MTUxCnNnMTcKRjEzODEyNTI1ODEzNjcuNTE1MQpzZzE4ClZienBwCnA2OApzZzIwCkYxMzgxMjUyNTgxLjM2NzUxNTEKc2cyMQpJNTQ2CnNnMjIKVi9hbGxfdHlwZXMvZm9vMi9iYXIKcDY5CnNnMjMKSTAKc2cyNApWZm9sZGVyCnA3MApzZzI2ClZmb2xkZXIKcDcxCnNnMjgKVmJhcgpwNzIKc3NnMzAKVmJrdHoKcDczCnNnMzEKVmJ6cHAKcDc0CnNnMzMKVmZzcmMKcDc1CnNhKGRwNzYKZzUKKGxwNzcKVjFjYTI0ZDIzYWNkMzQwZTVlZjljOGJmMWY2NWNhYTRjYzE5N2Q5MDQKcDc4CmFGMTM4MTI1MjU5My45MDQ1ODMKYXNnNgooZHA3OQpnOApWYnpwcApwODAKc2c5ClZjcnlwdG9fZG9jX2UzYjg1NzJjNDUyMjRjY2Y4NWYwOGZmM2U1Mjg3M2Y3CnA4MQpzZzEwClYvYWxsX3R5cGVzL2ZvbzIvYmFyL3Rlc3QzLnR4dApwODIKc2cxMQpWMDgvMTAvMTMgMTk6MTYKcDgzCnNnMTMKRjEzODEyNTI1OTMuMDMxNTA4CnNnMTQKVnRlc3QzdHh0CnA4NApzZzE2CkYxMzgxMjUyNTkzLjkwNDU4MwpzZzE3CkYxMzgxMjUyNTkzMDMxLjQxMzEKc2cxOApWdHFwYgpwODUKc2cyMApGMTM4MTI1MjU5My4wMzE0MTMxCnNnMjEKSTU0NgpzZzIyClYvYWxsX3R5cGVzL2ZvbzIvYmFyL3Rlc3QzdHh0CnA4NgpzZzIzCkkwCnNnMjQKVmZpbGUKcDg3CnNnMjYKVnRleHQvcGxhaW4KcDg4CnNnMjgKVnRlc3QzLnR4dApwODkKc3NnMzAKVmJrdHoKcDkwCnNnMzEKVnRxcGIKcDkxCnNnMzMKVmJ6cHAKcDkyCnNhKGRwOTMKZzUKKGxwOTQKVjFjYTI0ZDIzYWNkMzQwZTVlZjljOGJmMWY2NWNhYTRjYzE5N2Q5MDQKcDk1CmFGMTM4MTI1MjU5MC4xODg3NjEKYXNnNgooZHA5NgpnOApWZnNyYwpwOTcKc2c5ClZjcnlwdG9fZG9jXzA3MTVlM2RiYTNkNDRmNzBhN2M3ZTJhNWExOWNjNTE5CnA5OApzZzEwClYvYWxsX3R5cGVzL2ZvbzIvdGVzdDIudHh0CnA5OQpzZzExClYwOC8xMC8xMyAxOToxNgpwMTAwCnNnMTMKRjEzODEyNTI1ODkuMDQ2NzE2CnNnMTQKVnRlc3QydHh0CnAxMDEKc2cxNgpGMTM4MTI1MjU5MC4xODg3NjEKc2cxNwpGMTM4MTI1MjU4OTA0Ni42Mjc5CnNnMTgKVnBubXAKcDEwMgpzZzIwCkYxMzgxMjUyNTg5LjA0NjYyOApzZzIxCkk1NDYKc2cyMgpWL2FsbF90eXBlcy9mb28yL3Rlc3QydHh0CnAxMDMKc2cyMwpJMQpzZzI0ClZmaWxlCnAxMDQKc2cyNgpWdGV4dC9wbGFpbgpwMTA1CnNnMjgKVnRlc3QyLnR4dApwMTA2CnNzZzMwClZia3R6CnAxMDcKc2czMQpWcG5tcApwMTA4CnNnMzMKVmZzcmMKcDEwOQpzYShkcDExMApnNQpOc2c2CihkcDExMQpnOApWYmt0egpwMTEyCnNnOQpWCnNnMTAKVi9hbGxfdHlwZXMvZm9vCnAxMTMKc2cxMQpWMDgvMTAvMTMgMTk6MTYKcDExNApzZzEzCkYxMzgxMjUyNTgxLjQyMjY2MzkKc2cxNApWZm9vCnAxMTUKc2cxNgpGMTM4MTI1MjU4MS40MjI1NjMxCnNnMTcKRjEzODEyNTI1ODE0MjIuNTYzCnNnMTgKVnFqeGgKcDExNgpzZzIwCkYxMzgxMjUyNTgxLjQyMjU2MzEKc2cyMQpJNTQ2CnNnMjIKVi9hbGxfdHlwZXMvZm9vCnAxMTcKc2cyMwpJMQpzZzI0ClZmb2xkZXIKcDExOApzZzI2ClZmb2xkZXIKcDExOQpzZzI4ClZmb28KcDEyMApzc2czMApWYmt0egpwMTIxCnNnMzEKVnFqeGgKcDEyMgpzZzMzClZia3R6CnAxMjMKc2EoZHAxMjQKZzUKKGxwMTI1ClYxY2EyNGQyM2FjZDM0MGU1ZWY5YzhiZjFmNjVjYWE0Y2MxOTdkOTA0CnAxMjYKYUYxMzgxMjUyNTg1LjYyNjYyNzkKYXNnNgooZHAxMjcKZzgKVnFqeGgKcDEyOApzZzkKVmNyeXB0b19kb2NfZjUyMWI0NjhjMmFiNDE4YmJjYjE2MDQzMWU4NzljMjEKcDEyOQpzZzEwClYvYWxsX3R5cGVzL2Zvby90ZXN0LnR4dApwMTMwCnNnMTEKVjA4LzEwLzEzIDE5OjE2CnAxMzEKc2cxMwpGMTM4MTI1MjU4My41ODM4MDIKc2cxNApWdGVzdHR4dApwMTMyCnNnMTYKRjEzODEyNTI1ODUuNjI2NjI3OQpzZzE3CkYxMzgxMjUyNTgzNTgzLjY2NDgKc2cxOApWam5rcgpwMTMzCnNnMjAKRjEzODEyNTI1ODMuNTgzNjY0OQpzZzIxCkk1NDYKc2cyMgpWL2FsbF90eXBlcy9mb28vdGVzdHR4dApwMTM0CnNnMjMKSTAKc2cyNApWZmlsZQpwMTM1CnNnMjYKVnRleHQvcGxhaW4KcDEzNgpzZzI4ClZ0ZXN0LnR4dApwMTM3CnNzZzMwClZia3R6CnAxMzgKc2czMQpWam5rcgpwMTM5CnNnMzMKVnFqeGgKcDE0MApzYShkcDE0MQpnNQoobHAxNDIKVjk3ZWNmMjE4NDM4NDIxMTk3NjE5NWFlYTc2MWE2YmY5Mzc0ZGY3ZGQKcDE0MwphRjEzODEyNTI1ODUuODU4OTI4OQphc2c2CihkcDE0NApnOApWYmt0egpwMTQ1CnNnOQpWY3J5cHRvX2RvY184MGNiYmQ5ZTMxNzQ0MjQ4OGVjM2FiNDVkMzRjZGQ1OApwMTQ2CnNnMTAKVi9hbGxfdHlwZXMvZG9jdW1lbnQucGRmCnAxNDcKc2cxMQpWMDgvMTAvMTMgMTk6MTYKcDE0OApzZzEzCkYxMzgxMjUyNTg0LjgwNTYzMzEKc2cxNApWZG9jdW1lbnRwZGYKcDE0OQpzZzE2CkYxMzgxMjUyNTg1Ljg1ODkyODkKc2cxNwpGMTM4MTI1MjU4NDgwNS41NDIKc2cxOApWZ3NyZgpwMTUwCnNnMjAKRjEzODEyNTI1ODQuODA1NTQyCnNnMjEKSTQ4Mzg5CnNnMjIKVi9hbGxfdHlwZXMvZG9jdW1lbnRwZGYKcDE1MQpzZzIzCkkyCnNnMjQKVmZpbGUKcDE1MgpzZzI2ClZhcHBsaWNhdGlvbi9wZGYKcDE1MwpzZzI4ClZkb2N1bWVudC5wZGYKcDE1NApzc2czMApWYmt0egpwMTU1CnNnMzEKVmdzcmYKcDE1NgpzZzMzClZia3R6CnAxNTcKc2EoZHAxNTgKZzUKKGxwMTU5ClY0YmRmZDdmNTY2ODEzMTY1OWZmYjIzNTg3MzJhMmRiYmM4YmM2MTMwCnAxNjAKYUYxMzgxMjUyNTg3LjU5NjAyMzEKYXNnNgooZHAxNjEKZzgKVmJrdHoKcDE2MgpzZzkKVmNyeXB0b19kb2NfZTk2ZDUxMTI1NmFhNGRhYzkyZTdkMWU1MmUyZjVlMmYKcDE2MwpzZzEwClYvYWxsX3R5cGVzL2JtcHRlc3QucG5nCnAxNjQKc2cxMQpWMDgvMTAvMTMgMTk6MTYKcDE2NQpzZzEzCkYxMzgxMjUyNTg2LjYwNDY2NjkKc2cxNApWYm1wdGVzdHBuZwpwMTY2CnNnMTYKRjEzODEyNTI1ODcuNTk2MDIzMQpzZzE3CkYxMzgxMjUyNTg2NjA0LjU0NzEKc2cxOApWbXd6YgpwMTY3CnNnMjAKRjEzODEyNTI1ODYuNjA0NTQ3CnNnMjEKSTExOTI0MwpzZzIyClYvYWxsX3R5cGVzL2JtcHRlc3RwbmcKcDE2OApzZzIzCkkzCnNnMjQKVmZpbGUKcDE2OQpzZzI2ClZpbWFnZS9wbmcKcDE3MApzZzI4ClZibXB0ZXN0LnBuZwpwMTcxCnNzZzMwClZia3R6CnAxNzIKc2czMQpWbXd6YgpwMTczCnNnMzMKVmJrdHoKcDE3NApzYShkcDE3NQpnNQoobHAxNzYKVjVjZmI0OTI4MjhjMTllYTNkMmQ2NDJkODUxYjVjZTY3MTk3OWIwN2UKcDE3NwphRjEzODEyNTI1ODkuNzQ4NTc3MQphc2c2CihkcDE3OApnOApWYmt0egpwMTc5CnNnOQpWY3J5cHRvX2RvY18zYjAzYzk0YjRhMDI0NWRkYjc2ZWIyNTQ1OGFlNzZjNQpwMTgwCnNnMTAKVi9hbGxfdHlwZXMvd29yZC5kb2N4CnAxODEKc2cxMQpWMDgvMTAvMTMgMTk6MTYKcDE4MgpzZzEzCkYxMzgxMjUyNTg4LjA4MTIyOApzZzE0ClZ3b3JkZG9jeApwMTgzCnNnMTYKRjEzODEyNTI1ODkuNzQ4NTc3MQpzZzE3CkYxMzgxMjUyNTg4MDgxLjAzMgpzZzE4ClZrYm16CnAxODQKc2cyMApGMTM4MTI1MjU4OC4wODEwMzIKc2cyMQpJMjYyMzIKc2cyMgpWL2FsbF90eXBlcy93b3JkZG9jeApwMTg1CnNnMjMKSTQKc2cyNApWZmlsZQpwMTg2CnNnMjYKVmFwcGxpY2F0aW9uL3ZuZC5vcGVueG1sZm9ybWF0cy1vZmZpY2Vkb2N1bWVudC53b3JkcHJvY2Vzc2luZ21sLmRvY3VtZW50CnAxODcKc2cyOApWd29yZC5kb2N4CnAxODgKc3NnMzAKVmJrdHoKcDE4OQpzZzMxClZrYm16CnAxOTAKc2czMwpWYmt0egpwMTkxCnNhKGRwMTkyCmc1Ck5zZzYKKGRwMTkzCmc4ClZ6emRoCnAxOTQKc2c5ClYKc2cxMApWL3NtYWxsdGVzdApwMTk1CnNnMTEKVjA4LzEwLzEzIDE5OjE2CnAxOTYKc2cxMwpGMTM4MTI1MjU4Mi40MTIyODcKc2cxNApWc21hbGx0ZXN0CnAxOTcKc2cxNgpGMTM4MTI1MjU4Mi40MTIyMDA5CnNnMTcKRjEzODEyNTI1ODI0MTIuMjAwOQpzZzE4ClZubmR6CnAxOTgKc2cyMApGMTM4MTI1MjU4Mi40MTIyMDA5CnNnMjEKSTEzCnNnMjIKVi9zbWFsbHRlc3QKcDE5OQpzZzIzCkkxCnNnMjQKVmZvbGRlcgpwMjAwCnNnMjYKVmZvbGRlcgpwMjAxCnNnMjgKVnNtYWxsdGVzdApwMjAyCnNzZzMwClZubmR6CnAyMDMKc2czMQpWbm5kegpwMjA0CnNnMzMKVnp6ZGgKcDIwNQpzYShkcDIwNgpnNQoobHAyMDcKVmM2NzMxZDhmNDZlMTg1M2Q0YjA2ZTZmYWYwNTVkZmQ0MDMzMmQzZjMKcDIwOAphRjEzODEyNTI1ODMuNzIzMTcKYXNnNgooZHAyMDkKZzgKVm5uZHoKcDIxMApzZzkKVmNyeXB0b19kb2NfMGI4YjM1YTRjZjdkNDg0ZTlkNDY5YmQ3NmUzMWQ0YTMKcDIxMQpzZzEwClYvc21hbGx0ZXN0L3Rlc3QuamF2YQpwMjEyCnNnMTEKVjA4LzEwLzEzIDE5OjE2CnAyMTMKc2cxMwpGMTM4MTI1MjU4Mi40MTI4MDc5CnNnMTQKVnRlc3RqYXZhCnAyMTQKc2cxNgpGMTM4MTI1MjU4My43MjMxNwpzZzE3CkYxMzgxMjUyNTgyNDEyLjczOQpzZzE4ClZ3bXJuCnAyMTUKc2cyMApGMTM4MTI1MjU4Mi40MTI3MzkKc2cyMQpJOQpzZzIyClYvc21hbGx0ZXN0L3Rlc3RqYXZhCnAyMTYKc2cyMwpJMApzZzI0ClZmaWxlCnAyMTcKc2cyNgpWdGV4dC94LWphdmEtc291cmNlCnAyMTgKc2cyOApWdGVzdC5qYXZhCnAyMTkKc3NnMzAKVm5uZHoKcDIyMApzZzMxClZ3bXJuCnAyMjEKc2czMwpWbm5kegpwMjIyCnNhKGRwMjIzCmc1CihscDIyNApWMzBkNzRkMjU4NDQyYzdjNjU1MTJlYWZhYjQ3NDU2OGRkNzA2YzQzMApwMjI1CmFGMTM4MTI1MjU5MS42NDU5MTY5CmFzZzYKKGRwMjI2Cmc4ClZubmR6CnAyMjcKc2c5ClZjcnlwdG9fZG9jXzdjZTk4NzlkYTdjZDQzMTU4YmQ4OTRkMDAwZTVhM2EzCnAyMjgKc2cxMApWL3NtYWxsdGVzdC90ZXN0LmNwcApwMjI5CnNnMTEKVjA4LzEwLzEzIDE5OjE2CnAyMzAKc2cxMwpGMTM4MTI1MjU5MC42NDQ1MzkxCnNnMTQKVnRlc3RjcHAKcDIzMQpzZzE2CkYxMzgxMjUyNTkxLjY0NTkxNjkKc2cxNwpGMTM4MTI1MjU5MDY0NC4zNDAxCnNnMTgKVnhya2YKcDIzMgpzZzIwCkYxMzgxMjUyNTkwLjY0NDM0CnNnMjEKSTQKc2cyMgpWL3NtYWxsdGVzdC90ZXN0Y3BwCnAyMzMKc2cyMwpJMQpzZzI0ClZmaWxlCnAyMzQKc2cyNgpWdGV4dC94LWMKcDIzNQpzZzI4ClZ0ZXN0LmNwcApwMjM2CnNzZzMwClZubmR6CnAyMzcKc2czMQpWeHJrZgpwMjM4CnNnMzMKVm5uZHoKcDIzOQpzYXNTJ2Rpcmxpc3QnCnAyNDAKKGxwMjQxClYvCmFWL2FsbF90eXBlcy9mb28yCnAyNDIKYVYvYWxsX3R5cGVzCnAyNDMKYVYvYWxsX3R5cGVzL2ZvbwpwMjQ0CmFWL3NtYWxsdGVzdApwMjQ1CmFWL2FsbF90eXBlcy9mb28yL2JhcgpwMjQ2CmFzVnRyZWVfdGltZXN0YW1wCnAyNDcKRjEzODEyNTI1OTQuMDk0NzA4OQpzLg=="))

        cbmemory, cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(memory, cboptions, localindex, serverindex)


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
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        cbmemory, cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)

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

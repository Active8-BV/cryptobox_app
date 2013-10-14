# coding=utf-8
"""
unit test for app commands
"""
__author__ = 'rabshakeh'
import os
import time
import couchdb
import cPickle
import subprocess
import unittest
import random
import requests
import sys
from cba_main import cryptobox_command
from cba_utils import Dict2Obj, smp_all_cpu_apply, Memory
from cba_index import make_local_index, index_and_encrypt, check_and_clean_dir, decrypt_and_build_filetree, hide_config
from cba_blobs import get_blob_dir, get_data_dir
from cba_network import authorize_user
from cba_sync import get_server_index, parse_serverindex, instruct_server_to_delete_folders, dirs_on_local, path_to_server_shortid, wait_for_tasks, sync_server, get_sync_changes, short_id_to_server_path, NoSyncDirFound
from cba_file import ensure_directory
from cba_crypto import make_checksum, encrypt_file_smp, decrypt_file_smp
from subprocess import Popen, PIPE
sys.path.append("/Users/rabshakeh/workspace/cryptobox")

#noinspection PyUnresolvedReferences
from couchdb_api import MemcachedServer, CouchDBServer, sync_all_views
#noinspection PyUnresolvedReferences
import crypto_api

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
        self.start_servers = True
        self.db_name = "test"
        server = "http://127.0.01:8000/"
        self.options_d = {"dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/testmap", "encrypt": True, "remove": False, "username": "rabshakeh", "password": "kjhfsd98", "cryptobox": self.db_name, "clear": False, "sync": False, "server": server, "numdownloadthreads": 12}
        self.cboptions = Dict2Obj(self.options_d)

        self.reset_cb_db_clean()

        os.system("ps aux | grep -ie runserver | awk '{print $2}' | xargs kill -9")
        os.system("ps aux | grep -ie cronjobe | awk '{print $2}' | xargs kill -9")
        if self.start_servers:
            self.server = subprocess.Popen(["/usr/local/bin/python", "manage.py", "runserver"], cwd="/Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl/server")
            self.cronjob = subprocess.Popen(["/usr/local/bin/python", "cronjob.py"], cwd="/Users/rabshakeh/workspace/cryptobox/crypto_taskworker")
        connected = False
        while not connected:
            #noinspection PyBroadException
            try:
                time.sleep(0.5)
                #noinspection PyUnusedLocal
                if self.start_servers:
                    data = requests.get("http://127.0.0.1:8000").content
                connected = True
            except Exception:
                time.sleep(0.5)

        mc = MemcachedServer(["127.0.0.1:11211"], "mutex")
        mc.flush_all()

        self.cbmemory = Memory()
        self.cbmemory.set("cryptobox_folder", self.cboptions.dir)

        if self.start_servers:
            self.cbmemory = authorize_user(self.cbmemory, self.cboptions, force=True)
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))
        self.do_wait_for_tasks = True
        testfile_sizes = ["1MB.zip", "200MB.zip", "100MB.zip", "20MB.zip", "5MB.zip", "1GB.zip", "50MB.zip"]

        for tfn in testfile_sizes:
            if not os.path.exists(os.path.join("testdata", tfn)):
                os.system("cd testdata; nohup wget http://download.thinkbroadband.com/" + tfn)

    def tearDown(self):
        """
        tearDown
        """
        if self.do_wait_for_tasks:
            wait_for_tasks(self.cbmemory, self.cboptions)
        if self.start_servers:
            self.server.terminate()
            self.cronjob.terminate()
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
        server = "http://127.0.0.1:5984/"

        if self.db_name in list(couchdb.Server(server)):
            couchdb.Server(server).delete(self.db_name)

        if self.db_name not in list(couchdb.Server(server)):
            couchdb.Server(server).create(self.db_name)

        os.system("rm -Rf testdata/testmap")
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))
        os.system("cp testdata/test.dump /Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl")
        self.pipe = Popen("nohup python server/manage.py load -c test", shell=True, stderr=PIPE, stdout=PIPE, cwd="/Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl")
        self.pipe.wait()
        dbase = CouchDBServer(self.db_name, ["http://127.0.0.1:5984/"], memcached_server_list=["127.0.0.1:11211"])
        sync_all_views(dbase, ["couchdb_api", "crypto_api"])

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
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 7)

        # add a new file
        open(os.path.join(self.cboptions.dir, "hello world.txt"), "w").write("hello world 123 Dit is random data")
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 8)

        # same content, blob count should not rise
        open(os.path.join(self.cboptions.dir, "hello world2.txt"), "w").write("hello world 123 Dit is random data")
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 8)

    def itest_index_encrypt_decrypt_clean(self):
        """
        test_index_encrypt_decrypt_clean
        """
        self.do_wait_for_tasks = False
        self.complete_reset()
        self.unzip_testfiles_clean()
        os.system("rm -Rf " + get_blob_dir(self.cboptions))
        self.cboptions.remove = True
        salt, secret, self.cbmemory, localindex1 = index_and_encrypt(self.cbmemory, self.cboptions)
        datadir = get_data_dir(self.cboptions)
        self.cbmemory.save(datadir)
        hide_config(self.cboptions, salt, secret)
        self.assertEqual(count_files_dir(self.cboptions.dir), 7)
        self.cbmemory = decrypt_and_build_filetree(self.cbmemory, self.cboptions)
        os.system("rm -Rf " + get_blob_dir(self.cboptions))
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
        dir_make_server, dir_del_local = dirs_on_local(self.cbmemory, self.cboptions, localindex, dirname_hashes_server, serverindex)
        return (len(dir_make_server) == 0) and (len(dir_del_local) == 0)

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
        import base64
        memory = cPickle.loads(base64.decodestring(
            "Y2NvcHlfcmVnCl9yZWNvbnN0cnVjdG9yCnAxCihjY2JhX3V0aWxzCk1lbW9yeQpwMgpjX19idWlsdGluX18Kb2JqZWN0CnAzCk50UnA0CihkcDUKUydtX2xvY2tlZCcKcDYKSTAwCnNTJ2RhdGEnCnA3CihkcDgKUydsb2NhbHBhdGhfaGlzdG9yeScKcDkKY19fYnVpbHRpbl9fCnNldApwMTAKKChscDExCihWL2ZvbzIKUydiNmZmMGQ5YzAxN2VjM2FlMmMzOGViOTNmNDdkNTgwYTQ0NTAwNTIwJwp0cDEyCmEoVi9mb28KUyc2ZGJkNTQ4Y2MwM2U0NGI4YjQ0YjZlNjhlNTYyNTVjZTQyNzNhZTQ5Jwp0cDEzCmEoVi8KUyc0MjA5OWI0YWYwMjFlNTNmZDhmZDRlMDU2YzI1NjhkN2MyZTNmZmE4Jwp0cDE0CmF0UnAxNQpzUydjcnlwdG9ib3hfZm9sZGVyJwpwMTYKUycvVXNlcnMvcmFic2hha2VoL3dvcmtzcGFjZS9jcnlwdG9ib3gvY3J5cHRvYm94X2FwcC9zb3VyY2UvY29tbWFuZHMvdGVzdGRhdGEvdGVzdG1hcCcKcDE3CnNTJ3NlcnZlcmluZGV4JwpwMTgKKGRwMTkKVmRvY2xpc3QKcDIwCihscDIxCihkcDIyClZjb250ZW50X2hhc2hfbGF0ZXN0X3RpbWVzdGFtcApwMjMKTnNWZG9jCnAyNAooZHAyNQpWbV9wYXJlbnQKcDI2ClYKc1ZtX2RhdGFfaWQKcDI3ClYKc1ZtX3BhdGgKcDI4ClYvCnNWbV9kYXRlX2h1bWFuCnAyOQpWMDgvMTAvMTMgMTM6NDYKcDMwCnNWbV9jcmVhdGlvbl90aW1lCnAzMQpGMTM4MTIzMjc2NS45OApzVm1fc2x1ZwpwMzIKVmRvY3VtZW50ZW4KcDMzCnNWdGltZXN0YW1wCnAzNApGMTM4MTIzMjc2NS45OApzVm1fZGF0ZV90aW1lCnAzNQpGMTM4MTIzMjc2NTk4MApzVm1fc2hvcnRfaWQKcDM2ClZ6emRoCnAzNwpzVm1fZGF0ZQpwMzgKRjEzODEyMzI3NjUuOTgKc1ZtX3NpemUKcDM5Ckk1MzUKc1ZtX3NsdWdwYXRoCnA0MApWLwpzVm1fb3JkZXIKcDQxCkkwCnNWbV9ub2RldHlwZQpwNDIKVmZvbGRlcgpwNDMKc1ZtX21pbWUKcDQ0ClZmb2xkZXIKcDQ1CnNWbV9uYW1lCnA0NgpWZG9jdW1lbnRlbgpwNDcKc3NWcm9vdHBhcmVudApwNDgKTnNWX2lkCnA0OQpWenpkaApwNTAKc1ZwYXJlbnQKcDUxCk5zYShkcDUyCmcyMwpOc2cyNAooZHA1MwpnMjYKVnp6ZGgKcDU0CnNnMjcKVgpzZzI4ClYvZm9vCnA1NQpzZzI5ClYxNC8xMC8xMyAxMDo0OApwNTYKc2czMQpGMTM4MTc0MDQ5MC4xNzQzODAxCnNnMzIKVmZvbwpwNTcKc2czNApGMTM4MTc0MDQ5MC4xNzQxOTI5CnNnMzUKRjEzODE3NDA0OTAxNzQuMTkyOQpzZzM2ClZ3aGt6CnA1OApzZzM4CkYxMzgxNzQwNDkwLjE3NDE5MjkKc2czOQpJMApzZzQwClYvZm9vCnA1OQpzZzQxCkkwCnNnNDIKVmZvbGRlcgpwNjAKc2c0NApWZm9sZGVyCnA2MQpzZzQ2ClZmb28KcDYyCnNzZzQ4ClZ3aGt6CnA2MwpzZzQ5ClZ3aGt6CnA2NApzZzUxClZ6emRoCnA2NQpzYShkcDY2CmcyMwpOc2cyNAooZHA2NwpnMjYKVnp6ZGgKcDY4CnNnMjcKVgpzZzI4ClYvZm9vMgpwNjkKc2cyOQpWMTQvMTAvMTMgMTA6NDgKcDcwCnNnMzEKRjEzODE3NDA0OTIuMjIyNzgzMQpzZzMyClZmb28yCnA3MQpzZzM0CkYxMzgxNzQwNDkyLjIyMjUyMTEKc2czNQpGMTM4MTc0MDQ5MjIyMi41MjEKc2czNgpWbXpieApwNzIKc2czOApGMTM4MTc0MDQ5Mi4yMjI1MjExCnNnMzkKSTUzNQpzZzQwClYvZm9vMgpwNzMKc2c0MQpJMQpzZzQyClZmb2xkZXIKcDc0CnNnNDQKVmZvbGRlcgpwNzUKc2c0NgpWZm9vMgpwNzYKc3NnNDgKVm16YngKcDc3CnNnNDkKVm16YngKcDc4CnNnNTEKVnp6ZGgKcDc5CnNhKGRwODAKZzIzCihscDgxClY5MjMzZjkyZDkwNGM2ZmMzMjIxMTkxOWNiMzJhMTgxNjdkMTliMTkxCnA4MgphRjEzODE3NDA0OTMuODA1NzMwMQphc2cyNAooZHA4MwpnMjYKVm16YngKcDg0CnNnMjcKVmNyeXB0b19kb2NfMTA5Njc5MTg4ZjI1NDBmYmEyZDczMDQ0MDUwNDRjNzUKcDg1CnNnMjgKVi9mb28yL3Rlc3QudHh0CnA4NgpzZzI5ClYxNC8xMC8xMyAxMDo0OApwODcKc2czMQpGMTM4MTc0MDQ5My45MDA5NTMxCnNnMzIKVnRlc3R0eHQKcDg4CnNnMzQKRjEzODE3NDA0OTMuODA1NzMwMQpzZzM1CkYxMzgxNzQwNDkzOTAwLjc1CnNnMzYKVnh0cnQKcDg5CnNnMzgKRjEzODE3NDA0OTMuOTAwNzQ5OQpzZzM5Ckk1MzUKc2c0MApWL2ZvbzIvdGVzdHR4dApwOTAKc2c0MQpJMApzZzQyClZmaWxlCnA5MQpzZzQ0ClZ0ZXh0L3BsYWluCnA5MgpzZzQ2ClZ0ZXN0LnR4dApwOTMKc3NnNDgKVm16YngKcDk0CnNnNDkKVnh0cnQKcDk1CnNnNTEKVm16YngKcDk2CnNhc1MnZGlybGlzdCcKcDk3CihscDk4ClYvZm9vMgpwOTkKYVYvCmFzVnRyZWVfdGltZXN0YW1wCnAxMDAKRjEzODE3NDA0OTMuOTI3ODQzMQpzc1Mnc2Vzc2lvbicKcDEwMQpnMQooY3JlcXVlc3RzLnNlc3Npb25zClNlc3Npb24KcDEwMgpnMwpOdFJwMTAzCihkcDEwNApTJ2Nvb2tpZXMnCnAxMDUKZzEKKGNyZXF1ZXN0cy5jb29raWVzClJlcXVlc3RzQ29va2llSmFyCnAxMDYKZzMKTnRScDEwNwooZHAxMDgKUydfbm93JwpwMTA5CkkxMzgxNzQwNTAwCnNTJ19wb2xpY3knCnAxMTAKKGljb29raWVsaWIKRGVmYXVsdENvb2tpZVBvbGljeQpwMTExCihkcDExMgpTJ3N0cmljdF9yZmMyOTY1X3VudmVyaWZpYWJsZScKcDExMwpJMDEKc1Mnc3RyaWN0X25zX2RvbWFpbicKcDExNApJMApzUydfYWxsb3dlZF9kb21haW5zJwpwMTE1Ck5zUydyZmMyMTA5X2FzX25ldHNjYXBlJwpwMTE2Ck5zUydyZmMyOTY1JwpwMTE3CkkwMApzUydzdHJpY3RfZG9tYWluJwpwMTE4CkkwMApzZzEwOQpJMTM4MTc0MDUwMApzUydzdHJpY3RfbnNfc2V0X3BhdGgnCnAxMTkKSTAwCnNTJ3N0cmljdF9uc191bnZlcmlmaWFibGUnCnAxMjAKSTAwCnNTJ3N0cmljdF9uc19zZXRfaW5pdGlhbF9kb2xsYXInCnAxMjEKSTAwCnNTJ2hpZGVfY29va2llMicKcDEyMgpJMDAKc1MnX2Jsb2NrZWRfZG9tYWlucycKcDEyMwoodHNTJ25ldHNjYXBlJwpwMTI0CkkwMQpzYnNTJ19jb29raWVzJwpwMTI1CihkcDEyNgpTJzEyNy4wLjAxJwpwMTI3CihkcDEyOApTJy8nCihkcDEyOQpTJ2NfdG9rZW4nCnAxMzAKKGljb29raWVsaWIKQ29va2llCnAxMzEKKGRwMTMyClMnY29tbWVudCcKcDEzMwpOc1MnZG9tYWluJwpwMTM0CmcxMjcKc1MnbmFtZScKcDEzNQpnMTMwCnNTJ2RvbWFpbl9pbml0aWFsX2RvdCcKcDEzNgpJMDAKc1MnZXhwaXJlcycKcDEzNwpOc1MndmFsdWUnCnAxMzgKUyciLmVKeHRWVGZQN0FvUnZUd1FoWl9nTjl3U3lRSjduWTFFWWEtOVR1dHNyME56NVp4enRvUkVpZmpWZk8tS2ttblBhT2FFNHZ6cmwzOU92X3VMLS1zNFYzdTBaai1hN0pwLWNmN3p4Ml9mX3ZyYnNMd2dhZDh0bV9sdVdOS0hjZmp2Q2hfOFJBQlZrdmloa0ZpR1VaNk15VE5MeGcwWWxQc1pWVC1oYTNseEY3VEN1aTZTX1B1Tzh1UUMyd3JkaVdRUGRmbmozbWtOUE5ybkhhbWg4QUxMcmtqYXZDWVJJM0lqdnNKbUVZWHZLYlVqdXlzNy16a0U0MUpvcWJrUEFseXUwZnVrRUZPMFFZQzliRTlKb3ZtQXU3c1FEaE9XOEhjQ3FSVjZwUTlKaUZkcmZMWnlEVjluajYxZzBWRmg3cUxoamZ1a2Z3dFpiMVdBRjhFcjNSUlduZkdKYlFoNVJTd3hMYjBQcnRFRGFubmFpTnJ1RlJYRmJ5d1dxa25pVE9WUnlEZUNzS1JZcll6T0FqaE14bVJpbExYOHBiZnVKdEhhVjI0Ull5LVlXdlFpcXI1WE1JSkt2Vm90VDVwQ3phWDZHR0psNDhTcXMtTExDb0I3Y1JzUU9tdGQ3LS03empTMjBISW41OVo2OXNxZ3J5d1pfNWk2S1hHTXliRE04R1UyYTEwUFdUVlRMUmxldHhJQnJtODdPZlFKbV9VWjJER3RYeEdOazZoSFBNUWVLWGJiNWJFaVhMYncyZW9NdURtRDRMVUdUYnp0dWxSZ2tER0xCUmc4dXJLU1kzVmZVLW5IQ0NxNW0zaFA5N0l5YTdYYmU3N1RUeVFzbkRpR1V0ckd0Skl3bk9PY0liR1A3SFlkTlJsZ1V2SEF0blZJSWlPbVFyNENQVjFVejRmbW9ISmVOUUtLWklIWDM4M0hwWllWZWxwbHl6bTdTX1pLeEJoNEg4c2Z3Q3A3TDVTRXg1cGVBUUloTnlQUkpDRm55cjBITWVRak5Oay1pMEFPQkVneVRqbFc0eVB5TjVHemZRYS13UGg2RlFBRWtyQXI2Vjhaam1YWHV6T1JKWHBTQnRLaXFMVDFDTWdiaTNBY0lRNVAzMU45VXBmZ2R2Y2lWZHZwNmZlcUd4VEFSRmF6QkRWZmIzaG1JX0RRbXRQZzNUMDU3YURRcWZGYXN4a0ZFalBRQTh6NlVkcll1N1dxRkt5ZWJrVEdvSkhKd0R5dUI5NDREc2dYZEtFd3VRZVRLZGZuczJQSXA2VWdueWtPd2s5VGVaWVNKRm80MWVNZVpRZy05SGJpdnNRVmdRRDB5TVlQV0JpMUt3NThmMkNxN1JWYklYWGhZYlRKdmQwZFRfV2x5V3gwR1J0d3Q1djZRMnV2ZVBuSm1KcjREOUFuY1dGcHBTUk9ocjlqMDd1M2NKeUdKVjFqUHZYRGxEd0kxaWhGRWJzRU9YWWlEME83dVNLVk8wZFJIYmNNbWtyQUV6LXlpX3FRd0RtaFVtRlRDdnV5YjV6S1Nxd3lyODZPeU1kRTFIeVVlM2gtWFp6MS1Fb1V2eTVURXNHSk1INjhBUzYzMkp3Z3E2WkV2Ym05azd6Mm5zSFFoLWZNTnBjWXpxUTIzNmY4RzJVR1dSbjdVV1pVam50ZVdLZzVjZDNvQXlDNmMydXhrV0M4enpyMEJ1M0VGRDFETGNYNzdXRW1YNkVJWEl0YWFKM1ZjMFdvTlVGWFc1TGsyeWVEN3ZxTXJodzRWUEVCTi1Ia1FHVkNJcnVCU0tFRVVUUjA3S3NscEM3T1RYWnV2OE45cFE3bGhJT3l0MHdMZTB5SzlKeWlJd2xZUU5ENWxUWThVbm1Ub01lTTlmRDY4TGVwc0FVcnNna0RpbGZUUVZtVjFXZzZLSFhnQ2t4R1h2WUFxYXlOdjBMOWRRTHVXaUdCOE1aQk91dHRyR09pc0VCNGJLa2Y3dkFLdkpjRFEzNDl2TFhobXJhLWRvNlhpYWpkZ1BCdFJhVUtMREVQd0F5Q05HUUtjOUpmekFrcFZhd2FadmlrMTZnQjgzVWFxeU1zN1l3WlRsOTdhc2ZseW83M0tBWjdmY21mR1huakdRN3N0UnN5ZzhBRWN6RjZaNzlRZEVQMi11Wlo2RUkyWURFMUNMRzZhTnVNSFh4bTJ3dEVZTnNTQm0yQnZXSHh2U29GWUdHR3J6VWFEN29JN2JYZGNzU3RadnZOSmR0bG9CVS1ZbFFXaFZkV2x6VmEtVXZESk0wQWxVNDVoUU9NeFZrOUFBd1NuWXE5YTNtSHpyZTg4VVBYYmhRLTNyQ0gzbGF6WXlSclh6MFhheXlKOHhaSlJCcmpfZ1A0V1NtOHh2M2Zxbkhfdk03YnN2NUlobTdjMW15ZWZ2OXY5MDlMdGl6VjBQOVloeWJycHpfNHIyX2Z2aEV0U0tyNEMtYlR3SkpJUFc2SG92cmZ4ZzhxU2pNYVJxTVlSV0dNb3RJNEppTWNqVEtLU21BOHdjbV96MUc4bEZHVGxkdmZfZ3V1ZjFSNjoxVlZkb3E6NE1tZ3NXZ2ZBcFdmM2I4RTMtbGJlYjJNblpBIicKcDEzOQpzUydkb21haW5fc3BlY2lmaWVkJwpwMTQwCkkwMApzUydfcmVzdCcKcDE0MQooZHAxNDIKUydodHRwb25seScKcDE0MwpOc3NTJ3ZlcnNpb24nCnAxNDQKSTAKc1MncG9ydF9zcGVjaWZpZWQnCnAxNDUKSTAwCnNTJ3JmYzIxMDknCnAxNDYKSTAwCnNTJ2Rpc2NhcmQnCnAxNDcKSTAxCnNTJ3BhdGhfc3BlY2lmaWVkJwpwMTQ4CkkwMQpzUydwYXRoJwpwMTQ5ClMnLycKc1MncG9ydCcKcDE1MApOc1MnY29tbWVudF91cmwnCnAxNTEKTnNTJ3NlY3VyZScKcDE1MgpJMDAKc2Jzc3NzYnNTJ3N0cmVhbScKcDE1MwpJMDAKc1MnaG9va3MnCnAxNTQKKGRwMTU1ClMncmVzcG9uc2UnCnAxNTYKKGxwMTU3CnNzUydhdXRoJwpwMTU4Ck5zUyd0cnVzdF9lbnYnCnAxNTkKSTAxCnNTJ2hlYWRlcnMnCnAxNjAKZzEKKGNyZXF1ZXN0cy5zdHJ1Y3R1cmVzCkNhc2VJbnNlbnNpdGl2ZURpY3QKcDE2MQpnMwpOdFJwMTYyCihkcDE2MwpTJ19zdG9yZScKcDE2NAooZHAxNjUKUydhY2NlcHQtZW5jb2RpbmcnCnAxNjYKKFMnQWNjZXB0LUVuY29kaW5nJwpwMTY3ClMnZ3ppcCwgZGVmbGF0ZSwgY29tcHJlc3MnCnRwMTY4CnNTJ2FjY2VwdCcKcDE2OQooUydBY2NlcHQnCnAxNzAKUycqLyonCnAxNzEKdHAxNzIKc1MndXNlci1hZ2VudCcKcDE3MwooUydVc2VyLUFnZW50JwpwMTc0ClMncHl0aG9uLXJlcXVlc3RzLzIuMC4wIENQeXRob24vMi43LjUgRGFyd2luLzEzLjAuMCcKdHAxNzUKc3Nic1MnY2VydCcKcDE3NgpOc1MncGFyYW1zJwpwMTc3CihkcDE3OApzUydwcmVmZXRjaCcKcDE3OQpOc1MndGltZW91dCcKcDE4MApOc1MndmVyaWZ5JwpwMTgxCkkwMQpzUydwcm94aWVzJwpwMTgyCihkcDE4MwpzUydhZGFwdGVycycKcDE4NApjcmVxdWVzdHMucGFja2FnZXMudXJsbGliMy5wYWNrYWdlcy5vcmRlcmVkX2RpY3QKT3JkZXJlZERpY3QKcDE4NQooKGxwMTg2CihscDE4NwpTJ2h0dHBzOi8vJwpwMTg4CmFnMQooY3JlcXVlc3RzLmFkYXB0ZXJzCkhUVFBBZGFwdGVyCnAxODkKZzMKTnRScDE5MAooZHAxOTEKUydfcG9vbF9ibG9jaycKcDE5MgpJMDAKc1MnX3Bvb2xfbWF4c2l6ZScKcDE5MwpJMTAKc1MnbWF4X3JldHJpZXMnCnAxOTQKSTAKc1MnY29uZmlnJwpwMTk1CihkcDE5NgpzUydfcG9vbF9jb25uZWN0aW9ucycKcDE5NwpJMTAKc2JhYShscDE5OApTJ2h0dHA6Ly8nCnAxOTkKYWcxCihnMTg5CmczCk50UnAyMDAKKGRwMjAxCmcxOTIKSTAwCnNnMTkzCkkxMApzZzE5NApJMApzZzE5NQooZHAyMDIKc2cxOTcKSTEwCnNiYWF0UnAyMDMKc1MnbWF4X3JlZGlyZWN0cycKcDIwNApJMzAKc2JzUydhdXRob3JpemVkJwpwMjA1CkkwMQpzUydzZXJ2ZXJwYXRoX2hpc3RvcnknCnAyMDYKZzEwCigobHAyMDcKKFMnL2ZvbzInClMnYjZmZjBkOWMwMTdlYzNhZTJjMzhlYjkzZjQ3ZDU4MGE0NDUwMDUyMCcKdHAyMDgKYShTJy9mb28nClMnNmRiZDU0OGNjMDNlNDRiOGI0NGI2ZTY4ZTU2MjU1Y2U0MjczYWU0OScKdHAyMDkKYShWLwpTJzQyMDk5YjRhZjAyMWU1M2ZkOGZkNGUwNTZjMjU2OGQ3YzJlM2ZmYTgnCnRwMjEwCmF0UnAyMTEKc1MndHJlZV9zZXEnCnAyMTIKSTYKc3NiLg=="))

        localindex = cPickle.loads(base64.decodestring(
            "KGRwMQpTJ2ZpbGVzdGF0cycKcDIKKGRwMwpzUydkaXJuYW1lcycKcDQKKGRwNQpTJ2RhMzlhM2VlNWU2YjRiMGQzMjU1YmZlZjk1NjAxODkwYWZkODA3MDknCnA2CihkcDcKUyduYW1lc2hhc2gnCnA4ClMnNmUxNzRlM2JmNzQzMzkwZDM0NTM3N2I5MzhjY2EzYTM2N2RhZGM2OCcKcDkKc1MnZGlybmFtZScKcDEwClMnL1VzZXJzL3JhYnNoYWtlaC93b3Jrc3BhY2UvY3J5cHRvYm94L2NyeXB0b2JveF9hcHAvc291cmNlL2NvbW1hbmRzL3Rlc3RkYXRhL3Rlc3RtYXAnCnAxMQpzUydmaWxlbmFtZXMnCnAxMgoobHAxMwpzUydkaXJuYW1laGFzaCcKcDE0Cmc2CnNzUydiNmZmMGQ5YzAxN2VjM2FlMmMzOGViOTNmNDdkNTgwYTQ0NTAwNTIwJwpwMTUKKGRwMTYKZzgKUydkYTM5YTNlZTVlNmI0YjBkMzI1NWJmZWY5NTYwMTg5MGFmZDgwNzA5JwpwMTcKc2cxMApTJy9Vc2Vycy9yYWJzaGFrZWgvd29ya3NwYWNlL2NyeXB0b2JveC9jcnlwdG9ib3hfYXBwL3NvdXJjZS9jb21tYW5kcy90ZXN0ZGF0YS90ZXN0bWFwL2ZvbzInCnAxOApzZzEyCihscDE5CnNnMTQKZzE1CnNzUyc2ZGJkNTQ4Y2MwM2U0NGI4YjQ0YjZlNjhlNTYyNTVjZTQyNzNhZTQ5JwpwMjAKKGRwMjEKZzgKUydkYTM5YTNlZTVlNmI0YjBkMzI1NWJmZWY5NTYwMTg5MGFmZDgwNzA5JwpwMjIKc2cxMApTJy9Vc2Vycy9yYWJzaGFrZWgvd29ya3NwYWNlL2NyeXB0b2JveC9jcnlwdG9ib3hfYXBwL3NvdXJjZS9jb21tYW5kcy90ZXN0ZGF0YS90ZXN0bWFwL2ZvbycKcDIzCnNnMTIKKGxwMjQKc2cxNApnMjAKc3NzLg=="))

        serverindex = cPickle.loads(base64.decodestring(
            "KGRwMQpWZG9jbGlzdApwMgoobHAzCihkcDQKVmNvbnRlbnRfaGFzaF9sYXRlc3RfdGltZXN0YW1wCnA1Ck5zVmRvYwpwNgooZHA3ClZtX3BhcmVudApwOApWCnNWbV9kYXRhX2lkCnA5ClYKc1ZtX3BhdGgKcDEwClYvCnNWbV9kYXRlX2h1bWFuCnAxMQpWMDgvMTAvMTMgMTM6NDYKcDEyCnNWbV9jcmVhdGlvbl90aW1lCnAxMwpGMTM4MTIzMjc2NS45OApzVm1fc2x1ZwpwMTQKVmRvY3VtZW50ZW4KcDE1CnNWdGltZXN0YW1wCnAxNgpGMTM4MTIzMjc2NS45OApzVm1fZGF0ZV90aW1lCnAxNwpGMTM4MTIzMjc2NTk4MApzVm1fc2hvcnRfaWQKcDE4ClZ6emRoCnAxOQpzVm1fZGF0ZQpwMjAKRjEzODEyMzI3NjUuOTgKc1ZtX3NpemUKcDIxCkk1MzUKc1ZtX3NsdWdwYXRoCnAyMgpWLwpzVm1fb3JkZXIKcDIzCkkwCnNWbV9ub2RldHlwZQpwMjQKVmZvbGRlcgpwMjUKc1ZtX21pbWUKcDI2ClZmb2xkZXIKcDI3CnNWbV9uYW1lCnAyOApWZG9jdW1lbnRlbgpwMjkKc3NWcm9vdHBhcmVudApwMzAKTnNWX2lkCnAzMQpWenpkaApwMzIKc1ZwYXJlbnQKcDMzCk5zYShkcDM0Cmc1Ck5zZzYKKGRwMzUKZzgKVnp6ZGgKcDM2CnNnOQpWCnNnMTAKVi9mb28KcDM3CnNnMTEKVjE0LzEwLzEzIDEwOjQ4CnAzOApzZzEzCkYxMzgxNzQwNDkwLjE3NDM4MDEKc2cxNApWZm9vCnAzOQpzZzE2CkYxMzgxNzQwNDkwLjE3NDE5MjkKc2cxNwpGMTM4MTc0MDQ5MDE3NC4xOTI5CnNnMTgKVndoa3oKcDQwCnNnMjAKRjEzODE3NDA0OTAuMTc0MTkyOQpzZzIxCkkwCnNnMjIKVi9mb28KcDQxCnNnMjMKSTAKc2cyNApWZm9sZGVyCnA0MgpzZzI2ClZmb2xkZXIKcDQzCnNnMjgKVmZvbwpwNDQKc3NnMzAKVndoa3oKcDQ1CnNnMzEKVndoa3oKcDQ2CnNnMzMKVnp6ZGgKcDQ3CnNhKGRwNDgKZzUKTnNnNgooZHA0OQpnOApWenpkaApwNTAKc2c5ClYKc2cxMApWL2ZvbzIKcDUxCnNnMTEKVjE0LzEwLzEzIDEwOjQ4CnA1MgpzZzEzCkYxMzgxNzQwNDkyLjIyMjc4MzEKc2cxNApWZm9vMgpwNTMKc2cxNgpGMTM4MTc0MDQ5Mi4yMjI1MjExCnNnMTcKRjEzODE3NDA0OTIyMjIuNTIxCnNnMTgKVm16YngKcDU0CnNnMjAKRjEzODE3NDA0OTIuMjIyNTIxMQpzZzIxCkk1MzUKc2cyMgpWL2ZvbzIKcDU1CnNnMjMKSTEKc2cyNApWZm9sZGVyCnA1NgpzZzI2ClZmb2xkZXIKcDU3CnNnMjgKVmZvbzIKcDU4CnNzZzMwClZtemJ4CnA1OQpzZzMxClZtemJ4CnA2MApzZzMzClZ6emRoCnA2MQpzYShkcDYyCmc1CihscDYzClY5MjMzZjkyZDkwNGM2ZmMzMjIxMTkxOWNiMzJhMTgxNjdkMTliMTkxCnA2NAphRjEzODE3NDA0OTMuODA1NzMwMQphc2c2CihkcDY1Cmc4ClZtemJ4CnA2NgpzZzkKVmNyeXB0b19kb2NfMTA5Njc5MTg4ZjI1NDBmYmEyZDczMDQ0MDUwNDRjNzUKcDY3CnNnMTAKVi9mb28yL3Rlc3QudHh0CnA2OApzZzExClYxNC8xMC8xMyAxMDo0OApwNjkKc2cxMwpGMTM4MTc0MDQ5My45MDA5NTMxCnNnMTQKVnRlc3R0eHQKcDcwCnNnMTYKRjEzODE3NDA0OTMuODA1NzMwMQpzZzE3CkYxMzgxNzQwNDkzOTAwLjc1CnNnMTgKVnh0cnQKcDcxCnNnMjAKRjEzODE3NDA0OTMuOTAwNzQ5OQpzZzIxCkk1MzUKc2cyMgpWL2ZvbzIvdGVzdHR4dApwNzIKc2cyMwpJMApzZzI0ClZmaWxlCnA3MwpzZzI2ClZ0ZXh0L3BsYWluCnA3NApzZzI4ClZ0ZXN0LnR4dApwNzUKc3NnMzAKVm16YngKcDc2CnNnMzEKVnh0cnQKcDc3CnNnMzMKVm16YngKcDc4CnNhc1MnZGlybGlzdCcKcDc5CihscDgwClYvZm9vMgpwODEKYVYvCmFzVnRyZWVfdGltZXN0YW1wCnA4MgpGMTM4MTc0MDQ5My45Mjc4NDMxCnMu"))
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(memory, self.cboptions, localindex, serverindex)
        return
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


    def test_mutation_history_file(self):
        """
        test_sync_delete_local_folder
        """
        self.complete_reset()
        self.reset_cb_db_clean()
        os.mkdir("testdata/testmap/foo")
        os.system("ls > testdata/testmap/foo/test.txt")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("rm -Rf testdata/testmap/foo/test.txt")
        dir_del_local, dir_del_server, dir_make_local, dir_make_server, file_del_local, file_del_server, file_downloads, file_uploads = self.get_sync_changes()
        self.assertEqual(len(file_del_server), 1)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        os.system("ls > testdata/testmap/foo/test.txt")
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

    def test_sync_delete_server_folder(self):
        """
        test_sync_delete_server_folder
        """
        self.reset_cb_db_clean()

        #self.unzip_testfiles_clean()
        os.makedirs("testdata/testmap/foo")
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions)
        dir_del_server = ['/foo']
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory = instruct_server_to_delete_folders(self.cbmemory, self.cboptions, serverindex, dir_del_server)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        cbmemory, cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex)
        self.assertEqual(len(dir_del_local), 1)

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

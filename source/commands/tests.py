# coding=utf-8
"""
unit test for app commands
"""
__author__ = 'rabshakeh'
import os
import time
import pickle
import unittest
import requests
from subprocess import Popen
from cba_main import run_app_command, ExitAppWarning
from cba_utils import dict2obj_new
from cba_index import make_local_index, index_and_encrypt
from cba_memory import Memory
from cba_blobs import get_blob_dir, get_data_dir
from cba_network import authorize_user, authorized
from cba_sync import get_server_index, parse_serverindex, parse_made_local, parse_removed_local
from cba_file import ensure_directory


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


class CryptoboxAppTestBasic(unittest.TestCase):
    """
    CryptoboTestCase
    """

    def setUp(self):
        """
        setUp
        """

        #SERVER = "https://www.cryptobox.nl/"
        os.system("rm -Rf testdata/testmap")
        os.system("cd testdata; unzip -o testmap.zip > /dev/null")
        self.options_d = {"dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/testmap",
                          "encrypt": True,
                          "username": "rabshakeh",
                          "password": "kjhfsd98",
                          "cryptobox": "test",
                          "clear": False,
                          "sync": False,
                          "fake": False,
                          "server": "http://127.0.0.1:8000/",
                          "numdownloadthreads": 2}

        self.cboptions = dict2obj_new(self.options_d)
        ensure_directory(self.cboptions.dir)
        self.memory = Memory()

    def tearDown(self):
        """
        tearDown
        """
        if self.memory.has("localindex"):
            self.memory.delete("localindex")
        self.memory.save(get_data_dir(self.cboptions))

        os.system("rm -Rf testdata/testmap")

    def test_index_no_box_given(self):
        """
        test_index
        """
        self.no_box_given = self.options_d.copy()
        self.no_box_given = dict2obj_new(self.no_box_given)
        del self.no_box_given["cryptobox"]

        with self.assertRaisesRegexp(ExitAppWarning, "No cryptobox given -b or --cryptobox"):
            run_app_command(self.no_box_given)

    def test_index_directory(self):
        """
        test_index
        """
        self.cboptions.sync = False
        localindex_check = pickle.load(open("testdata/localindex_test.pickle"))
        localindex = make_local_index(self.cboptions)
        self.assertTrue(localindex_check == localindex)

    def test_index_and_encrypt(self):
        """
        test_index_and_encrypt
        """
        localindex = make_local_index(self.cboptions)
        self.memory.replace("localindex", localindex)
        index_and_encrypt(self.cboptions)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 20)

        # add a new file
        open(os.path.join(self.cboptions.dir, "hello world.txt"), "w").write("hello world 123 Dit is random data")

        index_and_encrypt(self.cboptions)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 21)

        # same content, blob count should not raise

        open(os.path.join(self.cboptions.dir, "hello world2.txt"), "w").write("hello world 123 Dit is random data")

        index_and_encrypt(self.cboptions)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 21)


class CryptoboxAppTestServer(unittest.TestCase):
    """
    CryptoboTestCase
    """

    def setUp(self):
        """
        setUp
        """

        #SERVER = "https://www.cryptobox.nl/"
        os.system("rm -Rf testdata/testmap")

        #os.system("cd testdata; unzip -o testmap.zip > /dev/null")
        self.options_d = {"dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/testmap",
                          "encrypt": True,
                          "username": "rabshakeh",
                          "password": "kjhfsd98",
                          "cryptobox": "test",
                          "clear": False,
                          "sync": False,
                          "fake": False,
                          "server": "http://127.0.0.1:8000/",
                          "numdownloadthreads": 2}

        self.cboptions = dict2obj_new(self.options_d)
        self.memory = Memory()
        self.memory.set("cryptobox_folder", self.cboptions.dir)
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))
        self.pipe = Popen("python server/manage.py runserver 127.0.0.1:8000", shell=True, cwd="/Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl")
        django_starting = True

        while django_starting:
            try:
                requests.get("http://127.0.0.1:8000")
                django_starting = False
            except requests.ConnectionError:
                django_starting = True

    def tearDown(self):
        """
        tearDown
        """
        djangopid = os.popen("ps aux | grep manage").read()

        for l in djangopid.split("\n"):
            if "runserver 127.0.0.1:8000" in str(l):
                for i in range(0, 10):
                    l = l.replace("  ", " ")
                os.system("kill -9 "+l.split(" ")[1])

        if self.memory.has("localindex"):
            self.memory.delete("localindex")
        self.memory.save(get_data_dir(self.cboptions))

        #os.system("rm -Rf testdata/testmap")

    def test_new_tree(self):
        self.pipe = Popen("python server/manage.py load -c test", shell=True, cwd="/Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl")
        self.pipe.wait()

    def test_connection(self):
        """
        test_connection
        """
        self.memory = authorized(self.memory, self.cboptions)
        self.assertFalse(self.memory.get("authorized"))
        self.memory = authorize_user(self.memory, self.cboptions)
        self.assertTrue(self.memory.get("authorized"))
        self.memory = authorized(self.memory, self.cboptions)
        self.assertTrue(self.memory.get("authorized"))

    def test_get_server_tree(self):
        """
        test_get_server_tree
        """
        os.system("cd testdata; unzip -o testmap.zip > /dev/null")
        self.memory = authorize_user(self.memory, self.cboptions)
        self.assertTrue(self.memory.get("authorized"))
        self.memory = get_server_index(self.memory, self.cboptions)
        serverindex = self.memory.get("serverindex")
        serverindex_test = pickle.load(open("testdata/serverindex_test.pickle"))
        self.maxDiff = None
        self.assertEqual(serverindex, serverindex_test)

    def test_compare_server_with_local_tree(self):
        """
        test_compare_server_with_local_tree
        """
        self.memory = get_server_index(self.memory, self.cboptions)
        serverindex = self.memory.get("serverindex")
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        self.assertEqual(len(dirname_hashes_server), 4)
        self.assertEqual(len(fnodes), 9)
        self.assertEqual(len(unique_content), 4)

        self.memory.set("localindex", make_local_index(self.cboptions))
        dirs_to_make_on_server, dirs_to_remove_locally = parse_made_local(self.memory, self.cboptions, dirname_hashes_server, serverindex)
        self.assertEqual(len(dirs_to_make_on_server), 0)
        self.assertEqual(len(dirs_to_remove_locally), 0)
        dir_names_to_delete_on_server, memory = parse_removed_local(self.memory, self.cboptions, unique_dirs)
        self.assertEqual(len(dir_names_to_delete_on_server), 0)


if __name__ == '__main__':
    unittest.main()

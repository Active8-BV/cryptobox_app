# coding=utf-8
"""
unit test for app commands
"""
__author__ = 'rabshakeh'
import os
import pickle
import unittest
from cba_main import run_app_command, ExitAppWarning
from cba_utils import dict2obj_new
from cba_index import make_local_index, index_and_encrypt
from cba_memory import Memory
from cba_blobs import get_blob_dir, get_data_dir
from cba_network import authorize_user, authorized


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


class CryptoboxAppTest(unittest.TestCase):
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

        self.memory = Memory()

    def tearDown(self):
        """
        tearDown
        """
        self.memory.delete("localindex")
        self.memory.save(get_data_dir(self.cboptions))

        os.system("rm -Rf testdata/testmap")

    @unittest.skip("skip test_index_no_box_given")
    def test_index_no_box_given(self):
        """
        test_index
        """
        self.no_box_given = self.options_d.copy()
        self.no_box_given = dict2obj_new(self.no_box_given)
        del self.no_box_given["cryptobox"]

        with self.assertRaisesRegexp(ExitAppWarning, "No cryptobox given -b or --cryptobox"):
            run_app_command(self.no_box_given)

    @unittest.skip("skip test_index_directory")
    def test_index_directory(self):
        """
        test_index
        """
        self.cboptions.sync = False
        localindex_check = pickle.load(open("testdata/localindex_test.pickle"))
        localindex = make_local_index(self.cboptions)
        self.assertTrue(localindex_check == localindex)

    @unittest.skip("skip test_index_and_encrypt")
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

    @unittest.skip("skip test_connection")
    def test_connection(self):
        """
        test_connection
        """
        self.assertFalse(authorized(self.cboptions))
        self.assertTrue(authorize_user(self.cboptions))
        self.assertTrue(authorized(self.cboptions))

    #@unittest.skip("skip test_index_new_file")
    def test_index_new_file(self):
        """
        test_index_new_file
        """
        localindex = make_local_index(self.cboptions)


if __name__ == '__main__':
    unittest.main()

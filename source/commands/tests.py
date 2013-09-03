# coding=utf-8
"""
unit test for app commands
"""
__author__ = 'rabshakeh'
import os
import pickle
import unittest
from subprocess import Popen, PIPE
from cba_main import run_app_command, ExitAppWarning
from cba_utils import dict2obj_new
from cba_index import make_local_index, index_and_encrypt
from cba_memory import Memory
from cba_blobs import get_blob_dir, get_data_dir
from cba_network import authorize_user, authorized
from cba_sync import get_server_index, parse_serverindex, instruct_server_to_delete_folders, parse_removed_local, make_directories_local, parse_made_local, instruct_server_to_make_folders, sync_directories_with_server, diff_new_files_on_server, diff_new_files_locally, upload_file, get_unique_content, NoParentFound
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
        self.options_d = {"dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/testmap", "encrypt": True, "username": "rabshakeh", "password": "kjhfsd98", "cryptobox": "test", "clear": False, "sync": False, "fake": False, "server": "http://127.0.0.1:8000/", "numdownloadthreads": 2}
        self.cboptions = dict2obj_new(self.options_d)
        ensure_directory(self.cboptions.dir)
        self.memory = Memory()

    def tearDown(self):
        """
        tearDown
        """
        self.memory.save(get_data_dir(self.cboptions))

        os.system("rm -Rf testdata/testmap")

    def ignore_test_index_no_box_given(self):
        """
        test_index
        """
        self.no_box_given = self.options_d.copy()
        self.no_box_given = dict2obj_new(self.no_box_given)
        del self.no_box_given["cryptobox"]

        with self.assertRaisesRegexp(ExitAppWarning, "No cryptobox given -b or --cryptobox"):
            run_app_command(self.no_box_given)

    def ignore_test_index_directory(self):
        """
        test_index
        """
        self.cboptions.sync = False
        localindex_check = pickle.load(open("testdata/localindex_test.pickle"))
        localindex = make_local_index(self.cboptions)

        #pickle.dump(localindex, open("testdata/localindex_test.pickle", "w"))
        self.assertTrue(localindex_check == localindex)

    def ignore_test_index_and_encrypt(self):
        """
        test_index_and_encrypt
        """
        salt, secret, self.memory = index_and_encrypt(self.memory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 7)

        # add a new file
        open(os.path.join(self.cboptions.dir, "hello world.txt"), "w").write("hello world 123 Dit is random data")

        salt, secret, self.memory = index_and_encrypt(self.memory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 8)

        # same content, blob count should not rise
        open(os.path.join(self.cboptions.dir, "hello world2.txt"), "w").write("hello world 123 Dit is random data")

        salt, secret, self.memory = index_and_encrypt(self.memory, self.cboptions)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 8)


class CryptoboxAppTestServer(unittest.TestCase):
    """
    CryptoboTestCase
    """

    @staticmethod
    def kill_django():
        """
        kill_django
        """
        djangopid = os.popen("ps aux | grep manage").read()

        for l in djangopid.split("\n"):
            if "runserver 127.0.0.1:8000" in str(l):
                for i in range(0, 10):
                    l = l.replace("  ", " ")
                os.system("kill -9 " + l.split(" ")[1])
    def setUp(self):
        """
        setUp
        """

        #SERVER = "https://www.cryptobox.nl/"
        #os.system("cd testdata; unzip -o testmap.zip > /dev/null")
        self.options_d = {"dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/testmap", "encrypt": True, "username": "rabshakeh", "password": "kjhfsd98", "cryptobox": "test", "clear": False, "sync": False, "fake": False, "server": "http://127.0.0.1:8000/", "numdownloadthreads": 2}
        self.cboptions = dict2obj_new(self.options_d)
        self.memory = Memory()
        self.memory.set("cryptobox_folder", self.cboptions.dir)
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))
        self.kill_django()
        self.pipe = Popen("python server/manage.py runserver 127.0.0.1:8000", shell=True, stdout=PIPE, cwd="/Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl")
        os.system("wget -q -O '/dev/null' --retry-connrefused http://127.0.0.1:8000/")


    def tearDown(self):
        """
        tearDown
        """
        self.kill_django()
        self.memory.save(get_data_dir(self.cboptions))

    @staticmethod
    def unzip_testfiles_clean():
        """
        unzip_testfiles_clean
        """
        os.system("cd testdata; cp testmap_clean.zip testmap.zip")
        os.system("cd testdata; unzip -o testmap.zip > /dev/null")

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
        self.reset_cb_db()

    def complete_reset(self):
        """
        complete_reset
        """
        os.system("rm -Rf testdata/testmap")
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))

    def directories_synced(self):
        """
        directories_synced
        """
        serverindex, self.memory = get_server_index(self.memory, self.cboptions)
        localindex = make_local_index(self.cboptions)
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        dirs_to_make_on_server, dirs_to_remove_locally = parse_made_local(self.memory, self.cboptions, localindex, dirname_hashes_server, serverindex)
        return (len(dirs_to_make_on_server) == 0) and (len(dirs_to_remove_locally) == 0)

    def files_synced(self):
        """
        files_synced
        """
        serverindex, self.memory = get_server_index(self.memory, self.cboptions)
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        memory, files_to_delete_on_server, files_to_download = diff_new_files_on_server(self.memory, self.cboptions, fnodes)
        try:
            files_to_upload, self.memory = diff_new_files_locally(self.memory, self.cboptions)
        except NoParentFound:
            return False
        return (len(files_to_delete_on_server) == 0) and (len(files_to_download) == 0) and (len(files_to_upload) == 0)

    def ignore_test_connection(self):
        """
        test_connection
        """
        self.memory = authorized(self.memory, self.cboptions)
        self.assertFalse(self.memory.get("authorized"))
        self.memory = authorize_user(self.memory, self.cboptions)
        self.assertTrue(self.memory.get("authorized"))
        self.memory = authorized(self.memory, self.cboptions)
        self.assertTrue(self.memory.get("authorized"))

    def ignore_test_compare_server_tree_with_local_tree_folders(self):
        """
        test_compare_server_tree_with_local_tree_folders
        """
        self.complete_reset()
        self.reset_cb_db_clean()
        localindex = make_local_index(self.cboptions)
        serverindex, self.memory = get_server_index(self.memory, self.cboptions)
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        self.assertEqual(len(dirname_hashes_server), 4)
        self.assertEqual(len(fnodes), 8)
        self.assertEqual(len(unique_content), 3)

        # mirror the server structure to local
        dir_names_to_delete_on_server, dir_names_to_make_locally, memory = parse_removed_local(self.memory, self.cboptions, unique_dirs)
        self.assertEqual(len(dir_names_to_delete_on_server), 0)
        self.assertEqual(len(dir_names_to_make_locally), 3)

        # make dirs
        self.memory = make_directories_local(self.memory, self.cboptions, localindex, dir_names_to_make_locally)
        self.assertTrue(self.directories_synced())

        # mirror the local structure to server, remove a local directory
        os.system("rm -Rf testdata/testmap/map1")
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        dir_names_to_delete_on_server, dir_names_to_make_locally, memory = parse_removed_local(self.memory, self.cboptions, unique_dirs)
        self.assertEqual(len(dir_names_to_delete_on_server), 2)
        self.assertEqual(len(dir_names_to_make_locally), 0)
        self.memory.save(get_data_dir(self.cboptions))
        self.memory = instruct_server_to_delete_folders(self.memory, self.cboptions, serverindex, dir_names_to_delete_on_server)

        # check if we are the same now
        self.assertTrue(self.directories_synced())

        # unzip test files and make them on server
        self.unzip_testfiles_clean()
        localindex = make_local_index(self.cboptions)
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        dirs_to_make_on_server, dirs_to_remove_locally = parse_made_local(self.memory, self.cboptions, localindex, dirname_hashes_server, serverindex)
        self.assertFalse(self.directories_synced())

        serverindex, self.memory = instruct_server_to_make_folders(self.memory, self.cboptions, dirs_to_make_on_server)
        self.assertTrue(self.directories_synced())

    def ignore_test_compare_server_tree_with_local_tree_method_folders(self):
        """
        test_compare_server_tree_with_local_tree_method_folders
        """
        self.complete_reset()
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        serverindex, self.memory = sync_directories_with_server(self.memory, self.cboptions)
        self.assertTrue(self.directories_synced())

        # delete on server
        dir_names_to_delete_on_server = ['/map1']
        self.memory = instruct_server_to_delete_folders(self.memory, self.cboptions, serverindex, dir_names_to_delete_on_server)
        serverindex, self.memory = sync_directories_with_server(self.memory, self.cboptions)
        self.assertTrue(self.directories_synced())

        # delete local
        os.system("rm -Rf testdata/testmap/map2")
        serverindex, self.memory = sync_directories_with_server(self.memory, self.cboptions)
        self.assertTrue(self.directories_synced())

    def test_compare_clean_server_tree_with_local_tree_method_files(self):
        """
        test_compare_clean_server_tree_with_local_tree_method_files
        """
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()

        # build directories locally and on server
        serverindex, memory = get_server_index(self.memory, self.cboptions)
        dirname_hashes_server, file_nodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        serverindex, self.memory = sync_directories_with_server(self.memory, self.cboptions)
        self.assertTrue(self.directories_synced())

        # find new files on server
        self.memory, files_to_delete_on_server, files_to_download = diff_new_files_on_server(self.memory, self.cboptions, file_nodes)
        self.assertEqual(len(files_to_delete_on_server), 0)
        self.assertEqual(len(files_to_download), 5)

        # get the unique content and write to disk
        self.memory = get_unique_content(memory, self.cboptions, unique_content, files_to_download)

        # get new content locally and upload to server
        files_to_upload, self.memory = diff_new_files_locally(self.memory, self.cboptions)
        self.assertEqual(len(files_to_upload), 5)

        for uf in files_to_upload:
            self.memory = upload_file(self.memory, self.cboptions, open(uf.local_file_path, "rb"), uf.parent_short_id)
        self.assertTrue(self.files_synced())

    def ignore_test_compare_server_tree_with_local_tree_method_files(self):
        """
        test_compare_server_tree_with_local_tree_method_files
        """
        self.reset_cb_db_synced()
        self.unzip_testfiles_synced()

        # build directories locally and on server
        serverindex, memory = get_server_index(self.memory, self.cboptions)
        dirname_hashes_server, file_nodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        serverindex, self.memory = sync_directories_with_server(self.memory, self.cboptions)
        self.assertTrue(self.directories_synced())

        # find new files on server
        self.memory, files_to_delete_on_server, files_to_download = diff_new_files_on_server(self.memory, self.cboptions, file_nodes)
        self.assertEqual(len(files_to_delete_on_server), 0)
        self.assertEqual(len(files_to_download), 0)

        # get new content locally and upload to server
        files_to_upload, self.memory = diff_new_files_locally(self.memory, self.cboptions)
        self.assertEqual(len(files_to_download), 0)
        self.assertTrue(self.files_synced())


if __name__ == '__main__':
    unittest.main()

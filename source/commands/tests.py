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
from cba_index import make_local_index, index_and_encrypt, check_and_clean_dir
from cba_memory import Memory, del_local_file_history, del_server_file_history
from cba_blobs import get_blob_dir, get_data_dir
from cba_network import authorize_user, authorized
from cba_sync import get_server_index, parse_serverindex, instruct_server_to_delete_folders, \
    dirs_on_server, make_directories_local, dirs_on_local, instruct_server_to_make_folders, \
    sync_directories_with_server, diff_new_files_on_server, diff_files_locally, upload_file, \
    get_unique_content, instruct_server_to_delete_items, path_to_server_shortid, wait_for_tasks, \
    remove_local_files, sync_server
from cba_file import ensure_directory
from cba_tree import decrypt_and_build_filetree


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
        #os.system("cd testdata; unzip -o testmap.zip > /dev/null")
        self.options_d = {"dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/testmap", "encrypt": True, "remove": True, "username": "rabshakeh", "password": "kjhfsd98", "cryptobox": "test", "clear": False, "sync": False, "server": "http://127.0.0.1:8000/", "numdownloadthreads": 2}
        self.cboptions = dict2obj_new(self.options_d)
        self.cbmemory = Memory()
        self.cbmemory.set("cryptobox_folder", self.cboptions.dir)
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))
        self.do_wait_for_tasks = True

    def tearDown(self):
        """
        tearDown
        """
        if self.do_wait_for_tasks:
            wait_for_tasks(self.cbmemory, self.cboptions)
        self.cbmemory.save(get_data_dir(self.cboptions))

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
        self.reset_cb_db()

    def complete_reset(self):
        """
        complete_reset
        """
        os.system("rm -Rf testdata/testmap")
        ensure_directory(self.cboptions.dir)
        ensure_directory(get_data_dir(self.cboptions))

    def test_index_no_box_given(self):
        """
        test_index
        """
        self.do_wait_for_tasks = False
        self.no_box_given = self.options_d.copy()
        self.no_box_given = dict2obj_new(self.no_box_given)
        del self.no_box_given["cryptobox"]

        with self.assertRaisesRegexp(ExitAppWarning, "No cryptobox given -b or --cryptobox"):
            run_app_command(self.no_box_given)

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
        self.unzip_testfiles_clean()
        self.do_wait_for_tasks = False
        localindex = make_local_index(self.cboptions)
        salt, secret, self.cbmemory = index_and_encrypt(self.cbmemory, self.cboptions, localindex)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 7)

        # add a new file
        open(os.path.join(self.cboptions.dir, "hello world.txt"), "w").write("hello world 123 Dit is random data")

        localindex = make_local_index(self.cboptions)
        salt, secret, self.cbmemory = index_and_encrypt(self.cbmemory, self.cboptions, localindex)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 8)

        # same content, blob count should not rise
        open(os.path.join(self.cboptions.dir, "hello world2.txt"), "w").write("hello world 123 Dit is random data")

        localindex = make_local_index(self.cboptions)
        salt, secret, self.cbmemory = index_and_encrypt(self.cbmemory, self.cboptions, localindex)
        self.assertIsNotNone(salt)
        self.assertIsNotNone(secret)
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 8)

    def test_index_encrypt_decrypt_clean(self):
        """
        test_index_encrypt_decrypt_clean
        """
        self.do_wait_for_tasks = False
        self.unzip_testfiles_clean()
        os.system("rm -Rf " + get_blob_dir(self.cboptions))

        localindex1 = make_local_index(self.cboptions)
        self.cboptions.remove = True
        salt, secret, self.cbmemory, localindex1 = index_and_encrypt(self.cbmemory, self.cboptions, localindex1)
        self.assertEqual(count_files_dir(self.cboptions.dir), 9)
        self.cbmemory = decrypt_and_build_filetree(self.cbmemory, self.cboptions)
        os.system("rm -Rf " + get_blob_dir(self.cboptions))

        localindex2 = make_local_index(self.cboptions)
        salt, secret, self.cbmemory, localindex2 = index_and_encrypt(self.cbmemory, self.cboptions, localindex2)
        self.maxDiff = None

        def remove_atime(index):
            """
            remove_atime
            """

            def del_atime(ix, x):
                """
                del_atime
                """
                del ix[x]["st_atime"]
                del ix[x]["st_ctime"]

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
        salt, secret, self.cbmemory = index_and_encrypt(self.cbmemory, self.cboptions, localindex)
        self.cboptions.clear = True
        self.cboptions.encrypt = False
        check_and_clean_dir(self.cboptions)

    def directories_synced(self):
        """
        directories_synced
        """
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        localindex = make_local_index(self.cboptions)
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        dir_make_server, dir_del_local = dirs_on_local(self.cbmemory, self.cboptions, localindex, dirname_hashes_server, serverindex)
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

    def test_compare_server_tree_with_local_tree_folders(self):
        """
        test_compare_server_tree_with_local_tree_folders
        """
        self.complete_reset()
        self.reset_cb_db_clean()
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        self.assertEqual(len(dirname_hashes_server), 4)
        self.assertEqual(len(fnodes), 5)
        self.assertEqual(len(unique_content), 4)

        # mirror the server structure to local
        dir_del_server, dir_make_local, self.cbmemory = dirs_on_server(self.cbmemory, self.cboptions, unique_dirs)
        self.assertEqual(len(dir_del_server), 0)
        self.assertEqual(len(dir_make_local), 3)

        # make dirs
        self.cbmemory = make_directories_local(self.cbmemory, self.cboptions, localindex, dir_make_local)
        self.assertTrue(self.directories_synced())

        # mirror the local structure to server, remove a local directory
        os.system("rm -Rf testdata/testmap/map1")
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        dir_del_server, dir_make_local, self.cbmemory = dirs_on_server(self.cbmemory, self.cboptions, unique_dirs)
        self.assertEqual(len(dir_del_server), 2)
        self.assertEqual(len(dir_make_local), 0)
        self.cbmemory.save(get_data_dir(self.cboptions))
        self.cbmemory = instruct_server_to_delete_folders(self.cbmemory, self.cboptions, serverindex, dir_del_server)

        # check if we are the same now
        self.assertTrue(self.directories_synced())

        # unzip test files and make them on server
        self.unzip_testfiles_clean()
        localindex = make_local_index(self.cboptions)
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        dir_make_server, dir_del_local = dirs_on_local(self.cbmemory, self.cboptions, localindex, dirname_hashes_server, serverindex)
        self.assertFalse(self.directories_synced())

        serverindex, self.cbmemory = instruct_server_to_make_folders(self.cbmemory, self.cboptions, dir_make_server)
        self.assertTrue(self.directories_synced())

    def test_compare_server_tree_with_local_tree_method_folders(self):
        """
        test_compare_server_tree_with_local_tree_method_folders
        """
        self.complete_reset()
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory, dir_del_server = sync_directories_with_server(self.cbmemory, self.cboptions, localindex, serverindex)
        self.assertTrue(self.directories_synced())

        # delete on server
        dir_del_server = ['/map1']
        self.cbmemory = instruct_server_to_delete_folders(self.cbmemory, self.cboptions, serverindex, dir_del_server)

        # sync dirs again
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory, dir_del_server = sync_directories_with_server(self.cbmemory, self.cboptions, localindex, serverindex)
        self.assertTrue(self.directories_synced())

        # delete local
        os.system("rm -Rf testdata/testmap/map2")
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        self.cbmemory, dir_del_server = sync_directories_with_server(self.cbmemory, self.cboptions, localindex, serverindex)
        self.assertTrue(self.directories_synced())

    def test_sync_clean_tree(self):
        """
        test_sync_clean_tree
        """
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()

        # build directories locally and on server
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        dirname_hashes_server, server_file_nodes, unique_content, unique_dirs = parse_serverindex(serverindex)
        self.cbmemory, dir_del_server = sync_directories_with_server(self.cbmemory, self.cboptions, localindex, serverindex)
        self.assertTrue(self.directories_synced())

        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)

        # find new files on server
        self.cbmemory, file_del_server, file_downloads = diff_new_files_on_server(self.cbmemory, self.cboptions, server_file_nodes, dir_del_server)
        self.assertEqual(len(file_del_server), 0)
        self.assertEqual(len(file_downloads), 5)

        # get the unique content and write to disk
        self.cbmemory = get_unique_content(self.cbmemory, self.cboptions, unique_content, file_downloads)

        # get new content locally and upload to server
        localindex = make_local_index(self.cboptions)
        file_uploads, file_del_local, self.cbmemory = diff_files_locally(self.cbmemory, self.cboptions, localindex, serverindex)
        self.assertEqual(len(file_uploads), 5)
        self.assertEqual(len(file_del_local), 0)

        for uf in file_uploads:
            self.cbmemory = upload_file(self.cbmemory, self.cboptions, open(uf["local_file_path"], "rb"), uf["parent_short_id"])

        # remove local files
        remove_local_files(file_del_local)

        for fpath in file_del_server:
            self.cbmemory = del_server_file_history(self.cbmemory, fpath)
            self.cbmemory = del_local_file_history(self.cbmemory, fpath)

        for fpath in file_del_local:
            self.cbmemory = del_server_file_history(self.cbmemory, fpath)
            self.cbmemory = del_local_file_history(self.cbmemory, fpath)

        # should be in sync
        self.assertTrue(self.files_synced())

    def files_synced(self):
        """
        files_synced
        """
        file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local = self.get_sync_changes()

        for l in [file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local]:
            if len(l) != 0:
                return False
        return True

    def get_sync_changes(self):
        """
        get_sync_changes
        """
        localindex = make_local_index(self.cboptions)
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        dirname_hashes_server, server_file_nodes, unique_content, unique_dirs = parse_serverindex(serverindex)

        # server dirs
        dir_del_server, dir_make_local, self.cbmemory = dirs_on_server(self.cbmemory, self.cboptions, unique_dirs)

        #local dirs
        dir_make_server, dir_del_local = dirs_on_local(self.cbmemory, self.cboptions, localindex, dirname_hashes_server, serverindex)

        # find new files on server
        self.cbmemory, file_del_server, file_downloads = diff_new_files_on_server(self.cbmemory, self.cboptions, server_file_nodes, dir_del_server)

        #local files
        file_uploads, file_del_local, self.cbmemory = diff_files_locally(self.cbmemory, self.cboptions, localindex, serverindex)
        return file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local

    def test_sync_synced_tree_mutations_local(self):
        """
        test_sync_synced_tree_mutations_local
        """
        self.reset_cb_db_synced()
        self.unzip_testfiles_synced()
        self.cbmemory.load(get_data_dir(self.cboptions))
        self.cbmemory.delete("session")
        self.cbmemory.delete("authorized")
        os.system("date > testdata/testmap/map1/date.txt")
        os.system("mkdir testdata/testmap/map3")
        os.system("rm -Rf testdata/testmap/map2")
        os.system("rm -Rf testdata/testmap/all_types/word.docx")

        if not self.cbmemory.has("session"):
            self.cbmemory = authorize_user(self.cbmemory, self.cboptions)

        file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local = self.get_sync_changes()
        self.assertEqual(len(file_del_server), 1)
        self.assertEqual(len(file_downloads), 0)
        self.assertEqual(len(file_uploads), 1)
        self.assertEqual(len(dir_del_server), 1)
        self.assertEqual(len(dir_make_local), 0)
        self.assertEqual(len(dir_make_server), 1)
        self.assertEqual(len(dir_del_local), 0)
        self.assertEqual(len(file_del_local), 0)

    def test_sync_synced_tree_mutations_server(self):
        """
        test_sync_synced_tree_mutations_server
        """
        self.reset_cb_db_synced()
        self.unzip_testfiles_synced()
        self.cbmemory.load(get_data_dir(self.cboptions))
        self.cbmemory.delete("session")
        self.cbmemory.delete("authorized")

        if not self.cbmemory.has("session"):
            self.cbmemory = authorize_user(self.cbmemory, self.cboptions)

        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions)
        docpdf, self.cbmemory = path_to_server_shortid(self.cbmemory, self.cboptions, serverindex, '/all_types/document.pdf')
        bmppng, self.cbmemory = path_to_server_shortid(self.cbmemory, self.cboptions, serverindex, '/all_types/bmptest.png')
        self.cbmemory = instruct_server_to_delete_items(self.cbmemory, self.cboptions, [docpdf, bmppng])
        self.assertFalse(self.files_synced())

        file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local = self.get_sync_changes()

        # remove local files
        remove_local_files(file_del_local)

        for fpath in file_del_server:
            self.cbmemory = del_server_file_history(self.cbmemory, fpath)
            self.cbmemory = del_local_file_history(self.cbmemory, fpath)

        for fpath in file_del_local:
            self.cbmemory = del_server_file_history(self.cbmemory, fpath)
            self.cbmemory = del_local_file_history(self.cbmemory, fpath)
        self.assertEqual(len(file_del_server), 0)
        self.assertEqual(len(file_del_local), 2)
        self.assertEqual(len(file_downloads), 0)
        self.assertEqual(len(file_uploads), 0)
        self.assertEqual(len(dir_del_server), 0)
        self.assertEqual(len(dir_make_local), 0)
        self.assertEqual(len(dir_make_server), 0)
        self.assertEqual(len(dir_del_local), 0)

        os.system("ls > testdata/testmap/all_types/bmptest.png")
        file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local = self.get_sync_changes()
        self.assertEqual(len(file_uploads), 1)

    def test_sync_method_clean_tree(self):
        """
        test_sync_method_clean_tree
        """
        self.reset_cb_db_clean()
        self.unzip_testfiles_clean()
        localindex = make_local_index(self.cboptions)
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions, localindex)
        self.assertTrue(self.files_synced())

        os.system("ls > testdata/testmap/all_types/test.txt")
        self.assertFalse(self.files_synced())


if __name__ == '__main__':
    unittest.main()

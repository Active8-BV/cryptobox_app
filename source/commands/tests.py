# coding=utf-8 # ##^ comment 0
""" # ##^  1n 1n_python_comment 0
unit test for app commands # ##^ for statement prevented by None 1n 1n_python_comment 0
""" # ##^  0
__author__ = 'rabshakeh' # ##^ ass1gnment on global 0
import os # ##^  0
import pickle # ##^  0
import unittest # ##^  0
import random # ##^  0
from subprocess import Popen, PIPE # ##^  0
from cba_main import cryptobox_command # ##^  0
from cba_utils import Dict2Obj, run_in_pool # ##^  0
from cba_index import make_local_index, index_and_encrypt, check_and_clean_dir, decrypt_and_build_filetree # ##^  0
from cba_memory import Memory, del_local_file_history, del_server_file_history # ##^  0
from cba_blobs import get_blob_dir, get_data_dir # ##^  0
from cba_network import authorize_user, authorized # ##^  0
from cba_sync import get_server_index, parse_serverindex, instruct_server_to_delete_folders, \ # ##^  0
    dirs_on_server, make_directories_local, dirs_on_local, instruct_server_to_make_folders, \ # ##^  0
    instruct_server_to_delete_items, path_to_server_shortid, wait_for_tasks, \ # ##^  0
    remove_local_files, sync_server, get_sync_changes, short_id_to_server_path # ##^  0
from cba_file import ensure_directory # ##^  0
from cba_crypto import encrypt_file, decrypt_file, make_hash_str # ##^  0
from StringIO import StringIO # ##^  0
from Crypto import Random # ##^  0
import multiprocessing # ##^  0


def add(a, b): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    add # ##^  1n 1n_python_comment 0
    """ # ##^  0
    return a + b # ##^  after doc comment 0


def pc(p): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type p: int # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    """ # ##^  0
    print "tests.py:41", p # ##^ debug statement 0


def count_files_dir(fpath): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    count_files_dir # ##^  1n 1n_python_comment 0
    @type fpath: str, unicode # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    s = set() # ##^ methodcall and ass1gned  after  0

    for path, dirs, files in os.walk(fpath): # ##^ for statement 0
        for f in files: # ##^  0
            s.add(f) # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 0

    return len(s) # ##^  wh1tespace |  0


def encrypt_a_file(secret, pc, chunk): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    encrypt_a_file # ##^  1n 1n_python_comment 0
    """ # ##^  0
    Random.atfork() # ##^ methodcall after  0
    return encrypt_file(secret, StringIO(chunk), perc_callback=pc) # ##^  after keyword 0


def encrypt_file_smp(secret, fname): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type secret: str, unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    @type fname: str, unicode # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    stats = os.stat(fname) # ##^ methodcall and ass1gned  after  0
    chunksize = int(float(stats.st_size) / multiprocessing.cpu_count()) + 64 # ##^ ass1gnment 0
    chunklist = [] # ##^ ass1gnment 0
    with open(fname) as infile: # ##^ methodcall after ass1gnment 0
        chunk = infile.read(chunksize) # ##^ methodcall and ass1gned nested method call 0

        while chunk: # ##^ wh1le statement 0
            chunklist.append(chunk) # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 0
            chunk = infile.read(chunksize) # ##^ methodcall and ass1gned nested method call 0

    l = len(chunklist) # ##^ methodcall and ass1gned  method call h1gher scope 8 scope>2  0
    x = run_in_pool(chunklist, encrypt_a_file, base_params=(secret, pc)) # ##^ ass1gnment 0

#noinspection PyPep8Naming # ##^ no-1nspect1on 0


class CryptoboxAppTest(unittest.TestCase): # ##^ class def 0
    """ # ##^  1n 1n_python_comment 0
    CryptoboTestCase ADDTYPES # ##^  1n 1n_python_comment 0
    """ # ##^  0

    def setUp(self): # ##^ funct1on def nested somewhere f1rst method 0
        """ # ##^  1n 1n_python_comment 0
        setUp # ##^  1n 1n_python_comment 0
        """ # ##^  0

        #SERVER = "https://www.cryptobox.nl/" # ##^ comment -> member 1n1t1al1zat1on 0
        #os.system("cd testdata; unzip -o testmap.zip > /dev/null") # ##^ comment -> methodcall after comment 0
        #server = "https://www.cryptobox.nl/" # ##^ comment -> member 1n1t1al1zat1on 0
        server = "http://127.0.01:8000/" # ##^ ass1gnment 0
        self.options_d = {"dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testdata/testmap", "encrypt": True, "remove": False, "username": "rabshakeh", "password": "kjhfsd98", "cryptobox": "test", "clear": False, "sync": False, "server": server, "numdownloadthreads": 2} # ##^ ass1gnment 0
        self.cboptions = Dict2Obj(self.options_d) # ##^ methodcall and ass1gned method call data ass1gnment 0 0
        self.cbmemory = Memory() # ##^ methodcall and ass1gned nested method call 0
        self.cbmemory.set("cryptobox_folder", self.cboptions.dir) # ##^ methodcallnested method call 0
        ensure_directory(self.cboptions.dir) # ##^ methodcallnested method call 0
        ensure_directory(get_data_dir(self.cboptions)) # ##^  0
        self.do_wait_for_tasks = True # ##^ ass1gnment 0
        testfile_sizes = ["1MB.zip", "200MB.zip", "100MB.zip", "20MB.zip", "5MB.zip", "1GB.zip", "50MB.zip"] # ##^ ass1gnment 0

        for tfn in testfile_sizes: # ##^ for statement 0
            if not os.path.exists(os.path.join("testdata", tfn)): # ##^  1f statement 1
                os.system("cd testdata; nohup wget http://download.thinkbroadband.com/" + tfn + " &") # ##^ member 1n1t1al1zat1on 1

        #sys.stdout = open('stdout.txt', 'w') # ##^ comment -> methodcall and ass1gned  method call h1gher scope 8 scope>2  -1
        #sys.stderr = open('stderr.txt', 'w') # ##^ comment -> methodcall and ass1gned nested method call -1
    #noinspection PyPep8Naming # ##^ no-1nspect1on -1
    def tearDown(self): # ##^ funct1on def nested after keyword a python class after no 1nspect1on after no1nspect1on -1
        """ # ##^  1n 1n_python_comment -1
        tearDown # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        if self.do_wait_for_tasks: # ##^  1f statement on same scope 0
            wait_for_tasks(self.cbmemory, self.cboptions) # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 0
        self.cbmemory.save(get_data_dir(self.cboptions)) # ##^  0
        if os.path.exists('stdout.txt'): # ##^  1f statement on same scope 1
            os.remove('stdout.txt') # ##^ methodcallnested method call 1

        if os.path.exists('stderr.txt'): # ##^  1f statement scope change 1
            os.remove('stderr.txt') # ##^ methodcallnested method call 1

    @staticmethod # ##^ property  -1
    def unzip_testfiles_clean(): # ##^ funct1on def nested somewhere after property or kw -1
        """ # ##^  1n 1n_python_comment -1
        unzip_testfiles_clean # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        os.system("cd testdata; cp testmap_clean.zip testmap.zip") # ##^ methodcall after  -1
        os.system("cd testdata; unzip -o testmap.zip > /dev/null") # ##^ methodcallnested method call -1
        os.system("rm testdata/testmap.zip") # ##^ methodcallnested method call -1

    @staticmethod # ##^ property  -1
    def unzip_testfiles_synced(): # ##^ funct1on def nested somewhere after property or kw -1
        """ # ##^  1n 1n_python_comment -1
        unzip_testfiles_synced # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        os.system("cd testdata; cp testmap_synced.zip testmap.zip") # ##^ methodcall after  -1
        os.system("cd testdata; unzip -o testmap.zip > /dev/null") # ##^ methodcallnested method call -1
        os.system("rm testdata/testmap.zip") # ##^ methodcallnested method call -1

    def reset_cb_db(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        reset_cb_db_clean # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        os.system("rm -Rf testdata/testmap") # ##^ methodcall after  -1
        ensure_directory(self.cboptions.dir) # ##^ methodcallnested method call -1
        ensure_directory(get_data_dir(self.cboptions)) # ##^  -1

        os.system("wget -q -O '/dev/null' --retry-connrefused http://127.0.0.1:8000/") # ##^ methodcall not after ass1gnment -1
        os.system("cp testdata/test.dump /Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl") # ##^ methodcallnested method call -1
        self.pipe = Popen("nohup python server/manage.py load -c test", shell=True, stderr=PIPE, stdout=PIPE, cwd="/Users/rabshakeh/workspace/cryptobox/www_cryptobox_nl") # ##^ methodcall and ass1gned nested method call -1
        self.pipe.wait() # ##^ methodcallnested method call -1

    def reset_cb_db_clean(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        reset_cb_db_clean # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        os.system("cp testdata/test_clean.dump testdata/test.dump") # ##^ methodcall after  -1
        self.reset_cb_db() # ##^ methodcallnested method call -1
        os.system("rm testdata/test.dump") # ##^ methodcallnested method call -1

    def reset_cb_db_synced(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        reset_cb_db_synced # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        os.system("cp testdata/test_synced.dump testdata/test.dump") # ##^ methodcall after  -1
        self.reset_cb_db() # ##^ methodcallnested method call -1

    def complete_reset(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        complete_reset # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        os.system("echo 'flush_all' | nc localhost 11211") # ##^ methodcall after  -1
        os.system("rm -Rf testdata/testmap") # ##^ methodcallnested method call -1
        ensure_directory(self.cboptions.dir) # ##^ methodcallnested method call -1
        ensure_directory(get_data_dir(self.cboptions)) # ##^  -1

    def ignore_test_run_in_pool(self): # ##^ funct1on def nested somewhere a python class -1
        self.do_wait_for_tasks = False # ##^ ass1gnment -1

        items = [(x, x + random.randint(1, 10)) for x in range(0, 10)] # ##^ for statement -1
        res_items = [x[0]+x[1] for x in items] # ##^ ass1gnment -1
        res_items2 = run_in_pool(items, "add", add) # ##^ methodcall and ass1gned  after ass1gnmentmethod call after 1f 3lse or wtch -1
        self.assertEquals(res_items, res_items2) # ##^ methodcallnested method call -1

    def itest_encrypt_file(self): # ##^ funct1on def nested somewhere a python class -1
        self.do_wait_for_tasks = False # ##^ ass1gnment -1
        fname = "testdata/1MB.zip" # ##^ ass1gnment -1
        secret = '\xeb>M\x04\xc22\x96!\xce\xed\xbb.\xe1u\xc7\xe4\x07h<.\x87\xc9H\x89\x8aj\xb4\xb2b5}\x95' # ##^ ass1gnment -1
        data_hash, initialization_vector, chunk_sizes_d, enc_file, secret = encrypt_file(secret, open(fname), perc_callback=pc) # ##^ ass1gnment -1
        enc_data = enc_file.read() # ##^ methodcall and ass1gned  after ass1gnment -1
        org_data = (open(fname).read()) # ##^ ass1gnment -1
        self.assertNotEqual(make_hash_str(enc_data, "1"), make_hash_str(org_data, "1")) # ##^  -1

        enc_file.seek(0) # ##^ methodcall not after ass1gnment -1
        df = decrypt_file(secret, enc_file, data_hash, initialization_vector, chunk_sizes_d, perc_callback=pc) # ##^ methodcall and ass1gned nested method call -1
        dec_data = df.read() # ##^ methodcall and ass1gned nested method call -1
        org_data = (open(fname).read()) # ##^ ass1gnment -1
        self.assertEqual(make_hash_str(dec_data, "1"), make_hash_str(org_data, "1")) # ##^  -1

    def test_encrypt_file_smp(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        test_encrypt_file # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        self.do_wait_for_tasks = False # ##^ ass1gnment -1
        fname = "testdata/1MB.zip" # ##^ ass1gnment -1
        secret = '\xeb>M\x04\xc22\x96!\xce\xed\xbb.\xe1u\xc7\xe4\x07h<.\x87\xc9H\x89\x8aj\xb4\xb2b5}\x95' # ##^ ass1gnment -1
        pass # ##^  -1
        return # ##^  after keyword -1

        for chunk in chunklist: # ##^ for statement -1
            data_hash, initialization_vector, chunk_sizes_d, enc_file, secret = encrypt_file(secret, StringIO(chunk), perc_callback=pc) # ##^ ass1gnment -1

        return # ##^  wh1tespace |  -1

        enc_data = enc_file.read() # ##^ methodcall and ass1gned  not after ass1gnment -1
        org_data = (open(fname).read()) # ##^ ass1gnment -1
        self.assertNotEqual(make_hash_str(enc_data, "1"), make_hash_str(org_data, "1")) # ##^  -1

        enc_file.seek(0) # ##^ methodcall not after ass1gnment -1
        df = decrypt_file(secret, enc_file, data_hash, initialization_vector, chunk_sizes_d, perc_callback=pc) # ##^ methodcall and ass1gned nested method call -1
        dec_data = df.read() # ##^ methodcall and ass1gned nested method call -1
        org_data = (open(fname).read()) # ##^ ass1gnment -1
        self.assertEqual(make_hash_str(dec_data, "1"), make_hash_str(org_data, "1")) # ##^  -1

        #self.assertEqual(open(fname).read(), df.read()) # ##^ comment -> double method call -1

    def ignore_test_index_no_box_given(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        test_index # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        self.do_wait_for_tasks = False # ##^ ass1gnment -1
        self.no_box_given = self.options_d.copy() # ##^ methodcall and ass1gned method call data ass1gnment -1method call after 1f 3lse or wtch -1
        self.no_box_given = Dict2Obj(self.no_box_given) # ##^ methodcall and ass1gned nested method call -1
        del self.no_box_given["cryptobox"] # ##^  -1

        #with self.assertRaisesRegexp(ExitAppWarning, "No cryptobox given -b or --cryptobox"): # ##^ comment -> methodcall not after ass1gnment -1
        self.assertFalse(cryptobox_command(self.no_box_given)) # ##^  -1

    def ignore_test_index_directory(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        test_index # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        self.do_wait_for_tasks = False # ##^ ass1gnment -1
        os.system("rm -Rf testdata/testmap") # ##^ methodcall after ass1gnmentmethod call after 1f 3lse or wtch -1
        self.unzip_testfiles_clean() # ##^ methodcallnested method call -1
        self.cboptions.sync = False # ##^ ass1gnment -1
        localindex_check = pickle.load(open("testdata/localindex_test.pickle")) # ##^ ass1gnment -1
        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned  after ass1gnment -1

        #pickle.dump(localindex, open("testdata/localindex_test.pickle", "w")) # ##^ comment -1
        self.assertTrue(localindex_check == localindex) # ##^ methodcall after comment -1

    def ignore_test_index_and_encrypt(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        test_index_and_encrypt # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        self.unzip_testfiles_clean() # ##^ methodcall after  -1
        self.do_wait_for_tasks = False # ##^ ass1gnment -1
        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned  after ass1gnmentmethod call after 1f 3lse or wtch -1
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions, localindex) # ##^ methodcall and ass1gned nested method call -1
        self.assertIsNotNone(salt) # ##^ methodcallnested method call -1
        self.assertIsNotNone(secret) # ##^ methodcallnested method call -1
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 7) # ##^  -1

        # add a new file # ##^ comment -1
        open(os.path.join(self.cboptions.dir, "hello world.txt"), "w").write("hello world 123 Dit is random data") # ##^  -1

        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned  not after ass1gnment -1
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions, localindex) # ##^ methodcall and ass1gned nested method call -1
        self.assertIsNotNone(salt) # ##^ methodcallnested method call -1
        self.assertIsNotNone(secret) # ##^ methodcallnested method call -1
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 8) # ##^  -1

        # same content, blob count should not rise # ##^ comment -1
        open(os.path.join(self.cboptions.dir, "hello world2.txt"), "w").write("hello world 123 Dit is random data") # ##^  -1

        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned  not after ass1gnment -1
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions, localindex) # ##^ methodcall and ass1gned nested method call -1
        self.assertIsNotNone(salt) # ##^ methodcallnested method call -1
        self.assertIsNotNone(secret) # ##^ methodcallnested method call -1
        self.assertEqual(count_files_dir(get_blob_dir(self.cboptions)), 8) # ##^  -1

    def ignore_test_index_encrypt_decrypt_clean(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        test_index_encrypt_decrypt_clean # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        self.complete_reset() # ##^ methodcall after  -1
        self.reset_cb_db_clean() # ##^ methodcallnested method call -1
        self.do_wait_for_tasks = False # ##^ ass1gnment -1
        self.unzip_testfiles_clean() # ##^ methodcallmethod call data ass1gnment -1method call after 1f 3lse or wtch -1
        os.system("rm -Rf " + get_blob_dir(self.cboptions)) # ##^  -1

        localindex1 = make_local_index(self.cboptions) # ##^ methodcall and ass1gned  not after ass1gnment -1
        self.cboptions.remove = True # ##^ ass1gnment -1
        salt, secret, self.cbmemory, localindex1 = index_and_encrypt(self.cbmemory, self.cboptions, localindex1) # ##^ methodcall and ass1gned  after ass1gnment -1
        self.assertEqual(count_files_dir(self.cboptions.dir), 7) # ##^  -1
        self.cbmemory = decrypt_and_build_filetree(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned method call data ass1gnment -1 -1
        os.system("rm -Rf " + get_blob_dir(self.cboptions)) # ##^  -1

        localindex2 = make_local_index(self.cboptions) # ##^ methodcall and ass1gned  not after ass1gnment -1
        salt, secret, self.cbmemory, localindex2 = index_and_encrypt(self.cbmemory, self.cboptions, localindex2) # ##^ methodcall and ass1gned nested method call -1
        self.max_diff = None # ##^ ass1gnment -1

        def remove_atime(index): # ##^ funct1on def nested after ass1gnement after 1f or else -1
            """ # ##^  1n 1n_python_comment -1
            remove_atime # ##^  1n 1n_python_comment -1
            @type index: dict # ##^ property  1n 1n_python_comment -1
            """ # ##^  -1

            def del_atime(ix, k): # ##^ funct1on def nested somewhere -1
                """ # ##^  1n 1n_python_comment -1
                del_atime # ##^  1n 1n_python_comment -1
                @type ix: dict # ##^ property  1n 1n_python_comment -1
                @type k: dict # ##^ property  1n 1n_python_comment -1
                """ # ##^  -1
                del ix[k]["st_atime"] # ##^  -1
                del ix[k]["st_ctime"] # ##^  -1
                return ix # ##^  after keyword -1

            filestats = [del_atime(index["filestats"], x) for x in index["filestats"]] # ##^ for statement -1
            index["filestats"] = filestats[0] # ##^ ass1gnment -1
            return index # ##^ retrn |  -1

        localindex1 = remove_atime(localindex1) # ##^ methodcall and ass1gned  not after ass1gnment -1
        localindex2 = remove_atime(localindex2) # ##^ methodcall and ass1gned nested method call -1
        self.assertEquals(localindex1["filestats"], localindex2["filestats"]) # ##^ methodcallnested method call -1

    def ignore_test_index_clear(self): # ##^ funct1on def nested somewhere a python class -1
        self.do_wait_for_tasks = False # ##^ ass1gnment -1
        self.unzip_testfiles_clean() # ##^ methodcallmethod call data ass1gnment -1method call after 1f 3lse or wtch -1
        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned nested method call -1
        salt, secret, self.cbmemory, localindex = index_and_encrypt(self.cbmemory, self.cboptions, localindex) # ##^ methodcall and ass1gned nested method call -1
        self.cboptions.clear = True # ##^ ass1gnment -1
        self.cboptions.encrypt = False # ##^ ass1gnment -1
        self.cboptions.clear = "1" # ##^ ass1gnment -1
        check_and_clean_dir(self.cboptions) # ##^ methodcall after ass1gnment -1
        dd = get_data_dir(self.cboptions) # ##^ methodcall and ass1gned nested method call -1
        self.assertEquals(os.path.exists(dd), False) # ##^  -1

    def directories_synced(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        directories_synced # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned  after  -1
        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned nested method call -1
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex) # ##^ methodcall and ass1gned nested method call -1
        dir_make_server, dir_del_local = dirs_on_local(self.cbmemory, self.cboptions, localindex, dirname_hashes_server, serverindex) # ##^ methodcall and ass1gned nested method call -1
        return (len(dir_make_server) == 0) and (len(dir_del_local) == 0) # ##^  after keyword -1

    def ignore_test_connection(self): # ##^ funct1on def nested after keyword on prev1ous scope a python class -1
        """ # ##^  1n 1n_python_comment -1
        test_connection # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        self.cbmemory = authorized(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned  after  -1
        self.assertFalse(self.cbmemory.get("authorized")) # ##^  -1
        self.cbmemory = authorize_user(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned method call data ass1gnment -1 -1
        self.assertTrue(self.cbmemory.get("authorized")) # ##^  -1
        self.cbmemory = authorized(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned method call data ass1gnment -1 -1
        self.assertTrue(self.cbmemory.get("authorized")) # ##^  -1

    def ignore_test_compare_server_tree_with_local_tree_folders(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        test_compare_server_tree_with_local_tree_folders # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        self.complete_reset() # ##^ methodcall after  -1
        self.reset_cb_db_clean() # ##^ methodcallnested method call -1
        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned nested method call -1
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call -1
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex) # ##^ methodcall and ass1gned nested method call -1
        self.assertEqual(len(dirname_hashes_server), 4) # ##^  -1
        self.assertEqual(len(fnodes), 5) # ##^  -1
        self.assertEqual(len(unique_content), 4) # ##^  -1

        # mirror the server structure to local # ##^ comment -1
        dir_del_server, dir_make_local, self.cbmemory = dirs_on_server(self.cbmemory, self.cboptions, unique_dirs) # ##^ methodcall and ass1gned  after comment -1
        self.assertEqual(len(dir_del_server), 0) # ##^  -1
        self.assertEqual(len(dir_make_local), 3) # ##^  -1

        # make dirs # ##^ comment -1
        self.cbmemory = make_directories_local(self.cbmemory, self.cboptions, localindex, dir_make_local) # ##^ methodcall and ass1gned  after comment -1
        self.assertTrue(self.directories_synced()) # ##^  -1

        # mirror the local structure to server, remove a local directory # ##^ comment -1
        os.system("rm -Rf testdata/testmap/map1") # ##^ methodcall after comment -1
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex) # ##^ methodcall and ass1gned nested method call -1
        dir_del_server, dir_make_local, self.cbmemory = dirs_on_server(self.cbmemory, self.cboptions, unique_dirs) # ##^ methodcall and ass1gned nested method call -1
        self.assertEqual(len(dir_del_server), 2) # ##^  -1
        self.assertEqual(len(dir_make_local), 0) # ##^  -1
        self.cbmemory.save(get_data_dir(self.cboptions)) # ##^  -1
        self.cbmemory = instruct_server_to_delete_folders(self.cbmemory, self.cboptions, serverindex, dir_del_server) # ##^ methodcall and ass1gned method call data ass1gnment -1 -1

        # check if we are the same now # ##^ comment -1
        self.assertTrue(self.directories_synced()) # ##^  -1

        # unzip test files and make them on server # ##^ comment -1
        self.unzip_testfiles_clean() # ##^ methodcall after comment -1
        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned nested method call -1
        dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex) # ##^ methodcall and ass1gned nested method call -1
        dir_make_server, dir_del_local = dirs_on_local(self.cbmemory, self.cboptions, localindex, dirname_hashes_server, serverindex) # ##^ methodcall and ass1gned nested method call -1
        self.assertFalse(self.directories_synced()) # ##^  -1

        serverindex, self.cbmemory = instruct_server_to_make_folders(self.cbmemory, self.cboptions, dir_make_server) # ##^ methodcall and ass1gned  not after ass1gnment -1
        self.assertTrue(self.directories_synced()) # ##^  -1

    def ignore_test_compare_server_tree_with_local_tree_method_folders(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        test_compare_server_tree_with_local_tree_method_folders # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        self.complete_reset() # ##^ methodcall after  -1
        self.reset_cb_db_clean() # ##^ methodcallnested method call -1
        self.unzip_testfiles_clean() # ##^ methodcallnested method call -1
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call -1
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call -1
        self.assertTrue(self.directories_synced()) # ##^  -1

        # delete on server # ##^ comment -1
        dir_del_server = ['/map1'] # ##^ ass1gnment -1
        self.cbmemory = instruct_server_to_delete_folders(self.cbmemory, self.cboptions, serverindex, dir_del_server) # ##^ methodcall and ass1gned  after ass1gnment -1

        # sync dirs again # ##^ comment -1
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned  after comment -1
        self.assertTrue(self.directories_synced()) # ##^  -1

        # delete local # ##^ comment -1
        os.system("rm -Rf testdata/testmap/map2") # ##^ methodcall after comment -1
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call -1
        self.assertTrue(self.directories_synced()) # ##^  -1

    def ignore_test_sync_clean_tree(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        test_sync_clean_tree # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        self.reset_cb_db_clean() # ##^ methodcall after  -1
        self.unzip_testfiles_clean() # ##^ methodcallnested method call -1

        # build directories locally and on server # ##^ comment -1
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned  after comment -1
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call -1
        self.assertTrue(self.directories_synced()) # ##^  -1
        self.assertTrue(self.files_synced()) # ##^  -1

    def ignore_test_upload(self): # ##^ funct1on def nested somewhere a python class -1
        """ # ##^  1n 1n_python_comment -1
        test_upload # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        self.reset_cb_db_clean() # ##^ methodcall after  -1
        self.unzip_testfiles_clean() # ##^ methodcallnested method call -1
        pass # ##^  -1

    def files_synced(self): # ##^ funct1on def nested after keyword on prev1ous scope a python class -1
        """ # ##^  1n 1n_python_comment -1
        files_synced # ##^  1n 1n_python_comment -1
        """ # ##^  -1
        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned  after  -1
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call -1
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex) # ##^ methodcall and ass1gned nested method call -1

        for l in [file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local]: # ##^ for statement -1
            if len(l) != 0: # ##^  1f statement 0
                return False # ##^  after keyword 0
        return True # ##^  after keyword 0

    def ignore_test_sync_synced_tree_mutations_local(self): # ##^ funct1on def nested after keyword on prev1ous scope a python class 0
        """ # ##^  1n 1n_python_comment 0
        test_sync_synced_tree_mutations_local # ##^  1n 1n_python_comment 0
        """ # ##^  0
        self.reset_cb_db_synced() # ##^ methodcall after  0
        self.unzip_testfiles_synced() # ##^ methodcallnested method call 0
        self.cbmemory.load(get_data_dir(self.cboptions)) # ##^  0
        self.cbmemory.delete("session") # ##^ methodcallmethod call data ass1gnment 0 0
        self.cbmemory.delete("authorized") # ##^ methodcallnested method call 0
        os.system("date > testdata/testmap/map1/date.txt") # ##^ methodcallnested method call 0
        os.system("mkdir testdata/testmap/map3") # ##^ methodcallnested method call 0
        os.system("rm -Rf testdata/testmap/map2") # ##^ methodcallnested method call 0
        os.system("rm -Rf testdata/testmap/all_types/word.docx") # ##^ methodcallnested method call 0

        if not self.cbmemory.has("session"): # ##^  1f statement on same scope after method call 1
            self.cbmemory = authorize_user(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call 1

        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned  method call h1gher scope 4 scope>2  0
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call 0
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex) # ##^ methodcall and ass1gned nested method call 0
        self.assertEqual(len(file_del_server), 1) # ##^  0
        self.assertEqual(len(file_downloads), 0) # ##^  0
        self.assertEqual(len(file_uploads), 1) # ##^  0
        self.assertEqual(len(dir_del_server), 1) # ##^  0
        self.assertEqual(len(dir_make_local), 0) # ##^  0
        self.assertEqual(len(dir_make_server), 1) # ##^  0
        self.assertEqual(len(dir_del_local), 0) # ##^  0
        self.assertEqual(len(file_del_local), 0) # ##^  0

    def ignore_test_sync_synced_tree_mutations_server(self): # ##^ funct1on def nested after keyword on prev1ous scope a python class 0
        """ # ##^  1n 1n_python_comment 0
        test_sync_synced_tree_mutations_server # ##^  1n 1n_python_comment 0
        """ # ##^  0
        self.reset_cb_db_synced() # ##^ methodcall after  0
        self.unzip_testfiles_synced() # ##^ methodcallnested method call 0
        self.cbmemory.load(get_data_dir(self.cboptions)) # ##^  0
        self.cbmemory.delete("session") # ##^ methodcallmethod call data ass1gnment 0 0
        self.cbmemory.delete("authorized") # ##^ methodcallnested method call 0

        if not self.cbmemory.has("session"): # ##^  1f statement on same scope after method call 1
            self.cbmemory = authorize_user(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call 1

        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned  method call h1gher scope 4 scope>2  0
        docpdf, self.cbmemory = path_to_server_shortid(self.cbmemory, self.cboptions, serverindex, '/all_types/document.pdf') # ##^ methodcall and ass1gned nested method call 0
        bmppng, self.cbmemory = path_to_server_shortid(self.cbmemory, self.cboptions, serverindex, '/all_types/bmptest.png') # ##^ methodcall and ass1gned nested method call 0
        self.cbmemory = instruct_server_to_delete_items(self.cbmemory, self.cboptions, serverindex, [docpdf, bmppng]) # ##^ methodcall and ass1gned nested method call 0
        self.assertFalse(self.files_synced()) # ##^  0

        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned  not after ass1gnment 0
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex) # ##^ methodcall and ass1gned nested method call 0

        # remove local files # ##^ comment 0
        remove_local_files(file_del_local) # ##^ methodcall after comment 0

        for fpath in file_del_server: # ##^ for statement 0
            self.cbmemory = del_server_file_history(self.cbmemory, fpath) # ##^ methodcall and ass1gned  not after ass1gnmentmethod call after 1f 3lse or wtch 0
            self.cbmemory = del_local_file_history(self.cbmemory, fpath) # ##^ methodcall and ass1gned nested method call 0

        for fpath in file_del_local: # ##^ for statement 0
            self.cbmemory = del_server_file_history(self.cbmemory, fpath) # ##^ methodcall and ass1gned  not after ass1gnmentmethod call after 1f 3lse or wtch 0
            self.cbmemory = del_local_file_history(self.cbmemory, fpath) # ##^ methodcall and ass1gned nested method call 0
        self.assertEqual(len(file_del_server), 0) # ##^  0
        self.assertEqual(len(file_del_local), 0) # ##^  0
        self.assertEqual(len(file_downloads), 0) # ##^  0
        self.assertEqual(len(file_uploads), 0) # ##^  0
        self.assertEqual(len(dir_del_server), 0) # ##^  0
        self.assertEqual(len(dir_make_local), 0) # ##^  0
        self.assertEqual(len(dir_make_server), 0) # ##^  0
        self.assertEqual(len(dir_del_local), 0) # ##^  0

    def ignore_test_sync_method_clean_tree(self): # ##^ funct1on def nested after keyword on prev1ous scope a python class 0
        """ # ##^  1n 1n_python_comment 0
        test_sync_method_clean_tree # ##^  1n 1n_python_comment 0
        """ # ##^  0
        self.reset_cb_db_clean() # ##^ methodcall after  0
        self.unzip_testfiles_clean() # ##^ methodcallnested method call 0
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call 0
        self.assertTrue(self.files_synced()) # ##^  0

        os.system("ls > testdata/testmap/all_types/test.txt") # ##^ methodcall not after ass1gnment 0
        self.assertFalse(self.files_synced()) # ##^  0

    def ignore_test_sync_conflict_folder(self): # ##^ funct1on def nested somewhere a python class 0
        """ # ##^  1n 1n_python_comment 0
        remove a folder on server and add same folder locally # ##^  1n 1n_python_comment 0
        """ # ##^  0
        self.reset_cb_db_synced() # ##^ methodcall after  0
        self.unzip_testfiles_synced() # ##^ methodcallnested method call 0
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call 0
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call 0
        os.system("ls > testdata/testmap/all_types/listing.txt") # ##^ methodcallnested method call 0
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call 0
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex) # ##^ methodcall and ass1gned nested method call 0
        self.assertEqual(len(file_uploads), 1) # ##^  0

    def ignore_test_find_short_ids(self): # ##^ funct1on def nested somewhere a python class 0
        """ # ##^  1n 1n_python_comment 0
        test_find_short_ids # ##^  1n 1n_python_comment 0
        """ # ##^  0
        self.reset_cb_db_clean() # ##^ methodcall after  0
        self.unzip_testfiles_clean() # ##^ methodcallnested method call 0
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call 0
        map1 = '/map1' # ##^ ass1gnment 0
        map1_short_id, self.cbmemory = path_to_server_shortid(self.cbmemory, self.cboptions, serverindex, '/map1') # ##^ methodcall and ass1gned  after ass1gnment 0
        map1_2, self.cbmemory = short_id_to_server_path(self.cbmemory, serverindex, map1_short_id) # ##^ methodcall and ass1gned nested method call 0
        self.assertEqual(map1, map1_2) # ##^ methodcallnested method call 0

    def ignore_test_sync_delete_server_and_local_restore_folder(self): # ##^ funct1on def nested somewhere a python class 0
        """ # ##^  1n 1n_python_comment 0
        test_sync_delete_server_and_local_restore_folder # ##^  1n 1n_python_comment 0
        """ # ##^  0
        self.reset_cb_db_clean() # ##^ methodcall after  0
        self.unzip_testfiles_clean() # ##^ methodcallnested method call 0
        localindex, self.cbmemory = sync_server(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call 0
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call 0
        all_types, self.cbmemory = path_to_server_shortid(self.cbmemory, self.cboptions, serverindex, '/all_types') # ##^ methodcall and ass1gned nested method call 0
        self.cbmemory = instruct_server_to_delete_items(self.cbmemory, self.cboptions, serverindex, [all_types]) # ##^ methodcall and ass1gned nested method call 0
        os.system("rm -Rf testdata/testmap/all_types") # ##^ methodcallnested method call 0
        self.assertTrue(os.path.exists("testdata/testmap")) # ##^  0
        self.assertFalse(os.path.exists("testdata/testmap/all_types")) # ##^  0
        self.unzip_testfiles_clean() # ##^ methodcallmethod call data ass1gnment 0 0
        localindex = make_local_index(self.cboptions) # ##^ methodcall and ass1gned nested method call 0
        serverindex, self.cbmemory = get_server_index(self.cbmemory, self.cboptions) # ##^ methodcall and ass1gned nested method call 0
        self.cbmemory, self.cboptions, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(self.cbmemory, self.cboptions, localindex, serverindex) # ##^ methodcall and ass1gned nested method call 0
        self.assertEqual(len(file_uploads), 3) # ##^  0
        self.assertEqual(len(dir_del_local), 0) # ##^  0
        self.assertEqual(len(dir_make_server), 1) # ##^  0


if __name__ == '__main__': # ##^ ma1n 1
    unittest.main() # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 1

 # ##^ global_class_declare 0

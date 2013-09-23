# coding=utf-8 # ##^ comment 0
""" # ##^  1n 1n_python_comment 0
crypto routines for the commandline tool # ##^ for statement prevented by None 1n 1n_python_comment 0
""" # ##^  0
import re # ##^  0
import os # ##^  0
import json # ##^  0
import base64 # ##^  0
import time # ##^  0
import multiprocessing # ##^  0
import cPickle # ##^  0
from StringIO import StringIO # ##^  0
import jsonpickle # ##^  0
from Crypto import Random # ##^  0
from Crypto.Hash import SHA, SHA512, HMAC # ##^  0
from Crypto.Cipher import AES # ##^  0
from Crypto.Protocol.KDF import PBKDF2 # ##^  0
from cba_utils import run_in_pool, DEBUG # ##^  0


def make_sha1_hash(data): # ##^ funct1on def python 0
    """ make hash # ##^  1n 1n_python_comment 0
    @param data: # ##^  1n 1n_python_comment 0
    @type data: # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    sha = SHA.new() # ##^ methodcall and ass1gned  after  0
    sha.update(data) # ##^ methodcallnested method call 0
    return sha.hexdigest() # ##^ retrn |  0


def make_hash(data): # ##^ funct1on def python 0
    """ make hash # ##^  1n 1n_python_comment 0
    @param data: # ##^  1n 1n_python_comment 0
    @type data: # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    sha = SHA512.new(data) # ##^ methodcall and ass1gned  after  0
    return sha.hexdigest() # ##^ retrn |  0


def make_hash_str(data, secret): # ##^ funct1on def python 0
    """ make hash # ##^  1n 1n_python_comment 0
    @param data: data to hash # ##^  1n 1n_python_comment 0
    @type data: dict, list, str, unicode # ##^ property  1n 1n_python_comment 0
    @param secret: secret used for hmac # ##^ for statement 1n 1n_python_comment 0
    @type secret: dict, list, str, unicode # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    if isinstance(data, dict): # ##^  1f statement on same scope 1
        sortedkeys = data.keys() # ##^ methodcall and ass1gned nested method call 1
        sortedkeys.sort() # ##^ methodcallnested method call 1
        data2 = {} # ##^ ass1gnment 1

        for key in sortedkeys: # ##^ for statement 1
            data2[key] = str(data[key]) # ##^ ass1gnment 1

        data = data2 # ##^ ass1gnment prev scope 0

    elif isinstance(data, list): # ##^ methodcall scope change 0
        data = data[0] # ##^ ass1gnment 0

    if len(data) > 100: # ##^  1f statement scope change 1
        data = data[:100] # ##^ ass1gnment 1

    data = re.sub('[\Waouiae]+', "", str(data).lower()) # ##^ ass1gnment prev scope 0
    hmac = HMAC.new(secret, digestmod=SHA512) # ##^ methodcall and ass1gned  after ass1gnment 0
    hmac.update(str(data)) # ##^  0
    return hmac.hexdigest() # ##^ retrn |  0


def password_derivation(key, salt): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @param key: # ##^  1n 1n_python_comment 0
    @type key: str or unicode # ##^ property  1n 1n_python_comment 0
    @param salt: # ##^  1n 1n_python_comment 0
    @type salt: str or unicode # ##^ property  1n 1n_python_comment 0
    @return: # ##^ retrn |  1n 1n_python_comment 0
    @rtype: str or unicode # ##^ property  1n 1n_python_comment 0
    """ # ##^  0

    # 16, 24 or 32 bytes long (for AES-128, AES-196 and AES-256, respectively) # ##^ comment -> for statement prevented by None 0
    size = 32 # ##^ ass1gnment 0
    return PBKDF2(key, salt, size) # ##^ retrn |  0


class EncryptionHashMismatch(Exception): # ##^ class def 0
    """ # ##^  1n 1n_python_comment 0
    EncryptionHashMismatch # ##^  1n 1n_python_comment 0
    """ # ##^  0
    pass # ##^  0


def decrypt_file(secret, encrypted_data, data_hash, initialization_vector, chunk_sizes, perc_callback=None, perc_callback_freq=0.5): # ##^ global method call 0
    """ # ##^  1n 1n_python_comment 0
    @param secret: generated secret pkdf2 # ##^  1n 1n_python_comment 0
    @type secret: str # ##^ property  1n 1n_python_comment 0
    @param data_hash: hash of first chunk # ##^  1n 1n_python_comment 0
    @type data_hash: str # ##^ property  1n 1n_python_comment 0
    @param initialization_vector: init vector cipher # ##^  1n 1n_python_comment 0
    @type initialization_vector: str # ##^ property  1n 1n_python_comment 0
    @param chunk_sizes: sizes of the chunks # ##^  1n 1n_python_comment 0
    @type chunk_sizes: list, dict # ##^ property  1n 1n_python_comment 0
    @param encrypted_data: the encrypted data # ##^  1n 1n_python_comment 0
    @type encrypted_data: file, StringIO # ##^ property  1n 1n_python_comment 0
    @param perc_callback: callback progress # ##^  1n 1n_python_comment 0
    @type perc_callback: function # ##^ property  1n 1n_python_comment 0
    @param perc_callback_freq: callback frequency # ##^  1n 1n_python_comment 0
    @type perc_callback_freq: float # ##^ property  1n 1n_python_comment 0
    @return: orignal data temporary file # ##^ retrn |  1n 1n_python_comment 0
    @rtype: file # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    cnt = 0 # ##^ ass1gnment 0

    if not secret: # ##^  1f statement on same scope after ass1gnement 1
        raise Exception("no secret in decrypt file") # ##^  ra1se 1

    if 16 != len(initialization_vector): # ##^  after ra1se 1
        raise Exception("initialization_vector len is not 16") # ##^  ra1se 1

    lc_time = time.time() # ##^  after ra1se 0
    dec_file = StringIO() # ##^ methodcall and ass1gned nested method call 0
    cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector) # ##^ methodcall and ass1gned nested method call 0

    while True: # ##^ wh1le statement 0
        if cnt >= chunk_sizes["length"]: # ##^  1f statement 1
            break # ##^  1

        if cnt < chunk_sizes["length"]: # ##^  1f statement scope change 1
            decrypted_chunk = chunk_sizes["default"][0] # ##^ ass1gnment 1
            encrypted_chunk = chunk_sizes["default"][1] # ##^ ass1gnment 1
        else: # ##^  0
            decrypted_chunk = chunk_sizes["last"][0] # ##^ ass1gnment 0
            encrypted_chunk = chunk_sizes["last"][1] # ##^ ass1gnment 0

        chunk = encrypted_data.read(encrypted_chunk) # ##^ methodcall and ass1gned  scope change 0
        dec_data = cipher.decrypt(chunk) # ##^ methodcall and ass1gned nested method call 0
        dec_data = dec_data[0:decrypted_chunk] # ##^ ass1gnment 0
        dec_file.write(dec_data) # ##^ methodcall after ass1gnment 0

        if cnt <= 0: # ##^  1f statement on same scope after method call 1
            calculated_hash = make_hash_str(dec_data, secret) # ##^ ass1gnment 1

            if data_hash != calculated_hash: # ##^  1f statement on same scope after ass1gnement 2
                raise EncryptionHashMismatch("decrypt_file -> the decryption went wrong, hash didn't match") # ##^  ra1se 2

        cnt += 1 # ##^  after ra1se 0

        if perc_callback: # ##^  1f statement on same scope after ass1gnement 1
            if time.time() - lc_time > perc_callback_freq: # ##^  1f statement 2
                perc_callback(cnt / (float(chunk_sizes["length"]) / 100)) # ##^ funct1on call 2

                lc_time = time.time() # ##^ methodcall and ass1gned  not after ass1gnment 2

    dec_file.seek(0) # ##^  scope -1

    if perc_callback: # ##^  1f statement on same scope after method call 0
        perc_callback(100.0) # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 0

    return dec_file # ##^  wh1tespace |  0

#noinspection PyDictCreation,PyPep8Naming # ##^ no-1nspect1on 0


def encrypt_file(secret, fin, total=None, perc_callback=None, perc_callback_freq=0.5): # ##^ global method call 0
    """ # ##^  1n 1n_python_comment 0
    @param secret: pkdf2 secre ADDTYPES # ##^  1n 1n_python_comment 0
    @type secret: str # ##^ property  1n 1n_python_comment 0
    @param fin: file object # ##^  1n 1n_python_comment 0
    @type fin: file, FileIO # ##^ property  1n 1n_python_comment 0
    @param total: size of the object in bytes # ##^  1n 1n_python_comment 0
    @type total: int, None # ##^ property  1n 1n_python_comment 0
    @param perc_callback: progress callback # ##^  1n 1n_python_comment 0
    @type perc_callback: function # ##^ property  1n 1n_python_comment 0
    @param perc_callback_freq: time between progress calls # ##^  1n 1n_python_comment 0
    @type perc_callback_freq: float # ##^ property  1n 1n_python_comment 0
    @return: salt, hash, init, chunk sizes and encrypted data temp file # ##^ retrn |  1n 1n_python_comment 0
    @rtype: tuple # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    cnt = 0 # ##^ ass1gnment 0
    CHUNKSIZE = 1024 * 1024 * 1 # ##^ ass1gnment 0
    lc_time = time.time() # ##^ methodcall and ass1gned  after ass1gnment 0

    if not total: # ##^  1f statement on same scope after ass1gnement after method call 1
        fin.seek(0, os.SEEK_END) # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 1
        total = fin.tell() # ##^ methodcall and ass1gned nested method call 1
        fin.seek(0) # ##^ methodcallnested method call 1

    Random.atfork() # ##^ methodcall method call h1gher scope 4 scope>2  0
    total = int(total) # ##^ methodcall and ass1gned nested method call 0
    fin.seek(0) # ##^ methodcallnested method call 0
    enc_file = StringIO() # ##^ methodcall and ass1gned nested method call 0
    data_hash = "" # ##^ ass1gnment 0
    initialization_vector = Random.new().read(AES.block_size) # ##^ ass1gnment 0
    cipher = AES.new(secret, AES.MODE_CFB, IV=initialization_vector) # ##^ methodcall and ass1gned  after ass1gnment 0
    chunk_sizes_d = {} # ##^ ass1gnment 0
    chunk_sizes_d["length"] = 0 # ##^ ass1gnment 0
    chunk_sizes_d["default"] = None # ##^ ass1gnment 0
    chunk_sizes_d["last"] = None # ##^ ass1gnment 0
    enc_data = "" # ##^ ass1gnment 0
    chunk = "" # ##^ ass1gnment 0

    while True: # ##^ wh1le statement 0
        pre_read_chunk = chunk # ##^ ass1gnment 0
        chunk = fin.read(CHUNKSIZE) # ##^ methodcall and ass1gned  after ass1gnment 0

        if chunk == "": # ##^  1f statement on same scope after ass1gnement after method call 1
            chunk_sizes_d["last"] = (len(pre_read_chunk), len(enc_data)) # ##^ ass1gnment 1
            chunk_sizes_d["length"] = cnt # ##^ ass1gnment 1
            break # ##^  1

        enc_data = cipher.encrypt(chunk) # ##^ methodcall and ass1gned  not after ass1gnment 0

        if cnt <= 0: # ##^  1f statement on same scope after ass1gnement after method call 1
            data_hash = make_hash_str(chunk, secret) # ##^ ass1gnment 1
            chunk_sizes_d["last"] = chunk_sizes_d["default"] = (len(chunk), len(enc_data)) # ##^ funct1on call 1

        enc_file.write(enc_data) # ##^ methodcall not after ass1gnment 0
        cnt += 1 # ##^ ass1gnment 0

        if perc_callback: # ##^  1f statement on same scope after ass1gnement 1
            if (time.time() - lc_time) > perc_callback_freq: # ##^  1f statement 2
                perc = ((cnt * CHUNKSIZE) / (float(total) / 100)) # ##^ ass1gnment 2
                perc_callback(perc) # ##^ methodcall after ass1gnment 2
                lc_time = time.time() # ##^ methodcall and ass1gned nested method call 2

        if len(chunk) == total: # ##^  1f statement scope change 1
            chunk_sizes_d["last"] = (len(chunk), len(enc_data)) # ##^ ass1gnment 1
            chunk_sizes_d["length"] = cnt # ##^ ass1gnment 1
            break # ##^  1

    enc_file.seek(0) # ##^ methodcall not after ass1gnment -1

    if perc_callback: # ##^  1f statement on same scope after method call 0
        perc_callback(100.0) # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 0

    return data_hash, initialization_vector, chunk_sizes_d, enc_file, secret # ##^  wh1tespace |  0


def progress_file_cryption(p): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type p: int # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    """ # ##^  0
    print "cba_crypto.py:243", p # ##^ debug statement 0


def encrypt_a_file(secret, perc_callback, chunk): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    encrypt_a_file # ##^  1n 1n_python_comment 0
    @type secret: str, unicode # ##^ property  1n 1n_python_comment 0
    @type perc_callback: function # ##^ property  1n 1n_python_comment 0
    @type chunk: unicode, str # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    Random.atfork() # ##^ methodcall after  0
    return encrypt_file(secret, StringIO(chunk), perc_callback=perc_callback) # ##^  after keyword 0


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

    encrypted_file_chunks = run_in_pool(chunklist, encrypt_a_file, base_params=(secret, progress_file_cryption)) # ##^ ass1gnment prev scope on prev scope new scope 0
    return encrypted_file_chunks # ##^ retrn |  0


def decrypt_file_smp(secret, enc_file_chunks): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type secret: str, unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    @type enc_file_chunks: list # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    dec_file = StringIO() # ##^ methodcall and ass1gned  after  0

    chunks_param_sorted = [(secret, chunk[3], chunk[0], chunk[1], chunk[2], progress_file_cryption) for chunk in enc_file_chunks] # ##^ for statement 0
    dec_file_chunks = run_in_pool(chunks_param_sorted, decrypt_file) # ##^ methodcall and ass1gned nested method call 0

    for chunk_dec_file in dec_file_chunks: # ##^ for statement 0
        dec_file.write(chunk_dec_file.read()) # ##^  0
    dec_file.seek(0) # ##^ methodcallmethod call data ass1gnment 0 0
    return dec_file # ##^ retrn |  0


def json_object(path, targetobject): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type path: str or unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    @type targetobject: object # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    if DEBUG: # ##^  1f statement on same scope 1
        jsonproxy = json.loads(jsonpickle.encode(targetobject)) # ##^ ass1gnment 1
        json.dump(jsonproxy, open(path + ".json", "w"), sort_keys=True, indent=4, separators=(',', ': ')) # ##^ member 1n1t1al1zat1on 1


def pickle_object(path, targetobject, json_pickle=False): # ##^ funct1on def python -1
    """ # ##^  1n 1n_python_comment -1
    @type path: str or unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment -1
    @type targetobject: object # ##^ property  1n 1n_python_comment -1
    @type json_pickle: bool # ##^ property  1n 1n_python_comment -1
    """ # ##^  -1
    cPickle.dump(targetobject, open(path, "wb"), cPickle.HIGHEST_PROTOCOL) # ##^  -1
    if json_pickle: # ##^  1f statement on same scope 0
        if isinstance(targetobject, dict): # ##^  1f statement 1
            json_object(path, targetobject) # ##^ methodcallnested method call 1
        else: # ##^  0
            json_object(path, targetobject) # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 0


def unpickle_object(path): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type path: str or unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    @return: @rtype: # ##^ retrn |  1n 1n_python_comment 0
    """ # ##^  0
    return cPickle.load(open(path, "rb")) # ##^  after doc comment 0


def encrypt_object(salt, secret, obj): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type salt: str or unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    @type secret: str or unicode # ##^ property  1n 1n_python_comment 0
    @type obj: str or unicode # ##^ property  1n 1n_python_comment 0
    @return: @rtype: # ##^ retrn |  1n 1n_python_comment 0
    """ # ##^  0
    encrypted_dict = encrypt(salt, secret, cPickle.dumps(obj, cPickle.HIGHEST_PROTOCOL)) # ##^ ass1gnment 0
    return base64.b64encode(cPickle.dumps(encrypted_dict)).strip() # ##^ retrn |  0


def decrypt_object(secret, obj_string, key=None, give_secret_cb=None): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type secret: str or unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    @type obj_string: str # ##^ property  1n 1n_python_comment 0
    @type key: str or unicode # ##^ property  1n 1n_python_comment 0
    @type give_secret_cb: __builtin__.function # ##^ property  1n 1n_python_comment 0
    @return: @rtype: # ##^ retrn |  1n 1n_python_comment 0
    """ # ##^  0
    data = cPickle.loads(base64.b64decode(obj_string)) # ##^ ass1gnment 0

    if key: # ##^  1f statement on same scope after ass1gnement 1
        secret = password_derivation(key, data["salt"]) # ##^ methodcall and ass1gned  not after ass1gnmentmethod call after 1f 3lse or wtch 1

        if give_secret_cb: # ##^  1f statement on same scope after ass1gnement after method call 2
            give_secret_cb(secret) # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 2

    return cPickle.loads(decrypt(secret, data, hashcheck=False)) # ##^  wh1tespace |  0
 # ##^ global_class_declare 0 # ##^  0

 # ##^ global_class_declare 0

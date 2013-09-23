# coding=utf-8 # ##^ comment 0
""" # ##^  1n 1n_python_comment 0
file operations # ##^  1n 1n_python_comment 0
""" # ##^  0
import os # ##^  0
from cba_utils import handle_exception, strcmp, log # ##^ except 0
from cba_crypto import pickle_object, unpickle_object, make_sha1_hash, encrypt_file # ##^  0


def ensure_directory(path): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type path: str or unicode or unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    """ # ##^  0
    if not os.path.exists(path): # ##^  1f statement on same scope 1
        log("making", path) # ##^ funct1on call 1
        os.makedirs(path) # ##^  1


def write_file(path, data, a_time, m_time, st_mode, st_uid, st_gid): # ##^ funct1on def python -1
    """ # ##^  1n 1n_python_comment -1
    @type path: unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment -1
    @type data: str or unicode # ##^ property  1n 1n_python_comment -1
    @type a_time: int # ##^ property  1n 1n_python_comment -1
    @type m_time: int # ##^ property  1n 1n_python_comment -1
    @type st_mode: __builtin__.NoneType # ##^ property  1n 1n_python_comment -1
    @type st_uid: __builtin__.NoneType # ##^ property  1n 1n_python_comment -1
    @type st_gid: __builtin__.NoneType # ##^ property  1n 1n_python_comment -1
    """ # ##^  -1
    fout = open(path, "wb") # ##^ ass1gnment -1
    fout.write(data) # ##^  -1
    fout.close() # ##^  -1
    os.utime(path, (a_time, m_time)) # ##^  -1
    if st_mode: # ##^  1f statement on same scope 0
        os.chmod(path, st_mode) # ##^  0

    if st_uid and st_gid: # ##^  1f statement scope change 1
        os.chown(path, st_uid, st_gid) # ##^  1


def read_file(path, read_data=False): # ##^ funct1on def python -1
    """ # ##^  1n 1n_python_comment -1
    @type path: str or unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment -1
    @type read_data: bool # ##^ property  1n 1n_python_comment -1
    @return: @rtype: # ##^ retrn |  1n 1n_python_comment -1
    """ # ##^  -1
    if read_data: # ##^  1f statement on same scope 0
        data = open(path, "rb").read() # ##^ ass1gnment 0
    else: # ##^  0
        data = None # ##^ ass1gnment 0

    stats = os.stat(path) # ##^ ass1gnment prev scope 0
    return stats.st_ctime, stats.st_atime, stats.st_mtime, stats.st_mode, stats.st_uid, stats.st_gid, data # ##^ retrn |  0


def read_file_to_fdict(path, read_data=False): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type path: str or unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    @type read_data: bool # ##^ property  1n 1n_python_comment 0
    @return: @rtype: ADDTYPES # ##^ retrn |  1n 1n_python_comment 0
    """ # ##^  0
    ft = read_file(path, read_data) # ##^ ass1gnment 0
    file_dict = {"st_ctime": int(ft[0]), # ##^ ass1gnment 0
                 "st_atime": int(ft[1]), # ##^ funct1on call 0
                 "st_mtime": int(ft[2]), # ##^ funct1on call 0
                 "st_mode": int(ft[3]), # ##^ funct1on call 0
                 "st_uid": int(ft[4]), # ##^ funct1on call 0
                 "st_gid": int(ft[5])} # ##^ funct1on call 0

    if read_data: # ##^  scope 1
        file_dict["data"] = ft[6] # ##^ ass1gnment 1

    return file_dict # ##^  wh1tespace |  0


def write_fdict_to_file(fdict, path): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @param fdict: dict # ##^  1n 1n_python_comment 0
    @type fdict: # ##^ property  1n 1n_python_comment 0
    @param path: str or unicode # ##^  1n 1n_python_comment 0
    @type path: # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    write_file(path, fdict["data"], fdict["st_atime"], fdict["st_mtime"], fdict["st_mode"], fdict["st_uid"], fdict["st_gid"]) # ##^ funct1on call 0


def read_and_encrypt_file(fpath, blobpath, secret): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type fpath: str or unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    @type blobpath: str or unicode # ##^ property  1n 1n_python_comment 0
    @type salt: str or unicode # ##^ property  1n 1n_python_comment 0
    @type secret: str or unicode # ##^ property  1n 1n_python_comment 0
    @return: @rtype: # ##^ retrn |  1n 1n_python_comment 0
    """ # ##^  0

    try: # ##^ try 0

        #file_dict = read_file_to_fdict(fpath) # ##^ comment -> ass1gnment 0
        encrypted_file_dict = {} # ##^ ass1gnment 0
        data_hash, initialization_vector_p64s, chunk_sizes, encrypted_data, secret = encrypt_file(secret, open(fpath), perc_callback=enc_callback) # ##^ ass1gnment 0

        #encrypt_file_smp # ##^ comment 0
        encrypted_file_dict["data_hash"] = data_hash # ##^ ass1gnment 0
        encrypted_file_dict["initialization_vector_p64s"] = initialization_vector_p64s # ##^ ass1gnment 0
        encrypted_file_dict["chunk_sizes"] = chunk_sizes # ##^ ass1gnment 0
        encrypted_file_dict["encrypted_data"] = encrypted_data # ##^ ass1gnment 0

        #encrypted_file_dict = encrypt(salt, secret, file_dict["data"]) # ##^ comment -> ass1gnment 0
        pickle_object(blobpath, encrypted_file_dict) # ##^ funct1on call 0
        return None # ##^ retrn |  0
    except Exception, e: # ##^ except 0
        handle_exception(e) # ##^ funct1on call 0


def decrypt_file_and_write(fpath, unenc_path, secret): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @type fpath: str or unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment 0
    @type unenc_path: str or unicode # ##^ property  1n 1n_python_comment 0
    @type secret: str or unicode # ##^ property  1n 1n_python_comment 0
    @return: @rtype: # ##^ retrn |  1n 1n_python_comment 0
    """ # ##^  0

    try: # ##^ try 0
        encrypted_file_dict = unpickle_object(fpath) # ##^ ass1gnment 0
        unencrypted_file_dict = decrypt(secret, encrypted_file_dict) # ##^ ass1gnment 0
        open(unenc_path, "wb").write(unencrypted_file_dict) # ##^  0
        return None # ##^ retrn |  0
    except Exception, e: # ##^ except 0
        handle_exception(e) # ##^ funct1on call 0


def decrypt_write_file(cryptobox_index, fdir, fhash, secret): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @param cryptobox_index: dict # ##^  1n 1n_python_comment 0
    @type cryptobox_index: # ##^ property  1n 1n_python_comment 0
    @param fdir: str or unicode # ##^  1n 1n_python_comment 0
    @type fdir: # ##^ property  1n 1n_python_comment 0
    @param fhash: str or unicode # ##^  1n 1n_python_comment 0
    @type fhash: # ##^ property  1n 1n_python_comment 0
    @param secret: str or unicode # ##^  1n 1n_python_comment 0
    @type secret: # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    blob_enc = unpickle_object(os.path.join(fdir, fhash[2:])) # ##^ ass1gnment 0
    file_blob = {"data": decrypt(secret, blob_enc)} # ##^ ass1gnment 0
    paths = [] # ##^ ass1gnment 0

    for dirhash in cryptobox_index["dirnames"]: # ##^ for statement 0
        for cfile in cryptobox_index["dirnames"][dirhash]["filenames"]: # ##^  0
            if strcmp(fhash, cfile["hash"]): # ##^  1f statement 1
                fpath = os.path.join(cryptobox_index["dirnames"][dirhash]["dirname"], cfile["name"]) # ##^ ass1gnment 1

                if not os.path.exists(fpath): # ##^  1f statement on same scope after ass1gnement 2
                    ft = cryptobox_index["filestats"][fpath] # ##^ ass1gnment 2
                    file_blob["st_atime"] = int(ft["st_atime"]) # ##^ ass1gnment 2
                    file_blob["st_mtime"] = int(ft["st_mtime"]) # ##^ ass1gnment 2
                    file_blob["st_mode"] = int(ft["st_mode"]) # ##^ ass1gnment 2
                    file_blob["st_uid"] = int(ft["st_uid"]) # ##^ ass1gnment 2
                    file_blob["st_gid"] = int(ft["st_gid"]) # ##^ ass1gnment 2
                    write_fdict_to_file(file_blob, fpath) # ##^ funct1on call 2
                    paths.append(fpath) # ##^  2

    return paths # ##^  scope -2


def make_cryptogit_hash(fpath, datadir, localindex): # ##^ funct1on def python -2
    """ # ##^  1n 1n_python_comment -2
    @type fpath: str or unicode # ##^ member 1n1t1al1zat1on 1n 1n_python_comment -2
    @type datadir: str or unicode # ##^ property  1n 1n_python_comment -2
    @type localindex: dict # ##^ property  1n 1n_python_comment -2
    @return: @rtype: # ##^ retrn |  1n 1n_python_comment -2
    """ # ##^  -2
    file_dict = read_file_to_fdict(fpath, read_data=True) # ##^ ass1gnment -2
    filehash = make_sha1_hash("blob " + str(len(file_dict["data"])) + "\0" + str(file_dict["data"])) # ##^ ass1gnment -2
    blobdir = os.path.join(os.path.join(datadir, "blobs"), filehash[:2]) # ##^ ass1gnment -2
    blobpath = os.path.join(blobdir, filehash[2:]) # ##^ ass1gnment -2
    filedata = {"filehash": filehash, # ##^ ass1gnment -2
                "fpath": fpath, # ##^ member 1n1t1al1zat1on -2
                "blobpath": blobpath, # ##^ member 1n1t1al1zat1on -2
                "blobdir": blobdir, # ##^ member 1n1t1al1zat1on -2
                "blob_exists": os.path.exists(blobpath)} # ##^ member 1n1t1al1zat1on -2

    del file_dict["data"] # ##^  scope -2
    localindex["filestats"][fpath] = file_dict # ##^ ass1gnment -2
    return filedata, localindex # ##^ retrn |  -2
 # ##^ global_class_declare -2 # ##^  -2 # ##^  -2 # ##^  -2
 # ##^ global_class_declare -2 # ##^  -2 # ##^  -2
 # ##^ global_class_declare -2 # ##^  -2

 # ##^ global_class_declare -2

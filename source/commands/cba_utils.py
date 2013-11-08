# coding=utf-8
"""
some utility functions
"""
import os
import sys
import math
import time
import threading
import multiprocessing
import uuid as _uu
import cPickle
import json
import subprocess
import jsonpickle
from Crypto.Hash import SHA
last_update_string_len = 0
g_lock = multiprocessing.Lock()
DEBUG = True
from multiprocessing import Pool


def open_folder(path):
    """
    :param path:
    """
    if sys.platform == 'darwin':
        subprocess.check_call(['open', '--', path])
    elif sys.platform == 'linux2':
        subprocess.check_call(['gnome-open', '--', path])
    elif sys.platform == 'windows':
        subprocess.check_call(['explorer', path])


def make_sha1_hash_utils(data):
    """ make hash
    @param data:
    @type data:
    """
    sha = SHA.new()
    sha.update(data)
    return sha.hexdigest()


def json_object(path, targetobject):
    """
    @type path: str or unicode
    @type targetobject: object
    """
    if DEBUG:
        jsonproxy = json.loads(jsonpickle.encode(targetobject))
        json.dump(jsonproxy, open(path + ".json", "w"), sort_keys=True, indent=4, separators=(',', ': '))


def pickle_object(path, targetobject, json_pickle=False):
    """
    @type path: str or unicode
    @type targetobject: object
    @type json_pickle: bool
    """
    cPickle.dump(targetobject, open(path, "wb"), cPickle.HIGHEST_PROTOCOL)
    if json_pickle:
        if isinstance(targetobject, dict):
            json_object(path, targetobject)
        else:
            json_object(path, targetobject)


def unpickle_object(path):
    """
    @type path: str or unicode
    @return: @rtype:
    """
    return cPickle.load(open(path, "rb"))


def output(msg):
    """
    @type msg: str, unicode
    """
    msg = str(msg)
    sys.stdout.write(msg)
    sys.stdout.write("\n")
    sys.stdout.flush()


def output_json(dict_obj):
    """
    @type dict_obj: dict
    """
    output(json.dumps(dict_obj))


def smp_all_cpu_apply(method, items, progress_callback=None):
    """
    @type method: function
    @type items: list
    @type progress_callback: function
    """
    pool = Pool(processes=multiprocessing.cpu_count())
    results_cnt = [0]
    last_update = [time.time()]

    def progress_callback_wrapper(result_func):
        """
        progress_callback
        @type result_func: object
        """
        if progress_callback:
            now = time.time()
            results_cnt[0] += 1
            perc = float(results_cnt[0]) / (float(len(items)) / 100)

            if results_cnt[0] == 1 and perc == 100:
                pass
            else:
                if now - last_update[0] > 0.1:
                    if perc > 100:
                        perc = 100
                    progress_callback(perc)
                    last_update[0] = now

        return result_func

    calculation_result = []

    for item in items:
        base_params_list = []

        if isinstance(item, tuple):
            for i in item:
                base_params_list.append(i)
        else:
            base_params_list.append(item)

        params = tuple(base_params_list)
        result = pool.apply_async(method, params, callback=progress_callback_wrapper)
        calculation_result.append(result)
    pool.close()
    pool.join()
    calculation_result_values = []

    for result in calculation_result:
        if not result.successful():
            result.get()
        else:
            calculation_result_values.append(result.get())
    pool.terminate()
    if progress_callback_wrapper:
        progress_callback_wrapper(100)

    return calculation_result_values


def exist(data):
    """
    @param data:
    @type data:
    @return: @rtype:
    """
    data = str(data).strip()

    if not data:
        return False

    elif str(data) == "":
        return False

    elif len(str(data)) == 0:
        return False

    elif str(data) == "False":
        return False

    elif str(data) == "false":
        return False

    elif str(data) == "undefined":
        return False

    elif str(data) == "null":
        return False

    elif str(data) == "none":
        return False

    elif str(data) == "None":
        return False
    return True


class Dict2Obj(dict):
    """
    Dict2Obj
    """

    def __init__(self, dict_):
        super(Dict2Obj, self).__init__(dict_)

        for key in self:
            item = self[key]

            if isinstance(item, list):
                for idx, it in enumerate(item):
                    if isinstance(it, dict):
                        item[idx] = Dict2Obj(it)

            elif isinstance(item, dict):
                self[key] = Dict2Obj(item)

    def __getattr__(self, key):

        # Enhanced to handle key not found.
        if key in self:
            return self[key]
        else:
            return None


def strcmp(s1, s2):
    """
    @type s1: str or unicode
    @type s2: str or unicode
    @return: @rtype: bool
    """
    s1 = str(s1)
    s2 = str(s2)

    if not s1 or not s2:
        return False

    s1 = s1.strip()
    s2 = s2.strip()
    return s1 == s2


def exit_app_warning(*arg):
    """
    exit_app_warning
    @param arg: list objects
    @type arg:
    """
    print "cba_utils.py:243", arg
    sys.exit(1)


def timestamp_to_string(ts, short=False):
    """Return the current time formatted for logging.
    Return the current time formatted for logging.timestamp_to_string
    @param ts: time string
    @type ts: string, unicode
    @param short: display format
    @type short: bool
    """
    monthname = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    year, month, day, hh, mm, ss, x, y, z = time.localtime(ts)

    if short:
        year -= 2000
        s = "%d-%d-%d %02d:%02d:%02d" % (day, month, year, hh, mm, ss)
    else:
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (day, monthname[month], year, hh, mm, ss)

    return s


def error_prefix():
    """
    error_prefix
    """
    return ">"


#noinspection PyUnresolvedReferences
def handle_exception(again=True, ret_err=False):
    """
    @param again: bool
    @type again:
    @param ret_err: bool
    @type ret_err:
    """
    import sys
    import traceback
    if again and ret_err:
        raise Exception("handle_exception, raise_again and ret_err can't both be true")

    exc_type, exc_value, exc_traceback = sys.exc_info()
    error = error_prefix() + " ---------------------------\n"
    error += error_prefix() + "   !!! EXCEPTION !!!\n"
    error += error_prefix() + " ---------------------------\n"
    error += error_prefix() + " " + str(exc_type) + "\n"
    error += error_prefix() + " " + str(exc_value) + "\n"
    error += error_prefix() + " ---------------------------\n"
    stack = traceback.format_exception(exc_type, exc_value, exc_traceback)
    stack.reverse()

    for line in stack:
        error += line

    if ret_err:
        return error
    else:
        import sys
        sys.stderr.write(str(error))

    if again:
        raise exc

    return error


def get_uuid(size):
    """
    make a human readable unique identifier
    @param size:
    @type size:
    """
    unique_id = _uu.uuid4().int
    alphabet = "bcdfghjkmnpqrstvwxz"
    alphabet_length = len(alphabet)
    output_guid = ""

    while unique_id > 0:
        digit = unique_id % alphabet_length
        output_guid += alphabet[digit]
        unique_id = int(unique_id / alphabet_length)

    return output_guid[0:size]


class MemoryNoKey(Exception):
    """
    MemoryNoKey
    """
    pass


class MemoryExpired(Exception):
    """
    MemoryExpired
    """
    pass


class ListNameClash(Exception):
    """
    ListNameClash
    """
    pass


class ListDoesNotExist(Exception):
    """
    ListDoesNotExist
    """
    pass


class MemoryCorruption(Exception):
    """
    MemoryCorruption
    """
    pass


memory_lock = threading.Lock()


class Memory(object):
    """
    Memory
    """

    def __init__(self):
        """
        @return: Memory instance
        @rtype: Memory
        """
        self.data = {}
        self.m_locked = False

    def set(self, key, value):
        """
        @type key: string, unicode
        @type value: string, unicode
        """
        if key in self.data:
            raise MemoryCorruption("overwrite of " + str(key))

        self.data[key] = value

    def get(self, key):
        """
        @type key: string, unicode
        """
        if self.has(key):
            return self.data[key]
        else:
            raise MemoryNoKey(str(key))

    def has_get(self, key):
        """
        @type key: string, unicode
        """
        if self.has(key):
            return self.data[key]
        else:
            return None

    def delete(self, key):
        """
        @type key: string, unicode
        """
        if self.has(key):
            del self.data[key]
        else:
            raise MemoryNoKey(str(key))

    def has(self, key):
        """
        @type key: string, unicode
        """
        return key in self.data

    def replace(self, key, value):
        """
        @type key: string, unicode
        @type value: string, unicode
        """
        if self.has(key):
            self.delete(key)
        self.set(key, value)

    def size(self):
        """
        size
        """
        return len(self.data)

    def lock(self):
        """
        lock
        """
        if not self.m_locked:
            global memory_lock
            memory_lock.acquire()
            self.m_locked = True

    def unlock(self):
        """
        unlock
        """
        global memory_lock
        memory_lock.release()
        self.m_locked = False

    def save(self, datadir, keep_lock=False):
        """
        @type datadir: string, unicode
        @type keep_lock: bool
        """

        #noinspection PyBroadException
        try:
            self.lock()
            if os.path.exists(datadir):
                mempath = os.path.join(datadir, "memory.pickle")
                pickle_object(mempath, self.data, json_pickle=True)
        finally:
            if not keep_lock:
                self.unlock()

    def load(self, datadir, keep_lock=False):
        """
        @type datadir: string, unicode
        @type keep_lock: bool
        """

        #noinspection PyBroadException
        try:
            self.lock()
            mempath = os.path.join(datadir, "memory.pickle")

            if os.path.exists(mempath):
                #noinspection PyAttributeOutsideInit
                self.data = unpickle_object(mempath)

                for k in self.data.copy():
                    try:
                        self.has(k)
                    except MemoryExpired:
                        pass
                return True
        finally:
            if not keep_lock:
                self.unlock()

        return False

    def set_add_value(self, list_name, value):
        """
        @type list_name: string, unicode
        @type value: string, unicode
        """
        if not self.has(list_name):
            self.set(list_name, set())

        collection = self.get(list_name)

        if not isinstance(collection, set):
            raise ListNameClash(collection + " is not a list")

        collection.add(value)

    def set_have_value(self, list_name, value):
        """
        @type list_name: string, unicode
        @type value: string, unicode
        """
        if not self.has(list_name):
            self.set(list_name, set())
            return False

        collection = self.get(list_name)

        for v in collection:
            if value == v:
                return True
        return False

    def set_delete_value(self, list_name, value):
        """
        @type list_name: string, unicode
        @type value: string, unicode
        """
        if not self.has(list_name):
            return False

        collection = self.get(list_name)
        collection.remove(value)
        return True


def update_item_progress(p):
    """
    update_progress
    @type p:int
    """

    try:
        if 0 < int(p) <= 100:
            output_json({"item_progress": p})
    except Exception:
        handle_exception(False)


def update_progress(curr, total, msg):
    """
    @type curr: int
    @type total: int
    @type msg: str or unicode
    """
    if total == 0:
        return

    progress = int(math.ceil(float(curr) / (float(total) / 100)))

    if progress > 100:
        progress = 100

    if 0 < int(progress) <= 100:
        if len(msg) > 0:
            output_json({"global_progress": progress, "msg": msg})
        else:
            output_json({"global_progress": progress})


def check_command_folder(command_folder):
    """
    @type command_folder: str, unicode
    """
    commands = []

    if not os.path.exists(command_folder):
        return commands

    for fp in os.listdir(command_folder):
        fp = os.path.join(command_folder, fp)

        if os.path.exists(fp):
            try:
                if str(fp).endswith(".cmd"):
                    fin = open(fp)
                    jdata = fin.read()

                    try:
                        cmd = json.loads(jdata)

                        if not isinstance(cmd, dict):
                            tmp_data = cmd
                            cmd = {"data": tmp_data}

                        cmd["name"] = os.path.basename(fin.name)
                        cmd["name"] = cmd["name"].replace(".cmd", "")
                        commands.append(cmd)
                    except ValueError:
                        print "cba_utils.py:607", "json parse errror"
                        print "cba_utils.py:608", jdata

            except Exception:
                handle_exception(False)
            finally:
                if str(fp).endswith(".cmd"):
                    if os.path.exists(fp):
                        os.remove(fp)

    return commands


def add_command_to_folder(command_folder, name, data=None):
    """
    @type command_folder: str, unicode
    @type name: str, unicode
    @type data: str, unicode
    """
    if not os.path.exists(command_folder):
        os.makedirs(command_folder)

    if not data:
        data = "null"
    open(os.path.join(command_folder, name + ".cmd"), "w").write(data)


def add_command_result_to_folder(command_folder, data):
    """
    @type command_folder: str, unicode
    @type data: dict
    """
    if not os.path.exists(command_folder):
        os.makedirs(command_folder)

    if not data:
        data = "null"

    if not "name" in data:
        raise Exception("no name in result object")

    open(os.path.join(command_folder, data["name"] + ".result"), "w").write(json.dumps(data))

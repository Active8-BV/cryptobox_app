# coding=utf-8
"""
some utility functions
"""
import os
import sys
import math
import time
import xmlrpclib
import multiprocessing
import threading
import uuid as _uu
import json
import jsonpickle
import cPickle
from Crypto.Hash import SHA
last_update_string_len = 0


g_lock = multiprocessing.Lock()
DEBUG = True
from multiprocessing import Pool


def make_sha1_hash_utils(data):
    """ make hash
    @param data:
    @type data:
    """
    sha = SHA.new()
    sha.update(data)
    return sha.hexdigest()


def unpickle_json(path):
    return jsonpickle.decode(open(path).read())

def pickle_json(path, targetobject):
    """
    @type path: str or unicode
    @type targetobject: object
    """
    if DEBUG:
        jsonproxy = json.loads(jsonpickle.encode(targetobject))
        json.dump(jsonproxy, open(path, "w"), sort_keys=True, indent=4, separators=(',', ': '))


def pickle_object(path, targetobject):
    """
    @type path: str or unicode
    @type targetobject: object
    """
    cPickle.dump(targetobject, open(path, "wb"), cPickle.HIGHEST_PROTOCOL)


def unpickle_object(path):
    """
    @type path: str or unicode
    @return: @rtype:
    """
    return cPickle.load(open(path, "rb"))


def smp_all_cpu_apply(method, items, base_params=()):
    """
    @type items: list
    @type method: function
    @type base_params: tuple
    """
    pool = Pool(processes=multiprocessing.cpu_count())
    results = []

    def done_proc(result_func):
        """
        done_downloading
        @type result_func: object
        """
        results.append(result_func)
        return result_func

    calculation_result = []

    for item in items:
        base_params_list = list(base_params)

        if isinstance(item, tuple):
            for i in item:
                base_params_list.append(i)
        else:
            base_params_list.append(item)

        params = tuple(base_params_list)
        result = pool.apply_async(method, params, callback=done_proc)
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


def log(*arg):
    """
    log
    @param arg: list objects
    @type arg:
    """
    msg = " ".join([str(s) for s in arg]).strip(" ")
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


def exit_app_warning(*arg):
    """
    exit_app_warning
    @param arg: list objects
    @type arg:
    """
    log("cba_utils.py:40", *arg)
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


def log_date_time_string():
    """
    log_date_time_string
    """
    return "[" + timestamp_to_string(time.time()) + "]"


def stack_trace(depth=6, line_num_only=False):
    """
    stack_trace
    @param depth: stack depth
    @type line_num_only: only return the line number of the ecxeption
    """
    import traceback
    stack = traceback.format_stack()
    stack.reverse()
    space = ""
    cnt = 0
    error = ""

    for line in stack:
        if cnt > 1:
            s = line
            parsed_line = s.strip().replace("\n", ":").split(",")
            error += space
            error += "/".join(parsed_line[0].split("/")[len(parsed_line[0].split("/")) - 2:]).replace('"', '')
            error += ":"

            if line_num_only:
                return error + parsed_line[1].replace("line ", "").strip()

            error += parsed_line[1].replace("line ", "").strip()
            error += parsed_line[2].replace("  ", " ").replace("  ", " ").replace("  ", " ")
            space += "  "
            error += "\n"

        cnt += 1

        if len(space) > len("  " * depth):
            error += ("  " * depth) + "....\n"
            break

    return error


def handle_exception(exc, again=True, ret_err=False):
    """
    @param exc: Exception
    @type exc:
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
    error = "\n\033[95m" + log_date_time_string() + " ---------------------------\n"
    error += "\033[95m" + log_date_time_string() + "   !!! EXCEPTION !!!\n"
    error += "\033[95m" + log_date_time_string() + " ---------------------------\n"
    items = traceback.extract_tb(exc_traceback)

    #items.reverse()
    leni = 0
    error += "\033[93m" + log_date_time_string() + " " + str(exc_type) + "\n"
    error += "\033[93m" + log_date_time_string() + " " + str(exc) + "\n"
    error += "\033[95m" + log_date_time_string() + " ---------------------------\n"
    error += "\033[93m"

    try:
        linenumsize = 0

        for line in items:
            fnamesplit = str(line[0]).split("/")
            fname = "/".join(fnamesplit[len(fnamesplit) - 2:])
            ls = len(fname + ":" + str(line[1]))

            if ls > linenumsize:
                linenumsize = ls
        items.reverse()

        for line in items:
            leni += 1
            tabs = leni * "  "
            fnamesplit = str(line[0]).split("/")
            fname = "/".join(fnamesplit[len(fnamesplit) - 2:])
            fname_number = fname + ":" + str(line[1])
            fname_number += (" " * (linenumsize - len(fname_number)))
            val = ""

            if line[3]:
                val = line[3]

            error += fname_number + " | " + tabs + val + "\n"

        if len(items) < 4:
            error += stack_trace()
    except Exception, e:
        print "\033[93m" + log_date_time_string(), "cba_utils.py:335", e, '\033[m'
        print "\033[93m" + log_date_time_string(), "cba_utils.py:336", exc, '\033[m'

    error += "\033[95m" + log_date_time_string() + " ---------------------------\n"

    if ret_err:
        return error.replace("\033[95m", "")
    else:
        import sys
        sys.stderr.write(str(error) + '\033[0m')

    if again:
        raise exc

    return "\033[93m" + error


def get_uuid(size):
    """
    make a human readable unique identifier
    @param size:
    @type size:
    """
    unique_id = _uu.uuid4().int
    alphabet = "bcdfghjkmnpqrstvwxz"
    alphabet_length = len(alphabet)
    output = ""

    while unique_id > 0:
        digit = unique_id % alphabet_length
        output += alphabet[digit]
        unique_id = int(unique_id / alphabet_length)

    return output[0:size]


class SingletonMemoryNoKey(Exception):
    """
    SingletonMemoryNoKey
    """
    pass


class SingletonMemoryExpired(Exception):
    """
    SingletonMemoryExpired
    """
    pass


class SingletonMemory(object):
    #noinspection PyUnresolvedReferences
    """
    @param cls:
    @type cls:
    @param args:
    @type args:
    @param kwargs:
    @type kwargs:
    @return:
    @rtype:
    """
    _instance = None
    data = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            #noinspection PyAttributeOutsideInit,PyArgumentList
            cls._instance = super(SingletonMemory, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def set(self, key, value):
        """
        @param key:
        @type key:
        @param value:
        @type value:
        """
        self.data[key] = value

    def has(self, key):
        """
        @param key:
        @type key:
        @return: @rtype: @raise SingletonMemoryExpired:

        """
        return key in self.data

    def get(self, key):
        """
        @param key:
        @type key:
        @return: @rtype: @raise SingletonMemoryNoKey:

        """
        if self.has(key):
            return self.data[key]
        else:
            return ""

    def delete(self, key):
        """
        @param key:
        @type key:
        @raise SingletonMemoryNoKey:

        """
        if self.has(key):
            del self.data[key]
            return True
        else:
            raise SingletonMemoryNoKey(str(key))

    def size(self):
        """
        @return: @rtype:
        """
        return len(self.data)


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

    def save(self, datadir):
        """
        @type datadir: string, unicode
        """
        if os.path.exists(datadir):
            mempath = os.path.join(datadir, "memory.pickle")
            pickle_json(mempath, self.data)

    def load(self, datadir):
        """
        @type datadir: string, unicode
        """
        mempath = os.path.join(datadir, "memory.pickle")

        if os.path.exists(mempath):
            #noinspection PyAttributeOutsideInit
            self.data = unpickle_json(mempath)

            for k in self.data.copy():
                try:
                    self.has(k)
                except MemoryExpired:
                    pass

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


def path_to_relative_path_unix_style(memory, relative_path_name):
    """
    path_to_relative_path_unix_style
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_name = relative_path_name.replace(memory.get("cryptobox_folder"), "")
    relative_path_unix_style = relative_path_name.replace(os.path.sep, "/")
    return relative_path_unix_style, memory


def have_serverhash(memory, node_path):
    """
    have_serverhash
    @type memory: Memory
    @type node_path: str, unicode
    """
    node_path_relative, memory = path_to_relative_path_unix_style(memory, node_path)
    return memory.set_have_value("serverhash_history", (node_path_relative, make_sha1_hash_utils(node_path_relative))), memory


def in_server_file_history(memory, relative_path_name):
    """
    in_server_file_history
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style, memory = path_to_relative_path_unix_style(memory, relative_path_name)
    has_server_hash, memory = have_serverhash(memory, relative_path_unix_style)
    return has_server_hash, memory


def add_server_file_history(memory, relative_path_name):
    """
    add_server_file_history
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style, memory = path_to_relative_path_unix_style(memory, relative_path_name)
    memory.set_add_value("serverhash_history", (relative_path_unix_style, make_sha1_hash_utils(relative_path_unix_style)))
    return memory


def del_serverhash(memory, relative_path_name):
    """
    del_serverhash
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style, memory = path_to_relative_path_unix_style(memory, relative_path_name)

    if memory.set_have_value("serverhash_history", (relative_path_unix_style, make_sha1_hash_utils(relative_path_unix_style))):
        memory.set_delete_value("serverhash_history", (relative_path_unix_style, make_sha1_hash_utils(relative_path_unix_style)))
    return memory


def del_server_file_history(memory, relative_path_name):
    """
    @type memory: Memory
    del_server_file_history
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style, memory = path_to_relative_path_unix_style(memory, relative_path_name)
    memory = del_serverhash(memory, relative_path_name)
    return memory


def add_local_file_history(memory, relative_path_name):
    """
    @type memory: Memory
    add_local_file_history
    @type relative_path_name: str, unicode
    """
    fnode_hash, memory = path_to_relative_path_unix_style(memory, relative_path_name)
    memory.set_add_value("localpath_history", (fnode_hash, make_sha1_hash_utils(fnode_hash)))
    return memory


def in_local_file_history(memory, relative_path_name):
    """
    @type memory: Memory
    in_local_file_history
    @type relative_path_name: str, unicode
    """
    fnode_hash, memory = path_to_relative_path_unix_style(memory, relative_path_name)
    return memory.set_have_value("localpath_history", (fnode_hash, make_sha1_hash_utils(fnode_hash))), memory


def del_local_file_history(memory, relative_path_name):
    """
    @type memory: Memory
    del_local_file_history
    @type relative_path_name: str, unicode
    """
    fnode_hash, memory = path_to_relative_path_unix_style(memory, relative_path_name)

    if memory.set_have_value("localpath_history", (fnode_hash, make_sha1_hash_utils(fnode_hash))):
        memory.set_delete_value("localpath_history", (fnode_hash, make_sha1_hash_utils(fnode_hash)))
    return memory


def update_memory_progress(p):
    """
    update_progress
    @type p:int
    """
    mem = SingletonMemory()
    mem.set("progress", p)


def reset_memory_progress():
    """
    reset_memory_progress
    """
    mem = SingletonMemory()
    mem.set("progress", 0)


class AsyncUpdateProgressItem(threading.Thread):
    """
    AsyncUpdateProgressItem
    """

    def __init__(self, p):
        """
        @type p: int
        """
        self.p = p
        super(AsyncUpdateProgressItem, self).__init__()

    def run(self):
        """
        run
        """

        #noinspection PyBroadException
        try:
            s = xmlrpclib.ServerProxy('http://localhost:8654/RPC2')
            s.set_smemory("item_progress", self.p)
        except Exception:
            print "progress:", self.p


def update_item_progress(p, server=False):
    """
    update_progress
    @type server:bool
    @type p:int
    """
    print p
    if server:
        try:
            api = AsyncUpdateProgressItem(p)
            api.start()
        except Exception, e:
            print "cba_utils.py:773", "AsyncUpdateProgressItem exception", str(e)
    else:
        mem = SingletonMemory()
        mem.set("item_progress", p)


def get_item_progress():
    """
    get_item_progress
    """
    mem = SingletonMemory()

    if mem.has("item_progress"):
        return mem.get("item_progress")
    return 0


def reset_item_progress():
    """
    reset_memory_item_progress
    """
    mem = SingletonMemory()
    mem.set("item_progress", 0)


def update_progress(curr, total, msg, console=False):
    """
    @type curr: int
    @type total: int
    @type msg: str or unicode
    @type console: bool
    """
    global last_update_string_len
    if total == 0:
        return

    progress = int(math.ceil(float(curr) / (float(total) / 100)))

    if progress > 100:
        progress = 100
    update_memory_progress(progress)
    msg = msg + " " + str(curr) + "/" + str(total)
    update_string = "\r\033[94m[{0}{1}] {2}% {3}\033[0m".format(progress / 2 * "#", (50 - progress / 2) * " ", progress, msg)

    if console:
        sys.stderr.write(update_string + "\n")
        sys.stderr.flush()

    last_update_string_len = len(update_string)

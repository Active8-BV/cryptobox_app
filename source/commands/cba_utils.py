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

    def progress_callback_wrapper(result_func):
        """
        progress_callback
        @type result_func: object
        """
        if progress_callback:
            results_cnt[0] += 1
            perc = float(results_cnt[0]) / (float(len(items)) / 100)
            if results_cnt[0] == 1 and perc == 100:
                pass
            else:
                progress_callback(perc-3)

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


#noinspection PyUnresolvedReferences
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
        print "\033[93m" + log_date_time_string(), "cba_utils.py:367", e, '\033[m'
        print "\033[93m" + log_date_time_string(), "cba_utils.py:368", exc, '\033[m'

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

        finally:
            if not keep_lock:
                self.unlock()

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
    return relative_path_unix_style


def have_serverhash(memory, node_path):
    """
    have_serverhash
    @type memory: Memory
    @type node_path: str, unicode
    """
    node_path_relative = path_to_relative_path_unix_style(memory, node_path)
    return memory.set_have_value("serverpath_history", (node_path_relative, make_sha1_hash_utils(node_path_relative))), memory


def in_server_file_history(memory, relative_path_name):
    """
    in_server_file_history
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style = path_to_relative_path_unix_style(memory, relative_path_name)
    has_server_hash, memory = have_serverhash(memory, relative_path_unix_style)
    return has_server_hash, memory


def add_server_path_history(memory, relative_path_name):
    """
    add_server_path_history
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style = path_to_relative_path_unix_style(memory, relative_path_name)
    memory.set_add_value("serverpath_history", (relative_path_unix_style, make_sha1_hash_utils(relative_path_unix_style)))
    return memory


def del_serverhash(memory, relative_path_name):
    """
    del_serverhash
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style = path_to_relative_path_unix_style(memory, relative_path_name)

    if memory.set_have_value("serverpath_history", (relative_path_unix_style, make_sha1_hash_utils(relative_path_unix_style))):
        memory.set_delete_value("serverpath_history", (relative_path_unix_style, make_sha1_hash_utils(relative_path_unix_style)))
    return memory


def del_server_file_history(memory, relative_path_name):
    """
    @type memory: Memory
    del_server_file_history
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style = path_to_relative_path_unix_style(memory, relative_path_name)
    memory = del_serverhash(memory, relative_path_unix_style)
    return memory


def add_local_file_history(memory, relative_path_name):
    """
    @type memory: Memory
    add_local_file_history
    @type relative_path_name: str, unicode
    """
    fnode_hash = path_to_relative_path_unix_style(memory, relative_path_name)
    memory.set_add_value("localpath_history", (fnode_hash, make_sha1_hash_utils(fnode_hash)))
    return memory


def in_local_file_history(memory, relative_path_name):
    """
    @type memory: Memory
    in_local_file_history
    @type relative_path_name: str, unicode
    """
    fnode_hash = path_to_relative_path_unix_style(memory, relative_path_name)
    return memory.set_have_value("localpath_history", (fnode_hash, make_sha1_hash_utils(fnode_hash))), memory


def del_local_file_history(memory, relative_path_name):
    """
    @type memory: Memory
    del_local_file_history
    @type relative_path_name: str, unicode
    """
    fnode_hash = path_to_relative_path_unix_style(memory, relative_path_name)

    if memory.set_have_value("localpath_history", (fnode_hash, make_sha1_hash_utils(fnode_hash))):
        memory.set_delete_value("localpath_history", (fnode_hash, make_sha1_hash_utils(fnode_hash)))
    return memory


def update_item_progress(p):
    """
    update_progress
    @type p:int
    """

    try:
        if 0 < int(p) <= 100:
            output(json.dumps({"item_progress": p}))
    except Exception, e:
        handle_exception(e, False)


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
        output(json.dumps({"progress": progress, "msg": msg}))


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
                        print "cba_utils.py:775", "json parse errror"
                        print "cba_utils.py:776", jdata

            except Exception, e:
                handle_exception(e, False)
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

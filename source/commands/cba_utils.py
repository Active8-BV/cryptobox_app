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
import base64
import urllib
import jsonpickle

last_update_string_len = 0
g_lock = multiprocessing.Lock()
DEBUG = True
from multiprocessing import Pool


def get_files_dir(fpath):
    """
    count_files_dir
    @type fpath: str, unicode
    """
    s = set()

    for path, dirs, files in os.walk(fpath):
        for f in files:
            if os.path.isdir(f):
                s.union(get_files_dir(f))
            s.add(os.path.join(path, f))

    return tuple(s)


def open_folder(path):
    """
    :param path:
    """
    if not os.path.exists(path):
        output_json({"message": "folder does not exist"})
        return

    if sys.platform == 'darwin':
        subprocess.check_call(['open', '--', path])
    elif sys.platform == 'linux2':
        subprocess.check_call(['gnome-open', '--', path])
    elif sys.platform == 'windows':
        subprocess.check_call(['explorer', path])


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


def message_json(msg):
    """
    @type msg: str
    """
    output_json({"message": msg})


def log_json(msg):
    """
    @type msg: str
    """
    output_json({"log": msg})


def smp_all_cpu_apply_0(method, items, progress_callback=None):
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

            try:
                perc = float(results_cnt[0]) / (float(len(items)) / 100)
            except ZeroDivisionError:
                perc = 0

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
    print "cba_utils.py:257", arg
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


def update_item_progress(p, output_name="item_progress"):
    """
    update_progress
    @type p:int
    @type output_name: str
    """

    #noinspection PyBroadException
    try:
        if 0 < int(p) <= 100:
            output_json({output_name: p})
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
            #noinspection PyBroadException
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
                        print "cba_utils.py:624", "json parse errror"
                        print "cba_utils.py:625", jdata

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


def get_b64mstyle():
    """
    @return: @rtype:
    """
    return "data:b64encode:mstyle,"


def key_ascii(s):
    """
    @param s:
    @type s:
    @return: @rtype:
    """
    if not isinstance(s, str) and not isinstance(s, unicode):
        return s

    s2 = ""

    for c in s:
        if c in "_012345678909ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz":
            s2 += c

    return s2.encode("ascii")


def b64_encode_mstyle(s):
    """
    @param s:
    @type s:
    @return: @rtype:
    """
    if not isinstance(s, str) and not isinstance(s, unicode):
        return s

    b64mstyle = get_b64mstyle()
    if s.find(b64mstyle) != -1:
        return s
    try:
        s = urllib.quote(s, safe='~()*!.\'')
    except KeyError:
        s = key_ascii(s)

    s = base64.encodestring(s).replace("=", "-").replace("\n", "")
    s = b64mstyle + s
    return s


g_start_time = time.time()


#noinspection PyPep8Naming
def console(*args):
    """
    @param args:
    @type args:
    @return: @rtype:
    """
    HOSTNAME = subprocess.check_output("hostname")

    if "node" in HOSTNAME:
        return
    global g_start_time
    runtime = "%0.2f" % float(time.time() - g_start_time)
    dbs = str(runtime)
    toggle = True
    arguments = list(args)

    def sanitize(santize_string):
        """
        @param santize_string:
        @type santize_string:
        @return: @rtype:
        """
        santize_string = str(santize_string)
        santize_string = santize_string.replace("/__init__.py", "")
        return santize_string

    arguments = [sanitize(x) for x in arguments if x]
    for s in arguments:
        if toggle:
            pass

        else:
            pass

        toggle = not toggle
        dbs += " |"

        if s:
            if s == arguments[len(arguments) - 1]:
                dbs += " " + str(s)[:160].replace("\n", "")
            else:
                dbs += " " + str(s)[:160].replace("\n", "")

                #if len(str(s)) < 10:
                #    dbs += " " * (20 - len(str(s).replace("\033[91m", "")))

    dbs += "\n"
    log_json(dbs)
    return


class Timers(object):
    """
    Timers
    """
    timers = {}
    done_timers = []
    _instance = None
    last_event = []
    total = 0.0
    print_totals = True
    last_event_name = ""

    def __new__(cls, *args, **kwargs):
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

        #noinspection PyProtectedMember
        if not cls._instance:
            #noinspection PyArgumentList,PyAttributeOutsideInit
            cls._instance = super(Timers, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def event(self, name):
        """
        @param name:
        @type name:
        @return: @rtype:
        """
        last_name = None

        if len(self.last_event) > 0:
            last_name = self.last_event.pop()

            if name == last_name:
                return

        if last_name in self.timers:
            if last_name in self.last_event:
                self.last_event.remove(last_name)

            result = {"name": last_name, "time": time.time() - self.timers[last_name]}
            self.done_timers.append(result)
            del self.timers[last_name]
        self.last_event.append(name)
        self.timers[name] = time.time()

        #noinspection PyAttributeOutsideInit
        self.last_event_name = name
        return

    def event_stop(self):
        """
        event_stop
        """
        self.event(self.last_event_name)

    def print_result(self, result, total):
        """
        @param result:
        @type result:
        @param total:
        @type total:
        @return: @rtype:
        """
        total += float(result["time"])
        fv = float(result["time"])
        result["time"] = "%0.4f" % float(result["time"])
        totals = "%0.4f" % total

        if self.print_totals:
            if fv > 0.85:
                console(result["name"], str("* " + str(result["time"]) + " *"), totals)
            else:
                console(result["name"], str(result["time"]), totals)
        else:
            if fv > 0.85:
                console(result["name"], str("*" + str(result["time"]) + "*"))
            else:
                console(result["name"], str(result["time"]))

        return total

    #noinspection PyAttributeOutsideInit
    def report_measurements(self):
        """
        report_measurements(self):
        """
        self.event("done")
        total = 0.0

        for result in self.done_timers:
            total = self.print_result(result, total)

        if self.print_totals:
            totals = "%0.4f" % total
            console("total runtime", totals)

        self.timers = {}
        self.done_timers = []
        self.last_event = []

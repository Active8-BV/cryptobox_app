# coding=utf-8
"""
memory singleton which get written to disk
"""
import os
from cba_crypto import pickle_object, unpickle_object, make_sha1_hash


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
            pickle_object(mempath, self.data, json_pickle=True)

    def load(self, datadir):
        """
        @type datadir: string, unicode
        """
        mempath = os.path.join(datadir, "memory.pickle")

        if os.path.exists(mempath):
            #noinspection PyAttributeOutsideInit
            self.data = unpickle_object(mempath)

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
    return memory.set_have_value("serverhash_history", (node_path_relative, make_sha1_hash(node_path_relative))), memory


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
    memory.set_add_value("serverhash_history", (relative_path_unix_style, make_sha1_hash(relative_path_unix_style)))
    return memory


def del_serverhash(memory, relative_path_name):
    """
    del_serverhash
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_unix_style, memory = path_to_relative_path_unix_style(memory, relative_path_name)

    if memory.set_have_value("serverhash_history", (relative_path_unix_style, make_sha1_hash(relative_path_unix_style))):
        memory.set_delete_value("serverhash_history", (relative_path_unix_style, make_sha1_hash(relative_path_unix_style)))
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
    memory.set_add_value("localpath_history", (fnode_hash, make_sha1_hash(fnode_hash)))
    return memory


def in_local_file_history(memory, relative_path_name):
    """
    @type memory: Memory
    in_local_file_history
    @type relative_path_name: str, unicode
    """
    fnode_hash, memory = path_to_relative_path_unix_style(memory, relative_path_name)
    return memory.set_have_value("localpath_history", (fnode_hash, make_sha1_hash(fnode_hash))), memory


def del_local_file_history(memory, relative_path_name):
    """
    @type memory: Memory
    del_local_file_history
    @type relative_path_name: str, unicode
    """
    fnode_hash, memory = path_to_relative_path_unix_style(memory, relative_path_name)

    if memory.set_have_value("localpath_history", (fnode_hash, make_sha1_hash(fnode_hash))):
        memory.set_delete_value("localpath_history", (fnode_hash, make_sha1_hash(fnode_hash)))
    return memory


def update_memory_progress(p):
    """
    update_progress
    @type p:int
    """
    mem = SingletonMemory()
    mem.set("progress", p)
    if mem.has("progress"):
        if mem.get("progress") <= p:
            mem.set("progress", p)
    else:
        mem.set("progress", p)


def reset_memory_progress():
    """
    reset_memory_progress
    """
    mem = SingletonMemory()
    mem.set("progress", 0)


def update_file_progress(p):
    """
    update_progress
    @type p:int
    """
    mem = SingletonMemory()
    mem.set("file_progress", p)
    if mem.has("file_progress"):
        if mem.get("file_progress") <= p:
            mem.set("file_progress", p)
    else:
        mem.set("file_progress", p)


def get_file_progress():
    """
    get_file_progress
    """
    mem = SingletonMemory()

    if mem.has("file_progress"):
        return mem.get("file_progress")
    return 0


def reset_file_progress():
    """
    reset_memory_file_progress
    """
    mem = SingletonMemory()
    mem.set("file_progress", 0)

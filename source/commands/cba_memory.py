# coding=utf-8
"""
memory singleton which get written to disk
"""
import os
from cba_crypto import pickle_object, unpickle_object


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
        return value in collection

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


def server_file_history_setup(memory, relative_path_name):
    """
    server_file_history_setup
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    relative_path_name = relative_path_name.replace(memory.get("cryptobox_folder"), "")
    fnode_path_id = relative_path_name.replace(os.path.sep, "/")
    return fnode_path_id, memory


def have_serverhash(fnodehash):
    """
    have_serverhash
    @type fnodehash: str, unicode
    """
    memory = Memory()
    return memory.set_have_value("serverhash_history", fnodehash)


def in_server_file_history(memory, relative_path_name):
    """
    in_server_file_history
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    fnode_path_id, memory = server_file_history_setup(memory, relative_path_name)
    return have_serverhash(fnode_path_id), memory


def add_server_file_history(memory, relative_path_name):
    """
    add_server_file_history
    @type memory: Memory
    @type relative_path_name: str, unicode
    """
    fnode_path_id, memory = server_file_history_setup(memory, relative_path_name)
    memory.set_add_value("serverhash_history", fnode_path_id)
    return memory


def del_serverhash(fnode_hash):
    """
    del_serverhash
    @type fnode_hash: str, unicode
    """
    memory = Memory()

    if memory.set_have_value("serverhash_history", fnode_hash):
        memory.set_delete_value("serverhash_history", fnode_hash)


def del_server_file_history(relative_path_name):
    """
    del_server_file_history
    @type relative_path_name: str, unicode
    """
    fnode_path_id, memory = server_file_history_setup(relative_path_name)
    del_serverhash(fnode_path_id)


def add_local_file_history(relative_path_name):
    """
    add_local_file_history
    @type relative_path_name: str, unicode
    """
    fnode_hash, memory = server_file_history_setup(relative_path_name)
    memory.set_add_value("localpath_history", fnode_hash)


def in_local_file_history(relative_path_name):
    """
    in_local_file_history
    @type relative_path_name: str, unicode
    """
    fnode_hash, memory = server_file_history_setup(relative_path_name)
    return memory.set_have_value("localpath_history", fnode_hash)


def del_local_file_history(relative_path_name):
    """
    del_local_file_history
    @type relative_path_name: str, unicode
    """
    fnode_path_id, memory = server_file_history_setup(relative_path_name)

    if memory.set_have_value("localpath_history", fnode_path_id):
        memory.set_delete_value("localpath_history", fnode_path_id)

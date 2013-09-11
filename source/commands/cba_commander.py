# coding=utf-8
"""
python version
"""
import sys
import threading
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler


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


class Memory(object):
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
            cls._instance = super(Memory, cls).__new__(cls, *args, **kwargs)
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
        @return: @rtype: @raise MemoryExpired:

        """
        return key in self.data

    def get(self, key):
        """
        @param key:
        @type key:
        @return: @rtype: @raise MemoryNoKey:

        """
        if self.has(key):
            return self.data[key]
        else:
            return ""

    def delete(self, key):
        """
        @param key:
        @type key:
        @raise MemoryNoKey:

        """
        if self.has(key):
            del self.data[key]
            return True
        else:
            raise MemoryNoKey(str(key))

    def size(self):
        """
        @return: @rtype:
        """
        return len(self.data)


class XMLRPCThread(threading.Thread):
    """
    XMLRPCThread
    """

    def run(self):
        """
        run
        """
        memory = Memory()
        #noinspection PyClassicStyleClass
        class RequestHandler(SimpleXMLRPCRequestHandler):
            """
            RequestHandler
            """
            rpc_paths = ('/RPC2',)

        # Create server
        server = SimpleXMLRPCServer(("localhost", 8654), requestHandler=RequestHandler)
        server.register_introspection_functions()

        def set_val(name, val):
            """
            set_val
            @type name: str, unicode
            @type val: str, unicode
            """
            memory.set(name, val)

        def get_val(name):
            """
            set_val
            @type name: str, unicode
            """
            memory.get(name)

        server.register_function(set_val, 'set_val')
        server.register_function(get_val, 'get_val')
        server.serve_forever()


commandserver = XMLRPCThread()
commandserver.start()


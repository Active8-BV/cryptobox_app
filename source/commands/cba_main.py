# coding=utf-8
# coding=utf-8
"""
some utility functions
"""
import sys
reload(sys)
#noinspection PyUnresolvedReferences
sys.setdefaultencoding("utf-8")
import os
import time
import threading
import multiprocessing
import xmlrpclib
import SimpleXMLRPCServer
from optparse import OptionParser
from cba_memory import Memory, SingletonMemory
from cba_utils import cba_warning, strcmp, dict2obj_new, exit_app_warning
from cba_index import restore_hidden_config, cryptobox_locked, ensure_directory, hide_config, index_and_encrypt, \
    make_local_index, ExitAppWarning, check_and_clean_dir, decrypt_and_build_filetree
from cba_network import authorize_user
from cba_sync import sync_server, get_server_index, get_sync_changes
from cba_blobs import get_data_dir


def add_options():
    """
    options for the command line tool
    """
    parser = OptionParser()
    parser.add_option("-f", "--dir", dest="dir", help="index this DIR", metavar="DIR")
    parser.add_option("-e", "--encrypt", dest="encrypt", action='store_true', help="index and possible decrypt files", metavar="ENCRYPT")
    parser.add_option("-d", "--decrypt", dest="decrypt", action='store_true', help="decrypt and correct the directory", metavar="DECRYPT")
    parser.add_option("-r", "--remove", dest="remove", action='store_true', help="remove the unencrypted files", metavar="DECRYPT")
    parser.add_option("-c", "--clear", dest="clear", action='store_true', help="clear all cryptobox data", metavar="DECRYPT")
    parser.add_option("-u", "--username", dest="username", help="cryptobox username", metavar="USERNAME")
    parser.add_option("-p", "--password", dest="password", help="password used encryption", metavar="PASSWORD")
    parser.add_option("-b", "--cryptobox", dest="cryptobox", help="cryptobox slug", metavar="CRYPTOBOX")
    parser.add_option("-s", "--sync", dest="sync", action='store_true', help="sync with server", metavar="SYNC")
    parser.add_option("-o", "--check", dest="check", action='store_true', help="check with server", metavar="CHECK")
    parser.add_option("-n", "--numdownloadthreads", dest="numdownloadthreads", help="number if downloadthreads", metavar="NUMDOWNLOADTHREADS")
    parser.add_option("-x", "--server", dest="server", help="server address", metavar="SERVERADDRESS")
    parser.add_option("-v", "--version", dest="version", action='store_true', help="client version", metavar="VERSION")
    return parser.parse_args()


def cryptobox_command(options):
    """
    @param options: dictionary with options
    @type options: namedtuple, Values
    @return: succes indicator
    @rtype: bool
    """
    if isinstance(options, dict):
        options = dict2obj_new(options)

    if options.version:
        return "0.1"

    if not options.numdownloadthreads:
        options.numdownloadthreads = multiprocessing.cpu_count() * 2
    else:
        options.numdownloadthreads = int(options.numdownloadthreads)

    if not options.dir:
        raise ExitAppWarning("Need DIR -f or --dir to continue")

    if not options.cryptobox:
        raise ExitAppWarning("No cryptobox given -b or --cryptobox")

    options.basedir = options.dir
    ensure_directory(options.basedir)
    options.dir = os.path.join(options.dir, options.cryptobox)
    datadir = get_data_dir(options)

    if not datadir:
        cba_warning("datadir is None")

    if not os.path.exists(datadir):
        cba_warning("datadir does not exists")

    restore_hidden_config(options)
    memory = Memory()
    memory.load(datadir)
    memory.replace("cryptobox_folder", options.dir)

    try:
        if not os.path.exists(options.basedir):
            raise ExitAppWarning("DIR [", options.dir, "] does not exist")

        if not options.encrypt and not options.decrypt:
            cba_warning("No encrypt or decrypt directive given (-d or -e)")

        if not options.password:
            raise ExitAppWarning("No password given (-p or --password)")

        if options.username or options.cryptobox:
            if not options.username:
                raise ExitAppWarning("No username given (-u or --username)")

            if not options.cryptobox:
                raise ExitAppWarning("No cryptobox given (-b or --cryptobox)")

        if options.sync:
            if not options.username:
                raise ExitAppWarning("No username given (-u or --username)")

            if not options.password:
                raise ExitAppWarning("No password given (-p or --password)")

        localindex = make_local_index(options)

        if options.password and options.username and options.cryptobox:
            authorize_user(memory, options)

            if memory.get("authorized"):
                if options.sync:
                    if not options.encrypt:
                        raise ExitAppWarning("A sync step should always be followed by an encrypt step (-e or --encrypt)")

                    if cryptobox_locked(memory):
                        raise ExitAppWarning("cryptobox is locked, nothing can be added now first decrypt (-d)")

                    ensure_directory(options.dir)
                    localindex, memory = sync_server(memory, options)

                if options.check:
                    ensure_directory(options.dir)
                    serverindex, memory = get_server_index(memory, options)
                    localindex = make_local_index(options)
                    memory, options, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(memory, options, localindex, serverindex)

        salt = None
        secret = None

        if options.encrypt:
            salt, secret, memory, localindex = index_and_encrypt(memory, options, localindex)

        if options.decrypt:
            if options.remove:
                raise ExitAppWarning("option remove (-r) cannot be used together with decrypt (dataloss)")

            if not options.clear:
                memory = decrypt_and_build_filetree(memory, options)

        check_and_clean_dir(options)
    finally:
        if memory.has("session"):
            memory.delete("session")

        if memory.has("authorized"):
            memory.delete("authorized")

        memory.save(datadir)

    hide_config(options, salt, secret)
    return True


class XMLRPCThread(threading.Thread):
    """
    XMLRPCThread
    """

    def run(self):
        """
        run
        """
        memory = SingletonMemory()
 
        #noinspection PyClassicStyleClass

        class RequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
            """
            RequestHandler
            """
            rpc_paths = ('/RPC2',)

        #noinspection PyClassicStyleClass

        class StoppableRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer):
            """
            StoppableRPCServer
            """
            allow_reuse_address = True
            stopped = False

            def __init__(self, *args, **kw):
                SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, *args, **kw)
                self.register_function(lambda: 'OK', 'ping')

            def serve_forever(self, poll_interval=0.1):
                """
                :param poll_interval:
                :return: :rtype:
                """
                while not self.stopped:
                    self.handle_request()
                    time.sleep(poll_interval)

                return True

            def force_stop(self):
                """
                :return: :rtype:
                """
                #noinspection PyAttributeOutsideInit
                self.stopped = True

                #self.server_close()
                #self.stopped = True
                #self.create_dummy_request()
                return True

            def create_dummy_request(self):
                """
                create_dummy_request
                """
                server = xmlrpclib.Server('http://%s:%s' % self.server_address)
                server.ping()

        # Create server
        server = StoppableRPCServer(("localhost", 8654), requestHandler=RequestHandler)
        server.register_introspection_functions()

        def set_val(name, val):
            """
            set_val
            @type name: str, unicode
            @type val: str, unicode
            """
            memory.set(name, val)
            return True

        def get_val(name):
            """
            set_val
            @type name: str, unicode
            """
            return memory.get(name)

        def force_stop():
            """
            stop_server
            """
            server.force_stop()
            return True

        server.register_function(set_val, 'set_val')
        server.register_function(get_val, 'get_val')
        server.register_function(force_stop, 'force_stop')
        server.register_function(cryptobox_command, "cryptobox_command")

        try:
            server.serve_forever()
        finally:
            print "cba_main.py:255", "stopping"
            server.force_stop()
            server.server_close()


def main():
    """
    @return: @rtype:
    """

    try:
        (options, args) = add_options()

        if not options.cryptobox and not options.version:
            print "cba_main.py:269", "xmlrpc server running"
            commandserver = XMLRPCThread()
            commandserver.start()

            while True:
                time.sleep(1)
        else:
            try:
                cryptobox_command(options)
            except ExitAppWarning, ex:
                exit_app_warning(str(ex))

    except KeyboardInterrupt:
        server = xmlrpclib.ServerProxy("http://localhost:8654/RPC2")
        server.force_stop()


if strcmp(__name__, '__main__'):
    main()

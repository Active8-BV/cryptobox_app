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
import threading
import socket
import cPickle
import time
import multiprocessing
import xmlrpclib
import random
import SimpleXMLRPCServer
from tendo import singleton
from optparse import OptionParser
from cba_utils import strcmp, Dict2Obj, log, Memory, SingletonMemory, reset_memory_progress, reset_item_progress, handle_exception, open_folder
from cba_index import restore_hidden_config, cryptobox_locked, ensure_directory, hide_config, index_and_encrypt, make_local_index, check_and_clean_dir, decrypt_and_build_filetree
from cba_network import authorize_user, on_server
from cba_sync import sync_server, get_server_index, get_sync_changes
from cba_blobs import get_data_dir
import multiprocessing.forking


def monkeypatch_popen():
    """
    hack for pyinstaller on windows
    """
    if sys.platform.startswith('win'):

        class _Popen(multiprocessing.forking.Popen):

            def __init__(self, *args, **kw):
                if hasattr(sys, 'frozen'):

                    # We have to set original _MEIPASS2 value from sys._MEIPASS
                    # to get --onefile mode working.
                    # Last character is stripped in C-loader. We have to add
                    # '/' or '\\' at the end.

                    #noinspection PyProtectedMember,PyUnresolvedReferences
                    os.putenv('_MEIPASS2', sys._MEIPASS + os.sep)

                try:
                    super(_Popen, self).__init__(*args, **kw)
                finally:
                    if hasattr(sys, 'frozen'):

                        # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                        # available. In those cases we cannot delete the variable
                        # but only set it to the empty string. The bootloader
                        # can handle this case.
                        if hasattr(os, 'unsetenv'):
                            os.unsetenv('_MEIPASS2')
                        else:
                            os.putenv('_MEIPASS2', '')

        #noinspection PyUnusedLocal

        class Process(multiprocessing.Process):
            """
            Process
            """
            _Popen = _Popen

monkeypatch_popen()


def add_options():
    """
    options for the command line tool
    """
    parser = OptionParser()
    parser.add_option("-f", "--dir", dest="dir", help="index this DIR", metavar="DIR")
    parser.add_option("-e", "--encrypt", dest="encrypt", action='store_true', help="index and possible decrypt files", metavar="ENCRYPT")
    parser.add_option("-d", "--decrypt", dest="decrypt", action='store_true', help="decrypt and correct the directory", metavar="DECRYPT")
    parser.add_option("-r", "--remove", dest="remove", action='store_true', help="remove the unencrypted files", metavar="REMOVE")
    parser.add_option("-c", "--clear", dest="clear", action='store_true', help="clear all cryptobox data", metavar="CLEAR")
    parser.add_option("-u", "--username", dest="username", help="cryptobox username", metavar="USERNAME")
    parser.add_option("-p", "--password", dest="password", help="password used encryption", metavar="PASSWORD")
    parser.add_option("-b", "--cryptobox", dest="cryptobox", help="cryptobox slug", metavar="CRYPTOBOX")
    parser.add_option("-s", "--sync", dest="sync", action='store_true', help="sync with server", metavar="SYNC")
    parser.add_option("-o", "--check", dest="check", action='store_true', help="check with server", metavar="CHECK")
    parser.add_option("-t", "--treeseq", dest="treeseq", action='store_true', help="check tree sequence", metavar="TREESEQ")
    parser.add_option("-l", "--logout", dest="logout", action='store_true', help="log session out", metavar="LOGOUT")
    parser.add_option("-n", "--numdownloadthreads", dest="numdownloadthreads", help="number if downloadthreads", metavar="NUMDOWNLOADTHREADS")
    parser.add_option("-x", "--server", dest="server", help="server address", metavar="SERVERADDRESS")
    parser.add_option("-v", "--version", dest="version", action='store_true', help="client version", metavar="VERSION")
    return parser.parse_args()


def consoledict(*args):
    """
    @param args:
    @type args:
    @return: @rtype:
    """
    dbs = ""

    for s in args:
        if s:
            if isinstance(s, dict):
                dbs += "--- dict ---\n"

                for i in s:
                    dbs += " " + str(i) + " : " + str(s[i]) + "\n"

                dbs += "------------\n"
            else:
                dbs += " " + str(s)

    log(dbs)


def cryptobox_command(options):
    """
    @param options: dictionary with options
    @type options: namedtuple, Values
    @return: succes indicator
    @rtype: bool
    """
    lock = threading.Lock()
    try:
        lock.acquire()
        smemory = SingletonMemory()
        smemory.set("working", False)

        if isinstance(options, dict):
            options = Dict2Obj(options)

        if options.version:
            return "0.1"

        if not options.numdownloadthreads:
            options.numdownloadthreads = 8
        else:
            options.numdownloadthreads = int(options.numdownloadthreads)

        if not options.dir:
            log("Need DIR -f or --dir to continue")
            return False

        if not options.cryptobox:
            log("No cryptobox given -b or --cryptobox")
            return False

        options.basedir = options.dir
        ensure_directory(options.basedir)
        options.dir = os.path.join(options.dir, options.cryptobox)
        restore_hidden_config(options)
        ensure_directory(options.dir)
        datadir = get_data_dir(options)
        ensure_directory(datadir)
        if not datadir:
            log("datadir is None")

        memory = Memory()
        memory.load(datadir)
        memory.replace("cryptobox_folder", options.dir)

        if not os.path.exists(options.basedir):
            log("DIR [", options.dir, "] does not exist")
            return False

        if not options.check and not options.treeseq and not options.logout:
            if not options.encrypt and not options.decrypt:
                log("No encrypt or decrypt directive given (-d or -e)")
                return False

        if not options.password:
            log("No password given (-p or --password)")
            return False

        if options.username or options.cryptobox:
            if not options.username:
                log("No username given (-u or --username)")
                return False

            if not options.cryptobox:
                log("No cryptobox given (-b or --cryptobox)")
                return False

        if options.sync:
            if not options.username:
                log("No username given (-u or --username)")
                return False

            if not options.password:
                log("No password given (-p or --password)")
                return False

        localindex = make_local_index(options)
        reset_memory_progress()
        reset_item_progress()
        smemory.set("cryptobox_locked", cryptobox_locked(memory))
        if options.logout:
            result, memory = on_server(memory, options, "logoutserver", {}, memory.get("session"))
            return result[0]
        elif options.treeseq:
            if memory.has("session"):
                clock_tree_seq, memory = on_server(memory, options, "clock", {}, memory.get("session"))
                smemory = SingletonMemory()
                smemory.set("tree_sequence", clock_tree_seq[1])
                print smemory.get("tree_sequence")
        elif options.password and options.username and options.cryptobox:
            memory = authorize_user(memory, options)
            if memory.get("authorized"):
                if options.check:
                    if cryptobox_locked(memory):
                        return False
                    ensure_directory(options.dir)
                    serverindex, memory = get_server_index(memory, options)
                    localindex = make_local_index(options)
                    memory, options, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(memory, options, localindex, serverindex)
                elif options.sync:
                    if not options.encrypt:
                        log("A sync step should always be followed by an encrypt step (-e or --encrypt)")
                        return False

                    if cryptobox_locked(memory):
                        log("cryptobox is locked, nothing can be added now first decrypt (-d)")
                        return False
                    ensure_directory(options.dir)
                    smemory.set("working", True)
                    localindex, memory = sync_server(memory, options)

        salt = None
        secret = None

        if options.encrypt:
            smemory.set("working", True)
            salt, secret, memory, localindex = index_and_encrypt(memory, options, localindex)

        if options.decrypt:
            if options.remove:
                log("option remove (-r) cannot be used together with decrypt (dataloss)")
                return False

            if not options.clear == "1":
                smemory.set("working", True)
                memory = decrypt_and_build_filetree(memory, options)
        check_and_clean_dir(options)
        smemory.set("last_ping", time.time())
        memory.save(datadir)
        hide_config(options, salt, secret)
        reset_memory_progress()
        reset_item_progress()
        smemory.set("cryptobox_locked", cryptobox_locked(memory))
    except Exception, e:
        handle_exception(e)
    finally:
        smemory = SingletonMemory()
        smemory.set("working", False)
        lock.release()
    return True


class XMLRPCThread(multiprocessing.Process):
    """
    XMLRPCThread
    """

    def run(self):
        """
        run
        """

        try:
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
                timeout = 1

                def __init__(self, *args, **kw):
                    SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, *args, **kw)

                def serve_forever(self, poll_interval=0.1):
                    """
                    :param poll_interval:
                    :return: :rtype:
                    """
                    while not self.stopped:
                        tslp = time.time() - memory.get("last_ping")

                        if int(tslp) < 30:
                            self.handle_request()
                            time.sleep(poll_interval)
                        else:
                            log("no ping received for 30 seconds")

                def force_stop(self):
                    """
                    :return: :rtype:
                    """
                    self.server_close()

                    #noinspection PyAttributeOutsideInit
                    self.stopped = True

                    #noinspection PyBroadException
                    try:
                        self.create_dummy_request()
                    except:
                        pass

                @staticmethod
                def create_dummy_request():
                    """
                    create_dummy_request
                    """
                    xmlrpclib.ServerProxy("http://localhost:8654/RPC2").ping()

            # Create server
            server = StoppableRPCServer(("localhost", 8654), requestHandler=RequestHandler, allow_none=True)
            server.register_introspection_functions()

            def force_stop():
                """
                stop_server
                """
                log("force_stop")
                #log("force_stop DISABLED")
                #return False
                server.force_stop()
                return True

            def last_ping():
                """
                ping from client
                """
                log("last_ping")
                memory.set("last_ping", time.time())
                return "ping received"

            def reset_progress():
                """
                reset_progress
                """
                log("reset_progress")
                reset_memory_progress()

            def do_reset_item_progress():
                """
                reset_item_progress
                """
                log("do_reset_item_progress")
                reset_item_progress()

            def ping():
                """
                simple ping
                """
                #log("ping")
                t = time.time()
                return t

            def run_cb_command(options):
                """
                run_cb_command
                @type options: dict
                """
                log("run_cb_command")
                t1 = threading.Thread(target=cryptobox_command, args=(options,))
                t1.start()

            def get_all_smemory():
                """
                get_all_smemory
                """
                #log("get_all_smemory")
                smemory = SingletonMemory()
                return smemory.data

            def set_smemory(k, v):
                """
                set_smemory
                :param k:
                :param v:
                """
                log("set_smemory")
                smemory = SingletonMemory()
                return smemory.set(k, v)

            def get_motivation():
                """
                get_motivation
                """
                log("get_motivation")
                #noinspection PyBroadException
                qlist = cPickle.load(open("quotes.list"))
                q = qlist[random.randint(0, len(qlist))]
                return q[0] + "<br/><br/>- " + q[1]

            def do_open_folder(folder_path, servername):
                """
                do_open_folder
                """
                log("do_open_folder")
                open_folder(os.path.join(folder_path, servername))

            def get_tree_sequence(options):
                log("get_tree_sequence")
                return cryptobox_command(options)

            server.register_function(ping, 'ping')
            server.register_function(force_stop, 'force_stop')
            server.register_function(last_ping, 'last_ping')
            server.register_function(run_cb_command, "cryptobox_command")
            server.register_function(reset_progress, "reset_progress")
            server.register_function(do_reset_item_progress, "reset_item_progress")
            server.register_function(set_smemory, "set_smemory")
            server.register_function(get_all_smemory, "get_all_smemory")
            server.register_function(get_motivation, "get_motivation")
            server.register_function(do_open_folder, "do_open_folder")
            server.register_function(get_tree_sequence, "get_tree_sequence")

            try:
                memory.set("last_ping", time.time())
                reset_progress()
                reset_item_progress()
                server.serve_forever()
            finally:
                server.force_stop()
                server.server_close()
        except KeyboardInterrupt:
            print "cba_main.py:475", "bye xmlrpc server"


#noinspection PyClassicStyleClass
def main():
    """
    @return: @rtype:
    """
    (options, args) = add_options()

    if not options.cryptobox and not options.version:
        #noinspection PyBroadException,PyUnusedLocal
        me = singleton.SingleInstance()
        queue = multiprocessing.Queue()
        log("xmlrpc server up")
        commandserver = XMLRPCThread(args=(queue,))
        commandserver.start()

        while True:
            time.sleep(10)
            try:
                if commandserver.is_alive():
                    s = xmlrpclib.ServerProxy('http://localhost:8654/RPC2')
                    socket.setdefaulttimeout(2)
                    s.ping()
                    socket.setdefaulttimeout(None)
            except socket.error, ex:
                print "cba_main.py:503", "kill it", ex
                #commandserver.terminate()

            if not commandserver.is_alive():
                break

    else:
        cryptobox_command(options)


if strcmp(__name__, '__main__'):
    try:
        # On Windows calling this function is necessary.
        if sys.platform.startswith('win'):
            multiprocessing.freeze_support()
        main()
    except KeyboardInterrupt:
        print "cba_main.py:521", "\nbye main"

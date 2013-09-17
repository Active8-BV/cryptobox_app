# coding=utf-8 # ##^ comment 0
# coding=utf-8 # ##^ comment 0
""" # ##^  1n 1n_python_comment 0
some utility functions # ##^  1n 1n_python_comment 0
""" # ##^  0
import sys # ##^  0
reload(sys) # ##^ methodcallmethod call global scope 0

#noinspection PyUnresolvedReferences # ##^ pycharm d1rect1ve 0


sys.setdefaultencoding("utf-8") # ##^ global method call 0
import os # ##^  0
import socket # ##^  0
import time # ##^  0
import multiprocessing # ##^  0
import xmlrpclib # ##^  0
import SimpleXMLRPCServer # ##^  0
from tendo import singleton # ##^  0
from optparse import OptionParser # ##^  0
from cba_memory import Memory, SingletonMemory, reset_memory_progress # ##^  0
from cba_utils import strcmp, Dict2Obj, exit_app_warning, log # ##^  0
from cba_index import restore_hidden_config, cryptobox_locked, ensure_directory, hide_config, index_and_encrypt, make_local_index, ExitAppWarning, check_and_clean_dir, decrypt_and_build_filetree # ##^  0
from cba_network import authorize_user # ##^  0
from cba_sync import sync_server, get_server_index, get_sync_changes # ##^  0
from cba_blobs import get_data_dir # ##^  0


def add_options(): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    options for the command line tool # ##^ for statement prevented by None 1n 1n_python_comment 0
    """ # ##^  0
    parser = OptionParser() # ##^ methodcall and ass1gned  after  0
    parser.add_option("-f", "--dir", dest="dir", help="index this DIR", metavar="DIR") # ##^ methodcallnested method call 0
    parser.add_option("-e", "--encrypt", dest="encrypt", action='store_true', help="index and possible decrypt files", metavar="ENCRYPT") # ##^ methodcallnested method call 0
    parser.add_option("-d", "--decrypt", dest="decrypt", action='store_true', help="decrypt and correct the directory", metavar="DECRYPT") # ##^ methodcallnested method call 0
    parser.add_option("-r", "--remove", dest="remove", action='store_true', help="remove the unencrypted files", metavar="REMOVE") # ##^ methodcallnested method call 0
    parser.add_option("-c", "--clear", dest="clear", action='store_true', help="clear all cryptobox data", metavar="CLEAR") # ##^ methodcallnested method call 0
    parser.add_option("-u", "--username", dest="username", help="cryptobox username", metavar="USERNAME") # ##^ methodcallnested method call 0
    parser.add_option("-p", "--password", dest="password", help="password used encryption", metavar="PASSWORD") # ##^ methodcallnested method call 0
    parser.add_option("-b", "--cryptobox", dest="cryptobox", help="cryptobox slug", metavar="CRYPTOBOX") # ##^ methodcallnested method call 0
    parser.add_option("-s", "--sync", dest="sync", action='store_true', help="sync with server", metavar="SYNC") # ##^ methodcallnested method call 0
    parser.add_option("-o", "--check", dest="check", action='store_true', help="check with server", metavar="CHECK") # ##^ methodcallnested method call 0
    parser.add_option("-n", "--numdownloadthreads", dest="numdownloadthreads", help="number if downloadthreads", metavar="NUMDOWNLOADTHREADS") # ##^ methodcallnested method call 0
    parser.add_option("-x", "--server", dest="server", help="server address", metavar="SERVERADDRESS") # ##^ methodcallnested method call 0
    parser.add_option("-v", "--version", dest="version", action='store_true', help="client version", metavar="VERSION") # ##^ methodcallnested method call 0
    return parser.parse_args() # ##^ retrn |  0


def cryptobox_command(options): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @param options: dictionary with options # ##^  1n 1n_python_comment 0
    @type options: namedtuple, Values # ##^ property  1n 1n_python_comment 0
    @return: succes indicator # ##^ retrn |  1n 1n_python_comment 0
    @rtype: bool # ##^ property  1n 1n_python_comment 0
    """ # ##^  0
    if isinstance(options, dict): # ##^  1f statement on same scope 1
        options = Dict2Obj(options) # ##^ methodcall and ass1gned nested method call 1

    if options.version: # ##^  1f statement scope change 1
        return "0.1" # ##^  after keyword 1

    if not options.numdownloadthreads: # ##^  1f statement scope change 1
        options.numdownloadthreads = 2 # ##^ ass1gnment 1
    else: # ##^  0
        options.numdownloadthreads = int(options.numdownloadthreads) # ##^ methodcall and ass1gned  not after ass1gnmentmethod call after 1f 3lse or wtch 0

    log("downloadthreads", options.numdownloadthreads) # ##^ methodcall method call h1gher scope 4 scope>2  0

    if not options.dir: # ##^  1f statement on same scope after method call 1
        raise ExitAppWarning("Need DIR -f or --dir to continue") # ##^  ra1se 1

    if not options.cryptobox: # ##^  after ra1se 1
        raise ExitAppWarning("No cryptobox given -b or --cryptobox") # ##^  ra1se 1

    options.basedir = options.dir # ##^  after ra1se 0
    ensure_directory(options.basedir) # ##^ methodcall after ass1gnment 0
    options.dir = os.path.join(options.dir, options.cryptobox) # ##^ methodcall and ass1gned nested method call 0
    datadir = get_data_dir(options) # ##^ methodcall and ass1gned nested method call 0

    if not datadir: # ##^  1f statement on same scope after ass1gnement after method call 1
        log("datadir is None") # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 1

    if not os.path.exists(datadir): # ##^  1f statement scope change 1
        log("datadir does not exists") # ##^ methodcallnested method call 1

    restore_hidden_config(options) # ##^ methodcall method call h1gher scope 4 scope>2  0
    memory = Memory() # ##^ methodcall and ass1gned nested method call 0
    memory.load(datadir) # ##^ methodcallnested method call 0
    memory.replace("cryptobox_folder", options.dir) # ##^ methodcallnested method call 0

    if memory.has("session"): # ##^  1f statement on same scope after method call 1
        memory.delete("session") # ##^ methodcallnested method call 1

    if memory.has("authorized"): # ##^  1f statement scope change 1
        memory.replace("authorized", False) # ##^ methodcallnested method call 1

    try: # ##^ try 0
        if not os.path.exists(options.basedir): # ##^  1f statement 1
            log("DIR [", options.dir, "] does not exist") # ##^ methodcallnested method call 1
            return # ##^ retrn |  1

        if not options.check: # ##^  1f statement scope change 1
            if not options.encrypt and not options.decrypt: # ##^  1f statement 2
                log("No encrypt or decrypt directive given (-d or -e)") # ##^ funct1on call 2

        if not options.password: # ##^  1f statement scope change 1
            log("No password given (-p or --password)") # ##^ funct1on call 1

        if options.username or options.cryptobox: # ##^  1f statement scope change 1
            if not options.username: # ##^  1f statement 2
                log("No username given (-u or --username)") # ##^ funct1on call 2
                return # ##^ retrn |  2

            if not options.cryptobox: # ##^  1f statement scope change 2
                log("No cryptobox given (-b or --cryptobox)") # ##^ funct1on call 2
                return # ##^ retrn |  2

        if options.sync: # ##^  1f statement scope change 1
            if not options.username: # ##^  1f statement 2
                log("No username given (-u or --username)") # ##^ funct1on call 2
                return # ##^ retrn |  2

            if not options.password: # ##^  1f statement scope change 2
                log("No password given (-p or --password)") # ##^ funct1on call 2
                return # ##^  after keyword 2

        localindex = make_local_index(options) # ##^ methodcall and ass1gned  not after ass1gnment 0
        reset_memory_progress() # ##^ methodcallnested method call 0

        if options.password and options.username and options.cryptobox: # ##^  1f statement on same scope after method call 1
            authorize_user(memory, options) # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 1

            if memory.get("authorized"): # ##^  1f statement on same scope after method call 2
                if options.check: # ##^  1f statement 3
                    if cryptobox_locked(memory): # ##^  1f statement 4
                        raise ExitAppWarning("cryptobox is locked, nothing can be added now first decrypt (-d)") # ##^  ra1se 4

                    ensure_directory(options.dir) # ##^  after ra1se 3
                    serverindex, memory = get_server_index(memory, options) # ##^ methodcall and ass1gned nested method call 3
                    localindex = make_local_index(options) # ##^ methodcall and ass1gned nested method call 3
                    memory, options, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(memory, options, localindex, serverindex) # ##^ methodcall and ass1gned nested method call 3

                    log("files to download", "\n" + "\n".join([x["doc"]["m_path"] for x in file_downloads]), "\n") # ##^ for statement 3
                    log("files to upload", "\n" + "\n".join([x["path"] for x in file_uploads]), "\n") # ##^  3
                    log("dirs to delete server", "\n" + "\n".join(dir_del_server), "\n") # ##^  3

                    log("dirs to make local", "\n" + "\n".join([x["name"] for x in dir_make_local]), "\n") # ##^ for statement 3
                    log("dirs to make server", "\n" + "\n".join([x["dirname"] for x in dir_make_server]), "\n") # ##^  3
                    log("dirs to delete local", "\n" + "\n".join([x["dirname"] for x in dir_del_local]), "\n") # ##^  3
                    log("files to delete server", "\n" + "\n".join(file_del_server), "\n") # ##^  3
                    log("files to delete local", "\n" + "\n".join(file_del_local), "\n") # ##^  3
                elif options.sync: # ##^  2
                    if not options.encrypt: # ##^  1f statement 3
                        log("A sync step should always be followed by an encrypt step (-e or --encrypt)") # ##^ funct1on call 3
                        return # ##^ retrn |  3

                    if cryptobox_locked(memory): # ##^  1f statement scope change 3
                        log("cryptobox is locked, nothing can be added now first decrypt (-d)") # ##^ funct1on call 3
                        return # ##^ retrn |  3

                    ensure_directory(options.dir) # ##^ methodcall not after ass1gnment 2
                    localindex, memory = sync_server(memory, options) # ##^ methodcall and ass1gned nested method call 2

        salt = None # ##^  scope -1
        secret = None # ##^ ass1gnment -1

        if options.encrypt: # ##^  1f statement on same scope after ass1gnement 0
            salt, secret, memory, localindex = index_and_encrypt(memory, options, localindex) # ##^ methodcall and ass1gned  not after ass1gnmentmethod call after 1f 3lse or wtch 0

        if options.decrypt: # ##^  1f statement scope change 1
            if options.remove: # ##^  1f statement 2
                log("option remove (-r) cannot be used together with decrypt (dataloss)") # ##^ funct1on call 2
                return # ##^  after keyword 2

            if not options.clear == "1": # ##^  1f statement scope change 2
                memory = decrypt_and_build_filetree(memory, options) # ##^ methodcall and ass1gned  not after ass1gnmentmethod call after 1f 3lse or wtch 2

        check_and_clean_dir(options) # ##^ methodcall method call h1gher scope 8 scope>2  0
        memory = SingletonMemory() # ##^ methodcall and ass1gned nested method call 0
        memory.set("last_ping", time.time()) # ##^  0
    finally: # ##^  0
        if memory.has("session"): # ##^  1f statement 1
            memory.delete("session") # ##^ methodcallnested method call 1

        if memory.has("authorized"): # ##^  1f statement scope change 1
            memory.delete("authorized") # ##^ methodcallnested method call 1

        memory.save(datadir) # ##^ methodcall method call h1gher scope 4 scope>2  0

    hide_config(options, salt, secret) # ##^ methodcall method call h1gher scope 4 scope>2  0
    return True # ##^ retrn |  0


class XMLRPCThread(multiprocessing.Process): # ##^ class def 0
    """ # ##^  1n 1n_python_comment 0
    XMLRPCThread # ##^  1n 1n_python_comment 0
    """ # ##^  0

    def run(self): # ##^ funct1on def nested somewhere f1rst method 0
        """ # ##^  1n 1n_python_comment 0
        run # ##^  1n 1n_python_comment 0
        """ # ##^  0

        try: # ##^ try 0
            memory = SingletonMemory() # ##^ methodcall and ass1gned  not after ass1gnmentmethod call after 1f 3lse or wtch 0

            #noinspection PyClassicStyleClass # ##^ pycharm d1rect1ve 0

            class RequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler): # ##^ class def 0
                """ # ##^  1n 1n_python_comment 0
                RequestHandler # ##^  1n 1n_python_comment 0
                """ # ##^  0
                rpc_paths = ('/RPC2',) # ##^ methodcall and ass1gned  after  0

            #noinspection PyClassicStyleClass # ##^ pycharm d1rect1ve 0

            class StoppableRPCServer(SimpleXMLRPCServer.SimpleXMLRPCServer): # ##^ class def 0
                """ # ##^  1n 1n_python_comment 0
                StoppableRPCServer # ##^  1n 1n_python_comment 0
                """ # ##^  0
                allow_reuse_address = True # ##^ ass1gnment 0
                stopped = False # ##^ ass1gnment 0
                timeout = 1 # ##^ ass1gnment 0

                def __init__(self, *args, **kw): # ##^ funct1on def nested after ass1gnement a python class 0
                    SimpleXMLRPCServer.SimpleXMLRPCServer.__init__(self, *args, **kw) # ##^ methodcallnested method call 0

                def serve_forever(self, poll_interval=0.01): # ##^ funct1on def nested somewhere a python class 0
                    """ # ##^  1n 1n_python_comment 0
                    :param poll_interval: # ##^  1n 1n_python_comment 0
                    :return: :rtype: # ##^ retrn |  1n 1n_python_comment 0
                    """ # ##^  0
                    while not self.stopped: # ##^ wh1le statement prevented by None 0
                        tslp = time.time() - memory.get("last_ping") # ##^ ass1gnment 0

                        if int(tslp) < 20: # ##^  1f statement on same scope after ass1gnement 1
                            self.handle_request() # ##^ methodcallnested method call 1
                            time.sleep(poll_interval) # ##^ methodcallnested method call 1
                        else: # ##^  0
                            log("no ping received, stopping") # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 0
                            self.force_stop() # ##^ methodcallnested method call 0

                def force_stop(self): # ##^  scope 0
                    """ # ##^  1n 1n_python_comment 0
                    :return: :rtype: # ##^  after doc comment 1n 1n_python_comment 0
                    """ # ##^  0
                    self.server_close() # ##^ methodcall after  0

                    #noinspection PyAttributeOutsideInit # ##^ pycharm d1rect1ve 0
                    self.stopped = True # ##^ ass1gnment 0

                    #noinspection PyBroadException # ##^ pycharm d1rect1ve keyword (not class) 1n nextl1ne 0
                    try: # ##^  0
                        self.create_dummy_request() # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 0
                    except: # ##^ except 0
                        pass # ##^  0

                @staticmethod # ##^ property  0
                def create_dummy_request(): # ##^ funct1on def nested somewhere after property or kw 0
                    """ # ##^  1n 1n_python_comment 0
                    create_dummy_request # ##^  1n 1n_python_comment 0
                    """ # ##^  0
                    xmlrpclib.ServerProxy("http://localhost:8654/RPC2").ping() # ##^  0

            # Create server # ##^ comment 0
            server = StoppableRPCServer(("localhost", 8654), requestHandler=RequestHandler, allow_none=True) # ##^ ass1gnment 0
            server.register_introspection_functions() # ##^ methodcall after ass1gnment 0

            def set_val(name, val): # ##^ funct1on def nested somewhere 0
                """ # ##^  1n 1n_python_comment 0
                set_val # ##^  1n 1n_python_comment 0
                @type name: str, unicode # ##^ property  1n 1n_python_comment 0
                @type val: str, unicode # ##^ property  1n 1n_python_comment 0
                """ # ##^  0
                memory.set(name, val) # ##^ methodcall after  0
                return True # ##^ retrn |  0

            def get_val(name): # ##^ funct1on def nested after keyword on prev1ous scope 0
                """ # ##^  1n 1n_python_comment 0
                set_val # ##^  1n 1n_python_comment 0
                @type name: str, unicode # ##^ property  1n 1n_python_comment 0
                """ # ##^  0
                return memory.get(name) # ##^  after doc comment 0

            def force_stop(): # ##^ funct1on def nested after keyword on prev1ous scope 0
                """ # ##^  1n 1n_python_comment 0
                stop_server # ##^  1n 1n_python_comment 0
                """ # ##^  0
                server.force_stop() # ##^ methodcall after  0
                return True # ##^  after keyword 0

            def last_ping(): # ##^ funct1on def nested after keyword on prev1ous scope 0
                """ # ##^  1n 1n_python_comment 0
                ping from client # ##^  1n 1n_python_comment 0
                """ # ##^  0
                print "cba_main.py:299", "last_ping" # ##^ debug statement 0
                memory.set("last_ping", time.time()) # ##^  0
                return "ping received" # ##^ retrn |  0

            def get_progress(): # ##^ funct1on def nested after keyword on prev1ous scope 0
                """ # ##^  1n 1n_python_comment 0
                progress for the progress bar # ##^ for statement prevented by None 1n 1n_python_comment 0
                """ # ##^  0
                if not memory.has("progress"): # ##^  1f statement on same scope 1
                    return 0 # ##^  after keyword 1
                return memory.get("progress") # ##^  after keyword 0

            def reset_progress(): # ##^ funct1on def nested after keyword on prev1ous scope 0
                """ # ##^  1n 1n_python_comment 0
                reset_progress # ##^  1n 1n_python_comment 0
                """ # ##^  0
                reset_memory_progress() # ##^ methodcall after  0

            def ping(): # ##^ funct1on def nested somewhere 0
                """ # ##^  1n 1n_python_comment 0
                simple ping # ##^  1n 1n_python_comment 0
                """ # ##^  0
                t = time.time() # ##^ methodcall and ass1gned  after  0
                return t # ##^ retrn |  0

            server.register_function(ping, 'ping') # ##^ methodcall not after ass1gnment 0
            server.register_function(set_val, 'set_val') # ##^ methodcallnested method call 0
            server.register_function(get_val, 'get_val') # ##^ methodcallnested method call 0
            server.register_function(force_stop, 'force_stop') # ##^ methodcallnested method call 0
            server.register_function(last_ping, 'last_ping') # ##^ methodcallnested method call 0
            server.register_function(cryptobox_command, "cryptobox_command") # ##^ methodcallnested method call 0
            server.register_function(get_progress, "get_progress") # ##^ methodcallnested method call 0
            server.register_function(reset_progress, "reset_progress") # ##^ methodcallnested method call 0

            try: # ##^ try 0
                memory.set("last_ping", time.time()) # ##^  0

                reset_progress() # ##^ methodcall not after ass1gnment 0
                server.serve_forever() # ##^ methodcallnested method call 0
            finally: # ##^  0
                server.force_stop() # ##^ methodcall after f1nally 0
                server.server_close() # ##^ methodcallnested method call 0
        except KeyboardInterrupt: # ##^ except 0
            print "cba_main.py:342", "bye xmlrpc server" # ##^ debug statement 0

#noinspection PyClassicStyleClass # ##^  scope 0


def main(): # ##^ funct1on def python 0
    """ # ##^  1n 1n_python_comment 0
    @return: @rtype: ADDTYPES # ##^  after doc comment 1n 1n_python_comment 0
    """ # ##^  0
    (options, args) = add_options() # ##^ ass1gnment 0

    if not options.cryptobox and not options.version: # ##^  1f statement on same scope after ass1gnement 1
        #noinspection PyBroadException # ##^ pycharm d1rect1veafter keyword 1
        me = singleton.SingleInstance() # will sys.exit(-1) if other instance is running # ##^ ass1gnment 1
        queue = multiprocessing.Queue() # ##^ methodcall and ass1gned  after ass1gnmentmethod call after 1f 3lse or wtch 1
        log("xmlrpc server up") # ##^ methodcallnested method call 1
        commandserver = XMLRPCThread(args=(queue,)) # ##^ ass1gnment 1
        commandserver.start() # ##^ methodcall after ass1gnment 1

        while True: # ##^ wh1le statement 1
            time.sleep(0.5) # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch 1

            try: # ##^ try 1
                if commandserver.is_alive(): # ##^  1f statement 2
                    s = xmlrpclib.ServerProxy('http://localhost:8654/RPC2') # ##^ methodcall and ass1gned nested method call 2
                    socket.setdefaulttimeout(10) # ##^ methodcallnested method call 2
                    s.ping() # ##^ methodcallnested method call 2
                    socket.setdefaulttimeout(None) # ##^ methodcallnested method call 2
            except socket.error, ex: # ##^ except 0
                print "cba_main.py:371", "kill it damnit", ex # ##^ debug statement 0
                commandserver.terminate() # ##^ methodcall after pr1nt 0

            if not commandserver.is_alive(): # ##^  1f statement scope change 1
                break # ##^  1

    else: # ##^ tr1ple scope change -2
        try: # ##^  -2
            cryptobox_command(options) # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch -2
        except ExitAppWarning, ex: # ##^ except -2
            exit_app_warning(str(ex)) # ##^ funct1on call -2


if strcmp(__name__, '__main__'): # ##^ ma1n -1
    try: # ##^  -1
        main() # ##^ methodcall not after ass1gnmentmethod call after 1f 3lse or wtch -1
    except KeyboardInterrupt: # ##^ except -1
        print "cba_main.py:388", "\nbye main" # ##^ debug statement -1

 # ##^ global_class_declare -1

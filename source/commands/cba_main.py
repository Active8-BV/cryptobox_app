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
import cPickle
import time
import multiprocessing
import random
from optparse import OptionParser
from cba_utils import strcmp, Dict2Obj, log, Memory, SingletonMemory, handle_exception, open_folder, check_command_folder, add_command_result_to_folder
from cba_index import restore_hidden_config, ensure_directory, hide_config, index_and_encrypt, make_local_index, check_and_clean_dir, decrypt_and_build_filetree, quick_lock_check
from cba_network import authorize_user, on_server
from cba_sync import sync_server, get_server_index, get_sync_changes, get_tree_sequence
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
    parser.add_option("-i", "--ipcfolder", dest="ipcfolder", help="folder to store command objects", metavar="IPCFOLDER")
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


def delete_progress_file(fname):
    """
    @type fname: str, unicode
    """
    p = os.path.join(os.getcwd(), fname)

    if os.path.exists(p):
        os.remove(p)


def cryptobox_command(options):
    """
    @param options: dictionary with options
    @type options: namedtuple, Values
    @return: succes indicator
    @rtype: bool
    """

    try:
        smemory = SingletonMemory()
        smemory.set("working", True)
        if isinstance(options, dict):
            options = Dict2Obj(options)

        if options.version:
            return "0.1"

        if not options.numdownloadthreads:
            options.numdownloadthreads = 2
        else:
            options.numdownloadthreads = int(options.numdownloadthreads)

        options.numdownloadthreads = 8

        if not options.dir:
            log("Need DIR -f or --dir to continue")
            return False

        if not options.cryptobox:
            log("No cryptobox given -b or --cryptobox")
            return False

        options.basedir = options.dir
        ensure_directory(options.basedir)
        options.dir = os.path.join(options.dir, options.cryptobox)

        if not options.decrypt:
            if quick_lock_check(options):
                smemory.set("cryptobox_locked", True)
                log("Cryptobox locked")
                return False

        if not options.encrypt:
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

        if options.logout:
            result, memory = on_server(memory, options, "logoutserver", {}, memory.get("session"))
            return result[0]
        elif options.treeseq:
            if memory.has("session"):
                memory, smemory = get_tree_sequence(memory, options)
                return smemory.get("tree_sequence")
        elif options.password and options.username and options.cryptobox:
            memory = authorize_user(memory, options, force=True)

            if memory.get("authorized"):
                if options.check:
                    if quick_lock_check(options):
                        return False
                    ensure_directory(options.dir)
                    serverindex, memory = get_server_index(memory, options)
                    localindex = make_local_index(options)
                    memory, options, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_file_nodes, unique_content = get_sync_changes(memory, options, localindex, serverindex)
                elif options.sync:
                    if not options.encrypt:
                        log("A sync step should always be followed by an encrypt step (-e or --encrypt)")
                        return False

                    if quick_lock_check(options):
                        log("cryptobox is locked, nothing can be added now first decrypt (-d)")
                        return False
                    ensure_directory(options.dir)
                    localindex, memory = sync_server(memory, options)

        salt = None
        secret = None

        if options.encrypt:
            smemory.set("cryptobox_locked", True)
            salt, secret, memory, localindex = index_and_encrypt(memory, options)

        if options.decrypt:
            if options.remove:
                log("option remove (-r) cannot be used together with decrypt (dataloss)")
                return False

            if not options.clear == "1":
                memory = decrypt_and_build_filetree(memory, options)
        check_and_clean_dir(options)
        smemory.set("last_ping", time.time())
        memory.save(datadir)
        hide_config(options, salt, secret)
        smemory.set("cryptobox_locked", quick_lock_check(options))
    except Exception, e:
        handle_exception(e, False)
    finally:
        smemory = SingletonMemory()
        smemory.set("working", False)
        delete_progress_file("progress")
        delete_progress_file("item_progress")
    return True


def has_option(options, optname):
    """
    @type options: dict
    @type optname: str, unicode
    """
    if optname in options:
        if options[optname] == "1":
            return True
    return False


def do_open_folder(cmd):
    """
    do_open_folder
    :param cmd:
    """
    log("do_open_folder")
    open_folder(os.path.join(cmd["data"][0], cmd["data"][1]))


def add(cmd):
    """
    add
    """
    return cmd["a"] + cmd["b"]


#noinspection PyUnusedLocal
def get_motivation(cmd):
    """
    get_motivation
    """
    qlist = cPickle.load(open("quotes.list"))
    q = qlist[random.randint(0, len(qlist)) - 1]
    return q[0] + "<br/><br/>- " + q[1]


#noinspection PyUnusedLocal
def do_exit(cmd):
    """
    do_exit
    """
    log("exit disabled!!")
    #exit(1)
    return True


#noinspection PyUnusedLocal
def ping_client(cmd):
    """
    ping_client
    """
    memory = SingletonMemory()
    memory.set("last_ping", time.time())
    return True


def run_cb_command(options):
    """
    run_cb_command
    @type options: dict
    """
    logged = False

    if has_option(options, "check"):
        log("check sync stats")
        logged = True

    if has_option(options, "sync"):
        log("sync")
        logged = True

    if has_option(options, "encrypt"):
        log("encrypt")
        logged = True

    if has_option(options, "decrypt"):
        log("decrypt")
        logged = True

    if not logged:
        log("cb_command", options)

    t1 = threading.Thread(target=cryptobox_command, args=(options,))
    t1.start()
    log("cb_command started")


#noinspection PyUnusedLocal
def get_all_smemory(cmd):
    """
    get_all_smemory
    """
    smemory = SingletonMemory()
    return smemory.data


#noinspection PyClassicStyleClass
def main():
    """
    @return: @rtype:
    """
    print "cba_main up"
    memory = SingletonMemory()
    memory.set("last_ping", time.time())
    (options, args) = add_options()

    if not options.cryptobox and not options.version:
        #noinspection PyBroadException,PyUnusedLocal
        if not options.ipcfolder.strip():
            raise Exception("ipcfolder (-i) not given")

        cmd_folder_path = options.ipcfolder.strip()

        for fp in os.listdir(cmd_folder_path):
            fp = os.path.join(cmd_folder_path, fp)

            if os.path.exists(fp):
                os.remove(fp)

        while True:
            commands = check_command_folder(cmd_folder_path)

            for cmd in commands:
                if cmd["name"] not in globals():
                    print "cba_main.py:392", cmd["name"], "not found"
                else:
                    func = globals()[cmd["name"]]
                    cmd["result"] = func(cmd)
                    add_command_result_to_folder(cmd_folder_path, cmd)
            time.sleep(0.2)
            tslp = time.time() - memory.get("last_ping")

            if int(tslp) > 30:
                log("exit")
                exit(1)

    else:
        cryptobox_command(options)


if strcmp(__name__, '__main__'):
    try:

        # On Windows calling this function is necessary.
        if sys.platform.startswith('win'):
            multiprocessing.freeze_support()
        main()
    except KeyboardInterrupt:
        print "cba_main.py:416", "\nbye main"

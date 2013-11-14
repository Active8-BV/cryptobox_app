# coding=utf-8
# coding=utf-8
"""
some utility functions
"""
import sys
reload(sys)

#noinspection PyUnresolvedReferences
sys.setdefaultencoding("utf-8")
import webbrowser
import os
import cPickle
import multiprocessing.forking
import multiprocessing
import random
import shutil
from optparse import OptionParser
from cba_utils import output_json, \
    strcmp, \
    Dict2Obj, \
    Memory, \
    open_folder, \
    handle_exception, \
    message_json, \
    b64_encode_mstyle
from cba_index import restore_hidden_config, \
    ensure_directory, \
    hide_config, \
    index_and_encrypt, \
    make_local_index, \
    reset_cryptobox_local, \
    decrypt_and_build_filetree, \
    quick_lock_check
from cba_network import authorize_user, \
    on_server
from cba_sync import sync_server, \
    get_server_index, \
    get_sync_changes, \
    get_tree_sequence
from cba_blobs import get_data_dir
from tendo import singleton


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
    parser.add_option("-a", "--acommand", dest="acommand", help="a helper command", metavar="ACOMMAND")
    parser.add_option("-b", "--cryptobox", dest="cryptobox", help="cryptobox slug", metavar="CRYPTOBOX")
    parser.add_option("-c", "--clear", dest="clear", help="clear all cryptobox data", metavar="CLEAR")
    parser.add_option("-d", "--decrypt", dest="decrypt", action='store_true', help="decrypt and correct the directory", metavar="DECRYPT")
    parser.add_option("-e", "--encrypt", dest="encrypt", action='store_true', help="index and possible decrypt files", metavar="ENCRYPT")
    parser.add_option("-f", "--dir", dest="dir", help="index this DIR", metavar="DIR")
    parser.add_option("-l", "--logout", dest="logout", action='store_true', help="log session out", metavar="LOGOUT")
    parser.add_option("-m", "--motivation", dest="motivation", help="get motivational quote", metavar="MOTIVATION")
    parser.add_option("-n", "--numdownloadthreads", dest="numdownloadthreads", help="number if downloadthreads", metavar="NUMDOWNLOADTHREADS")
    parser.add_option("-o", "--check", dest="check", action='store_true', help="check with server", metavar="CHECK")
    parser.add_option("-p", "--password", dest="password", help="password used encryption", metavar="PASSWORD")
    parser.add_option("-r", "--remove", dest="remove", action='store_true', help="remove the unencrypted files", metavar="REMOVE")
    parser.add_option("-s", "--sync", dest="sync", action='store_true', help="sync with server", metavar="SYNC")
    parser.add_option("-t", "--treeseq", dest="treeseq", action='store_true', help="check tree sequence", metavar="TREESEQ")
    parser.add_option("-u", "--username", dest="username", help="cryptobox username", metavar="USERNAME")
    parser.add_option("-v", "--version", dest="version", action='store_true', help="client version", metavar="VERSION")
    parser.add_option("-x", "--server", dest="server", help="server address", metavar="SERVERADDRESS")
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

    print "cba_main.py:134", dbs


def delete_progress_file(fname):
    """
    @type fname: str, unicode
    """
    p = os.path.join(os.getcwd(), fname)

    if os.path.exists(p):
        os.remove(p)


def all_item_zero_len(items):
    """
    @type items: list
    """
    for l in items:
        if len(l) != 0:
            return False
    return True


def cryptobox_command(options):
    """
    @param options: dictionary with options
    @type options: namedtuple, Values
    @return: succes indicator
    @rtype: bool
    """

    try:
        if options.acommand:
            if options.acommand == "open_folder":
                if options.dir:
                    open_folder(os.path.join(options.dir, options.cryptobox))
                else:
                    print "cba_main.py:171", "no folder given(-f)"
            elif options.acommand == "delete_blobs":
                if not options.dir:
                    message_json("dir mising")
                    return

                if not options.cryptobox:
                    message_json("cryptobox mising")
                    return

                blobpath = os.path.join(options.dir, options.cryptobox)
                blobpath = os.path.join(blobpath, ".cryptobox")
                blobpath = os.path.join(blobpath, "blobs")

                if os.path.exists(blobpath):
                    shutil.rmtree(blobpath, True)
                    message_json("encrypted cache emptied")

                return
            elif options.acommand == "open_website":
                if not options.username:
                    message_json("username mising")
                    return

                if not options.password:
                    message_json("password missing")
                    return

                if not options.cryptobox:
                    message_json("cryptobox missing")
                    return

                m = Memory()
                m = authorize_user(m, options, force=True)

                if not m.get("authorized"):
                    message_json("Username or password is not correct")
                else:
                    encoded_token = b64_encode_mstyle("session_token:" + m.get("session_token"))
                    private_key = b64_encode_mstyle(m.get("private_key"))
                    webbrowser.open_new_tab(options.server + options.cryptobox + "/autologin/" + options.username + "/" + encoded_token + "/" + private_key)
            else:
                print "cba_main.py:213", "unknown command"
            return

        if options.motivation:
            qlist = cPickle.load(open("quotes.list"))
            q = qlist[random.randint(0, len(qlist)) - 1]
            output_json({"motivation": q[0] + "\n\n- " + q[1]})
            return

        #noinspection PyUnusedLocal
        single_instance = singleton.SingleInstance()

        if not options.check and not options.treeseq and not options.logout:
            if not options.encrypt and not options.decrypt:
                print "cba_main.py:227", "No encrypt directive given (-e)"
                return False

        if options.decrypt:
            if options.remove:
                print "cba_main.py:232", "option remove (-r) cannot be used together with decrypt (dataloss)"
                return False

            if options.sync:
                print "cba_main.py:236", "option sync (-s) cannot be used together with decrypt (hashmismatch)"
                return False

            if options.check:
                print "cba_main.py:240", "option check (-o) cannot be used together with decrypt (hashmismatch)"
                return False

        if not options.password:
            print "cba_main.py:244", "No password given (-p or --password)"
            return False

        if options.username or options.cryptobox:
            if not options.username:
                print "cba_main.py:249", "No username given (-u or --username)"
                return False

            if not options.cryptobox:
                print "cba_main.py:253", "No cryptobox given (-b or --cryptobox)"
                return False

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
            print "cba_main.py:270", "Need DIR -f or --dir to continue"
            return False

        if not options.cryptobox:
            print "cba_main.py:274", "No cryptobox given -b or --cryptobox"
            return False

        options.basedir = options.dir
        ensure_directory(options.basedir)
        options.dir = os.path.join(options.dir, options.cryptobox)

        if not options.decrypt:
            if quick_lock_check(options):
                output_json({"locked": True})
                return False

        if not options.encrypt:
            restore_hidden_config(options)
        ensure_directory(options.dir)
        datadir = get_data_dir(options)

        if options.clear == "1":
            shutil.rmtree(datadir)
            output_json({"info_message": "cryptobox cache removed: " + str(datadir)})
            return

        ensure_directory(datadir)
        if not datadir:
            print "cba_main.py:298", "datadir is None"

        memory = Memory()
        memory.load(datadir)
        memory.replace("cryptobox_folder", options.dir)
        if not os.path.exists(options.basedir):
            print "cba_main.py:304", "DIR [", options.dir, "] does not exist"
            return False

        if options.sync:
            if not options.username:
                print "cba_main.py:309", "No username given (-u or --username)"
                return False

            if not options.password:
                print "cba_main.py:313", "No password given (-p or --password)"
                return False

        if options.logout:
            result, memory = on_server(memory, options, "logoutserver", {}, memory.get("session"))
            return result[0]
        elif options.treeseq:
            memory = authorize_user(memory, options)
            tree_seq = get_tree_sequence(memory, options)

            if tree_seq:
                output_json({"tree_seq": tree_seq})

            return True
        elif options.password and options.username and options.cryptobox and (options.sync or options.check):
            memory = authorize_user(memory, options, force=True)

            if not memory.get("authorized"):
                message_json("Username or password is not correct")
                output_json({"instruction": "lock_buttons_password_wrong"})
                return

            if memory.get("authorized"):
                if options.check:
                    if quick_lock_check(options):
                        return False
                    ensure_directory(options.dir)
                    serverindex, memory = get_server_index(memory, options)
                    localindex = make_local_index(options)
                    memory, options, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_path_nodes, unique_content, rename_server = get_sync_changes(memory, options, localindex, serverindex)
                    all_synced = all_item_zero_len([file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local])
                    outputdict = {"file_del_server": file_del_server,
                                  "file_downloads": file_downloads,
                                  "file_uploads": file_uploads,
                                  "dir_del_server": dir_del_server,
                                  "dir_make_local": dir_make_local,
                                  "dir_make_server": dir_make_server,
                                  "dir_del_local": dir_del_local,
                                  "file_del_local": file_del_local,
                                  "all_synced": all_synced}

                    output_json(outputdict)
                elif options.sync:
                    if not options.encrypt:
                        print "cba_main.py:357", "A sync step should always be followed by an encrypt step (-e or --encrypt)"
                        return False

                    if quick_lock_check(options):
                        print "cba_main.py:361", "cryptobox is locked, nothing can be added now first decrypt (-d)"
                        return False
                    ensure_directory(options.dir)
                    localindex, memory = sync_server(memory, options)

        salt = secret = None
        if options.encrypt:
            salt, secret, memory, localindex = index_and_encrypt(memory, options)
            output_json({"msg": ""})
            output_json({"item_progress": 0})
            output_json({"global_progress": 0})

        if options.decrypt:
            if not options.clear == "1":
                memory = decrypt_and_build_filetree(memory, options)
                output_json({"msg": ""})
                output_json({"item_progress": 0})
                output_json({"global_progress": 0})
        reset_cryptobox_local(options)
        memory.save(datadir)
        if options.remove and salt and secret:
            hide_config(options, salt, secret)
            output_json({"msg": ""})
            output_json({"item_progress": 0})
            output_json({"global_progress": 0})
    finally:
        pass
    return True


def test_output():
    from cba_utils import message_json
    message_json("hello")
    message_json("world")
    message_json(str(range(0, 10000)))
    message_json(str(range(0, 1000000)))
    return


def main():
    #noinspection PyUnusedLocal
    (options, args) = add_options()

    try:
        cryptobox_command(options)
    except Exception:
        exs = handle_exception(False, True)
        output_json({"error_message": exs})

        raise

if strcmp(__name__, '__main__'):
    try:

        # On Windows calling this function is necessary.
        if sys.platform.startswith('win'):
            multiprocessing.freeze_support()
        main()
    except KeyboardInterrupt:
        print "cba_main.py:420", "\nbye main"

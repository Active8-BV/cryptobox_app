# coding=utf-8
# coding=utf-8
"""
some utility functions
"""
import os
import shutil
import multiprocessing
from optparse import OptionParser
from cba_memory import Memory
from cba_utils import log, exit_app_warning, cba_warning, strcmp
from cba_index import restore_hidden_config, make_local_index, cryptobox_locked, ensure_directory, hide_config, index_and_encrypt
from cba_tree import decrypt_and_build_filetree
from cba_network import authorize_user
from cba_sync import sync_server
from cba_blobs import get_data_dir


def add_options():
    """
    options for the command line tool
    """
    parser = OptionParser()
    parser.add_option("-f", "--dir", dest="dir", help="index this DIR", metavar="DIR")
    parser.add_option("-e", "--encrypt", dest="encrypt", action='store_true', help="index and possible decrypt files)", metavar="ENCRYPT")
    parser.add_option("-d", "--decrypt", dest="decrypt", action='store_true', help="decrypt and correct the directory", metavar="DECRYPT")
    parser.add_option("-r", "--remove", dest="remove", action='store_true', help="remove the unencrypted files", metavar="DECRYPT")
    parser.add_option("-c", "--clear", dest="clear", action='store_true', help="clear all cryptobox data", metavar="DECRYPT")
    parser.add_option("-u", "--username", dest="username", help="cryptobox username", metavar="USERNAME")
    parser.add_option("-p", "--password", dest="password", help="password used encryption", metavar="PASSWORD")
    parser.add_option("-b", "--cryptobox", dest="cryptobox", help="cryptobox slug", metavar="CRYPTOBOX")
    parser.add_option("-s", "--sync", dest="sync", action='store_true', help="sync with server", metavar="SYNC")
    parser.add_option("-n", "--numdownloadthreads", dest="numdownloadthreads", help="number if downloadthreads", metavar="NUMDOWNLOADTHREADS")
    parser.add_option("-x", "--debug", dest="debug", action='store_true', help="drop to debug repl", metavar="DEBUG")
    parser.add_option("-k", "--fake", dest="fake", action='store_true', help="fake server run", metavar="FAKE")
    return parser.parse_args()


def interact():
    """
    interact
    """
    import code

    #noinspection PyUnresolvedReferences
    import readline

    myglobals = globals()
    myglobals["m"] = Memory()
    myglobals["md"] = myglobals["m"].data
    code.InteractiveConsole(locals=myglobals).interact()


class ExitAppWarning(Exception):
    """
    ExitAppWarning
    """
    pass


def run_app_command(options):
    """
    @param options: dictionary with options
    @type options: namedtuple, Values
    @return: succes indicator
    @rtype: bool
    """
    if options.fake:
        log("doing fake server operations")

    if not options.numdownloadthreads:
        options.numdownloadthreads = multiprocessing.cpu_count() * 2
    else:
        options.numdownloadthreads = int(options.numdownloadthreads)

    if not options.dir:
        raise ExitAppWarning("Need DIR -f or --dir to continue")

    if not options.cryptobox:
        raise ExitAppWarning("No cryptobox given -b or --cryptobox")

    options.basedir = options.dir
    options.dir = os.path.join(options.dir, options.cryptobox)
    datadir = get_data_dir(options)
    restore_hidden_config(options)
    memory = Memory()
    memory.load(datadir)
    memory.replace("cryptobox_folder", options.dir)

    if options.debug:
        log("drop to repl")
        interact()

        raise ExitAppWarning("done with repl")

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

        if not cryptobox_locked():
            localindex = make_local_index(options)
            memory.replace("localindex", localindex)

        if options.password and options.username and options.cryptobox:
            if authorize_user(options):
                if options.sync:
                    if not options.encrypt:
                        raise ExitAppWarning("A sync step should always be followed by an encrypt step (-e or --encrypt)")

                    if cryptobox_locked():
                        raise ExitAppWarning("cryptobox is locked, nothing can be added now first decrypt (-d)")

                    ensure_directory(options.dir)
                    sync_server(options)

        salt = None
        secret = None

        if options.encrypt:
            salt, secret = index_and_encrypt(options)

        if options.decrypt:
            if options.remove:
                raise ExitAppWarning("option remove (-r) cannot be used together with decrypt (dataloss)")

            if not options.clear:
                decrypt_and_build_filetree(options)

        if options.clear:
            if options.encrypt:
                raise ExitAppWarning("clear options cannot be used together with encrypt, possible data loss")

            datadir = get_data_dir(options)
            shutil.rmtree(datadir, True)
            log("cleared all meta data in ", get_data_dir(options))
    finally:
        memory.delete("localindex")
        memory.save(datadir)

    hide_config(options, salt, secret)
    return True


def main():
    """
    @return: @rtype:
    """
    (options, args) = add_options()

    try:
        run_app_command(options)
    except ExitAppWarning, ex:
        exit_app_warning(str(ex))


if strcmp(__name__, '__main__'):
    main()

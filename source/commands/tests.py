# coding=utf-8
"""
unit test for app commands
"""
__author__ = 'rabshakeh'
import os
import unittest
from cba_main import run_app_command
from collections import namedtuple


def options():
    """
    options for the command line tool
    """
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-f", "--dir", dest="dir",
                      help="index this DIR", metavar="DIR")

    parser.add_option("-e", "--encrypt", dest="encrypt", action='store_true',
                      help="index and possible decrypt files)", metavar="ENCRYPT")

    parser.add_option("-d", "--decrypt", dest="decrypt", action='store_true',
                      help="decrypt and correct the directory", metavar="DECRYPT")

    parser.add_option("-r", "--remove", dest="remove", action='store_true',
                      help="remove the unencrypted files", metavar="DECRYPT")

    parser.add_option("-c", "--clear", dest="clear", action='store_true',
                      help="clear all cryptobox data", metavar="DECRYPT")

    parser.add_option("-u", "--username", dest="username",
                      help="cryptobox username", metavar="USERNAME")

    parser.add_option("-p", "--password", dest="password",

                      help="password used for encryption", metavar="PASSWORD")

    parser.add_option("-b", "--cryptobox", dest="cryptobox",
                      help="cryptobox slug", metavar="CRYPTOBOX")

    parser.add_option("-s", "--sync", dest="sync", action='store_true',
                      help="sync with server", metavar="SYNC")

    parser.add_option("-n", "--numdownloadthreads", dest="numdownloadthreads",
                      help="number if downloadthreads", metavar="NUMDOWNLOADTHREADS")

    parser.add_option("-x", "--debug", dest="debug", action='store_true',
                      help="drop to debug repl", metavar="DEBUG")

    parser.add_option("-k", "--fake", dest="fake", action='store_true',
                      help="fake server run", metavar="FAKE")

    return parser.parse_args()


class CryptoboxAppTest(unittest.TestCase):
    """
    CryptoboTestCase
    """

    def setUp(self):
        """
        setUp
        """
        os.system("rm -Rf testmap")
        os.system("unzip testmap.zip > /dev/null")
        self.index_option = {"dir": "/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/commands/testmap",
                             "encrypt": True,
                             "username": "rabshakeh",
                             "password": "kjhfsd98",
                             "cryptobox": "test",
                             "sync": True,
                             "numdownloadthreads": 2}

        self.no_box_given = self.index_option.copy()
        del self.no_box_given["cryptobox"]
        self.index_option = namedtuple("options", self.index_option)

    def tearDown(self):
        """
        tearDown
        """
        os.system("rm -Rf testmap")

    def test_index_no_box_given(self):
        """
        test_index
        """
        run_app_command(self.no_box_given)


if __name__ == '__main__':
    unittest.main()

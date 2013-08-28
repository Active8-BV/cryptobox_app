# coding=utf-8
"""
unit test for app commands
"""
__author__ = 'rabshakeh'
import os
import unittest


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

    def tearDown(self):
        """
        tearDown
        """
        os.system("rm -Rf testmap")

    def test_index(self):
        """
        test_index
        """


if __name__ == '__main__':
    unittest.main()

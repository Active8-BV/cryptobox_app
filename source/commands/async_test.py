# coding=utf-8
"""
async test script
"""

import threading

from inspect import getmodule
from multiprocessing.dummy import Pool


import threading
def foo(a, b):
    import time
    time.sleep(1)
    print "heello", a, 7

t1 = threading.Thread(target=foo, args=(4,7))
t1.start()
print "done"

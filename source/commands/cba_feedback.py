# coding=utf-8
"""
communications with userinterface
"""
import sys
import math
from cba_memory import update_memory_progress
last_update_string_len = 0


def update_progress(curr, total, msg, console=True):
    """
    @type curr: int
    @type total: int
    @type msg: str or unicode
    @type console: bool
    """
    global last_update_string_len
    if total == 0:
        return

    progress = int(math.ceil(float(curr) / (float(total) / 100)))

    if progress > 100:
        progress = 100

    update_memory_progress(progress)
    msg = msg + " " + str(curr) + "/" + str(total)

    #update_string = "\r\033[94m[{0}{1}] {2}% {3}\033[0m".format(progress / 2 * "#", (50 - progress / 2) * " ", progress, msg)
    update_string = "{0}% {1}".format(progress, msg)

    if console:

        #if len(update_string) < last_update_string_len:
        #    sys.stderr.write("\r\033[94m{0}\033[0m".format(" " * 100))
        sys.stderr.write(update_string+"\n")
        sys.stderr.flush()

    last_update_string_len = len(update_string)

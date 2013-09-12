# coding=utf-8
"""
some utility functions
"""
import sys
import time
import multiprocessing
import uuid as _uu
g_lock = multiprocessing.Lock()
DEBUG = True


def exist(data):
    """
    @param data:
    @type data:
    @return: @rtype:
    """
    data = str(data).strip()

    if not data:
        return False

    elif str(data) == "":
        return False

    elif len(str(data)) == 0:
        return False

    elif str(data) == "False":
        return False

    elif str(data) == "false":
        return False

    elif str(data) == "undefined":
        return False

    elif str(data) == "null":
        return False

    elif str(data) == "none":
        return False

    elif str(data) == "None":
        return False
    return True


class dict2obj_new(dict):
    """
    dict2obj_new
    """

    def __init__(self, dict_):
        super(dict2obj_new, self).__init__(dict_)

        for key in self:
            item = self[key]

            if isinstance(item, list):
                for idx, it in enumerate(item):
                    if isinstance(it, dict):
                        item[idx] = dict2obj_new(it)

            elif isinstance(item, dict):
                self[key] = dict2obj_new(item)

    def __getattr__(self, key):

        # Enhanced to handle key not found.
        if key in self:
            return self[key]
        else:
            return None


def cba_warning(*arg):
    """
    cba_warning
    @param arg: a list of objects to display
    @type arg:
    """
    sys.stderr.write("\033[91mwarning: " + " ".join([str(s) for s in arg]).strip(" ") + "\033[0m\n")


def strcmp(s1, s2):
    """
    @type s1: str or unicode
    @type s2: str or unicode
    @return: @rtype: bool
    """
    s1 = str(s1)
    s2 = str(s2)

    if not s1 or not s2:
        return False

    s1 = s1.strip()
    s2 = s2.strip()
    return s1 == s2


def log(*arg):
    """
    log
    @param arg: list objects
    @type arg:
    """
    msg = " ".join([str(s) for s in arg]).strip(" ")
    sys.stderr.write("\033[93m" + msg + "\n\033[0m")


def exit_app_warning(*arg):
    """
    exit_app_warning
    @param arg: list objects
    @type arg:
    """
    cba_warning("cba_utils.py:40", *arg)
    sys.exit(1)


def timestamp_to_string(ts, short=False):
    """Return the current time formatted for logging.
    Return the current time formatted for logging.timestamp_to_string
    @param ts: time string
    @type ts: string, unicode
    @param short: display format
    @type short: bool
    """
    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    year, month, day, hh, mm, ss, x, y, z = time.localtime(ts)

    if short:
        year -= 2000
        s = "%d-%d-%d %02d:%02d:%02d" % (day, month, year, hh, mm, ss)
    else:
        s = "%02d/%3s/%04d %02d:%02d:%02d" % (day, monthname[month], year, hh, mm, ss)

    return s


def log_date_time_string():
    """
    log_date_time_string
    """
    return "[" + timestamp_to_string(time.time()) + "]"


def stack_trace(depth=6, line_num_only=False):
    """
    stack_trace
    @param depth: stack depth
    @type line_num_only: only return the line number of the ecxeption
    """
    import traceback

    stack = traceback.format_stack()
    stack.reverse()
    space = ""
    cnt = 0
    error = ""

    for line in stack:
        if cnt > 1:
            s = line
            parsed_line = s.strip().replace("\n", ":").split(",")
            error += space
            error += "/".join(parsed_line[0].split("/")[len(parsed_line[0].split("/")) - 2:]).replace('"', '')
            error += ":"

            if line_num_only:
                return error + parsed_line[1].replace("line ", "").strip()

            error += parsed_line[1].replace("line ", "").strip()
            error += parsed_line[2].replace("  ", " ").replace("  ", " ").replace("  ", " ")
            space += "  "
            error += "\n"

        cnt += 1

        if len(space) > len("  " * depth):
            error += ("  " * depth) + "....\n"
            break

    return error


def handle_exception(exc, again=True, ret_err=False):
    """
    @param exc: Exception
    @type exc:
    @param again: bool
    @type again:
    @param ret_err: bool
    @type ret_err:
    """
    import sys
    import traceback
    if again and ret_err:
        raise Exception("handle_exception, raise_again and ret_err can't both be true")

    exc_type, exc_value, exc_traceback = sys.exc_info()
    error = "\n\033[95m" + log_date_time_string() + " ---------------------------\n"
    error += "\033[95m" + log_date_time_string() + "   !!! EXCEPTION !!!\n"
    error += "\033[95m" + log_date_time_string() + " ---------------------------\n"
    items = traceback.extract_tb(exc_traceback)

    #items.reverse()
    leni = 0
    error += "\033[93m" + log_date_time_string() + " " + str(exc_type) + "\n"
    error += "\033[93m" + log_date_time_string() + " " + str(exc) + "\n"
    error += "\033[95m" + log_date_time_string() + " ---------------------------\n"
    error += "\033[93m"

    try:
        linenumsize = 0

        for line in items:
            fnamesplit = str(line[0]).split("/")
            fname = "/".join(fnamesplit[len(fnamesplit) - 2:])
            ls = len(fname + ":" + str(line[1]))

            if ls > linenumsize:
                linenumsize = ls

        items.reverse()

        for line in items:
            leni += 1
            tabs = leni * "  "
            fnamesplit = str(line[0]).split("/")
            fname = "/".join(fnamesplit[len(fnamesplit) - 2:])
            fname_number = fname + ":" + str(line[1])
            fname_number += (" " * (linenumsize - len(fname_number)))
            val = ""

            if line[3]:
                val = line[3]

            error += fname_number + " | " + tabs + val + "\n"

        if len(items) < 4:
            error += stack_trace()
    except Exception, e:
        print "\033[93m" + log_date_time_string(), "cba_utils.py:252", e, '\033[m'
        print "\033[93m" + log_date_time_string(), "cba_utils.py:253", exc, '\033[m'

    error += "\033[95m" + log_date_time_string() + " ---------------------------\n"

    if ret_err:
        return error.replace("\033[95m", "")
    else:
        import sys
        sys.stderr.write(str(error) + '\033[0m')

    if again:
        raise exc

    return "\033[93m" + error


def get_uuid(size):
    """
    make a human readable unique identifier
    @param size:
    @type size:
    """
    unique_id = _uu.uuid4().int
    alphabet = "bcdfghjkmnpqrstvwxz"
    alphabet_length = len(alphabet)
    output = ""

    while unique_id > 0:
        digit = unique_id % alphabet_length
        output += alphabet[digit]
        unique_id = int(unique_id / alphabet_length)

    return output[0:size]

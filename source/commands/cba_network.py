# coding=utf-8
"""
routines to connect to cryptobox
"""
import os
import time
import threading
import base64
import urllib
import subprocess
import json
import requests
from cba_utils import log, Memory, update_item_progress


def get_b64mstyle():
    """
    get_b64mstyle
    """
    return "data:b64encode/mstyle,"


def b64_decode_mstyle(s):
    """
    b64_decode_mstyle
    @type s: str, unicode
    """
    if not isinstance(s, str) and not isinstance(s, unicode):
        return s

    b64mstyle = get_b64mstyle()

    if s.find(b64mstyle) != 0:
        return s

    s = s.replace(b64mstyle, "")
    s = base64.decodestring(s.replace("-", "="))
    s = urllib.unquote(s)
    return s


def b64_encode_mstyle(s):
    """
    b64_encode_mstyle
    @type s: str, unicode
    """
    if not isinstance(s, str) and not isinstance(s, unicode):
        return s

    b64mstyle = get_b64mstyle()

    if s.find(b64mstyle) != -1:
        return s

    s = urllib.quote(s, safe='~()*!.\'')
    s = base64.encodestring(s).replace("=", "-").replace("\n", "")
    s = b64mstyle + s
    return s


def b64_object_mstyle(d):
    """
    b64_object_mstyle
    @type d: dict, list, object
    """
    if isinstance(d, dict):
        for k in d:
            d[k] = b64_object_mstyle(d[k])

        return d

    if isinstance(d, list):
        cnt = 0

        for k in d:
            d[cnt] = b64_object_mstyle(k)
            cnt += 1

        return d

    d = b64_decode_mstyle(d)
    return d


def object_b64_mstyle(d):
    """
    object_b64_mstyle
    @type d: dict, list, object
    """
    if isinstance(d, dict):
        for k in d:
            d[k] = object_b64_mstyle(d[k])

        return d

    if isinstance(d, list):
        cnt = 0

        for k in d:
            d[cnt] = object_b64_mstyle(k)
            cnt += 1

        return d

    d = b64_encode_mstyle(d)
    return d


def request_error(result):
    """
    request_error
    @type result: str, unicode
    """
    open("error.html", "w").write(result.text)
    subprocess.call(["lynx", "error.html"])
    os.remove("error.html")
    return


class ServerForbidden(Exception):
    """
    ServerForbidden
    """
    pass


class ServerError(Exception):
    """
    ServerError
    """
    pass


class NotAuthorized(Exception):
    """
    NotAuthorized
    """
    pass


def parse_http_result(result):
    """
    parse_http_result
    @param result: -
    @type result: str, unicode
    """
    if result.status_code == 403:
        raise ServerForbidden(result.reason)

    if result.status_code == 500:
        request_error(result)

        raise ServerError(result.reason)

    if result.raw.headers["content-type"] == "application/json":
        result = result.json()

    return result


on_server_lock = threading.Lock()


def on_server(memory, options, method, payload, session, files=None):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
    @type method: str or unicode
    @type payload: dict or None
    @type session: requests.sessions.Session or None
    @type files: dict
    @return: @rtype:
    """
    global on_server_lock

    try:
        on_server_lock.acquire()
        server = options.server
        cryptobox = options.cryptobox
        cookies = {}
        service = server + cryptobox + "/" + method + "/" + str(time.time())

        if not session:
            session = requests

        #verifyarg = os.path.join(os.getcwd(), "ca.cert")
        verifyarg = False

        if not payload:
            result = session.post(service, cookies=cookies, files=files, verify=verifyarg)
        elif files:
            result = session.post(service, data=payload, cookies=cookies, files=files, verify=verifyarg)
        else:
            result = session.post(service, data=json.dumps(payload), cookies=cookies, verify=verifyarg)
        try:
            return parse_http_result(result), memory
        except ServerForbidden:
            return (None, None), memory
    finally:
        on_server_lock.release()


def download_server(memory, options, url):
    """
    download_server
    @type memory: Memory
    @type options: optparse.Values, instance
    @type url: str, unicode
    """
    url = os.path.normpath(url)
    url = options.server + options.cryptobox + "/" + url

    #log("download server:", URL)
    session = memory.get("session")
    result = session.get(url, timeout=3600, stream=True, verify=False)

    if result.status_code == 403:
        raise ServerForbidden(result.reason)

    if result.status_code == 500:
        request_error(result)

        raise ServerError(result.reason)

    size = int(result.headers['Content-Length'].strip())
    downloaded_bytes = 0
    fileb = []

    for buf in result.iter_content(1024):
        if buf:
            fileb.append(buf)
            downloaded_bytes += len(buf)
            divider = float(size) / 100

            if divider > 0:
                percentage = int(float(downloaded_bytes) / divider)

                #percentage += get_item_progress()
                #percentage /= options.numdownloadthreads
                update_item_progress(percentage)

    content = b"".join(fileb)
    return content


def server_time(memory, options):
    """
    server_time
    @type memory: Memory
    @type options: optparse.Values, instance
    """
    result, memory = on_server(memory, options, "clock", payload=None, session=None)
    stime = float(result[0])
    return stime, memory


class PasswordException(Exception):
    """
    PasswordException
    """
    pass


def authorize(memory, options):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
    @rtype session, results, memory: dict, list, Memory
    """
    session = requests.Session()
    payload = {"username": options.username, "password": options.password, "trust_computer": True}
    result, memory = on_server(memory, options, "authorize", payload=payload, session=session)
    payload["trust_computer"] = True
    payload["trused_location_name"] = "Cryptobox"

    if result[0]:
        results = result[1]
        results["cryptobox"] = options.cryptobox
        results["payload"] = payload
        return session, results, memory
    else:
        raise PasswordException(options.username)


def authorize_user(memory, options, force=False):
    """
    authorize_user
    @type memory: Memory
    @type options: optparse.Values, instance
    @type force: bool
    """

    try:
        if memory.has("authorized"):
            if force:
                memory.replace("authorized", False)
            else:
                if memory.get("authorized"):
                    return memory

        session, results, memory = authorize(memory, options)
        memory.replace("session", session)
        memory.replace("authorized", True)
        return memory
    except PasswordException, p:
        log(p, "not authorized")
        memory.replace("authorized", False)
        return memory


def authorized(memory, options):
    """
    authorized
    @type options: optparse.Values, instance
    @type memory: Memory
    """
    if not memory.has("session"):
        memory.replace("authorized", False)
        return memory

    result, memory = on_server(memory, options, "authorized", payload=None, session=memory.get("session"))
    memory.replace("authorized", result[0])
    return memory

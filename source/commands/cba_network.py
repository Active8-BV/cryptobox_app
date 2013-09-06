# coding=utf-8
"""
routines to connect to cryptobox
"""
import os
import time
import base64
import urllib
import subprocess
import json
import requests
from cba_utils import cba_warning, log
from cba_memory import Memory


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


def on_server(memory, options, method, payload, session, files=None, retry=False):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
    @type method: str or unicode
    @type payload: dict or None
    @type session: requests.sessions.Session or None
    @type retry: bool
    @type files: dict
    @return: @rtype:
    """
    server = options.server
    cryptobox = options.cryptobox
    cookies = {}
    SERVICE = server + cryptobox + "/" + method + "/" + str(time.time())

    if not session:
        session = requests

    if not payload:
        result = session.post(SERVICE, cookies=cookies, files=files)
    elif files:
        result = session.post(SERVICE, data=payload, cookies=cookies, files=files)
    else:
        result = session.post(SERVICE, data=json.dumps(payload), cookies=cookies)

    try:
        return parse_http_result(result), memory
    except ServerForbidden, ex:
        if retry:
            log("unauthorized exit")
        else:
            log("unauthorized try again")

            if memory.has("session"):
                memory.delete("session")

            memory = authorize_user(memory, options)
            return on_server(memory, options, method, payload, session, files, retry=True)

        raise ex


def download_server(memory, options, url):
    """
    download_server
    @type memory: Memory
    @type options: optparse.Values, instance
    @type url: str, unicode
    """
    cookies = {}
    url = os.path.normpath(url)
    URL = options.server + options.cryptobox + "/" + url

    #log("download server:", URL)
    session = memory.get("session")
    result = session.get(URL, cookies=cookies)
    return parse_http_result(result), memory


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


def check_otp(memory, options, session, results):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
    @type session: requests.sessions.Session
    @type results: dict, instance
    """
    if not "otp" in results:
        return True
    else:
        payload = results["payload"]

        if "trust_computer" in payload:
            return True

        payload["otp"] = results["otp"]
        results, memory = on_server(memory, options, "checkotp", payload=payload, session=session)
        results = results.json()
        return results, memory


def authorize_user(memory, options):
    """
    authorize_user
    @type memory: Memory
    @type options: optparse.Values, instance
    """

    try:
        if memory.has("authorized"):
            if memory.get("authorized"):
                return memory

        if memory.has("session"):
            memory.replace("authorized", True)
            return memory

        session, results, memory = authorize(memory, options)
        memory.set("session", session)

        #if check_otp(memory, options, session, results):
        memory.replace("authorized", True)

        #else:
        #    memory.replace("authorized", False)
        return memory
    except PasswordException, p:
        cba_warning(p, "not authorized")
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

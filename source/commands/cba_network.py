# coding=utf-8
"""
routines to connect to cryptobox
"""
import os
import time
import base64
import urllib
import requests
import subprocess
import json
from cba_utils import cba_warning
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

    return result


def on_server(server, method, cryptobox, payload, session, files=None):
    """
    @type server: str or unicode
    @type method: str or unicode
    @type cryptobox: str or unicode
    @type payload: dict or None
    @type session: requests.sessions.Session or None
    @type files: dict
    @return: @rtype:
    """
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

    return parse_http_result(result)


def download_server(options, url):
    """
    download_server
    @type options: instance
    @type url: str, unicode
    """
    cookies = {}
    url = os.path.normpath(url)
    URL = options.server + options.cryptobox + "/" + url

    #log("download server:", URL)
    memory = Memory()
    session = memory.get("session")
    result = session.get(URL, cookies=cookies)
    return parse_http_result(result)


def server_time(server, cryptobox):
    """
    server_time
    @type server: str, unicode
    @type cryptobox: str, unicode
    """
    return float(on_server(server, "clock", cryptobox, payload=None, session=None)[0])


class PasswordException(Exception):
    """
    PasswordException
    """
    pass


def authorize(server, cryptobox, username, password):
    """
    @type server: str, unicode
    @type cryptobox: str or unicode
    @type username: str or unicode
    @type password: str or unicode
    """
    session = requests.Session()
    payload = {"username": username,
               "password": password, "trust_computer": True}

    result = on_server(server, "authorize", cryptobox=cryptobox, payload=payload, session=session)
    payload["trust_computer"] = True
    payload["trused_location_name"] = "Cryptobox"
    results = result.json()

    if results[0]:
        results = results[1]
        results["cryptobox"] = cryptobox
        results["payload"] = payload
        return session, results
    else:
        raise PasswordException(username)


def check_otp(server, session, results):
    """
    @type server: str, unicode
    @type session: requests.sessions.Session
    @type results: dict
    """
    if not "otp" in results:
        return True
    else:

        payload = results["payload"]
        if "trust_computer" in payload:
            return True
        cryptobox = results["cryptobox"]
        payload["otp"] = results["otp"]
        results = on_server(server, "checkotp", cryptobox=cryptobox, payload=payload, session=session)
        results = results.json()
        return results


def authorize_user(memory, options):
    """
    authorize_user
    @type options: instance
    @type memory: Memory
    """

    try:
        if memory.has("authorized"):
            if memory.get("authorized"):
                return memory
        if memory.has("session"):
            memory.replace("authorized", True)
            return memory

        session, results = authorize(options.server, options.cryptobox, options.username, options.password)
        memory.set("session", session)
        if check_otp(options.server, session, results):
            memory.replace("authorized", True)
        else:
            memory.replace("authorized", False)
        return memory
    except PasswordException, p:
        cba_warning(p, "not authorized")
        memory.replace("authorized", False)
        return memory


def authorized(memory, options):
    """
    authorized
    @type options: instance
    @type memory: Memory
    """

    if not memory.has("session"):
        memory.replace("authorized", False)
        return memory

    cryptobox = options.cryptobox
    result = on_server(options.server, "authorized", cryptobox=cryptobox, payload=None, session=memory.get("session")).json()
    memory.replace("authorized", result[0])
    return memory

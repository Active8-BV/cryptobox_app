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
SERVER = "http://127.0.0.1:8000/"

#SERVER = "https://www.cryptobox.nl/"


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


def on_server(method, cryptobox, payload, session, files=None):
    """
    @type method: str or unicode
    @type cryptobox: str or unicode
    @type payload: dict or None
    @type session: requests.sessions.Session or None
    @type files: dict
    @return: @rtype:
    """
    cookies = {}
    SERVICE = SERVER + cryptobox + "/" + method + "/" + str(time.time())
    print "cba_network.py:175", SERVICE
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
    global SERVER
    cookies = {}
    url = os.path.normpath(url)
    URL = SERVER + options.cryptobox + "/" + url

    #log("download server:", URL)
    memory = Memory()
    session = memory.get("session")
    result = session.get(URL, cookies=cookies)
    return parse_http_result(result)


def server_time(cryptobox):
    """
    server_time
    @type cryptobox: str, unicode
    """
    return float(on_server("clock", cryptobox, payload=None, session=None)[0])


class PasswordException(Exception):
    """
    PasswordException
    """
    pass


def authorize(username, password, cryptobox):
    """
    @type username: str or unicode
    @type password: str or unicode
    @type cryptobox: str or unicode
    @return: @rtype: @raise:

    """
    session = requests.Session()
    payload = {"username": username,
               "password": password}

    result = on_server("authorize", cryptobox=cryptobox, payload=payload, session=session)
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


def check_otp(session, results):
    """
    @type session: requests.sessions.Session
    @type results: dict
    @return: @rtype:
    """
    if not "otp" in results:
        return True
    else:
        payload = results["payload"]
        cryptobox = results["cryptobox"]
        payload["otp"] = results["otp"]
        results = on_server("checkotp", cryptobox=cryptobox, payload=payload, session=session)
        results = results.json()
        return results


def authorize_user(options):
    """
    authorize_user
    @type options: instance
    """

    try:
        memory = Memory()

        if memory.has("session"):
            return True

        session, results = authorize(options.username, options.password, options.cryptobox)
        memory.set("session", session)
        return check_otp(session, results)
    except PasswordException, p:
        cba_warning(p, "not authorized")
        return False


def authorized(options):
    """
    authorized
    @type options: instance
    """
    memory = Memory()
    cryptobox = options.cryptobox
    result = on_server("authorized", cryptobox=cryptobox, payload=None, session=memory.get("session")).json()
    return result[0]

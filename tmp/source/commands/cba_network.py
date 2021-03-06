# coding=utf-8
"""
routines to connect to cryptobox
"""
import os
import time
import threading
import base64
import urllib
import json
import requests
from cba_utils import Memory, update_item_progress, message_json
from cba_crypto import get_named_temporary_file


def get_b64safe():
    """
    get_b64safe
    """
    return "data:b64encode/safe,"


def b64_decode_safe(s):
    """
    b64_decode_safe
    @type s: str, unicode
    """
    if not isinstance(s, str) and not isinstance(s, unicode):
        return s

    b64safe = get_b64safe()
    if s.find(b64safe) != 0:
        return s

    s = s.replace(b64safe, "")
    s = base64.decodestring(s.replace("-", "="))
    s = urllib.unquote(s)
    return s


def b64_encode_safe(s):
    """
    b64_encode_safe
    @type s: str, unicode
    """
    if not isinstance(s, str) and not isinstance(s, unicode):
        return s

    b64safe = get_b64safe()
    if s.find(b64safe) != -1:
        return s

    s = urllib.quote(s, safe='~()*!.\'')
    s = base64.encodestring(s).replace("=", "-").replace("\n", "")
    s = b64safe + s
    return s


def b64_object_safe(d):
    """
    b64_object_safe
    @type d: dict, list, object
    """
    if isinstance(d, dict):
        for k in d:
            d[k] = b64_object_safe(d[k])

        return d

    if isinstance(d, list):
        cnt = 0

        for k in d:
            d[cnt] = b64_object_safe(k)
            cnt += 1

        return d

    d = b64_decode_safe(d)
    return d


def object_b64_safe(d):
    """
    object_b64_safe
    @type d: dict, list, object
    """
    if isinstance(d, dict):
        for k in d:
            d[k] = object_b64_safe(d[k])

        return d

    if isinstance(d, list):
        cnt = 0

        for k in d:
            d[cnt] = object_b64_safe(k)
            cnt += 1

        return d

    d = b64_encode_safe(d)
    return d


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

    if result.status_code >= 500:
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
            result = session.post(service, cookies=cookies, files=files, verify=verifyarg, timeout=60)
        elif files:
            result = session.post(service, data=payload, cookies=cookies, files=files, verify=verifyarg)
        else:
            result = session.post(service, data=json.dumps(payload), cookies=cookies, verify=verifyarg, timeout=60)
        try:
            return parse_http_result(result), memory
        except ServerForbidden:
            return (None, None), memory
    finally:
        on_server_lock.release()


def download_server(memory, options, url, output_name_item_percentage=None):
    """
    download_server
    @type memory: Memory, None
    @type options: optparse.Values, instance
    @type url: str, unicode
    @type output_name_item_percentage: str
    """
    if memory:
        url = os.path.normpath(url)
        url = options.server + options.cryptobox + "/" + url
        session = memory.get("session")
        result = session.get(url, timeout=3600, stream=True, verify=False)
    else:
        result = requests.get(url, timeout=3600, stream=True, verify=False)

    if result.status_code == 403:
        raise ServerForbidden(result.reason)

    if result.status_code == 500:
        raise ServerError(result.reason)

    tf_download = get_named_temporary_file(auto_delete=False)

    if "Content-Length" in result.headers:
        size = int(result.headers['Content-Length'].strip())
        downloaded_bytes = 0
        prev_percenage = -1
        last_update = time.time()

        for buf in result.iter_content(1024):
            if buf:
                tf_download.write(buf)
                downloaded_bytes += len(buf)
                divider = float(size) / 100

                if divider > 0:
                    percentage = int(float(downloaded_bytes) / divider)
                    if percentage != prev_percenage:
                        if time.time() - last_update > 0.5:
                            if output_name_item_percentage:
                                update_item_progress(percentage, output_name_item_percentage)
                            else:
                                update_item_progress(percentage)

                            last_update = time.time()

                        prev_percenage = percentage

        return tf_download
    else:
        tf_download.write(result.content)

    return tf_download.name


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

    def __init__(self, *args, **kwargs): # real signature unknown
        super(PasswordException, self).__init__(args, kwargs)


def authorize(memory, options):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
    @rtype session, results, memory: dict, list, Memory
    """
    session = requests.Session()
    payload = {"username": options.username,
               "password": options.password,
               "trust_computer": True}

    result, memory = on_server(memory, options, "authorize", payload=payload, session=session)
    payload["trust_computer"] = True
    payload["trused_location_name"] = "Cryptobox"

    if result[0]:
        results = result[1]
        results["cryptobox"] = options.cryptobox
        results["payload"] = payload
        memory.replace("session_token", results["session_token"])
        memory.replace("private_key", results["private_key"])
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

    #noinspection PyBroadException
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
        memory.replace("connection", True)
        return memory
    except requests.ConnectionError:
        message_json("No connection possible")
        memory.replace("authorized", False)
        memory.replace("connection", False)
        return memory
    except:
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

    if not result[0]:
        memory.replace("authorized", False)
        memory.delete("session")
    else:
        memory.replace("authorized", result[0])

    return memory


def new_mandate(memory, options, mandate_key_param):
    """
    @type options: optparse.Values, instance
    @type memory: Memory
    @type mandate_key_param: str
    """
    if not memory.has_get("authorized"):
        message_json("request_mandate not authorized")

        raise NotAuthorized("new_mandate")

    result = on_server(memory, options, "newmandate", {"mandate_key_param": mandate_key_param}, session=memory.get("session"))
    if len(result) > 1:
        if result[0] is not None:
            if result[0] != "mandate_with_this_name_exists":
                return result[0]
    raise NotAuthorized("mandate_denied")


def get_mandate(memory, options, mandate_key_param):
    """
    @type options: optparse.Values, instance
    @type memory: Memory
    @type mandate_key_param: str
    """
    if not memory.has_get("authorized"):
        message_json("request_mandate not authorized")

        raise NotAuthorized("new_mandate")

    result = on_server(memory, options, "getmandate", {"mandate_key_param": mandate_key_param}, session=memory.get("session"))
    if len(result) > 1:
        if result[0] is not None:
            return result[0]
    raise NotAuthorized("mandate_denied")

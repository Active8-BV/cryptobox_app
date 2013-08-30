# coding=utf-8
"""
sync functions
"""
import os
import uuid
import base64
import urllib
import shutil
import multiprocessing
from cba_index import get_local_index, cryptobox_locked, TreeLoadError
from cba_blobs import write_blobs_to_filepaths, have_blob
from cba_feedback import update_progress
from cba_network import download_server, on_server, NotAuthorized, ServerForbidden, authorize_user
from cba_utils import handle_exception, strcmp, log, exit_app_warning
from cba_memory import have_serverhash, \
    Memory, \
    add_server_file_history, \
    in_server_file_history, \
    del_serverhash, \
    add_local_file_history, \
    in_local_file_history, \
    del_local_file_history, \
    del_server_file_history
from cba_file import ensure_directory
from cba_crypto import make_sha1_hash


def download_blob(options, node):
    """
    download_blob
    @type options: instance
    @type node: dict
    """

    try:
        url = "download/" + node["doc"]["m_short_id"]
        result = download_server(options, url)
        return {"url": result.url, "content_hash": node["content_hash_latest_timestamp"][0], "content": result.content}
    except Exception, e:
        handle_exception(e)


def get_unique_content(options, all_unique_nodes, local_file_paths):
    """
    @type options: optparse.Values
    @type all_unique_nodes: dict
    @type local_file_paths: list
    """
    if len(local_file_paths) == 0:
        return

    unique_nodes_hashes = [fhash for fhash in all_unique_nodes if not have_blob(options, fhash)]
    unique_nodes = [all_unique_nodes[fhash] for fhash in all_unique_nodes if fhash in unique_nodes_hashes]
    pool = multiprocessing.Pool(processes=options.numdownloadthreads)
    downloaded_files = []

    #noinspection PyUnusedLocal

    def done_downloading(result):
        """
        done_downloading
        @type result: dict
        """
        write_blobs_to_filepaths(options, local_file_paths, result["content"], result["content_hash"])
        downloaded_files.append(result["url"])
        update_progress(len(downloaded_files), len(unique_nodes), "downloading")

    download_results = []

    unique_nodes = [node for node in unique_nodes if not os.path.exists(os.path.join(options.dir, node["doc"]["m_path"].lstrip(os.path.sep)))]
    for node in unique_nodes:
        result = pool.apply_async(download_blob, (options, node), callback=done_downloading)
        download_results.append(result)

    pool.close()
    pool.join()

    for result in download_results:
        if not result.successful():
            result.get()

    pool.terminate()


def sync_directories_with_server(options, serverindex, dirname_hashes_server, unique_dirs):
    """
    sync_directories_with_server
    @type options: instance
    @type serverindex: dict
    @type dirname_hashes_server: dict
    @type unique_dirs: set
    """
    fake = options.fake
    localindex = get_local_index()
    local_dirs_not_on_server = []

    for dirhashlocal in localindex["dirnames"]:
        found = False

        for dirhashserver in dirname_hashes_server:
            if strcmp(dirhashserver, localindex["dirnames"][dirhashlocal]["dirnamehash"]):
                found = True

        if not found:
            if localindex["dirnames"][dirhashlocal]["dirname"] != options.dir:
                local_dirs_not_on_server.append(localindex["dirnames"][dirhashlocal])

    dirs_to_make_on_server = []
    dirs_to_remove_locally = []

    for node in local_dirs_not_on_server:
        if float(os.stat(node["dirname"]).st_mtime) >= float(serverindex["tree_timestamp"]):
            dirs_to_make_on_server.append(node)

        elif have_serverhash(node["dirnamehash"]):
            dirs_to_remove_locally.append(node)
        else:
            dirs_to_make_on_server.append(node)

    memory = Memory()
    cryptobox = options.cryptobox

    payload = {"foldernames": [dir_name["dirname"].replace(options.dir, "") for dir_name in dirs_to_make_on_server]}
    for dir_name in payload["foldernames"]:
        log("add server", dir_name)

        if not fake:
            add_server_file_history(dir_name)

    if not fake and len(payload["foldernames"]) > 0:
        on_server(options.server, "docs/makefolder", cryptobox=cryptobox, payload=payload, session=memory.get("session")).json()

    for node in dirs_to_remove_locally:
        log("remove local", node["dirname"])

        if os.path.exists(node["dirname"]):
            if not fake:
                shutil.rmtree(node["dirname"], True)

    on_server_not_local = [np for np in [os.path.join(options.dir, np.lstrip("/")) for np in unique_dirs] if not os.path.exists(np)]
    dir_names_to_delete_on_server = []

    for dir_name in on_server_not_local:
        dirname_rel = dir_name.replace(options.dir, "")

        if in_server_file_history(dirname_rel):
            dir_names_to_delete_on_server.append(dirname_rel)
        else:
            log("add local:", dir_name)

            if not fake:
                ensure_directory(dir_name)
                add_server_file_history(dirname_rel)

    short_node_ids_to_delete = []
    shortest_paths = set()

    for drl1 in dir_names_to_delete_on_server:
        shortest = ""

        for drl2 in dir_names_to_delete_on_server:
            if drl2 in drl1 or drl1 in drl2:
                if len(drl2) < len(shortest) or len(shortest) == 0:
                    shortest = drl2

        shortest_paths.add(shortest)

    for dir_name_rel in shortest_paths:
        log("remove server:", dir_name_rel)

        if not fake:
            del_serverhash(dir_name_rel)

        short_node_ids_to_delete.extend([node["doc"]["m_short_id"] for node in serverindex["doclist"] if node["doc"]["m_path"] == dir_name_rel])

    if len(short_node_ids_to_delete) > 0:
        payload = {"tree_item_list": short_node_ids_to_delete}

        if not fake:
            on_server(options.server, "docs/delete", cryptobox=cryptobox, payload=payload, session=memory.get("session")).json()


def upload_file(options, file_object, parent):
    """
    @param options:
    @type options:
    @param file_object:
    @type file_object:
    @param parent:
    @type parent:
    @raise NotAuthorized:

    """
    memory = Memory()

    if not memory.has("session"):
        raise NotAuthorized("trying to upload without a session")

    payload = {"uuid": uuid.uuid4().hex, "parent": parent, "path": ""}
    files = {'file': file_object}
    on_server(options.server, "docs/upload", cryptobox=options.cryptobox, payload=payload, session=memory.get("session"), files=files)


def save_encode_b64(s):
    """
    @param s:
    @type s:
    @return: @rtype:
    """
    s = urllib.quote(s)
    s = base64.encodestring(s)
    s = s.replace("=", "-")
    return s


class MultipleGuidsForPath(Exception):
    """
    MultipleGuidsForPath
    """
    pass


class NoParentFound(Exception):
    """
    NoParentFound
    """
    pass


def path_to_server_parent_guid(options, path):
    """
    @param options:
    @type options:
    @param path:
    @type path:
    @return: @rtype: @raise MultipleGuidsForPath:

    """
    memory = Memory()
    path = path.replace(options.dir, "")
    path = os.path.dirname(path)

    result = [x["doc"]["m_short_id"] for x in memory.get("serverindex")["doclist"] if strcmp(x["doc"]["m_path"], path)]

    if len(result) == 0:
        raise NoParentFound(path)

    elif len(result) == 1:
        return result[0]
    else:
        raise MultipleGuidsForPath(path)


def get_server_index(memory, options):
    """
    @type memory: Memory
    @type options: instance
    @return: index
    @rtype: dict
    """
    try:
        result = on_server(options.server, "tree", cryptobox=options.cryptobox, payload={'listonly': True}, session=memory.get("session")).json()
    except ServerForbidden:
        log("unauthorized try again")

        if memory.has("session"):
            memory.delete("session")

        memory = authorize_user(memory, options)
        result = on_server(options.server, "tree", cryptobox=options.cryptobox, payload={'listonly': True}, session=memory.get("session")).json()
    if not result[0]:
        raise TreeLoadError()
    serverindex = result[1]
    memory.set("serverindex", serverindex)
    return memory


def sync_server(options):
    """
    @type options: optparse.Values
    @return: @rtype: @raise:

    """
    fake = options.fake

    if cryptobox_locked():
        exit_app_warning("cryptobox is locked, no sync possible, first decrypt (-d)")
        return

    memory = Memory()
    cryptobox = options.cryptobox

    serverindex = get_server_index(memory, options)
    memory.replace("serverindex", serverindex)
    unique_content = {}
    unique_dirs = set()
    fnodes = []
    checked_dirnames = []
    dirname_hashes_server = {}

    for node in serverindex["doclist"]:
        if node["doc"]["m_nodetype"] == "folder":
            dirname_of_path = node["doc"]["m_path"]
        else:
            dirname_of_path = os.path.dirname(node["doc"]["m_path"])

        node["dirname_of_path"] = dirname_of_path
        unique_dirs.add(dirname_of_path)

        if node["content_hash_latest_timestamp"]:
            unique_content[node["content_hash_latest_timestamp"][0]] = node
            fnodes.append(node)

        if dirname_of_path not in checked_dirnames:
            dirname_hash = make_sha1_hash(dirname_of_path.replace(os.path.sep, "/"))
            dirname_hashes_server[dirname_hash] = node

        checked_dirnames.append(dirname_of_path)

    sync_directories_with_server(options, serverindex, dirname_hashes_server, unique_dirs)
    localindex = get_local_index()
    local_paths_to_delete_on_server = []
    new_server_files_to_local_paths = []

    for fnode in fnodes:
        server_path_to_local = os.path.join(options.dir, fnode["doc"]["m_path"].lstrip(os.path.sep))

        if os.path.exists(server_path_to_local):
            add_local_file_history(server_path_to_local)
        else:
            if in_local_file_history(server_path_to_local):
                local_paths_to_delete_on_server.append(server_path_to_local)
            else:
                log("new file on server", server_path_to_local)
                new_server_files_to_local_paths.append(fnode)

    local_filenames = [(localindex["dirnames"][d]["dirname"], localindex["dirnames"][d]["filenames"]) for d in localindex["dirnames"] if len(localindex["dirnames"][d]["filenames"]) > 0]
    local_filenames_set = set()

    for ft in local_filenames:
        for fname in ft[1]:
            if not str(fname["name"]).startswith("."):
                local_file = os.path.join(ft[0], fname["name"])
                local_filenames_set.add(local_file)

    for local_file_path in local_filenames_set:
        if os.path.exists(local_file_path):
            print "cba_sync.py:341", local_file_path
            if not in_local_file_history(local_file_path):
                parent = path_to_server_parent_guid(options, local_file_path)

                if parent:
                    log("new file on disk", local_file_path, parent)
                    upload_file(options, open(local_file_path, "rb"), parent)

    get_unique_content(options, unique_content, new_server_files_to_local_paths)
    delete_file_guids = []

    for fpath in local_paths_to_delete_on_server:
        relpath = fpath.replace(options.dir, "")

        guids = [x["doc"]["m_short_id"] for x in serverindex["doclist"] if x["doc"]["m_path"] == relpath]

        if len(guids) == 1:
            log("delete file from server", fpath)
            delete_file_guids.append(guids[0])

    if len(delete_file_guids) > 0:
        payload = {"tree_item_list": delete_file_guids}

        if not fake:
            on_server(options.server, "docs/delete", cryptobox=cryptobox, payload=payload, session=memory.get("session")).json()

    for fpath in local_paths_to_delete_on_server:
        del_server_file_history(fpath)
        del_local_file_history(fpath)

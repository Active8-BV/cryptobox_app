# coding=utf-8
"""
sync functions
"""
import os
import time
import uuid
import base64
import urllib
import shutil
from cba_index import cryptobox_locked, TreeLoadError, index_files_visit, make_local_index
from cba_blobs import write_blobs_to_filepaths, have_blob
from cba_feedback import update_progress
from cba_network import download_server, on_server, NotAuthorized, authorize_user
from cba_utils import handle_exception, strcmp, exit_app_warning, log
from cba_memory import have_serverhash, Memory, add_server_file_history, in_server_file_history, \
    add_local_file_history, in_local_file_history, del_server_file_history, del_local_file_history
from cba_file import ensure_directory
from cba_crypto import make_sha1_hash


def download_blob(memory, options, node):
    """
    download_blob
    @type memory: Memory
    @type options: instance
    @type node: dict
    """

    try:
        url = "download/" + node["doc"]["m_short_id"]
        result, memory = download_server(memory, options, url)
        return {"url": result.url, "content_hash": node["content_hash_latest_timestamp"][0], "content": result.content}
    except Exception, e:
        handle_exception(e)


def get_unique_content(memory, options, all_unique_nodes, local_file_paths):
    """
    @type memory: Memory
    @type options: istance
    @type all_unique_nodes: dict
    @type local_file_paths: list
    """
    if len(local_file_paths) == 0:
        return memory

    unique_nodes_hashes = [fhash for fhash in all_unique_nodes if not have_blob(options, fhash)]
    unique_nodes = [all_unique_nodes[fhash] for fhash in all_unique_nodes if fhash in unique_nodes_hashes]
    from multiprocessing.dummy import Pool

    pool = Pool(processes=options.numdownloadthreads)
    downloaded_files = []

    #noinspection PyUnusedLocal

    def done_downloading(result):
        """
        done_downloading
        @type result: dict
        """
        downloaded_files.append(result)
        update_progress(len(downloaded_files), len(unique_nodes), "downloading")

    download_results = []

    unique_nodes = [node for node in unique_nodes if not os.path.exists(os.path.join(options.dir, node["doc"]["m_path"].lstrip(os.path.sep)))]
    for node in unique_nodes:
        result = pool.apply_async(download_blob, (memory, options, node), callback=done_downloading)
        download_results.append(result)

    pool.close()
    pool.join()

    for result in download_results:
        if not result.successful():
            result.get()

    pool.terminate()

    for result in downloaded_files:
        memory = write_blobs_to_filepaths(memory, options, local_file_paths, result["content"], result["content_hash"])
        update_progress(len(downloaded_files), len(unique_nodes), "writing")

    return memory


def dirs_on_local(memory, options, localindex, dirname_hashes_server, tree_timestamp):
    """
    @type memory: Memory
    @param dirname_hashes_server: folders on server
    @type dirname_hashes_server: dict
    @type tree_timestamp: float
    @param options: options
    @type options: instance
    @type localindex: dict
    @return: list of dirs on server or to remove locally
    @rtype: tuple
    """
    local_dirs_not_on_server = []

    for dirhashlocal in localindex["dirnames"]:
        found = False

        for dirhashserver in dirname_hashes_server:
            if strcmp(dirhashserver, localindex["dirnames"][dirhashlocal]["dirnamehash"]):
                found = True

        if not found:
            if localindex["dirnames"][dirhashlocal]["dirname"] != options.dir:
                local_dirs_not_on_server.append(localindex["dirnames"][dirhashlocal])

    dirs_make_server = []
    dirs_del_local = []

    for node in local_dirs_not_on_server:
        if float(os.stat(node["dirname"]).st_mtime) >= tree_timestamp:
            dirs_make_server.append(node)

        have_hash_on_server, memory = have_serverhash(memory, node["dirnamehash"])

        if have_hash_on_server:
            dirs_del_local.append(node)
        else:
            dirs_make_server.append(node)

    return dirs_make_server, dirs_del_local


def instruct_server_to_make_folders(memory, options, dirs_make_server):
    """
    @type memory: Memory
    @type options: instance
    @type dirs_make_server: list
    @rtype: Memory
    """
    payload = {"foldernames": [dir_name["dirname"].replace(options.dir, "") for dir_name in dirs_make_server]}
    for dir_name in payload["foldernames"]:
        add_server_file_history(memory, dir_name)

    if len(payload["foldernames"]) > 0:
        result, memory = on_server(memory, options, "docs/makefolder", payload=payload, session=memory.get("session"))

    serverindex, memory = get_server_index(memory, options)
    return serverindex, memory


def remove_local_folders(dirs_del_local):
    """
    @type dirs_del_local: list
    """
    for node in dirs_del_local:
        if os.path.exists(node["dirname"]):
            shutil.rmtree(node["dirname"], True)


def remove_local_files(file_del_local):
    """
    @type file_del_local: list
    """
    for fpath in file_del_local:
        if os.path.exists(fpath):
            os.remove(fpath)


def make_directories_local(memory, options, localindex, folders):
    """
    @type memory: Memory
    @type options: instance
    @type localindex: dict
    @type folders: list
    """
    for f in folders:
        ensure_directory(f["name"])
        memory = add_server_file_history(memory, f["relname"])
        arg = {"DIR": options.dir, "folders": {"dirnames": {}}, "numfiles": 0}
        index_files_visit(arg, f["name"], [])

        for k in arg["folders"]["dirnames"]:
            localindex["dirnames"][k] = arg["folders"]["dirnames"][k]

    return memory


def dirs_on_server(memory, options, unique_dirs_server):
    """
    @type memory: Memory
    @type options: instance
    @type unique_dirs_server: set
    @rtype: list, Memory
    """
    local_folders_removed = [np for np in [os.path.join(options.dir, np.lstrip(os.path.sep)) for np in unique_dirs_server] if not os.path.exists(np)]
    dirs_del_server = []
    dirs_make_local = []

    for dir_name in local_folders_removed:
        dirname_rel = dir_name.replace(options.dir, "")
        have_on_server, memory = in_server_file_history(memory, dirname_rel)

        if have_on_server:
            dirs_del_server.append(dirname_rel)
        else:
            folder = {"name": dir_name, "relname": dirname_rel}
            dirs_make_local.append(folder)

    return dirs_del_server, dirs_make_local, memory


def wait_for_tasks(memory, options):
    """
    wait_for_tasks
    @type memory: Memory
    @type options: instance
    """
    while True:
        result, memory = on_server(memory, options, "tasks", payload={}, session=memory.get("session"))
        num_tasks = len(result[1])

        if num_tasks == 0:
            return memory

        if num_tasks < 2:
            time.sleep(0.2)
        else:
            time.sleep(1)

            if num_tasks > 4:
                log("waiting for tasks")
                time.sleep(2)


def instruct_server_to_delete_items(memory, options, short_node_ids_to_delete):
    """
    @type memory: Memory
    @type options: instance
    @type short_node_ids_to_delete: list
    """
    if len(short_node_ids_to_delete) > 0:
        payload = {"tree_item_list": short_node_ids_to_delete}
        result, memory = on_server(memory, options, "docs/delete", payload=payload, session=memory.get("session"))
        memory = wait_for_tasks(memory, options)
    return memory


def instruct_server_to_delete_folders(memory, options, serverindex, dirs_del_server):
    """
    @type memory: Memory
    @type options: instance
    @type serverindex: dict
    @type dirs_del_server: list
    @return:
    @rtype:
    """
    short_node_ids_to_delete = []
    shortest_paths = set()

    for drl1 in dirs_del_server:
        shortest = ""

        for drl2 in dirs_del_server:
            if drl2 in drl1 or drl1 in drl2:
                if len(drl2) < len(shortest) or len(shortest) == 0:
                    shortest = drl2

        shortest_paths.add(shortest)

    for dir_name_rel in shortest_paths:
        short_node_ids_to_delete.extend([node["doc"]["m_short_id"] for node in serverindex["doclist"] if node["doc"]["m_path"] == dir_name_rel])

    memory = instruct_server_to_delete_items(memory, options, short_node_ids_to_delete)
    return memory


def sync_directories_with_server(memory, options, localindex, serverindex):
    """
    sync_directories_with_server
    @type memory: Memory
    @type options: instance
    @type localindex: dict
    @type serverindex: dict
    """
    dirname_hashes_server, fnodes, unique_content, unique_dirs = parse_serverindex(serverindex)
    tree_timestamp = float(serverindex["tree_timestamp"])

    # find new folders locally and determine if we need to make on server or delete locally
    dirs_make_server, dirs_del_local = dirs_on_local(memory, options, localindex, dirname_hashes_server, tree_timestamp)
    serverindex, memory = instruct_server_to_make_folders(memory, options, dirs_make_server)
    remove_local_folders(dirs_del_local)

    # local checking
    dirs_del_server, dirs_make_local, memory = dirs_on_server(memory, options, unique_dirs)
    memory = make_directories_local(memory, options, localindex, dirs_make_local)

    # find new folders on server and determine local creation or server removal
    dirs_del_server, dirs_make_local, memory = dirs_on_server(memory, options, unique_dirs)
    memory = instruct_server_to_delete_folders(memory, options, serverindex, dirs_del_server)
    return memory, dirs_del_server


def upload_file(memory, options, file_object, parent):
    """
    @type memory: Memory
    @param options:
    @type options:
    @param file_object:
    @type file_object:
    @param parent:
    @type parent:
    @raise NotAuthorized:

    """
    if not memory.has("session"):
        raise NotAuthorized("trying to upload without a session")

    payload = {"uuid": uuid.uuid4().hex, "parent": parent, "path": ""}
    files = {'file': file_object}
    result, memory = on_server(memory, options, "docs/upload", payload=payload, session=memory.get("session"), files=files)
    return memory


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


def path_to_server_parent_guid(memory, options, serverindex, path):
    """
    @type memory: Memory
    @param options:
    @type options:
    @param path:
    @type path:
    @type serverindex: dict
    @return: @rtype: @raise MultipleGuidsForPath:

    """
    path = path.replace(options.dir, "")
    path = os.path.dirname(path)

    result = [x["doc"]["m_short_id"] for x in serverindex["doclist"] if strcmp(x["doc"]["m_path"], path)]

    if len(result) == 0:
        raise NoParentFound(path)

    elif len(result) == 1:
        return result[0], memory
    else:
        raise MultipleGuidsForPath(path)


def path_to_server_shortid(memory, options, serverindex, path):
    """
    @type memory: Memory
    @param options:
    @type options:
    @param path:
    @type path:
    @type serverindex: dict
    @return: @rtype: @raise MultipleGuidsForPath:

    """
    path = path.replace(options.dir, "")

    result = [x["doc"]["m_short_id"] for x in serverindex["doclist"] if strcmp(x["doc"]["m_path"], path)]

    if len(result) == 0:
        raise NoParentFound(path)

    elif len(result) == 1:
        return result[0], memory
    else:
        raise MultipleGuidsForPath(path)


def get_server_index(memory, options):
    """
    @type memory: Memory
    @type options: instance
    @return: index
    @rtype: dict, Memory
    """
    if not memory.has("session"):
        memory = authorize_user(memory, options)

    result, memory = on_server(memory, options, "tree", payload={'listonly': True}, session=memory.get("session"))
    if not result[0]:
        raise TreeLoadError()

    serverindex = result[1]
    memory.replace("serverindex", serverindex)
    return serverindex, memory


def parse_serverindex(serverindex):
    """
    @type serverindex: dict
    @rtype: dict, list, dict, set
    """
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

    return dirname_hashes_server, fnodes, unique_content, unique_dirs


def diff_new_files_on_server(memory, options, server_file_nodes, dirs_scheduled_for_removal):
    """
    diff_new_files_on_server
    @type memory: Memory
    @type options: instance
    @type server_file_nodes: list
    @type dirs_scheduled_for_removal: list
    """
    file_del_server = []
    file_downloads = []

    for fnode in server_file_nodes:
        server_path_to_local = os.path.join(options.dir, fnode["doc"]["m_path"].lstrip(os.path.sep))

        if os.path.exists(server_path_to_local):
            memory = add_local_file_history(memory, server_path_to_local)
        else:
            seen_local_file_before, memory = in_local_file_history(memory, server_path_to_local)

            if seen_local_file_before:
                file_del_server.append(server_path_to_local)
            else:
                file_downloads.append(fnode)

    dirs_scheduled_for_removal = [os.path.join(options.dir, d.lstrip(os.path.sep)) for d in dirs_scheduled_for_removal]
    file_del_server = [f for f in file_del_server if os.path.dirname(f) not in dirs_scheduled_for_removal]
    return memory, file_del_server, file_downloads


def diff_files_locally(memory, options, localindex, serverindex):
    """
    diff_files_locally
    @type memory: Memory
    @type options: instance
    @type localindex: dict
    @type serverindex: dict
    """
    local_filenames = [(localindex["dirnames"][d]["dirname"], localindex["dirnames"][d]["filenames"]) for d in localindex["dirnames"] if len(localindex["dirnames"][d]["filenames"]) > 0]
    local_filenames_set = set()
    file_uploads = []

    for ft in local_filenames:
        for fname in ft[1]:
            if not str(fname["name"]).startswith("."):
                local_file = os.path.join(ft[0], fname["name"])
                local_filenames_set.add(str(local_file))

    server_file_paths = [str(os.path.join(options.dir, x["doc"]["m_path"].lstrip(os.path.sep))) for x in serverindex["doclist"]]
    for local_file_path in local_filenames_set:
        if os.path.exists(local_file_path):
            seen_local_file_before, memory = in_local_file_history(memory, local_file_path)

            if not seen_local_file_before:
                parent, memory = path_to_server_parent_guid(memory, options, serverindex, local_file_path)

                if parent:
                    upload_file_object = {"local_file_path": local_file_path, "parent_short_id": parent}
                    file_uploads.append(upload_file_object)

    file_del_local = []

    for local_file_path in local_filenames_set:
        if os.path.exists(local_file_path):
            if local_file_path not in server_file_paths:
                seen_local_file_before, memory = in_local_file_history(memory, local_file_path)

                if seen_local_file_before:
                    file_del_local.append(local_file_path)

    return file_uploads, file_del_local, memory


def sync_server(memory, options, localindex):
    """
    @type memory: Memory
    @type options: optparse.Values
    @type localindex: dict
    @return: @rtype: @raise:

    """
    if cryptobox_locked(memory):
        exit_app_warning("cryptobox is locked, no sync possible, first decrypt (-d)")
        return

    serverindex, memory = get_server_index(memory, options)

    # folder structure
    dirname_hashes_server, server_file_nodes, unique_content, unique_dirs = parse_serverindex(serverindex)
    memory, dirs_del_server = sync_directories_with_server(memory, options, localindex, serverindex)
    serverindex, memory = get_server_index(memory, options)

    # file diff
    memory, file_del_server, file_downloads = diff_new_files_on_server(memory, options, server_file_nodes, dirs_del_server)
    memory = get_unique_content(memory, options, unique_content, file_downloads)
    localindex = make_local_index(options)
    file_uploads, file_del_local, memory = diff_files_locally(memory, options, localindex, serverindex)
    for uf in file_uploads:
        memory = upload_file(memory, options, open(uf["local_file_path"], "rb"), uf["parent_short_id"])

    remove_local_files(file_del_local)

    for fpath in file_del_server:
        memory = del_server_file_history(memory, fpath)
        memory = del_local_file_history(memory, fpath)

    for fpath in file_del_local:
        memory = del_server_file_history(memory, fpath)
        memory = del_local_file_history(memory, fpath)

    return localindex, memory

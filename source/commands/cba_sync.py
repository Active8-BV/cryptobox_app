# coding=utf-8
"""
sync functions
"""
import os
import uuid
import base64
import urllib
import shutil
from collections import namedtuple
from cba_index import cryptobox_locked, TreeLoadError, index_files_visit
from cba_blobs import write_blobs_to_filepaths, have_blob
from cba_feedback import update_progress
from cba_network import download_server, on_server, NotAuthorized, ServerForbidden, authorize_user
from cba_utils import handle_exception, strcmp, log, exit_app_warning
from cba_memory import have_serverhash, \
    Memory, \
    add_server_file_history, \
    in_server_file_history, \
    add_local_file_history, \
    in_local_file_history, \
    del_local_file_history, \
    del_server_file_history
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

    dirs_to_make_on_server = []
    dirs_to_remove_locally = []

    for node in local_dirs_not_on_server:
        if float(os.stat(node["dirname"]).st_mtime) >= tree_timestamp:
            dirs_to_make_on_server.append(node)

        have_hash_on_server, memory = have_serverhash(memory, node["dirnamehash"])

        if have_hash_on_server:
            dirs_to_remove_locally.append(node)
        else:
            dirs_to_make_on_server.append(node)

    return dirs_to_make_on_server, dirs_to_remove_locally


def instruct_server_to_make_folders(memory, options, dirs_to_make_on_server):
    """
    @type memory: Memory
    @type options: instance
    @type dirs_to_make_on_server: list
    @rtype: Memory
    """
    payload = {"foldernames": [dir_name["dirname"].replace(options.dir, "") for dir_name in dirs_to_make_on_server]}
    for dir_name in payload["foldernames"]:
        add_server_file_history(memory, dir_name)

    if len(payload["foldernames"]) > 0:
        on_server(options.server, "docs/makefolder", cryptobox=options.cryptobox, payload=payload, session=memory.get("session")).json()

    serverindex, memory = get_server_index(memory, options)
    return serverindex, memory


def remove_local_folders(dirs_to_remove_locally):
    """
    @type dirs_to_remove_locally: list
    """
    for node in dirs_to_remove_locally:
        if os.path.exists(node["dirname"]):
            shutil.rmtree(node["dirname"], True)


def make_directories_local(memory, options, localindex, folders):
    """
    @type memory: Memory
    @type options: instance
    @type localindex: dict
    @type folders: list
    """
    for f in folders:
        ensure_directory(f.name)
        memory = add_server_file_history(memory, make_sha1_hash(f.relname))
        arg = {"DIR": options.dir, "folders": {"dirnames": {}}, "numfiles": 0}
        index_files_visit(arg, f.name, [])

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
    local_folders_removed = [np for np in [os.path.join(options.dir, np.lstrip("/")) for np in unique_dirs_server] if not os.path.exists(np)]
    dir_names_to_delete_on_server = []
    dir_names_to_make_locally = []

    for dir_name in local_folders_removed:
        dirname_rel = dir_name.replace(options.dir, "")
        have_on_server, memory = in_server_file_history(memory, dirname_rel)

        if have_on_server:
            dir_names_to_delete_on_server.append(dirname_rel)
        else:
            folder = namedtuple("folder", ["name", "relname"])
            folder.name = dir_name
            folder.relname = dirname_rel
            dir_names_to_make_locally.append(folder)

    return dir_names_to_delete_on_server, dir_names_to_make_locally, memory


def instruct_server_to_delete_folders(memory, options, serverindex, dir_names_to_delete_on_server):
    """
    @type memory: Memory
    @type options: instance
    @type serverindex: dict
    @type dir_names_to_delete_on_server: list
    @return:
    @rtype:
    """
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
        short_node_ids_to_delete.extend([node["doc"]["m_short_id"] for node in serverindex["doclist"] if node["doc"]["m_path"] == dir_name_rel])

    if len(short_node_ids_to_delete) > 0:
        payload = {"tree_item_list": short_node_ids_to_delete}
        on_server(options.server, "docs/delete", cryptobox=options.cryptobox, payload=payload, session=memory.get("session")).json()
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
    tree_timestamp= float(serverindex["tree_timestamp"])

    # find new folders locally and determine if we need to make on server or delete locally
    dirs_to_make_on_server, dirs_to_remove_locally = dirs_on_local(memory, options, localindex, dirname_hashes_server, tree_timestamp)
    serverindex, memory = instruct_server_to_make_folders(memory, options, dirs_to_make_on_server)
    remove_local_folders(dirs_to_remove_locally)

    # local checking
    dir_names_to_delete_on_server, dir_names_to_make_locally, memory = dirs_on_server(memory, options, unique_dirs)
    memory = make_directories_local(memory, options, localindex, dir_names_to_make_locally)

    # find new folders on server and determine local creation or server removal
    dir_names_to_delete_on_server, dir_names_to_make_locally, memory = dirs_on_server(memory, options, unique_dirs)
    memory = instruct_server_to_delete_folders(memory, options, serverindex, dir_names_to_delete_on_server)

    return memory, dir_names_to_delete_on_server


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
    on_server(options.server, "docs/upload", cryptobox=options.cryptobox, payload=payload, session=memory.get("session"), files=files)
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


def path_to_server_parent_guid(memory, options, path):
    """
    @type memory: Memory
    @param options:
    @type options:
    @param path:
    @type path:
    @return: @rtype: @raise MultipleGuidsForPath:

    """
    path = path.replace(options.dir, "")
    path = os.path.dirname(path)

    result = [x["doc"]["m_short_id"] for x in memory.get("serverindex")["doclist"] if strcmp(x["doc"]["m_path"], path)]

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


def diff_new_files_on_server(memory, options, file_nodes, dirs_scheduled_for_removal):
    """
    diff_new_files_on_server
    @type memory: Memory
    @type options: instance
    @type file_nodes: list
    @type dirs_scheduled_for_removal: list
    """
    locally_deleted_files = []
    files_to_download = []

    for fnode in file_nodes:
        server_path_to_local = os.path.join(options.dir, fnode["doc"]["m_path"].lstrip(os.path.sep))

        if os.path.exists(server_path_to_local):
            memory = add_local_file_history(memory, server_path_to_local)
        else:
            seen_local_file_before, memory = in_local_file_history(memory, server_path_to_local)

            if seen_local_file_before:
                locally_deleted_files.append(server_path_to_local)
            else:
                files_to_download.append(fnode)

    dirs_scheduled_for_removal = [os.path.join(options.dir, d.lstrip("/")) for d in dirs_scheduled_for_removal]
    locally_deleted_files = [f for f in locally_deleted_files if os.path.dirname(f) not in dirs_scheduled_for_removal]

    return memory, locally_deleted_files, files_to_download


def diff_new_files_locally(memory, options, localindex):
    """
    diff_new_files_locally
    @type memory: Memory
    @type options: instance
    @type localindex: dict
    """
    local_filenames = [(localindex["dirnames"][d]["dirname"], localindex["dirnames"][d]["filenames"]) for d in localindex["dirnames"] if len(localindex["dirnames"][d]["filenames"]) > 0]
    local_filenames_set = set()
    files_to_upload = []

    for ft in local_filenames:
        for fname in ft[1]:
            if not str(fname["name"]).startswith("."):
                local_file = os.path.join(ft[0], fname["name"])
                local_filenames_set.add(local_file)

    for local_file_path in local_filenames_set:
        if os.path.exists(local_file_path):
            seen_local_file_before, memory = in_local_file_history(memory, local_file_path)

            if not seen_local_file_before:
                parent, memory = path_to_server_parent_guid(memory, options, local_file_path)

                if parent:
                    upload_file_object = namedtuple("upload_file_object", ["local_file_path", "parent_short_id"])
                    upload_file_object.local_file_path = local_file_path
                    upload_file_object.parent_short_id = parent
                    files_to_upload.append(upload_file_object)

    return files_to_upload, memory


def sync_server(memory, options, localindex):
    """
    @type memory: Memory
    @type options: optparse.Values
    @type localindex: dict
    @return: @rtype: @raise:

    """
    fake = options.fake

    if cryptobox_locked(memory):
        exit_app_warning("cryptobox is locked, no sync possible, first decrypt (-d)")
        return

    cryptobox = options.cryptobox
    serverindex, memory = get_server_index(memory, options)
    dirname_hashes_server, file_nodes, unique_content, unique_dirs = parse_serverindex(serverindex)
    memory, dir_names_to_delete_on_server = sync_directories_with_server(memory, options, localindex, serverindex)
    memory, locally_deleted_files, files_to_download = diff_new_files_on_server(memory, options, file_nodes, dir_names_to_delete_on_server)
    files_to_upload, memory = diff_new_files_locally(memory, options, localindex)
    for uf in files_to_upload:
        memory = upload_file(memory, options, open(uf.local_file_path, "rb"), uf.parent_short_id)

    memory = get_unique_content(memory, options, unique_content, files_to_download)
    delete_file_guids = []

    for fpath in locally_deleted_files:
        relpath = fpath.replace(options.dir, "")

        guids = [x["doc"]["m_short_id"] for x in serverindex["doclist"] if x["doc"]["m_path"] == relpath]

        if len(guids) == 1:
            delete_file_guids.append(guids[0])

    if len(delete_file_guids) > 0:
        payload = {"tree_item_list": delete_file_guids}

        if not fake:
            on_server(options.server, "docs/delete", cryptobox=cryptobox, payload=payload, session=memory.get("session")).json()

    for fpath in locally_deleted_files:
        memory = del_server_file_history(memory, fpath)
        memory = del_local_file_history(memory, fpath)
    return memory

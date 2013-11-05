# coding=utf-8
"""
sync functions
"""
import os
import time
import uuid
import cPickle
import base64
import urllib
import shutil
import urllib2
import poster
from cba_index import quick_lock_check, TreeLoadError, index_files_visit, make_local_index, get_localindex
from cba_blobs import write_blobs_to_filepaths, have_blob
from cba_network import download_server, on_server, NotAuthorized, authorize_user, authorized
from cba_utils import handle_exception, strcmp, exit_app_warning, update_progress, update_item_progress, Memory
from cba_file import ensure_directory, add_server_path_history, in_server_path_history, add_local_path_history, in_local_path_history, del_server_path_history, del_local_path_history, path_to_relative_path_unix_style
from cba_crypto import make_sha1_hash
from cba_file import write_file, read_file


def download_blob(memory, options, node):
    """
    download_blob
    @type memory: Memory
    @type options: optparse.Values, instance
    @type node: dict
    """
    url = "download/" + node["doc"]["m_short_id"]
    result = download_server(memory, options, url)
    return result, node["content_hash_latest_timestamp"][0]


def get_unique_content(memory, options, all_unique_nodes, local_paths):
    """
    @type memory: Memory
    @type options: istance
    @type all_unique_nodes: dict
    @type local_paths: list
    """
    if len(local_paths) == 0:
        return memory

    unique_nodes_hashes = [fhash for fhash in all_unique_nodes if not have_blob(options, fhash)]
    unique_nodes = [all_unique_nodes[fhash] for fhash in all_unique_nodes if fhash in unique_nodes_hashes]
    downloaded_files_cnt = 0
    unique_nodes = [node for node in unique_nodes if not os.path.exists(os.path.join(options.dir, node["doc"]["m_path"].lstrip(os.path.sep)))]
    for node in unique_nodes:
        downloaded_files_cnt += 1
        update_progress(downloaded_files_cnt, len(unique_nodes), "downloading " + str(node["doc"]["m_name"]))
        content, content_hash = download_blob(memory, options, node)
        memory = write_blobs_to_filepaths(memory, options, local_paths, content, content_hash)

        for local_path in local_paths:
            memory = add_local_path_history(memory, local_path["doc"]["m_path"])

    for lp in local_paths:
        source_path = None
        file_path = os.path.join(options.dir, lp["doc"]["m_path"].lstrip(os.path.sep))

        if not os.path.exists(file_path):
            for lph in all_unique_nodes:
                if lph == lp["content_hash_latest_timestamp"][0]:
                    source_path = os.path.join(options.dir, all_unique_nodes[lph]["doc"]["m_path"].lstrip(os.path.sep))
                    break

        if source_path:
            st_ctime, st_atime, st_mtime, st_mode, st_uid, st_gid, st_size, data = read_file(source_path, True)
            st_mtime = int(lp["content_hash_latest_timestamp"][1])
            write_file(file_path, data, st_mtime, st_mtime, st_mode, st_uid, st_gid)

    local_paths_not_written = [fp for fp in local_paths if not os.path.exists(os.path.join(options.dir, fp["doc"]["m_path"].lstrip(os.path.sep)))]

    if len(local_paths_not_written) > 0:
        local_index = get_localindex(memory)
        local_path_hashes = {}

        for ldir in local_index["dirnames"]:
            for f in local_index["dirnames"][ldir]["filenames"]:
                if "hash" in f:
                    local_path_hashes[f["hash"]] = os.path.join(local_index["dirnames"][ldir]["dirname"], f["name"])

        for lfnw in local_paths_not_written:
            w = False

            for lfh in local_path_hashes:
                if not w:
                    if strcmp(lfnw["content_hash_latest_timestamp"][0], lfh):
                        w = True
                        open(os.path.join(options.dir, lfnw["doc"]["m_path"].lstrip(os.path.sep)), "w").write(open(local_path_hashes[lfh]).read())

    return memory


def dirs_on_local(memory, options, localindex, dirname_hashes_server, serverindex):
    """
    @type memory: Memory
    @param dirname_hashes_server: folders on server
    @type dirname_hashes_server: dict
    @type serverindex: dict
    @param options: options
    @type options: optparse.Values, instance
    @type localindex: dict
    @return: list of dirs on server or to remove locally
    @rtype: tuple
    """
    if "tree_timestamp" not in serverindex:
        raise Exception("dirs_on_local needs a tree timestamp")

    tree_timestamp = int(serverindex["tree_timestamp"])
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
    server_dir_history = []

    if memory.has("serverpath_history"):
        server_dir_history = [path_to_relative_path_unix_style(memory, x[0]) for x in memory.get("serverpath_history")]
    for node in local_dirs_not_on_server:
        if os.path.exists(node["dirname"]):
            rel_dirname = path_to_relative_path_unix_style(memory, node["dirname"])
            node["relname"] = rel_dirname

            if rel_dirname not in serverindex["dirlist"]:
                folder_timestamp = os.stat(node["dirname"]).st_mtime
                if int(folder_timestamp) >= int(tree_timestamp):
                    dirs_make_server.append(node)
                else:
                    if node["dirname"].replace(options.dir, "") not in server_dir_history:
                        dirs_make_server.append(node)
                    else:
                        dirs_del_local.append(node)

            else:
                dirs_del_local.append(node)

    dirs_make_server_unique = []
    key_set = set([k["dirnamehash"] for k in dirs_make_server])
    for k in key_set:
        for i in dirs_make_server:
            if strcmp(i["dirnamehash"], k):
                dirs_make_server_unique.append(i)
                break

    return dirs_make_server_unique, dirs_del_local


def instruct_server_to_make_folders(memory, options, dirs_make_server):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
    @type dirs_make_server: list
    @rtype: Memory
    """
    foldernames = [dir_name["dirname"].replace(options.dir, "").lstrip(os.sep) for dir_name in dirs_make_server]
    for dir_name in foldernames:
        add_server_path_history(memory, dir_name)

    for foldername in foldernames:
        payload = {"foldername": foldername}
        result, memory = on_server(memory, options, "docs/makefolder", payload=payload, session=memory.get("session"))

    serverindex, memory = get_server_index(memory, options)
    return serverindex, memory


def server_path_to_shortid(memory, options, path):
    path = save_encode_b64(path)
    payload = {"path": path}
    result, memory = on_server(memory, options, "pathtoshortid", payload=payload, session=memory.get("session"))

    if result[0]:
        return result[1]
    return None


def remove_local_folders(memory, dirs_del_local):
    """
    @type memory: Memory
    @type dirs_del_local: list
    """
    for node in dirs_del_local:
        if os.path.exists(node["dirname"]):
            shutil.rmtree(node["dirname"], True)
            memory = del_local_path_history(memory, node["dirname"])
    return memory


def remove_local_paths(memory, file_del_local):
    """
    @type memory: Memory
    @type file_del_local: list
    """
    for fpath in file_del_local:
        if os.path.exists(fpath):
            os.remove(fpath)
            memory = del_local_path_history(memory, fpath)
    return memory


def make_directories_local(memory, options, localindex, folders):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
    @type localindex: dict
    @type folders: list
    """
    for f in folders:
        ensure_directory(f["name"])
        memory = add_local_path_history(memory, f["name"])
        memory = add_server_path_history(memory, f["relname"])
        arg = {"DIR": options.dir,
               "folders": {"dirnames": {}},
               "numfiles": 0}
        index_files_visit(arg, f["name"], [])

        for k in arg["folders"]["dirnames"]:
            localindex["dirnames"][k] = arg["folders"]["dirnames"][k]

    return memory


def dirs_on_server(memory, options, unique_dirs_server):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
    @type unique_dirs_server: set
    @rtype: list, Memory
    """
    local_folders_removed_local_server = [np for np in [os.path.join(options.dir, np.lstrip(os.path.sep)) for np in unique_dirs_server] if not os.path.exists(np)]
    dirs_del_server = []
    dirs_make_local = []

    # check if they are really removed or just new

    if memory.has("localpath_history"):
        local_path_history = memory.get("localpath_history")
        local_path_history_disk = [os.path.join(options.dir, x[0].lstrip(os.sep)) for x in local_path_history]
        local_path_history_disk_folders = [x for x in local_path_history_disk if os.path.isdir(x)]
        local_path_history_disk_file_folders = [os.path.dirname(x) for x in local_path_history_disk if not os.path.isdir(x)]
        local_path_history_disk_folders.extend(local_path_history_disk_file_folders)
        local_path_history_disk_folders = tuple(set(local_path_history_disk_folders))
        local_folders_removed = [x for x in local_folders_removed_local_server if x in local_path_history_disk_folders]

        if len(local_folders_removed) == 0:
            local_folders_removed = [x for x in local_folders_removed_local_server if x in local_path_history_disk]

            if len(local_folders_removed) == 0:

                # first run
                dirs_make_local = [{"name": os.path.join(options.dir, x.lstrip(os.sep)), "relname": x} for x in unique_dirs_server if (os.path.exists(os.path.join(options.dir, x.lstrip(os.sep))) not in local_path_history_disk_folders and not os.path.exists(os.path.join(options.dir, x.lstrip(os.sep))))]

    else:
        local_folders_removed = []

    for dir_name in local_folders_removed:
        dirname_rel = dir_name.replace(options.dir, "")
        had_on_server, memory = in_server_path_history(memory, dirname_rel)
        have_on_server = False

        if not had_on_server:
            if memory.has("serverindex"):
                serverindex = memory.get("serverindex")

                if "dirlist" in serverindex:
                    have_on_server = dirname_rel in memory.get("serverindex")["dirlist"]

        if have_on_server:
            memory = add_server_path_history(memory, dirname_rel)

        # initial run, download everything
        if not memory.has("localpath_history"):
            had_on_server = have_on_server = False

        if had_on_server or have_on_server:
            dirs_del_server.append(dirname_rel)
        else:
            folder = {"name": dir_name,
                      "relname": dirname_rel}
            dirs_make_local.append(folder)

    return dirs_del_server, dirs_make_local, memory


def wait_for_tasks(memory, options):
    """
    wait_for_tasks
    @type memory: Memory
    @type options: optparse.Values, instance
    """
    initial_num_tasks = -1

    while True:
        session = None

        if memory.has("session"):
            session = memory.get("session")

        result, memory = on_server(memory, options, "tasks", payload={}, session=session)

        if result:
            if len(result) > 1:
                if result[1]:
                    num_tasks = len([x for x in result[1] if x["m_command_object"] != "StorePassword"])

                    if initial_num_tasks == -1:
                        initial_num_tasks = num_tasks

                    update_progress(initial_num_tasks - num_tasks, initial_num_tasks, "waiting for tasks to finish on server")
                    if num_tasks == 0:
                        return memory

                    if num_tasks > 3:
                        time.sleep(1)
                        if num_tasks > 6:
                            print "cba_sync.py:328", "waiting for tasks", num_tasks

                else:
                    return memory

        time.sleep(1)


def instruct_server_to_delete_items(memory, options, short_node_ids_to_delete):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
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
    @type options: optparse.Values, instance
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


def save_encode_b64(s):
    """
    @param s:
    @type s:
    @return: @rtype:
    """
    s = urllib.quote(s.encode("utf8"))
    s = base64.encodestring(s)
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
    parent_path = path.replace(options.dir, "")
    parent_path = os.path.dirname(parent_path)
    result = [x["doc"]["m_short_id"] for x in serverindex["doclist"] if strcmp(x["doc"]["m_path"], parent_path)]

    if len(result) > 1:
        raise MultipleGuidsForPath(parent_path)

    if len(result) == 0:
        shortid = server_path_to_shortid(memory, options, parent_path)
    else:
        if len(result) > 1:
            raise MultipleGuidsForPath(parent_path)

        shortid = result[0]

    if not shortid:
        result = [x["doc"]["m_short_id"] for x in serverindex["doclist"] if strcmp(x["doc"]["m_path"], "/")]

        if len(result) > 1:
            raise MultipleGuidsForPath(parent_path)

        shortid = result[0]

    if not shortid:
        raise NoParentFound(parent_path)

    return shortid, parent_path, memory


class MultiplePathsForSID(Exception):
    """
    MultiplePathsForSID
    """
    pass


class NoPathFound(Exception):
    """
    NoPathFound
    """
    pass


def short_id_to_server_path(memory, serverindex, short_id):
    """
    @type memory: Memory
    @param short_id:
    @type short_id: str, unicode
    @type serverindex: dict
    @return: @rtype: @raise MultipleGuidsForPath:

    """
    result = [x["doc"]["m_path"] for x in serverindex["doclist"] if strcmp(x["doc"]["m_short_id"], short_id)]

    if len(result) == 0:
        raise NoPathFound(short_id)

    elif len(result) == 1:
        return result[0], memory
    else:
        raise MultiplePathsForSID(short_id)


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


def get_tree_sequence(memory, options):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
    """
    clock_tree_seq, memory = on_server(memory, options, "clock", {}, memory.get("session"))
    return int(clock_tree_seq[1])


def get_server_index(memory, options):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
    @return: index
    @rtype: dict, Memory
    """
    if not memory.has("session"):
        if memory.has("authorized"):
            memory.delete("authorized")

    if not memory.has("session"):
        memory = authorize_user(memory, options)

    tree_seq = get_tree_sequence(memory, options)
    memory.replace("tree_seq", tree_seq)
    result, memory = on_server(memory, options, "tree", payload={'listonly': True}, session=memory.get("session"))
    if not result[0]:
        if memory.has("authorized"):
            memory.delete("authorized")

        memory = authorize_user(memory, options)
        result, memory = on_server(memory, options, "tree", payload={'listonly': True}, session=memory.get("session"))
        if not result[0]:
            raise TreeLoadError()

    serverindex = result[1]

    dirlistfiles = [os.path.dirname(x["doc"]["m_path"]) for x in serverindex["doclist"] if x["doc"]["m_nodetype"] == "file"]
    dirlistfolders = [x["doc"]["m_path"] for x in serverindex["doclist"] if x["doc"]["m_nodetype"] == "folder"]
    dirlistserver = dirlistfiles
    dirlistserver.extend(dirlistfolders)
    serverindex["dirlist"] = tuple(list(set(dirlistserver)))
    serverindex["doclist"] = tuple(serverindex["doclist"])
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


def diff_new_files_on_server(memory, options, server_path_nodes, dirs_scheduled_for_removal):
    """
    diff_new_files_on_server
    @type memory: Memory
    @type options: optparse.Values, instance
    @type server_path_nodes: list
    @type dirs_scheduled_for_removal: list
    """
    file_del_server = []
    file_downloads = []

    for fnode in server_path_nodes:
        server_path_to_local = os.path.join(options.dir, fnode["doc"]["m_path"].lstrip(os.path.sep))

        if os.path.exists(server_path_to_local):
            pass
        else:
            seen_local_path_before, memory = in_local_path_history(memory, server_path_to_local)

            if seen_local_path_before:
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
    @type options: optparse.Values, instance
    @type localindex: dict
    @type serverindex: dict
    """
    local_pathnames = [(localindex["dirnames"][d]["dirname"], localindex["dirnames"][d]["filenames"]) for d in localindex["dirnames"] if len(localindex["dirnames"][d]["filenames"]) > 0]
    local_pathnames_set = set()
    file_uploads = []

    for ft in local_pathnames:
        for fname in ft[1]:
            if not str(fname["name"]).startswith("."):
                local_path = os.path.join(ft[0], fname["name"])
                local_pathnames_set.add(str(local_path))

    server_path_paths = [str(os.path.join(options.dir, x["doc"]["m_path"].lstrip(os.path.sep))) for x in serverindex["doclist"]]
    for local_path in local_pathnames_set:
        if os.path.exists(local_path):
            seen_local_path_before, memory = in_local_path_history(memory, local_path)

            if not seen_local_path_before:
                upload_file_object = {"local_path": local_path,
                                      "parent_short_id": None,
                                      "path": local_path}

                file_uploads.append(upload_file_object)

    file_del_local = []

    for local_path in local_pathnames_set:
        if os.path.exists(local_path):
            if local_path not in server_path_paths:
                seen_local_path_before, memory = in_local_path_history(memory, local_path)

                if seen_local_path_before:
                    file_del_local.append(local_path)

    return file_uploads, file_del_local, memory


def print_pickle_variable_for_debugging(var, varname):
    """
    :param var:
    :param varname:
    """
    print "cba_sync.py:655", varname + " = cPickle.loads(base64.decodestring(\"" + base64.encodestring(cPickle.dumps(var)).replace("\n", "") + "\"))"


def get_sync_changes(memory, options, localindex, serverindex):
    """
    get_sync_changes
    @type memory: Memory
    @type options: optparse.Values, instance
    @type localindex: dict
    @type serverindex: dict
    @rtype (memory, options, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_path_nodes, unique_content): tuple
    """
    print_state = False

    #print_state = True

    if print_state:
        print_pickle_variable_for_debugging(memory, "memory")
        print_pickle_variable_for_debugging(localindex, "localindex")
        print_pickle_variable_for_debugging(serverindex, "serverindex")

    dirname_hashes_server, server_path_nodes, unique_content, unique_dirs = parse_serverindex(serverindex)

    # server dirs
    dir_del_server_tmp, dir_make_local, memory = dirs_on_server(memory, options, unique_dirs)

    #local dirs
    dir_make_server, dir_del_local = dirs_on_local(memory, options, localindex, dirname_hashes_server, serverindex)

    # find new files on server
    memory, file_del_server, file_downloads = diff_new_files_on_server(memory, options, server_path_nodes, dir_del_server_tmp)

    #local files
    file_uploads, file_del_local, memory = diff_files_locally(memory, options, localindex, serverindex)
    file_del_local = [x for x in file_del_local if os.path.dirname(x) not in [y["dirname"] for y in dir_del_local]]

    # filter out file uploads from dirs to delete
    dir_del_local = [x for x in dir_del_local if x["dirname"] not in [os.path.dirname(y["local_path"]) for y in file_uploads]]
    dir_make_server = [x for x in dir_make_server if x["dirname"] not in [os.path.dirname(y["local_path"]) for y in file_uploads]]

    # filter out dirs to make from file_uploads:
    dir_make_server_tmp = []

    for dms in dir_make_server:
        add = True

        for fu in file_uploads:
            if dms["dirname"] in fu["local_path"]:
                add = False

        if add:
            dir_make_server_tmp.append(dms)

    dir_make_server = dir_make_server_tmp

    # prune directories to delete from files to download
    dir_del_server = []
    file_download_dirs = list(set([x["dirname_of_path"] for x in file_downloads]))
    for dds_path in dir_del_server_tmp:
        if len(file_downloads) > 0:

            #for dfl in file_download_dirs:
            if dds_path not in file_download_dirs:
                dir_del_server.append(dds_path)
        else:
            dir_del_server.append(dds_path)

    def add_size_relpath(lf):
        lf["size"] = os.stat(lf["local_path"]).st_size
        lf["rel_path"] = lf["path"].replace(options.dir, "")
        return f

    file_uploads = [add_size_relpath(f) for f in file_uploads]
    file_uploads = sorted(file_uploads, key=lambda k: k["size"])
    return memory, options, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_path_nodes, unique_content


def upload_file(session, server, cryptobox, file_path, rel_file_path, parent):
    """
    @type session: instance
    @type server: str, unicode
    @type cryptobox: str, unicode
    @type file_path: str, unicode
    @type rel_file_path: str, unicode
    @type parent: str, unicode
    @raise NotAuthorized:

    """

    try:
        if not session:
            raise NotAuthorized("trying to upload without a session")

        last_progress = [0]

        #noinspection PyUnusedLocal
        def prog_callback(param, current, total):
            """
            @type param:
            @type current:
            @type total:
            prog_callback
            """

            try:
                if param:
                    if time.time() - param.last_cb_time > 500:
                        param.last_cb_time = time.time()
                        percentage = 100 - ((total - current ) * 100) / total
                        if percentage != last_progress[0]:
                            last_progress[0] = percentage
                            update_item_progress(percentage)

            except Exception, exc:
                print "cba_sync.py:769", "updating upload progress failed", str(exc)

        opener = poster.streaminghttp.register_openers()
        opener.add_handler(urllib2.HTTPCookieProcessor(session.cookies))
        service = server + cryptobox + "/" + "docs/upload" + "/" + str(time.time())
        file_object = open(file_path, "rb")
        rel_path = save_encode_b64(rel_file_path)
        params = {'file': file_object,
                  "uuid": uuid.uuid4().hex,
                  "parent": parent,
                  "path": rel_path,
                  "ufile_name": os.path.basename(file_object.name)}

        poster.encode.MultipartParam.last_cb_time = time.time()
        datagen, headers = poster.encode.multipart_encode(params, cb=prog_callback)
        request = urllib2.Request(service, datagen, headers)

        #noinspection PyUnusedLocal
        result = urllib2.urlopen(request)
        return file_path
    except Exception, e:
        handle_exception(e, False)


def possible_new_dirs(file_path, memory):
    """
    @type file_path: str, unicode
    @type memory: Memory
    """
    if file_path is None:
        raise Exception("possible_new_dirs is None")

    possible_new_dir_list = []
    file_dir = os.path.dirname(file_path)
    rel_unix_path = path_to_relative_path_unix_style(memory, file_dir)
    unix_paths = rel_unix_path.split("/")
    tmp_dir = ""

    for up in unix_paths:
        if len(up.strip()) > 0:
            tmp_dir += "/" + up
            possible_new_dir_list.append(tmp_dir)

    return list(set(possible_new_dir_list))


def possible_new_dirs_extend(file_path_list, memory):
    """
    @type file_path_list: lsit
    @type memory: Memory
    """
    for file_path in file_path_list:
        file_path_list.extend(possible_new_dirs(file_path, memory))

    file_path_list = list(set(file_path_list))
    file_path_list.sort()
    return file_path_list


def upload_files(memory, options, serverindex, file_uploads):
    """
    upload_files
    @type memory: Memory
    @type options: optparse.Values, instance
    @type serverindex: dict
    @type file_uploads: list
    """
    for uf in file_uploads:
        try:
            uf["parent_short_id"], uf["parent_path"], memory = path_to_server_parent_guid(memory, options, serverindex, uf["local_path"])
        except NoParentFound:
            uf["parent_short_id"] = uf["parent_path"] = ""

    files_uploaded = []

    for uf in file_uploads:
        update_item_progress(1)
        if os.path.exists(uf["local_path"]):
            update_progress(len(files_uploaded) + 1, len(file_uploads), "upload: " + uf["local_path"])
            file_path = upload_file(memory.get("session"), options.server, options.cryptobox, uf["local_path"], path_to_relative_path_unix_style(memory, uf["local_path"]), uf["parent_short_id"])
            files_uploaded.append(file_path)
        else:
            update_progress(len(files_uploaded) + 1, len(file_uploads), "can't fnd" + uf["local_path"])

    return memory, files_uploaded


class NoSyncDirFound(Exception):
    """
    NoSyncDirFound
    """
    pass


def add_path_history(fpath, memory):
    """
    @type fpath:str, unicode
    @type memory: Memory
    """
    memory = add_server_path_history(memory, fpath)
    memory = add_local_path_history(memory, fpath)
    return memory


def del_path_history(fpath, memory):
    """
    @type fpath:str, unicode
    @type memory: Memory
    """
    memory = del_server_path_history(memory, fpath)
    memory = del_local_path_history(memory, fpath)
    return memory


def sync_server(memory, options):
    """
    @type memory: Memory
    @type options: optparse.Values, instance
    @return: @rtype: @raise:

    """
    if memory.has("session"):
        memory = authorized(memory, options)

    if not os.path.exists(options.dir):
        raise NoSyncDirFound(options.dir)

    if quick_lock_check(options):
        exit_app_warning("cryptobox is locked, no sync possible, first decrypt (-d)")
        return

    serverindex, memory = get_server_index(memory, options)

    # update seen server history files
    localindex = make_local_index(options)
    memory.replace("localindex", localindex)
    memory, options, file_del_server, file_downloads, file_uploads, dir_del_server, dir_make_local, dir_make_server, dir_del_local, file_del_local, server_path_nodes, unique_content = get_sync_changes(memory, options, localindex, serverindex)

    if len(dir_make_server) > 0:
        serverindex, memory = instruct_server_to_make_folders(memory, options, dir_make_server)
        serverdirpaths = [x["doc"]["m_path"] for x in serverindex["doclist"]]
        for fpath in serverdirpaths:
            memory = add_path_history(fpath, memory)

    if len(dir_del_local) > 0:
        memory = remove_local_folders(memory, dir_del_local)

    if len(dir_make_local) > 0:
        memory = make_directories_local(memory, options, localindex, dir_make_local)

    if len(dir_del_server) > 0:
        memory = instruct_server_to_delete_folders(memory, options, serverindex, dir_del_server)

    del_server_items = []

    for del_file in file_del_server:
        del_short_guid, memory = path_to_server_shortid(memory, options, serverindex, del_file.replace(options.dir, ""))
        del_server_items.append(del_short_guid)

    # delete items
    if len(del_server_items) > 0:
        memory = instruct_server_to_delete_items(memory, options, del_server_items)

    if len(file_downloads) > 0:
        memory = get_unique_content(memory, options, unique_content, file_downloads)

    if len(file_uploads) > 0:
        memory, files_uploaded = upload_files(memory, options, serverindex, file_uploads)
        files_uploaded = possible_new_dirs_extend(files_uploaded, memory)

        for fpath in files_uploaded:
            memory = add_path_history(fpath, memory)

    if len(file_del_local) > 0:
        memory = remove_local_paths(memory, file_del_local)

    file_del_server = possible_new_dirs_extend(file_del_server, memory)
    file_del_local = possible_new_dirs_extend(file_del_local, memory)
    dir_del_server = possible_new_dirs_extend(dir_del_server, memory)
    dir_del_local = possible_new_dirs_extend([x["dirname"] for x in dir_del_local], memory)
    for fpath in file_del_server:
        memory = del_path_history(fpath, memory)

    for fpath in file_del_local:
        memory = del_path_history(fpath, memory)

    if memory.has("localpath_history"):
        localpath_history = memory.get("localpath_history")
        localpaths = [x[0] for x in localpath_history]
        for fpath in dir_del_server:
            for lfpath in localpaths:
                if str(fpath) in str(lfpath):
                    memory = del_path_history(lfpath, memory)

            memory = del_path_history(fpath, memory)

    if memory.has("serverpath_history"):
        serverpath_history = memory.get("serverpath_history")
        serverpaths = [x[0] for x in serverpath_history]
        for fpath in dir_del_local:
            for lfpath in serverpaths:
                if fpath in lfpath:
                    memory = del_path_history(fpath, memory)

            memory = del_path_history(fpath, memory)

    memory = wait_for_tasks(memory, options)
    return localindex, memory

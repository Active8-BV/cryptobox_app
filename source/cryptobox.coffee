
child_process = require("child_process")
path = require("path")
fs = require("fs")
gui = require('nw.gui')
g_output = []
g_cba_main = null
g_second_counter = 0
g_error_message = null
g_info_message = null
g_encrypt_g_tray_item = null
g_decrypt_g_tray_item = null
g_show_hide_tray_item = null
cb_server_url = "http://127.0.0.1:8000/"
g_winmain = gui.Window.get()
g_tray = new gui.Tray(
    icon: "images/cryptoboxstatus-idle-lep.tiff"
)


g_tray.on 'click', -> alert
g_menu = new gui.Menu(
    type: 'menubar'
)
g_trayactions = new gui.Menu()
g_tray.menu = g_trayactions
g_menuactions = new gui.Menu()
g_winmain.menu = g_menu
warning = (ln, w) ->
    if w?
        if w?.trim?
            w = w.trim()
    else
        return

    if exist(w)
        if w.faultString?
            add_output(w.faultString)
        else if w.message
            add_output(w.message)
        else
            add_output(w)


add_output = (msgs) ->
    add_msg = (msg) ->
        if msg.indexOf?
            if msg.indexOf("Error") == -1
                if msg.indexOf("POST /RPC2") > 0
                    return

        if msg.replace?
            msg = msg.replace("stderr:", "")
            msg.replace("\n", "")
            msg = msg.trim()

        if exist(msg)
            g_output.push(msg)

    if msgs?.split?
        _.each(msgs.split("\n"), add_msg)
    else if msgs == "true"
        pass
    else if msgs == "false"
        pass
    else if msgs == true
        pass
    else if msgs == false
        pass

    else
        if msgs?
            g_output.push(msgs)
    console.log msgs.trim()
    return true


print = (msg, others...) ->
    len_others = _.size(others)

    #noinspection CoffeeScriptSwitchStatementWithNoDefaultBranch
    switch len_others
        when 0
            add_output(msg)
        when 1
            add_output(msg + " " + others[0])
        when 2
            add_output(msg + " " + others[0] + " " + others[1])
        when 3
            add_output(msg + " " + others[0] + " " + others[1] + " " + others[2])
        when 4
            add_output(msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3])
        when 5
            add_output(msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3] + " " + others[4])
        else
            add_output(others)
            add_output(msg)


warning = (ln, w) ->
    if w?
        if w?.trim?
            w = w.trim()
    else
        return

    if exist(w)
        if w.faultString?
            add_output(w.faultString)
        else if w.message
            add_output(w.message)
        else
            add_output(w)


option_to_array = (name, option) ->
    for k in _.keys(option)
        if option[k] == true
            option[k] = "1"

        if option[k] == false
            option[k] = "0"

    cmd_str = ""
    cmd_str += " --acommand " + option.acommand if option.acommand?
    cmd_str += " --cryptobox " + option.cryptobox if option.cryptobox?
    cmd_str += " --clear " + option.clear if option.clear?
    cmd_str += " --decrypt " + option.decrypt if option.decrypt?
    cmd_str += " --encrypt " + option.encrypt if option.encrypt?
    cmd_str += " --dir " + option.dir if option.dir?
    cmd_str += " --logout " + option.logout if option.logout?
    cmd_str += " --motivation " + option.motivation if option.motivation?
    cmd_str += " --numdownloadthreads " + option.numdownloadthreads if option.numdownloadthreads?
    cmd_str += " --check " + option.check if option.check?
    cmd_str += " --password " + option.password if option.password?
    cmd_str += " --remove " + option.remove if option.remove?
    cmd_str += " --sync " + option.sync if option.sync?
    cmd_str += " --treeseq " + option.treeseq if option.treeseq?
    cmd_str += " --username " + option.username if option.username?
    cmd_str += " --version " + option.version if option.version?
    cmd_str += " --server " + option.server if option.server?
    cmd_str += " --compiled " + option.compiled if option.compiled?
    print "cryptobox.cf:143", "python cba_main.py", cmd_str.trim()
    param_array = []

    push_param_array = (i) ->
        if _.size(i.trim()) > 0
            param_array.push(i)
    _.each(cmd_str.split(" "), push_param_array)
    return param_array


already_running = (output) ->
    if output.indexOf("Another instance is already running, quitting.") >= 0
        return true
    return false


cnt_char = (data, c) ->
    _.size(String(data).split(c)) - 1


possible_json = (data) ->
    if cnt_char(data, "{") == cnt_char(data, "}")
        try
            JSON.parse(data)
            return true
        catch ex
            return false
    return false


parse_json = (method, data, givelist, debug) ->
    try
        output = []
        datacopy = data
        data = String(data).split("\n")

        try_cb = (datachunk) ->
            if datachunk?
                if _.size(datachunk) > 0
                    datachunk = JSON.parse(datachunk)

                    if datachunk?
                        if datachunk.error_message?
                            g_error_message = datachunk?.error_message
                            add_output("error> " + g_error_message)
                        else if datachunk.log?
                            console?.log? datachunk.log
                        else if datachunk.message?
                            g_info_message = datachunk.message
                            add_output("info> " + g_info_message)
                        else
                            output.push(datachunk)

        _.each(data, try_cb)
    catch ex
        if debug?
            print "cryptobox.cf:199", method, "could not parse json", ex
            console?.log? datacopy
            return null

    if not givelist
        if _.size(output) == 1
            return output[0]

        if _.size(output) > 1

            #require('nw.gui').Window.get().showDevTools()
            print "cryptobox.cf:210", method, "parse_json multiple elements but givelist is not requested"
            console?.log? datacopy

    return output


run_cba_main = (name, options, cb_done, cb_intermediate, give_list) ->
    cmd_to_run = path.join(process.cwd(), "commands")
    cmd_to_run = path.join(cmd_to_run, "cba_main")
    options.compiled = cmd_to_run
    params = option_to_array(name, options)
    cba_main = child_process.spawn(cmd_to_run, params)
    g_cba_main = cba_main
    output = ""
    error = ""
    data = ""
    intermediate_cnt = 0

    if not give_list?
        give_list = false

    stdout_data = (data) ->
        output += data

        if not exist(cb_intermediate)
            return

        ssp = String(output).split("\n")

        has_data = (item) ->
            if _.size(item) > 0
                return true
            return false

        ssp = _.filter(ssp, has_data)
        nls = _.size(ssp)

        if nls > 0
            loop_cnt = 0

            call_intermediate = (data) ->
                if loop_cnt == intermediate_cnt
                    pdata = null

                    if possible_json(data)
                        pdata = parse_json(name, data, give_list, true)

                    if pdata
                        cb_intermediate(pdata)
                        intermediate_cnt += 1

                loop_cnt += 1
            _.each(ssp, call_intermediate)
    cba_main.stdout.on "data", stdout_data

    cba_main.stderr.on "data", (data) ->
        error += data

    execution_done = (event) ->
        g_cba_main = null

        if already_running(output)
            print "cryptobox.cf:272", "already running"
            if cb_done?
                cb_done(false, output)
        else
            output = parse_json(name, output, give_list, true)

            if cb_done?
                if event > 0
                    cb_done(false, output)
                else
                    cb_done(true, output)

    cba_main.on("exit", execution_done)


on_exit = ->
    if g_cba_main?
        g_cba_main.kill?()
    gui.App.quit()


store_user_var = (k, v, $q) ->
    p = $q.defer()
    db = new PouchDB('cb_userinfo')

    if not exist(db)
        p.reject("no db")
    else
        record = 
            _id: k
            value: v
        db.get k, (e, d) ->
            if exist(d)
                if exist(d._rev)
                    record._rev = d._rev
            db.put record, (e, r) ->
                if exist(e)
                    p.reject(e)

                if exist(r)
                    if exist_truth(r.ok)
                        p.resolve(true)
                    else
                        p.reject(r)
                else
                    p.reject("store_user_var generic error")

    return p.promise


get_user_var = (k, $q) ->
    p = $q.defer()
    db = new PouchDB('cb_userinfo')

    if not exist(db)
        p.reject("no db")
    else
        db.get k, (e, d) ->
            if exist(e)
                p.reject(e)
            else
                if exist(d)
                    p.resolve(d.value)
                else
                    p.reject()

    return p.promise


set_user_var_scope = (name, scope_name, scope, $q) ->
    p = $q.defer()

    get_user_var(name, $q).then(
        (v) ->
            if exist(scope_name)
                scope[scope_name] = v
            else
                scope[name] = v
            p.resolve()

        (err) ->
            warning "cryptobox.cf:353", err
            p.reject(err)
    )
    p.promise


set_data_user_config = (scope, $q) ->
    p = $q.defer()
    promises = []
    promises.push(set_user_var_scope("cb_folder", "cb_folder_text", scope, $q))
    promises.push(set_user_var_scope("cb_username", null, scope, $q))
    promises.push(set_user_var_scope("cb_password", null, scope, $q))
    promises.push(set_user_var_scope("cb_name", null, scope, $q))
    promises.push(set_user_var_scope("cb_server", null, scope, $q))
    promises.push(set_user_var_scope("show_debug", null, scope, $q))

    $q.all(promises).then(
        ->
            if not exist(scope.cb_server)
                scope.cb_server = cb_server_url

            if exist(scope.cb_username) && exist(scope.cb_password) && exist(scope.cb_name)
                p.resolve()
            else
                scope.show_settings = true
                p.reject("not all data")

        (err) ->
            scope.cb_name = "test"
            scope.show_settings = true
            p.reject(err)
    )
    return p.promise


outofsync = (scope, items) ->
    if items?
        ioos = _.size(items)

        if ioos > 0
            scope.outofsync = true
            return ioos
    return 0


set_sync_check_on_scope = (scope, sync_results) ->
    scope.outofsync = false
    items_out_of_sync = 0

    human_readable_size = (item) ->
        item.doc.m_size = g_format_file_size(item.doc.m_size)

    human_readable_size2 = (item) ->
        item.size = g_format_file_size(item.size)

    if sync_results.file_downloads?
        items_out_of_sync += outofsync(scope, sync_results.file_downloads)
        scope.file_downloads = sync_results.file_downloads
        _.each(scope.file_downloads, human_readable_size)

    if sync_results.file_uploads?
        items_out_of_sync += outofsync(scope, sync_results.file_uploads)
        scope.file_uploads = sync_results.file_uploads
        _.each(scope.file_uploads, human_readable_size2)

    if sync_results.dir_del_server?
        items_out_of_sync += outofsync(scope, sync_results.dir_del_server)
        scope.dir_del_server = sync_results.dir_del_server

    if sync_results.dir_make_local?
        items_out_of_sync += outofsync(scope, sync_results.dir_make_local)
        scope.dir_make_local = sync_results.dir_make_local

    if sync_results.dir_make_server?
        items_out_of_sync += outofsync(scope, sync_results.dir_make_server)
        scope.dir_make_server = sync_results.dir_make_server

    if sync_results.dir_del_local?
        items_out_of_sync += outofsync(scope, sync_results.dir_del_local)
        scope.dir_del_local = sync_results.dir_del_local

    if sync_results.file_del_local?
        items_out_of_sync += outofsync(scope, sync_results.file_del_local)
        scope.file_del_local = sync_results.file_del_local

    if sync_results.file_del_server?
        items_out_of_sync += outofsync(scope, sync_results.file_del_server)
        scope.file_del_server = sync_results.file_del_server

    scope.items_out_of_sync = items_out_of_sync

    if scope.items_out_of_sync > 0
        scope.progress_message = scope.items_out_of_sync + " items out of sync"


update_sync_state = (scope) ->
    option = 
        dir: scope.cb_folder_text
        username: scope.cb_username
        password: scope.cb_password
        cryptobox: scope.cb_name
        server: scope.cb_server
        check: true

    result_sync_state = (result, sync_result_list) ->
        if scope.disable_check_button
            print "cryptobox.cf:459", "check done"
            scope.disable_check_button = false
            scope.disable_sync_button = false

        if result
            process_sync_result = (sync_results) ->
                if sync_results.instruction?
                    if sync_results.instruction == "lock_buttons_password_wrong"
                        print "cryptobox.cf:467", sync_results.instruction
                        scope.lock_buttons_password_wrong = true
                else
                    scope.request_update_sync_state = false

                    try
                        if sync_results?
                            if sync_results.locked?
                                if sync_results.locked
                                    cryptobox_locked_status_change(true, scope)
                            else
                                cryptobox_locked_status_change(false, scope)
                                set_sync_check_on_scope(scope, sync_results);
                                if sync_results.all_synced
                                    scope.disable_sync_button = true
                                else
                                    scope.disable_sync_button = false

                    catch ex
                        print "cryptobox.cf:486", ex
                        print "cryptobox.cf:487", sync_results

            _.each(sync_result_list, process_sync_result)

        return result

    give_list = true
    run_cba_main("update_sync_state", option, result_sync_state, null, give_list)


cryptobox_locked_status_change = (locked, scope) ->
    scope.cryptobox_locked = locked

    if scope.cryptobox_locked
        g_tray.icon = "images/icon-client-signed-out.png"
        scope.disable_folder_button = true
        scope.disable_encrypt_button = true
        scope.disable_decrypt_button = false
        scope.disable_sync_button = true

        if g_encrypt_g_tray_item?
            g_encrypt_g_tray_item.enabled = false

        if g_decrypt_g_tray_item?
            g_decrypt_g_tray_item.enabled = true
    else
        g_tray.icon = "images/cryptoboxstatus-idle-lep.tiff"
        scope.disable_folder_button = false
        scope.disable_encrypt_button = false
        scope.disable_decrypt_button = true
        scope.disable_sync_button = false

        if g_encrypt_g_tray_item?
            g_encrypt_g_tray_item.enabled = true

        if g_decrypt_g_tray_item?
            g_decrypt_g_tray_item.enabled = false


get_option = (scope) ->
    option = 
        dir: scope.cb_folder_text
        username: scope.cb_username
        password: scope.cb_password
        cryptobox: scope.cb_name
        server: scope.cb_server

    return option


add_g_traymenu_item = (label, icon, method) ->
    g_trayitem = new gui.MenuItem(
        type: "normal"
        label: label
        icon: icon
        click: method
    )
    g_trayactions.append g_trayitem
    return g_trayitem


add_checkbox_g_traymenu_item = (label, icon, method, enabled) ->
    g_trayitem_cb = new gui.MenuItem(
        type: "checkbox"
        label: label
        icon: icon
        click: method
        checked: enabled
    )
    g_trayactions.append g_trayitem_cb
    return g_trayitem_cb


add_g_traymenu_seperator = ->
    g_traymenubaritem = new gui.MenuItem(
        type: "separator"
    )
    g_trayactions.append g_traymenubaritem
    return g_traymenubaritem


add_checkbox_menu_item = (label, icon, method, enabled) ->
    menubaritem_cb = new gui.MenuItem(
        type: "checkbox"
        label: label
        icon: icon
        click: method
        checked: enabled
    )
    g_menuactions.append menubaritem_cb
    return menubaritem_cb


add_menu_seperator = () ->
    menubaritem = new gui.MenuItem(
        type: "separator"
    )
    g_menuactions.append menubaritem


set_menus_and_g_tray_icon = (scope) ->
    add_menu_seperator()
    g_show_hide_tray_item =  add_g_traymenu_item("Hide", "images/fa-search-minus.png", scope.hide_window)
    add_g_traymenu_seperator()
    add_g_traymenu_item("Website", "images/fa-external-link.png", scope.open_website)
    add_g_traymenu_item("Folder", "images/fa-folder-open.png", scope.open_folder )
    add_g_traymenu_seperator()
    g_encrypt_g_tray_item = add_g_traymenu_item("Lock ", "images/lock.png", scope.encrypt_btn)
    g_decrypt_g_tray_item = add_g_traymenu_item("Unlock", "images/unlock.png", scope.decrypt_btn)
    add_g_traymenu_seperator()

    #g_winmain.menu.insert(new gui.MenuItem({label: 'Actions', submenu: g_menuactions}), 1);
    add_g_traymenu_item("Debug", "images/fa-bug.png", scope.debug_btn )
    add_g_traymenu_item("Quit", "images/fa-power-off.png", scope.close_window_menu )


set_motivation = ($scope) ->
    motivation_cb = (result, output) ->
        if result
            $scope.motivation = output?.motivation.replace("\n", "<br/>")
            $scope.progress_message = $scope.motivation + "<br/><br/>"

    run_cba_main("motivation", {"motivation": true}, motivation_cb, null, false)


g_progress_callback = (scope, output) ->
    try
        if output.global_progress?
            scope.progress_bar = output.global_progress

        if output.item_progress?
            scope.progress_bar_item = output.item_progress

        if output.msg?
            scope.progress_message = output.msg

        if !scope.$$phase
            scope.$apply()
    catch err
        print "cryptobox.cf:626", "g_progress_callback", err


reset_bars_timer = null


reset_bars = (scope) ->
    return
    if scope.progress_bar_item >= 100
        if scope.progress_bar > 0
            if scope.progress_bar_item >= 100

                reset_bar_item = ->
                    scope.progress_bar_item = 0
                setTimeout(reset_bar_item, 2000)

    if scope.progress_bar >= 100
        if scope.progress_bar_item == 0
            reset_bar = ->
                if scope.progress_bar_item == 0
                    scope.progress_bar = 0
            setTimeout(reset_bar, 750)


delete_blobs = (scope) ->
    option = get_option(scope)
    option.acommand = "delete_blobs"

    cb_delete_blobs = (result, output) ->
        print "cryptobox.cf:655", "blobs deleted", result, output
    run_cba_main("delete_blobs", option, cb_delete_blobs)


check_for_new_release = (scope) ->
    option = get_option(scope)
    option.acommand = "check_new_release"

    cb_check_new_release = (result, output) ->
        if result
            if output.new_release
                scope.show_new_release_download_dialog = true

    run_cba_main("check_new_release", option, cb_check_new_release)


angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"])
cryptobox_ctrl = ($scope, memory, utils, $q) ->
    $scope.cba_version = 0.1
    $scope.cba_main = null
    $scope.quitting = false
    $scope.motivation = null
    $scope.progress_bar = 0
    $scope.progress_bar_item = 0
    $scope.progress_message = ""
    $scope.show_settings = true
    $scope.show_debug = false
    $scope.got_cb_name = false
    $scope.file_downloads = []
    $scope.file_uploads = []
    $scope.dir_del_server = []
    $scope.dir_make_local = []
    $scope.dir_make_server = []
    $scope.dir_del_local = []
    $scope.file_del_local = []
    $scope.file_del_server = []
    $scope.disable_encrypt_button = true
    $scope.disable_decrypt_button = true
    $scope.disable_check_button = false
    $scope.disable_sync_button = true
    $scope.file_watch_started = false
    $scope.request_update_sync_state = false
    $scope.state_syncing = false
    $scope.tree_sequence = null
    $scope.sync_requested = false
    $scope.error_message = null
    $scope.info_message = null
    $scope.disable_folder_button = false
    $scope.lock_buttons_password_wrong = false
    $scope.show_new_release_download_dialog = false
    $scope.show_new_release_download_dialog_message = "A new release of this app is available, click here to download"
    g_winmain.on('close', on_exit)

    $scope.download_new_release = ->
        option = get_option($scope)
        option.acommand = "download_new_release"
        run_cba_main("download_new_release", option, null, progress_callback)

    $scope.close_window_menu = ->
        g_winmain.close()

    $scope.close_window = ->
        close_callback = (result) ->
            if result
                g_winmain.close()
        bootbox.confirm("Exit application, are you sure?", close_callback)

    $scope.hide_window = ->
        g_show_hide_tray_item.label = "Show"
        g_show_hide_tray_item.icon = "images/fa-search-plus.png"
        g_show_hide_tray_item.click = $scope.show_window
        g_winmain.hide()
        $scope.set_window_size_settings()

    $scope.show_window = ->
        g_show_hide_tray_item.label = "Hide"
        g_show_hide_tray_item.icon = "images/fa-search-minus.png"
        g_show_hide_tray_item.click = $scope.hide_window
        g_winmain.show()
        $scope.set_window_size_settings()

    $scope.debug_btn = ->
        require('nw.gui').Window.get().showDevTools()
        document.location = "debug.html"

    $scope.get_progress_item_show = ->
        return $scope.progress_bar_item != 0

    $scope.get_progress_item = ->
        {width: $scope.progress_bar_item + "%"}

    $scope.get_progress = ->
        {width: $scope.progress_bar + "%"}

    $scope.form_changed = false

    $scope.form_change = ->
        $scope.form_changed = true

    $scope.reset_cache = ->
        option = get_option($scope)
        option.encrypt = true
        option.clear = true
        run_cba_main("reset_cache", option, null, progress_callback)

    $scope.form_save = ->
        store_user_var("cb_folder", $scope.cb_folder_text, $q)
        store_user_var("cb_username", $scope.cb_username, $q)
        store_user_var("cb_name", $scope.cb_name, $q)
        store_user_var("cb_server", $scope.cb_server, $q)
        store_user_var("show_debug", $scope.show_debug, $q)

        get_user_var("cb_password", $q).then(
            (oldpassword) ->
                if oldpassword != $scope.cb_password
                    delete_blobs($scope)
                    $scope.lock_buttons_password_wrong = false
                store_user_var("cb_password", $scope.cb_password, $q)

            (err) ->
                print "cryptobox.cf:775", "error setting password", err
        )
        $scope.form_changed = false
        $scope.request_update_sync_state = true

    $scope.file_input_change = (f) ->
        $scope.cb_folder_text = f[0].path
        $scope.form_save()

    $scope.check_btn = ->
        $scope.disable_check_button = true
        $scope.disable_sync_button = true
        $scope.request_update_sync_state = true

    $scope.sync_btn = ->
        $scope.sync_requested = true

    progress_callback = (output) ->
        g_progress_callback($scope, output)

    check_feedback_progress_callback = (output) ->
        g_progress_callback($scope, output)
        if output.file_uploads?
            set_sync_check_on_scope($scope, output)

    do_sync = ->
        print "cryptobox.cf:801", "start sync"
        $scope.disable_sync_button = true
        option = get_option($scope)
        option.encrypt = true
        option.clear = false
        option.sync = true
        $scope.state_syncing = true
        $scope.disable_encrypt_button = true
        $scope.disable_sync_button = true

        sync_cb = (result, output) ->
            if result
                $scope.state_syncing = false
                $scope.disable_sync_button = false
                $scope.disable_encrypt_button = false
                $scope.request_update_sync_state = true
        run_cba_main("sync_cb", option, sync_cb, check_feedback_progress_callback, false)

    $scope.encrypt_btn = ->
        option = get_option($scope)
        option.encrypt = true
        option.remove = true
        option.sync = false
        $scope.disable_encrypt_button = true
        $scope.disable_sync_button = true

        sync_cb = (result, output) ->
            if result
                print "cryptobox.cf:829", "encrypted"
                $scope.request_update_sync_state = true
        run_cba_main("encrypt", option, sync_cb, progress_callback)

    $scope.decrypt_btn = ->
        option = get_option($scope)
        option.decrypt = true
        $scope.disable_sync_button = true
        $scope.disable_decrypt_button = true

        sync_cb = (result, output) ->
            if result
                print "cryptobox.cf:841", "decrypted"
                $scope.disable_sync_button = true
                $scope.request_update_sync_state = true
        run_cba_main("decrypt", option, sync_cb, progress_callback)

    $scope.open_folder = ->
        option = get_option($scope)
        option.acommand = "open_folder"
        run_cba_main("open_folder", option)

    $scope.open_website = ->
        option = get_option($scope)
        option.acommand = "open_website"
        run_cba_main("open_website", option)

    g_window_width = 300

    $scope.set_window_size_settings = ->
        g_winmain.moveTo((screen.width - 900), 32)
        g_winmain.resizeTo(800, 700)

    $scope.toggle_settings = ->
        g_winmain.show()
        $scope.set_window_size_settings()
        $scope.form_save()

    $scope.toggle_debug = ->
        $scope.show_debug = !$scope.show_debug
        print "cryptobox.cf:869", $scope.show_debug

    $scope.clear_msg_buffer = ->
        g_output = []
        utils.force_digest($scope)

    set_data_user_config($scope, $q).then(
        ->
            update_sync_state($scope)
            $scope.set_window_size_settings()
            check_for_new_release($scope)

        (err) ->
            print "cryptobox.cf:882", err
            throw "set data user config error"
    )
    once_motivation = _.once(set_motivation)
    once_motivation($scope)
    set_menus_and_g_tray_icon($scope)

    digester = ->
        $scope.progress_message = utils.capfirst($scope.progress_message)
        output_msg = ""

        if utils.exist_truth($scope.lock_buttons_password_wrong)
            $scope.disable_encrypt_button = true
            $scope.disable_decrypt_button = true
            $scope.disable_sync_button = true

        make_stream = (msg) ->
            output_msg += msg + "\n"
        _.each(g_output, make_stream)
        $scope.cmd_output = output_msg
        reset_bars($scope)
        $scope.error_message = g_error_message

        if g_error_message?
            try
                $scope.subject_message_mail = String(g_error_message).split("> ---------------------------")[2].split(">")[3].trim()
                $scope.error_message_mail = String(g_error_message).replace(/\n/g, "%0A")
            catch
                $scope.error_message_mail = null

        if $scope.sync_requested
            $scope.sync_requested = false
            do_sync()
        utils.force_digest($scope)
        if g_info_message?
            $scope.info_message = g_info_message
            g_info_message = null

            clear_info = ->
                $scope.info_message = ""
            setTimeout(clear_info, 5000)
    setInterval(digester, 100)

    two_second_interval = ->
        if $scope.request_update_sync_state
            if $scope.progress_bar == 0
                if not $scope.lock_buttons_password_wrong
                    update_sync_state($scope)

    setInterval(two_second_interval, 2000)

    ten_second_interval = ->
        option = get_option($scope)
        option.treeseq = true
        $scope.request_update_sync_state = true

        if $scope.lock_buttons_password_wrong
            update_sync_state($scope)

        tree_sequence_cb = (result, output) ->
            if result
                ts = output
                if ts != $scope.tree_sequence
                    if $scope.tree_sequence?
                        $scope.request_update_sync_state = true

                $scope.tree_sequence = ts

        if $scope.progress_bar == 0
            run_cba_main("treeseq", option, tree_sequence_cb)
    setInterval(ten_second_interval, 10000)

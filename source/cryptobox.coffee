
child_process = require("child_process")
path = require("path")
fs = require("fs")
gui = require('nw.gui')

#gui.Window.get().showDevTools()
g_output = []
g_cba_main = null
g_second_counter = 0
g_error_message = null
g_encrypt_g_tray_item = null
cb_server_url = "http://127.0.0.1:8000/"
g_winmain = gui.Window.get()
g_tray = new gui.Tray(
    icon: "images/icon-client-signed-in-idle.png"
)
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
    if msgs?.indexOf?(".cf") >= 0
        msgs = "> " + msgs

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
    console.log msgs
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


parse_json = (data) ->
    try
        if data?
            if _.size(data) > 0
                return JSON.parse(data)

    catch
        pass

        #print "cryptobox.cf:121", "could not parse json"
        #print "cryptobox.cf:122", data
    return null


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
    print "cryptobox.cf:154", "python cba_main.py", cmd_str.trim()
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


run_cba_main = (name, options, cb_done, cb_intermediate) ->
    if !exist(cb_done)
        throw "run_cba_main needs a cb_done parameter (callback)"

    #params = option_to_array(name, options)
    cmd_to_run = path.join(process.cwd(), "cba_main")
    cba_main = child_process.spawn(cmd_to_run, "")
    g_cba_main = cba_main
    output = ""
    error = ""
    data = ""
    intermediate_cnt = 0

    stdout_data = (data) ->
        output += data
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

                    if strEndsWith(data, "}")
                        pdata = parse_json(data, true)

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
            print "node_test.cf:150", "already running"
            cb_done(false, output)
        else
            output = parse_json(output)

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
            warning "cryptobox.cf:305", err
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
    promises.push(set_user_var_scope("show_settings", null, scope, $q))

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


set_sync_check_on_scope = (scope, sync_results) ->
    human_readable_size = (item) ->
        item.doc.m_size = g_format_file_size(item.doc.m_size)

    human_readable_size2 = (item) ->
        item.size = g_format_file_size(item.size)

    if sync_results.file_downloads?
        scope.file_downloads = sync_results.file_downloads
        _.each(scope.file_downloads, human_readable_size)

    if sync_results.file_uploads?
        scope.file_uploads = sync_results.file_uploads
        _.each(scope.file_uploads, human_readable_size2)

    if sync_results.dir_del_server?
        scope.dir_del_server = sync_results.dir_del_server

    if sync_results.dir_make_local?
        scope.dir_make_local = sync_results.dir_make_local

    if sync_results.dir_make_server?
        scope.dir_make_server = sync_results.dir_make_server

    if sync_results.dir_del_local?
        scope.dir_del_local = sync_results.dir_del_local

    if sync_results.file_del_local?
        scope.file_del_local = sync_results.file_del_local

    if sync_results.file_del_server?
        scope.file_del_server = sync_results.file_del_server


update_sync_state = (scope) ->
    option =
        dir: scope.cb_folder_text
        username: scope.cb_username
        password: scope.cb_password
        cryptobox: scope.cb_name
        server: scope.cb_server
        check: true

    result_sync_state = (result, sync_results) ->
        if result
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
                print "cryptobox.cf:402", ex
                print "cryptobox.cf:403", sync_results
        return result

    run_cba_main("update_sync_state", option, result_sync_state)


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
    else
        g_tray.icon = "images/icon-client-signed-in-idle.png"
        scope.disable_folder_button = false
        scope.disable_encrypt_button = false
        scope.disable_decrypt_button = true
        scope.disable_sync_button = false

        if g_encrypt_g_tray_item?
            g_encrypt_g_tray_item.enabled = true


get_option = ($scope) ->
    option =
        dir: $scope.cb_folder_text
        username: $scope.cb_username
        password: $scope.cb_password
        cryptobox: $scope.cb_name
        server: $scope.cb_server

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


add_menu_item = (label, icon, method) ->
    menubaritem = new gui.MenuItem(
        type: "normal"
        label: label
        icon: icon
        click: method
    )
    g_menuactions.append menubaritem
    return menubaritem


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
    add_g_traymenu_seperator()
    add_menu_item("Encrypt local", "images/lock.png", scope.encrypt_btn)
    g_encrypt_g_tray_item = add_g_traymenu_item("Encrypt local", "images/lock.png", scope.encrypt_btn)
    add_menu_item("Decrypt local", "images/unlock.png", scope.decrypt_btn)
    add_g_traymenu_item("Decrypt local", "images/unlock.png", scope.decrypt_btn)
    g_winmain.menu.insert(new gui.MenuItem({label: 'Actions', submenu: g_menuactions}), 1);
    scope.settings_menubaritem = add_checkbox_menu_item("Settings", "images/cog.png", scope.toggle_settings, scope.show_settings)
    scope.settings_menubar_g_tray = add_checkbox_g_traymenu_item("Settings", "images/cog.png", scope.toggle_settings, scope.show_settings)

    scope.update_menu_checks = ->
        scope.settings_menubaritem.checked = scope.show_settings
        scope.settings_menubar_g_tray.checked = scope.show_settings
    scope.$watch "show_settings", scope.update_menu_checks


set_motivation = ($scope) ->
    motivation_cb = (result, output) ->
        if result
            $scope.motivation = output?.motivation.replace("\n", "<br/>")

    run_cba_main("motivation", {"motivation":true}, motivation_cb)


g_progress_callback = (scope, output) ->
    stored_output = output

    try
        if output.global_progress?
            scope.progress_bar = output.global_progress

        if output.item_progress?
            scope.progress_bar_item = output.item_progress

        if output.msg?
            scope.progress_message = output.msg

        if output.info_message?
            scope.info_message = output.info_message

            clear_info = ->
                scope.info_message = ""
            setTimeout(clear_info, 3000)

        if !scope.$$phase
            scope.$apply()
    catch err
        print "cryptobox.cf:552", "error"
        print "cryptobox.cf:553", stored_output
        print "cryptobox.cf:554", err


reset_bars_timer = null


reset_bars = (scope) ->
    if scope.progress_bar_item >= 100
        if scope.progress_bar > 0
            if scope.progress_bar_item >= 100

                reset_bar_item = ->
                    scope.progress_bar_item = 0
                setTimeout(reset_bar_item, 2000)

    if not reset_bars_timer?
        if scope.progress_bar >= 100 and (scope.progress_bar_item >= 100 || scope.progress_bar_item == 0)
            reset_bars_timer = new Date().getTime()
    else
        now = new Date().getTime()

        if now - reset_bars_timer > 2000
            scope.progress_bar = 0
            scope.progress_bar_item = 0
            scope.progress_message = ""
            reset_bars_timer = null


angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"])
cryptobox_ctrl = ($scope, memory, utils, $q) ->
    $scope.cba_version = 0.1
    $scope.cba_main = null
    $scope.quitting = false
    $scope.motivation = null
    $scope.progress_bar = 0
    $scope.progress_bar_item = 0
    $scope.progress_message = ""
    $scope.show_settings = false
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
    $scope.disable_sync_button = true
    $scope.file_watch_started = false
    $scope.request_update_sync_state = false
    $scope.state_syncing = false
    $scope.tree_sequence = null
    $scope.sync_requested = false
    $scope.error_message = null
    $scope.info_message = null
    $scope.disable_folder_button = false
    g_winmain.on('close', on_exit)

    $scope.debug_btn = ->
        require('nw.gui').Window.get().showDevTools()

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

        clear_cb = (result, output) ->
            print "cryptobox.cf:638", result, output
        run_cba_main("reset_cache", option, clear_cb, progress_callback)

    $scope.form_save = ->
        store_user_var("cb_folder", $scope.cb_folder_text, $q)
        store_user_var("cb_username", $scope.cb_username, $q)
        store_user_var("cb_password", $scope.cb_password, $q)
        store_user_var("cb_name", $scope.cb_name, $q)
        store_user_var("cb_server", $scope.cb_server, $q)
        store_user_var("show_settings", $scope.show_settings, $q)
        store_user_var("show_debug", $scope.show_debug, $q)
        $scope.reset_cache()
        $scope.form_changed = false
        $scope.request_update_sync_state = true

    $scope.file_input_change = (f) ->
        $scope.cb_folder_text = f[0].path
        $scope.form_save()

    $scope.sync_btn = ->
        $scope.sync_requested = true

    progress_callback = (output) ->
        g_progress_callback($scope, output)

    check_feedback_progress_callback = (output) ->

        #if output.file_uploads?
        #    print "cryptobox.cf:666", output.file_uploads
        g_progress_callback($scope, output)
        set_sync_check_on_scope($scope, output)

    do_sync = ->
        print "cryptobox.cf:671", "start sync"
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
                print "cryptobox.cf:683", "sync ok"
                $scope.state_syncing = false
                $scope.disable_sync_button = false
                $scope.disable_encrypt_button = false
                $scope.progress_bar = 100
                $scope.progress_bar_item = 100
                $scope.request_update_sync_state = true
        run_cba_main("sync server", option, sync_cb, check_feedback_progress_callback)

    $scope.encrypt_btn = ->
        option = get_option($scope)
        option.encrypt = true
        option.remove = true
        option.sync = false
        $scope.disable_encrypt_button = true
        $scope.disable_sync_button = true

        sync_cb = (result, output) ->
            if result
                print "cryptobox.cf:702", "encrypted"
                $scope.request_update_sync_state = true
                $scope.progress_bar = 100
                $scope.progress_bar_item = 100
        run_cba_main("encrypt", option, sync_cb, progress_callback)

    $scope.decrypt_btn = ->
        option = get_option($scope)
        option.decrypt = true
        $scope.disable_sync_button = true
        $scope.disable_decrypt_button = true

        sync_cb = (result, output) ->
            if result
                print "cryptobox.cf:716", "decrypted"
                $scope.disable_sync_button = true
                $scope.request_update_sync_state = true
                $scope.progress_bar = 100
                $scope.progress_bar_item = 100
        run_cba_main("decrypt", option, sync_cb, progress_callback)

    $scope.open_folder = ->
        option = get_option($scope)
        option.acommand = "open_folder"

        open_cb = (result, output) ->
            pass
        run_cba_main("open_folder", option, open_cb)

    $scope.open_website = ->
        option = get_option($scope)
        option.acommand = "open_website"

        open_cb = (result, output) ->
            pass
        run_cba_main("open_website", option, open_cb)

    $scope.toggle_settings = ->
        $scope.show_settings = !$scope.show_settings
        $scope.form_save()

    $scope.toggle_debug = ->
        $scope.show_debug = !$scope.show_debug
        print "cryptobox.cf:745", $scope.show_debug

    $scope.clear_msg_buffer = ->
        g_output = []
        utils.force_digest($scope)

    set_data_user_config($scope, $q).then(
        ->
            update_sync_state($scope)

        (err) ->
            print "cryptobox.cf:756", err
            throw "set data user config error"
    )
    once_motivation = _.once(set_motivation)
    once_motivation($scope)
    set_menus_and_g_tray_icon($scope)

    digester = ->
        output_msg = ""

        make_stream = (msg) ->
            output_msg += msg + "\n"
        _.each(g_output, make_stream)
        $scope.cmd_output = output_msg
        reset_bars($scope)
        $scope.error_message = g_error_message

        if g_error_message?
            $scope.subject_message_mail = String(g_error_message).split("> ---------------------------")[2].split(">")[3].trim()
            $scope.error_message_mail = String(g_error_message).replace(/\n/g, "%0A")

        if $scope.sync_requested
            $scope.sync_requested = false
            do_sync()
        utils.force_digest($scope)
    setInterval(digester, 100)

    two_second_interval = ->
        if $scope.request_update_sync_state
            if $scope.progress_bar == 0
                update_sync_state($scope)

    setInterval(two_second_interval, 2000)

    ten_second_interval = ->
        option = get_option($scope)
        option.treeseq = true
        $scope.request_update_sync_state = true

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

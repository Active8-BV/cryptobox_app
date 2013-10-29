
child_process = require("child_process")
path = require("path")
fs = require("fs")
watch = require("watch")
spawn = require("child_process")
gui = require('nw.gui')
g_output = []
g_second_counter = 0
cb_server_url = "http://127.0.0.1:8000/"
g_winmain = gui.Window.get()
g_tray = new gui.Tray(
    icon: "images/icon-client-signed-in-idle.png"
)

#gui.Window.get().showDevTools()
print = (msg, others...) ->
    len_others = _.size(others)

    #noinspection CoffeeScriptSwitchStatementWithNoDefaultBranch
    switch len_others
        when 0 then console?.log msg
        when 1 then console?.log msg + " " + others[0]
        when 2 then console?.log msg + " " + others[0] + " " + others[1]
        when 3 then console?.log msg + " " + others[0] + " " + others[1] + " " + others[2]
        when 4 then console?.log msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3]
        when 5 then console?.log msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3] + " " + others[4]
        else
            console?.log others, msg


warning = (ln, w) ->
    if w?
        if w?.trim?
            w = w.trim()
    else
        return

    if utils.exist(w)
        if w.faultString?
            add_output(w.faultString)
        else if w.message
            add_output(w.message)
        else
            add_output(w)


set_output_buffers = (cba_main_proc) ->
    if exist(cba_main_proc.stdout)
        cba_main_proc.stdout.on "data", (data) ->
            add_output("stdout:" + data)

    if exist(cba_main_proc.stderr)
        cba_main_proc.stderr.on "data", (data) ->
            add_output("stderr:" + data)


update_output = (scope) ->
    msgs = ""

    make_stream = (msg) ->
        msgs += msg + "\n"
    _.each(g_output, make_stream)
    scope.cmd_output = msgs


add_output = (msgs, scope) ->
    add_msg = (msg) ->
        if msg.indexOf?
            if msg.indexOf("Error") == -1
                if msg.indexOf("POST /RPC2") > 0
                    return

        if msg.replace?
            msg = msg.replace("stderr:", "")
            msg.replace("\n", "")
            msg = msg.trim()

        if utils.exist(msg)
            g_output.unshift(msg)

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
    update_output(scope)


warning = (ln, w) ->
    if w?
        if w?.trim?
            w = w.trim()
    else
        return

    if utils.exist(w)
        if w.faultString?
            add_output(w.faultString)
        else if w.message
            add_output(w.message)
        else
            add_output(w)


start_process = =>
    print "cryptobox.cf:115", "start_process"
    cmd_to_run = path.join(process.cwd(), "commands")
    cmd_to_run = path.join(cmd_to_run, "cba_main")
    cmd_folder = path.join(process.cwd(), "cba_commands")
    cba_main = spawn.spawn(cmd_to_run, ["-i " + cmd_folder])
    set_output_buffers(cba_main)


start_watch = ->
    if not file_watch_started
        watch_path = path.join($scope.cb_folder_text, $scope.cb_name)

        if fs.existsSync(watch_path)
            file_watch_started = true
            watch.watchTree watch_path, (f, curr, prev) ->
                if not String(f).contains("memory.pickle")
                    if typeof f is "object" and prev is null and curr is null
                        return

                    add_output("local filechange", f)
                    if prev is null
                        file_watch_started = false
                    else if curr.nlink is 0
                        file_watch_started = false
                    else
                        file_watch_started = false


check_result = (name) =>
    result_path = path.join(cmd_folder, name + ".result")

    if fs.existsSync(result_path)
        data = null

        try
            data = fs.readFileSync(result_path)
        catch ex
            pass

        if data?
            try
                data = JSON.parse(data)
            catch ex
                pass

        if data?
            if data["result"]?
                try
                    fs.unlinkSync(result_path)
                catch ex
                    print "cryptobox.cf:165", ex
                p.resolve(data["result"])
                return

    if result_cnt > 100
        print "cryptobox.cf:170", "too many result checks", name, result_cnt
    else
        setTimeout(check_result, 100, name)


run_command = (name, data) ->
    p = $q.defer()

    if not exist(data)
        data = ""

    cmd_folder = path.join(process.cwd(), "cba_commands")

    if not fs.existsSync(cmd_folder)
        fs.mkdirSync(cmd_folder)

    cmd_path = path.join(cmd_folder, name + ".cmd")
    result_path = path.join(cmd_folder, name + ".result")

    if fs.existsSync(result_path)
        fs.unlinkSync(result_path)

    fout = fs.openSync(cmd_path, "w")
    fs.writeSync(fout, JSON.stringify(data))
    fs.closeSync(fout)
    setTimeout(check_result, 100, name)
    p.promise


get_motivation = (scope) ->
    if not scope.motivation?
        run_command("get_motivation").then(
            (motivation) ->
                scope.motivation = motivation

            (error) ->
                print "cryptobox.cf:206", error
        )
    else
        setTimeout(get_motivation, scope, 200)


on_exit = ->
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

    get_user_var(name).then(
        (v) ->
            if exist(scope_name)
                scope[scope_name] = v
            else
                scope[name] = v
            p.resolve()

        (err) ->
            warning "cryptobox.cf:276", err
            p.reject()
    )
    p.promise


set_data_user_config = (scope) ->
    set_user_var_scope("cb_folder", "cb_folder_text").then(
        ->
            scope.got_folder_text = true
    )

    set_user_var_scope("cb_username")
    set_user_var_scope("cb_password")

    set_user_var_scope("cb_name").then(
        ->
            if not exist(scope.cb_name)
                scope.cb_name = "active8"

            scope.got_cb_name = true
    )

    set_user_var_scope("cb_server").then(
        ->
            if not exist(scope.cb_folder_text)
                scope.cb_folder_text = "https://www.cryptobox.nl/"
                scope.cb_folder = $scope.cb_folder_text

    )

    set_user_var_scope("show_settings")
    set_user_var_scope("show_debug")
    if not utils.exist(scope.cb_username)
        scope.show_settings = true

    if not exist(scope.cb_server)
        scope.cb_server = cb_server_url


get_sync_state = (q, scope) ->
    p = q.defer()
    option = 
        dir: scope.cb_folder_text
        username: scope.cb_username
        password: scope.cb_password
        cryptobox: scope.cb_name
        server: scope.cb_server
        check: "1"

    run_command("run_cb_command", option).then(
        ->
            p.resolve()

        (err) ->
            p.reject(err)
    )
    p.promise


update_sync_state = (smem) ->
    $scope.file_downloads = smem.file_downloads
    $scope.file_uploads = smem.file_uploads
    $scope.dir_del_server = smem.dir_del_server
    $scope.dir_make_local = smem.dir_make_local
    $scope.dir_make_server = smem.dir_make_server
    $scope.dir_del_local = smem.dir_del_local
    $scope.file_del_local = smem.file_del_local


cryptobox_locked_status_change = (locked) =>
    $scope.cryptobox_locked = locked

    if $scope.cryptobox_locked
        g_tray.icon = "images/icon-client-signed-out.png"
        $scope.disable_encrypt_button = true
        $scope.disable_decrypt_button = false
        $scope.disable_sync_button = true
        encrypt_g_tray_item.enabled = false
    else
        g_tray.icon = "images/icon-client-signed-in-idle.png"
        $scope.disable_encrypt_button = false
        $scope.disable_decrypt_button = true
        $scope.disable_sync_button = false
        encrypt_g_tray_item.enabled = true


change_workingstate = (wstate, scope) ->
    if exist_truth(wstate)
        scope.lock_buttons = true
        scope.working = true
    else
        scope.lock_buttons = false
        scope.working = false


get_all_smemory = (scope) ->
    run_command("get_all_smemory").then(
        (value) ->
            cryptobox_locked_status_change(exist_truth(value.cryptobox_locked))
            change_workingstate(value.working)
            if not exist_truth(value.working)
                update_sync_state(value)
            force_digest(scope)
            if exist(value.tree_sequence)
                scope.tree_sequence = value.tree_sequence
            force_digest(scope)

        (error) ->
            add_output("get_all_smemory" + " " + error)
            force_digest(scope)
    )


get_option = ->
    option = 
        dir: $scope.cb_folder_text
        username: $scope.cb_username
        password: $scope.cb_password
        cryptobox: $scope.cb_name
        server: $scope.cb_server

    return option


add_g_traymenu_item = (label, icon, method) =>
    g_trayitem = new gui.MenuItem(
        type: "normal"
        label: label
        icon: icon
        click: method
    )
    g_trayactions.append g_trayitem
    return g_trayitem


add_checkbox_g_traymenu_item = (label, icon, method, enabled) =>
    g_trayitem_cb = new gui.MenuItem(
        type: "checkbox"
        label: label
        icon: icon
        click: method
        checked: enabled
    )
    g_trayactions.append g_trayitem_cb
    return g_trayitem_cb


add_g_traymenu_seperator = () =>
    g_traymenubaritem = new gui.MenuItem(
        type: "separator"
    )
    g_trayactions.append g_traymenubaritem
    return g_traymenubaritem


add_menu_item = (label, icon, method) =>
    menubaritem = new gui.MenuItem(
        type: "normal"
        label: label
        icon: icon
        click: method
    )
    actions.append menubaritem
    return menubaritem


add_checkbox_menu_item = (label, icon, method, enabled) =>
    menubaritem_cb = new gui.MenuItem(
        type: "checkbox"
        label: label
        icon: icon
        click: method
        checked: enabled
    )
    actions.append menubaritem_cb
    return menubaritem_cb


add_menu_seperator = () =>
    menubaritem = new gui.MenuItem(
        type: "separator"
    )
    actions.append menubaritem


set_menus_and_g_tray_icon = (scope) ->
    g_trayactions = new gui.Menu()
    g_tray.menu = g_trayactions
    menubar = new gui.Menu(
        type: 'menubar'
    )
    actions = new gui.Menu()
    add_menu_seperator()
    add_g_traymenu_seperator()
    add_menu_item("Encrypt local", "images/lock.png", $scope.encrypt_btn)
    add_g_traymenu_item("Encrypt local", "images/lock.png", $scope.encrypt_btn)
    add_menu_item("Decrypt local", "images/unlock.png", $scope.decrypt_btn)
    add_g_traymenu_item("Decrypt local", "images/unlock.png", $scope.decrypt_btn)
    g_winmain.menu = menubar
    g_winmain.menu.insert(new gui.MenuItem({label: 'Actions', submenu: actions}), 1);
    scope.settings_menubaritem = add_checkbox_menu_item("Settings", "images/cog.png", scope.toggle_settings, scope.show_settings)
    scope.settings_menubar_g_tray = add_checkbox_g_traymenu_item("Settings", "images/cog.png", scope.toggle_settings, scope.show_settings)

    scope.update_menu_checks = ->
        scope.settings_menubaritem.checked = scope.show_settings
        scope.settings_menubar_g_tray.checked = scope.show_settings
    scope.$watch "show_settings", scope.update_menu_checks


second_interval = (scope) ->
    if scope.quitting
        print "cryptobox.cf:488", "quitting"
        return

    start_watch()
    g_second_counter += 1
    update_output()
    get_all_smemory()
    if g_second_counter % 10 == 0
        ping_client()


start_after_second = ->
    get_motivation()
    get_sync_state()
    setInterval(second_interval, 1000)


progress_checker = (fname, scope, utils) ->
    fprogress = path.join(process.cwd(), fname)

    if fs.existsSync(fprogress)
        data = fs.readFileSync(fprogress)
        data = parseInt(data, 10)

        if utils.exist(data)
            add_output(fname, data)
            scope[fname] = parseInt(data, 10)
            fs.unlinkSync(fprogress)

    if scope[fname] >= 100
        scope[fname] = 100
    utils.force_digest(scope)


check_all_progress = (scope, utils) ->
    progress_checker("progress", scope, utils)
    progress_checker("item_progress", scope, utils)


angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"])
cryptobox_ctrl = ($scope, $q, memory, utils) ->
    $scope.cba_version = 0.1
    $scope.cba_main = null
    $scope.quitting = false
    $scope.motivation = null
    $scope.rpc_server_started = false
    $scope.progress_bar = 0
    $scope.progress_bar_item = 0
    $scope.lock_buttons = true
    $scope.show_settings = false
    $scope.show_debug = false
    $scope.got_folder_text = false
    $scope.got_cb_name = false
    $scope.working = false
    $scope.file_downloads = []
    $scope.file_uploads = []
    $scope.dir_del_server = []
    $scope.dir_make_local = []
    $scope.dir_make_server = []
    $scope.dir_del_local = []
    $scope.file_del_local = []
    $scope.file_del_server = []
    $scope.disable_encrypt_button = false
    $scope.disable_decrypt_button = false
    $scope.disable_sync_button = false
    g_winmain.on('close', on_exit)

    $scope.debug_btn = ->
        require('nw.gui').Window.get().showDevTools()

    $scope.get_progress_item_show = =>
        return $scope.progress_bar_item != 0

    $scope.get_progress_item = =>
        {width:$scope.progress_bar_item + "%"}

    $scope.get_progress = =>
        {width:$scope.progress_bar + "%"}

    $scope.get_lock_buttons = ->
        return $scope.lock_buttons

    $scope.toggle_debug = ->
        $scope.show_debug = !$scope.show_debug
        $scope.form_change()

    $scope.form_change = ->
        p_cb_folder = store_user_var("cb_folder", $scope.cb_folder_text, $q)
        p_cb_username = store_user_var("cb_username", $scope.cb_username, $q)
        p_cb_password = store_user_var("cb_password", $scope.cb_password, $q)
        p_cb_name = store_user_var("cb_name", $scope.cb_name, $q)
        p_cb_server = store_user_var("cb_server", $scope.cb_server, $q)
        p_show_settings = store_user_var("show_settings", $scope.show_settings, $q)
        p_show_debug = store_user_var("show_debug", $scope.show_debug, $q)

        $q.all([p_cb_folder, p_cb_username, p_cb_password, p_cb_name, p_cb_server, p_show_settings, p_show_debug]).then(
            ->
                utils.force_digest($scope)

            (err) ->
                warning "cryptobox.cf:588", err
        )

    $scope.file_input_change = (f) ->
        $scope.cb_folder_text = f[0].path
        $scope.form_change()

    $scope.sync_btn = ->
        option = get_option()
        option.encrypt = true
        option.clear = "0"
        option.sync = "0"
        run_command("run_cb_command", option)

    $scope.encrypt_btn = ->
        option = get_option()
        option.encrypt = true
        option.remove = true
        option.sync = false
        run_command("run_cb_command", option)

    $scope.decrypt_btn = ->
        option = get_option()
        option.decrypt = true
        option.clear = false
        run_command("run_cb_command", option)

    $scope.open_folder = ->
        run_command("do_open_folder", [$scope.cb_folder_text, $scope.cb_name])

    $scope.open_website = ->
        gui.Shell.openExternal($scope.cb_server + $scope.cb_name)

    $scope.toggle_settings = ->
        $scope.show_settings = !$scope.show_settings
        $scope.form_change()

    utils.set_time_out("cryptobox.cf:625", start_after_second, 1000)
    utils.set_interval("cryptobox.cf:626", check_all_progress, 250, "check_all_progress")
    set_data_user_config_once = _.once(set_data_user_config)
    start_process_once = _.once(start_process)
    set_data_user_config_once()
    start_process_once()
    get_motivation()
    set_menus_and_g_tray_icon()

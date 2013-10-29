
child_process = require("child_process")
path = require("path")
fs = require("fs")
watch = require("watch")
gui = require('nw.gui')
sleep = require('sleep')


gui.Window.get().showDevTools()
g_output = []
g_second_counter = 0
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

    if exist(w)
        if w.faultString?
            add_output(w.faultString)
        else if w.message
            add_output(w.message)
        else
            add_output(w)


update_output = (scope) ->
    msgs = ""

    make_stream = (msg) ->
        msgs += msg + "\n"
    _.each(g_output, make_stream)
    if scope?
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

        if exist(msg)
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

    if exist(w)
        if w.faultString?
            add_output(w.faultString)
        else if w.message
            add_output(w.message)
        else
            add_output(w)


option_to_array = (option) ->
    for k in _.keys(option)
        if option[k] == true
            option[k] = "1"

        if option[k] == false
            option[k] = "0"

    cmd_str = ""
    cmd_str += " -a " + option.acommand if option.acommand?
    cmd_str += " -b " + option.cryptobox if option.cryptobox?
    cmd_str += " -c " + option.clear if option.clear?
    cmd_str += " -d " + option.decrypt if option.decrypt?
    cmd_str += " -e " + option.encrypt if option.encrypt?
    cmd_str += " -f " + option.dir if option.dir?
    cmd_str += " -l " + option.logout if option.logout?
    cmd_str += " -m " + option.motivation if option.motivation?
    cmd_str += " -n " + option.numdownloadthreads if option.numdownloadthreads?
    cmd_str += " -o " + option.check if option.check?
    cmd_str += " -p " + option.password if option.password?
    cmd_str += " -r " + option.remove if option.remove?
    cmd_str += " -s " + option.sync if option.sync?
    cmd_str += " -t " + option.treeseq if option.treeseq?
    cmd_str += " -u " + option.username if option.username?
    cmd_str += " -v " + option.version if option.version?
    cmd_str += " -x " + option.server if option.server?
    param_array = []

    push_param_array = (i) ->
        if _.size(i.trim()) > 0
            param_array.push(i)
    _.each(cmd_str.split(" "), push_param_array)
    return param_array


run_cba_main = (options, cb) ->
    params = option_to_array(options)
    print "cryptobox.cf:150", "start_process"
    cmd_to_run = path.join(process.cwd(), "commands")
    cmd_to_run = path.join(cmd_to_run, "cba_main")
    cba_main = child_process.spawn(cmd_to_run, params)
    output = ""
    cba_main.stdout.on "data", (data) ->
        output += data
    cba_main.stderr.on "data", (data) ->
        output += data

    execution_done = (event) ->
        if event > 0
            cb(false, output)
        else
            cb(true, output)
    cba_main.on("exit", execution_done)


on_exit = ->
    gui.App.quit()


store_user_var = (k, v) ->
    db = new PouchDB('cb_userinfo')

    if not exist(db)
        throw "no db"
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
                    throw e

                if exist(r)
                    if exist_truth(r.ok)
                        return true
                    else
                        throw e
                else
                    throw "store_user_var generic error"


get_user_var = (k) ->
    db = new PouchDB('cb_userinfo')

    if not exist(db)
        throw ("no db, get_user_var")
    else
        db.get k, (e, d) ->
            if exist(e)
                throw e
            else
                if exist(d)
                    return d.value
                else
                    throw ("error, get_user_var")


set_user_var_scope = (name, scope_name, scope) ->
    v = get_user_var(name)

    if exist(scope_name)
        scope[scope_name] = v
    else
        scope[name] = v

    return true


set_data_user_config = (scope) ->
    if set_user_var_scope("cb_folder", "cb_folder_text", scope)
        scope.got_folder_text = true
    set_user_var_scope("cb_username", null, scope)
    set_user_var_scope("cb_password", null, scope)
    if set_user_var_scope("cb_name", null, scope)
        if not exist(scope.cb_name)
            scope.cb_name = "active8"
            scope.got_cb_name = true

    if set_user_var_scope("cb_server", null, scope)
        if not exist(scope.cb_folder_text)
            scope.cb_folder_text = "https://www.cryptobox.nl/"
            scope.cb_folder = scope.cb_folder_text
    set_user_var_scope("show_settings", null, scope)
    set_user_var_scope("show_debug", null, scope)
    if not exist(scope.cb_username)
        scope.show_settings = true

    if not exist(scope.cb_server)
        scope.cb_server = cb_server_url


get_sync_state = (scope) ->
    option = 
        dir: scope.cb_folder_text
        username: scope.cb_username
        password: scope.cb_password
        cryptobox: scope.cb_name
        server: scope.cb_server
        check: true
    run_command("run_cb_command", option, scope)


start_watch = (scope) ->
    if not scope.file_watch_started
        if exist(scope.cb_folder_text) and exist(scope.cb_name)
            watch_path = path.join(scope.cb_folder_text, scope.cb_name)

            if fs.existsSync(watch_path)
                scope.file_watch_started = true
                watch.watchTree watch_path, (f, curr, prev) ->
                    if not String(f).contains("memory.pickle")
                        if typeof f is "object" and prev is null and curr is null
                            return

                        if scope.running_command
                            return

                        add_output("local filechange", f)
                        if prev is null
                            get_sync_state(scope)
                        else if curr.nlink is 0
                            get_sync_state(scope)
                        else
                            get_sync_state(scope)


update_sync_state = (smem, scope) ->
    scope.file_downloads = smem.file_downloads
    scope.file_uploads = smem.file_uploads
    scope.dir_del_server = smem.dir_del_server
    scope.dir_make_local = smem.dir_make_local
    scope.dir_make_server = smem.dir_make_server
    scope.dir_del_local = smem.dir_del_local
    scope.file_del_local = smem.file_del_local


cryptobox_locked_status_change = (locked) ->
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
    value = run_command("get_all_smemory", "", scope)
    cryptobox_locked_status_change(exist_truth(value.cryptobox_locked))
    change_workingstate(value.working)
    if not exist_truth(value.working)
        update_sync_state(value, scope)
    force_digest(scope)
    if exist(value.tree_sequence)
        scope.tree_sequence = value.tree_sequence
    force_digest(scope)


get_option = ->
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
    add_g_traymenu_item("Encrypt local", "images/lock.png", scope.encrypt_btn)
    add_menu_item("Decrypt local", "images/unlock.png", scope.decrypt_btn)
    add_g_traymenu_item("Decrypt local", "images/unlock.png", scope.decrypt_btn)
    g_winmain.menu.insert(new gui.MenuItem({label: 'Actions', submenu: g_menuactions}), 1);
    scope.settings_menubaritem = add_checkbox_menu_item("Settings", "images/cog.png", scope.toggle_settings, scope.show_settings)
    scope.settings_menubar_g_tray = add_checkbox_g_traymenu_item("Settings", "images/cog.png", scope.toggle_settings, scope.show_settings)

    scope.update_menu_checks = ->
        scope.settings_menubaritem.checked = scope.show_settings
        scope.settings_menubar_g_tray.checked = scope.show_settings
    scope.$watch "show_settings", scope.update_menu_checks


progress_checker = (fname, scope) ->
    fprogress = path.join(process.cwd(), fname)

    if fs.existsSync(fprogress)
        data = fs.readFileSync(fprogress)
        data = parseInt(data, 10)

        if exist(data)
            add_output(fname, data)
            scope[fname] = parseInt(data, 10)
            fs.unlinkSync(fprogress)

    if scope[fname] >= 100
        scope[fname] = 100


check_all_progress = (scope) ->
    progress_checker("progress", scope)
    progress_checker("item_progress", scope)


second_interval = (scope) ->
    if scope.quitting
        print "cryptobox.cf:443", "quitting"
        return

    g_second_counter += 1
    start_watch(scope)
    check_all_progress(scope)
    update_output(scope)
    get_all_smemory(scope)
    if g_second_counter % 10 == 0
        run_command("last_ping", "", scope)


angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"])
cryptobox_ctrl = ($scope, memory, utils) ->
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
    $scope.file_watch_started = false
    $scope.running_command = false
    g_winmain.on('close', on_exit)

    $scope.debug_btn = ->
        require('nw.gui').Window.get().showDevTools()

    $scope.get_progress_item_show = ->
        return $scope.progress_bar_item != 0

    $scope.get_progress_item = ->
        {width:$scope.progress_bar_item + "%"}

    $scope.get_progress = ->
        {width:$scope.progress_bar + "%"}

    $scope.get_lock_buttons = ->
        return $scope.lock_buttons

    $scope.toggle_debug = ->
        $scope.show_debug = !$scope.show_debug
        $scope.form_change()

    $scope.form_change = ->
        store_user_var("cb_folder", $scope.cb_folder_text)
        store_user_var("cb_username", $scope.cb_username)
        store_user_var("cb_password", $scope.cb_password)
        store_user_var("cb_name", $scope.cb_name)
        store_user_var("cb_server", $scope.cb_server)
        store_user_var("show_settings", $scope.show_settings)
        store_user_var("show_debug", $scope.show_debug)
        utils.force_digest($scope)

    $scope.file_input_change = (f) ->
        $scope.cb_folder_text = f[0].path
        $scope.form_change()

    $scope.sync_btn = ->
        option = get_option()
        option.encrypt = true
        option.clear = false
        option.sync = false
        run_command("run_cb_command", option, $scope)

    $scope.encrypt_btn = ->
        option = get_option()
        option.encrypt = true
        option.remove = true
        option.sync = false
        run_command("run_cb_command", option, $scope)

    $scope.decrypt_btn = ->
        option = get_option()
        option.decrypt = true
        option.clear = false
        run_command("run_cb_command", option, $scope)

    $scope.open_folder = ->
        run_command("do_open_folder", [$scope.cb_folder_text, $scope.cb_name], $scope)

    $scope.open_website = ->
        gui.Shell.openExternal($scope.cb_server + $scope.cb_name)

    $scope.toggle_settings = ->
        $scope.show_settings = !$scope.show_settings
        $scope.form_change()

    set_data_user_config_once = _.once(set_data_user_config)

    #start_process_once = _.once(start_process)
    set_data_user_config_once($scope)

    #start_process_once()
    motivation_options = {"motivation":true}

    motivation_cb = (result, output) ->
        if result?
            $scope.motivation = output.replace("\n", "<br/>")
    run_cba_main(motivation_options, motivation_cb)
    set_menus_and_g_tray_icon($scope)

    dodigest = =>
        utils.force_digest($scope)
    setInterval(dodigest, 500)

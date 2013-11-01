
child_process = require("child_process")
path = require("path")
fs = require("fs")
watch = require("watch")
gui = require('nw.gui')
sleep = require('sleep')

#gui.Window.get().showDevTools()
g_output = []
g_second_counter = 0
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


debug = (obj) ->
    console?.log? obj


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
    if msgs.indexOf(".cf") >= 0
        msgs = "> " + msgs
    console?.log msgs

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
    add_output(name)

    for k in _.keys(option)
        add_output("|   " + k + ": " + option[k])
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
    print "cryptobox.cf:148", "python cba_main.py", cmd_str.trim()
    param_array = []

    push_param_array = (i) ->
        if _.size(i.trim()) > 0
            param_array.push(i)
    _.each(cmd_str.split(" "), push_param_array)
    return param_array


run_cba_main = (name, options, cb, cb_stdout) ->
    if !exist(cb)
        throw "run_cba_main needs a cb parameter (callback)"

    params = option_to_array(name, options)
    cmd_to_run = path.join(process.cwd(), "commands")
    cmd_to_run = path.join(cmd_to_run, "cba_main")
    cba_main = child_process.spawn(cmd_to_run, params)
    output = ""
    cba_main.stdout.on "data", (data) ->

        #print "cryptobox.cf:157", new Date().getTime(), data
        output += data
    cba_main.stderr.on "data", (data) ->
        print "cryptobox.cf:172", data

        #print "cryptobox.cf:160", new Date().getTime(), data
        output += data

    execution_done = (event) ->
        defer_callback = =>

            #print "cryptobox.cf:165", new Date().getTime(), "execution done"
            if output.indexOf("Another instance is already running, quitting.") >= 0
                print "cryptobox.cf:182", "already running"
                cb(false, output)
            else
                if event > 0
                    cb(false, output)
                else
                    cb(true, output)

        setTimeout(defer_callback, 1)
    cba_main.on("exit", execution_done)


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

    get_user_var(name, $q).then(
        (v) ->
            if exist(scope_name)
                scope[scope_name] = v
            else
                scope[name] = v
            p.resolve()

        (err) ->
            warning "cryptobox.cf:258", err
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
    promises.push(set_user_var_scope("show_settings", null, scope, $q))
    promises.push(set_user_var_scope("show_debug", null, scope, $q))

    $q.all(promises).then(
        ->
            if not exist(scope.cb_server)
                scope.cb_server = cb_server_url
            p.resolve()

        (err) ->
            p.reject(err)
    )
    return p.promise


update_sync_state = (scope) ->
    option = 
        dir: scope.cb_folder_text
        username: scope.cb_username
        password: scope.cb_password
        cryptobox: scope.cb_name
        server: scope.cb_server
        check: true

    result_sync_state = (result, output) ->
        if result
            try
                sync_results = JSON.parse(output)

                if sync_results.locked?
                    if sync_results.locked
                        cryptobox_locked_status_change(true, scope)
                else
                    cryptobox_locked_status_change(false, scope)
                    scope.file_downloads = sync_results.file_downloads
                    scope.file_uploads = sync_results.file_uploads
                    scope.dir_del_server = sync_results.dir_del_server
                    scope.dir_make_local = sync_results.dir_make_local
                    scope.dir_make_server = sync_results.dir_make_server
                    scope.dir_del_local = sync_results.dir_del_local
                    scope.file_del_local = sync_results.file_del_local
                    scope.file_del_server = sync_results.file_del_server

                    if sync_results.all_synced
                        scope.disable_sync_button = true
                    else
                        scope.disable_sync_button = false

            catch ex
                print "cryptobox.cf:321", ex

    run_cba_main("update_sync_state", option, result_sync_state)


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

                        add_output("local filechange")
                        if prev is null
                            update_sync_state(scope)
                        else if curr.nlink is 0
                            update_sync_state(scope)
                        else
                            update_sync_state(scope)


cryptobox_locked_status_change = (locked, scope) ->
    scope.cryptobox_locked = locked

    if scope.cryptobox_locked
        g_tray.icon = "images/icon-client-signed-out.png"
        scope.disable_encrypt_button = true
        scope.disable_decrypt_button = false
        scope.disable_sync_button = true

        if g_encrypt_g_tray_item?
            g_encrypt_g_tray_item.enabled = false
    else
        g_tray.icon = "images/icon-client-signed-in-idle.png"
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
        print "cryptobox.cf:483", "quitting"
        return

    g_second_counter += 1
    start_watch(scope)
    check_all_progress(scope)
    update_output(scope)
    get_all_smemory(scope)
    if g_second_counter % 10 == 0
        run_command("last_ping", "", scope)


set_motivation = ($scope) ->
    motivation_cb = (result, output) ->
        if result
            $scope.motivation = output.replace("\n", "<br/>")

    run_cba_main("motivation", {"motivation":true}, motivation_cb)


angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"])
cryptobox_ctrl = ($scope, memory, utils, $q) ->
    $scope.cba_version = 0.1
    $scope.cba_main = null
    $scope.quitting = false
    $scope.motivation = null
    $scope.progress_bar = 0
    $scope.progress_bar_item = 0
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
    $scope.running_command = false
    g_winmain.on('close', on_exit)

    $scope.debug_btn = ->
        require('nw.gui').Window.get().showDevTools()

    $scope.get_progress_item_show = ->
        return $scope.progress_bar_item != 0

    $scope.get_progress_item = ->
        {width: $scope.progress_bar_item + "%"}

    $scope.get_progress = ->
        {width: $scope.progress_bar + "%"}

    $scope.toggle_debug = ->
        $scope.show_debug = !$scope.show_debug
        $scope.form_save()

    $scope.form_changed = false

    $scope.form_change = ->
        $scope.form_changed = true

    $scope.form_save = ->
        store_user_var("cb_folder", $scope.cb_folder_text, $q)
        store_user_var("cb_username", $scope.cb_username, $q)
        store_user_var("cb_password", $scope.cb_password, $q)
        store_user_var("cb_name", $scope.cb_name, $q)
        store_user_var("cb_server", $scope.cb_server, $q)
        store_user_var("show_settings", $scope.show_settings, $q)
        store_user_var("show_debug", $scope.show_debug, $q)
        $scope.form_changed = false

    $scope.file_input_change = (f) ->
        $scope.cb_folder_text = f[0].path
        $scope.form_save()

    $scope.sync_btn = ->
        add_output("start sync")
        $scope.disable_sync_button = true
        option = get_option($scope)
        option.encrypt = true
        option.clear = false
        option.sync = true

        sync_cb = (result, output) ->
            if result
                add_output("sync ok")
                update_sync_state($scope)
        run_cba_main("sync server", option, sync_cb)

    $scope.encrypt_btn = ->
        option = get_option($scope)
        option.encrypt = true
        option.remove = true
        option.sync = false
        $scope.disable_sync_button = true

        sync_cb = (result, output) ->
            if result
                add_output("encrypted")
                print "cryptobox.cf:588", output
        run_cba_main("encrypt", option, sync_cb)

    $scope.decrypt_btn = ->
        option = get_option($scope)
        option.decrypt = true
        $scope.disable_sync_button = true

        sync_cb = (result, output) ->
            if result
                $scope.disable_sync_button = true
                add_output("decrypted")
                print "cryptobox.cf:600", output
        run_cba_main("decrypt", option, sync_cb)

    $scope.open_folder = ->
        run_command("do_open_folder", [$scope.cb_folder_text, $scope.cb_name], $scope)

    $scope.open_website = ->
        gui.Shell.openExternal($scope.cb_server + $scope.cb_name)

    $scope.toggle_settings = ->
        $scope.show_settings = !$scope.show_settings
        $scope.form_save()

    $scope.clear_msg_buffer = ->
        g_output = []
        utils.force_digest($scope)

    set_data_user_config($scope, $q).then(
        ->
            update_sync_state($scope)
            start_watch($scope)

        (err) ->
            print "cryptobox.cf:623", err
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
        utils.force_digest($scope)
    setInterval(digester, 250)


child_process = require("child_process")
path = require("path")

gui = require('nw.gui')
xmlrpc = require('xmlrpc')


gui = require("nw.gui")
watch = require("watch")

# Create a tray icon


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


tray = new gui.Tray(
    icon: "images/icon-client-signed-in-idle.png"
)


angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"])
cryptobox_ctrl = ($scope, $q, memory, utils) ->
    print "cryptobox.cf:37", "cryptobox_ctrl"

    get_rpc_client = ->
        clientOptions = 
            host: "localhost"
            port: 8654
            path: "/RPC2"

        return xmlrpc.createClient(clientOptions)

    set_val = (k, v) ->
        p = $q.defer()
        client = get_rpc_client()
        client.methodCall "set_val", [k, v], (error, value) ->
            if exist(error)
                p.reject(error)
            else
                if utils.exist_truth(value)
                    p.resolve("set_val " + k + ":" + v)
                    utils.force_digest($scope)
                else
                    p.reject("error set_val")
                    utils.force_digest($scope)
            utils.force_digest($scope)
        p.promise

    get_val = (k) ->
        p = $q.defer()
        client = get_rpc_client()
        client.methodCall "get_val", [k], (error, value) ->
            if exist(error)
                p.reject(error)
                utils.force_digest($scope)
            else
                p.resolve(value)
                utils.force_digest($scope)
        p.promise

    $scope.cba_version = 0.1
    memory.set("g_running", true)
    cba_main = null

    $scope.on_exit = =>
        print "cryptobox.cf:80", "cryptobox app on_exit"
        client = get_rpc_client()
        client.methodCall "force_stop",[], (e,v) ->
            force_kill = =>
                if cba_main?
                    if cba_main.pid?
                        add_output("force kill!!!")
                        process.kill(cba_main.pid);
                        gui.App.quit()

            utils.set_time_out("cryptobox.cf:90", force_kill, 100)

    set_output_buffers = (cba_main_proc) ->
        if exist(cba_main_proc.stdout)
            cba_main_proc.stdout.on "data", (data) ->
                add_output("stdout:" + data)

        if exist(cba_main_proc.stderr)
            cba_main_proc.stderr.on "data", (data) ->
                add_output("stderr:" + data)

    winmain = gui.Window.get()
    winmain.on('close', $scope.on_exit);
    spawn = require("child_process").spawn
    cmd_to_run = path.join(process.cwd(), "commands")
    cmd_to_run = path.join(cmd_to_run, "cba_main")
    output = []

    $scope.clear_msg_buffer = ->
        output = []
        utils.force_digest($scope)

    $scope.debug_btn = ->
        require('nw.gui').Window.get().showDevTools()

    update_output = ->
        msgs = ""

        make_stream = (msg) ->
             msgs += msg + "\n"
        _.each(output, make_stream)
        $scope.cmd_output = msgs
        utils.force_digest($scope)

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

            if utils.exist(msg)
                output.unshift(utils.format_time(utils.get_local_time()) + ": " + msg)

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
                output.push(utils.format_time(utils.get_local_time()) + ": " + msgs)
        update_output()

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

    $scope.motivation = null

    get_motivation = ->
        if not utils.exist($scope.motivation)
            client = get_rpc_client()
            client.methodCall "get_motivation", [], (error, value) ->
                if utils.exist(value)
                    $scope.motivation = value

                if not utils.exist($scope.motivation)
                    utils.set_time_out("cryptobox.cf:179", get_motivation, 100)

    utils.set_time_out("cryptobox.cf:181", get_motivation, 500)

    ping_client = ->
        utils.force_digest($scope)
        client = get_rpc_client()
        client.methodCall "last_ping", [], (error, value) ->
            if utils.exist(error)
                cba_main = spawn(cmd_to_run, [""])
                set_output_buffers(cba_main)
            else
                $scope.rpc_server_started = true

    $scope.rpc_server_started = false

    start_process = =>
        print "cryptobox.cf:196", "start_process"
        client = get_rpc_client()
        client.methodCall "force_stop",[], (e,v) ->
            if utils.exist(v)
                print "cryptobox.cf:200", "killed existing deamon"
            else
                print "cryptobox.cf:202", "starting deamon"

            cba_main = spawn(cmd_to_run, [""])
            set_output_buffers(cba_main)

    start_process_once = _.once(start_process)
    print "cryptobox.cf:208", cmd_to_run
    start_process_once()
    progress_bar = 0
    progress_bar_item = 0

    $scope.get_progress_item_show = =>
        return progress_bar_item != 0

    $scope.get_progress_item = =>
        width:
            progress_bar_item + "%"

    $scope.get_progress = =>
        width:
            progress_bar + "%"

    reset_progress = ->
        client = get_rpc_client()
        client.methodCall "reset_progress",[], (e,v) ->
            if utils.exist(e)
                warning "cryptobox.cf:228", e

    reset_item_progress = ->
        client = get_rpc_client()
        client.methodCall "reset_item_progress",[], (e,v) ->
            if utils.exist(e)
                warning "cryptobox.cf:234", e

    $scope.lock_buttons = false

    $scope.get_lock_buttons = ->
        return $scope.lock_buttons

    get_working_state = ->
        client = get_rpc_client()
        client.methodCall "get_smemory",["working"], (e,v) ->
            if utils.exist(e)
                warning "cryptobox.cf:245", e
            else
                $scope.lock_buttons = v

    last_progress_bar = 0
    last_progress_bar_item = 0

    get_progress = =>
        if not $scope.rpc_server_started
            return

        client = get_rpc_client()
        client.methodCall "get_progress",[], (e,v) ->
            print "cryptobox.cf:258", v
            if utils.exist(e)
                warning "cryptobox.cf:260", e
            else
                progress = parseInt(v[0], 10)
                progress_item = parseInt(v[1], 10)

            last_progress_bar = progress_bar
            last_progress_bar_item = progress_bar_item

            if progress == 0
                if last_progress_bar > 10
                    progress_bar = 100

            if progress_item == 0
                if last_progress_bar_item > 10
                    progress_bar_item = 100

            if progress > parseInt(progress_bar, 10)
                progress_bar = progress

            if progress_item > parseInt(progress_bar_item, 10)
                progress_bar_item = progress_item

            if progress_bar >= 100

                reset_progress_bar = ->
                    progress_bar = 0
                    reset_progress()
                utils.set_time_out("cryptobox.cf:287", reset_progress_bar, 500)

            if progress_bar_item >= 100

                reset_progress_bar_item = ->
                    progress_bar_item = 0
                    reset_item_progress()
                utils.set_time_out("cryptobox.cf:294", reset_progress_bar_item, 500)
        utils.force_digest($scope)

    store_user_var = (k, v) ->
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
                        utils.force_digest($scope)

                    if exist(r)
                        if exist_truth(r.ok)
                            p.resolve(true)
                            utils.force_digest($scope)
                        else
                            p.reject(r)
                            utils.force_digest($scope)
                    else
                        p.reject("store_user_var generic error")
                        utils.force_digest($scope)

        return p.promise

    get_user_var = (k) ->
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
                        utils.force_digest($scope)
                    else
                        p.reject()

                        #utils.force_digest($scope)

        return p.promise

    set_user_var_scope = (name, scope_name) ->
        p = $q.defer()

        get_user_var(name).then(
            (v) ->
                if exist(scope_name)
                    $scope[scope_name] = v
                else
                    $scope[name] = v
                p.resolve()

            (err) ->
                warning "cryptobox.cf:362", err
                p.reject()
        )
        p.promise

    $scope.show_settings = false
    $scope.show_debug = false

    $scope.toggle_debug = ->
        $scope.show_debug = !$scope.show_debug
        $scope.form_change()

    $scope.got_folder_text = false
    $scope.got_cb_name = false

    try_get_sync_state = =>
        get_sync_state().then(
            (r) ->
                print "cryptobox.cf:380", "sync state retrieved"

            (e) ->
                warning "cryptobox.cf:383", e
        )
    utils.set_time_out("cryptobox.cf:385", try_get_sync_state, 1000)

    start_watch = ->
        if $scope.got_folder_text and $scope.got_cb_name
            watch.watchTree path.join($scope.cb_folder_text, $scope.cb_name), (f, curr, prev) ->
                if not String(f).contains("memory.pickle")
                    if typeof f is "object" and prev is null and curr is null
                        pass
                    else if prev is null
                        try_get_sync_state()
                    else if curr.nlink is 0
                        try_get_sync_state()
                    else
                        try_get_sync_state()

    set_data_user_config = ->
        set_user_var_scope("cb_folder", "cb_folder_text").then(
            ->
                $scope.got_folder_text = true
                start_watch()
        )

        set_user_var_scope("cb_username")
        set_user_var_scope("cb_password")

        set_user_var_scope("cb_name").then(
            ->
                $scope.got_cb_name = true
                start_watch()
        )

        set_user_var_scope("cb_server")
        set_user_var_scope("show_settings")
        set_user_var_scope("show_debug")
        if not utils.exist($scope.cb_username)
            $scope.show_settings = true

        if not utils.exist($scope.cb_server)
            $scope.cb_server = "http://127.0.0.1:8000/"

    set_data_user_config_once = _.once(set_data_user_config)
    set_data_user_config_once()

    $scope.$on "$includeContentLoaded", (event) ->
        console?.log event

    $scope.form_change = ->
        p_cb_folder = store_user_var("cb_folder", $scope.cb_folder_text)
        p_cb_username = store_user_var("cb_username", $scope.cb_username)
        p_cb_password = store_user_var("cb_password", $scope.cb_password)
        p_cb_name = store_user_var("cb_name", $scope.cb_name)
        p_cb_server = store_user_var("cb_server", $scope.cb_server)
        p_show_settings = store_user_var("show_settings", $scope.show_settings)
        p_show_debug = store_user_var("show_debug", $scope.show_debug)

        $q.all([p_cb_folder, p_cb_username, p_cb_password, p_cb_name, p_cb_server, p_show_settings, p_show_debug]).then(
            ->
                utils.force_digest($scope)

            (err) ->
                warning "cryptobox.cf:445", err
        )

    $scope.file_input_change = (f) ->
        $scope.cb_folder_text = f[0].path
        $scope.form_change()

    run_command = (command_name, command_arguments) ->
        client = get_rpc_client()
        p = $q.defer()
        client.methodCall command_name, command_arguments, (error, value) ->
            if exist(error)
                ca_str = ""

                bsca = (i) ->
                    if _.isObject(i)
                        _.each(_.keys(i), (k) ->
                            ca_str = ca_str + k + ":" + i[k] + "|"
                        )
                    else
                        ca_str = ca_str + i
                _.each(command_arguments, bsca)
                add_output(command_name + " " + ca_str + " " + error)
                p.reject(error)
                utils.force_digest($scope)
            else
                p.resolve(value)
                utils.force_digest($scope)
        p.promise

    $scope.file_downloads = []
    $scope.file_uploads = []
    $scope.dir_del_server = []
    $scope.dir_make_local = []
    $scope.dir_make_server = []
    $scope.dir_del_local = []
    $scope.file_del_local = []
    $scope.file_del_server = []

    cryptobox_locked_status_change = =>
        run_command("get_cryptobox_lock_status", []).then(
            (r) =>
                $scope.cryptobox_locked = r

                if $scope.cryptobox_locked
                    tray.icon = "images/icon-client-signed-out.png"
                    $scope.disable_encrypt_button = true
                    $scope.disable_decrypt_button = false
                    $scope.disable_sync_button = true
                    encrypt_tray_item.enabled = false
                else
                    tray.icon = "images/icon-client-signed-in-idle.png"
                    $scope.disable_encrypt_button = false
                    $scope.disable_decrypt_button = true
                    $scope.disable_sync_button = false
                    encrypt_tray_item.enabled = true

            (e) ->
                warning "cryptobox.cf:503", e
        )

    get_sync_state = ->
        p = $q.defer()
        option = 
            dir: $scope.cb_folder_text
            username: $scope.cb_username
            password: $scope.cb_password
            cryptobox: $scope.cb_name
            server: $scope.cb_server
            check: "1"

        run_command("cryptobox_command", [option]).then(
            (res) ->
                p.resolve()

            (err) ->
                p.reject(err)
        )
        p.promise

    update_sync_state = ->
        run_command("get_smemory", ["file_downloads"]).then(
            (r) ->
                $scope.file_downloads = r

            (e) ->
                warning "cryptobox.cf:531", e
        )

        run_command("get_smemory", ["file_uploads"]).then(
            (r) ->
                $scope.file_uploads = r

            (e) ->
                warning "cryptobox.cf:539", e
        )

        run_command("get_smemory", ["dir_del_server"]).then(
            (r) ->
                $scope.dir_del_server = r

            (e) ->
                warning "cryptobox.cf:547", e
        )

        run_command("get_smemory", ["dir_make_local"]).then(
            (r) ->
                $scope.dir_make_local = r

            (e) ->
                warning "cryptobox.cf:555", e
        )

        run_command("get_smemory", ["dir_make_server"]).then(
            (r) ->
                $scope.dir_make_server = r

            (e) ->
                warning "cryptobox.cf:563", e
        )

        run_command("get_smemory", ["dir_del_local"]).then(
            (r) ->
                $scope.dir_del_local = r

            (e) ->
                warning "cryptobox.cf:571", e
        )

        run_command("get_smemory", ["file_del_local"]).then(
            (r) ->
                $scope.file_del_local = r

            (e) ->
                warning "cryptobox.cf:579", e
        )

        run_command("get_smemory", ["file_del_server"]).then(
            (r) ->
                $scope.file_del_server = r

            (e) ->
                warning "cryptobox.cf:587", e
        )

    get_option = ->
        option = 
            dir: $scope.cb_folder_text
            username: $scope.cb_username
            password: $scope.cb_password
            cryptobox: $scope.cb_name
            server: $scope.cb_server

        return option

    $scope.sync_btn = ->
        option = get_option()
        option.encrypt = true
        option.clear = "0"
        option.sync = "0"

        run_command("cryptobox_command", [option]).then(
            (res) ->
                pass

            (err) ->
                warning "cryptobox.cf:611", err
        )

    $scope.encrypt_btn = ->
        option = get_option()
        option.encrypt = true
        option.remove = true
        option.sync = false

        run_command("cryptobox_command", [option]).then(
            (res) ->
                add_output(res)

            (err) ->
                warning "cryptobox.cf:625", err
        )

    $scope.decrypt_btn = ->
        option = get_option()
        option.decrypt = true
        option.clear = false

        run_command("cryptobox_command", [option]).then(
            (res) ->
                add_output(res)
                add_output("done decrypting")

            (err) ->
                warning "cryptobox.cf:639", err
        )

    $scope.tree_sequence = null

    get_tree_sequence = ->
        option = get_option()
        option.treeseq = true

        run_command("cryptobox_command", [option]).then(
            (res) ->
                add_output(res)
                $scope.tree_sequence = res

            (err) ->
                warning "cryptobox.cf:654", err
        )

    $scope.open_folder = ->
        run_command("do_open_folder", [$scope.cb_folder_text, $scope.cb_name])

    $scope.open_website = ->
        gui.Shell.openExternal($scope.cb_server+$scope.cb_name)

    trayactions = new gui.Menu()
    tray.menu = trayactions

    add_traymenu_item = (label, icon, method) =>
        trayitem = new gui.MenuItem(
            type: "normal"
            label: label
            icon: icon
            click: method
        )
        trayactions.append trayitem
        return trayitem

    add_checkbox_traymenu_item = (label, icon, method, enabled) =>
        trayitem_cb = new gui.MenuItem(
            type: "checkbox"
            label: label
            icon: icon
            click: method
            checked: enabled
        )
        trayactions.append trayitem_cb
        return trayitem_cb

    add_traymenu_seperator = () =>
        traymenubaritem = new gui.MenuItem(
            type: "separator"
        )
        trayactions.append traymenubaritem
        return traymenubaritem

    menubar = new gui.Menu(
        type: 'menubar'
    )
    actions = new gui.Menu()

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

    $scope.toggle_settings = ->
        $scope.show_settings = !$scope.show_settings
        $scope.form_change()

    settings_menubaritem = add_checkbox_menu_item("Settings", "images/cog.png", $scope.toggle_settings, $scope.show_settings)
    settings_menubar_tray = add_checkbox_traymenu_item("Settings", "images/cog.png", $scope.toggle_settings, $scope.show_settings)

    update_menu_checks = =>
        settings_menubaritem.checked = $scope.show_settings
        settings_menubar_tray.checked = $scope.show_settings
    $scope.$watch "show_settings", update_menu_checks
    add_menu_seperator()
    add_traymenu_seperator()
    add_menu_item("Encrypt local", "images/lock.png", $scope.encrypt_btn)
    encrypt_tray_item = add_traymenu_item("Encrypt local", "images/lock.png", $scope.encrypt_btn)
    add_menu_item("Decrypt local", "images/unlock.png", $scope.decrypt_btn)
    add_traymenu_item("Decrypt local", "images/unlock.png", $scope.decrypt_btn)
    winmain.menu = menubar
    winmain.menu.insert(new gui.MenuItem({ label: 'Actions', submenu: actions}), 1);
    $scope.disable_encrypt_button = false
    $scope.disable_decrypt_button = false
    $scope.disable_sync_button = false
    second_counter = 0

    second_interval = =>
        if not $scope.lock_buttons
            update_sync_state()
        get_progress()
        get_working_state()
        update_output()
        cryptobox_locked_status_change()
        second_counter += 1

        if second_counter % 10 == 0
            ping_client()
            get_tree_sequence()

    start_second_interval = =>
        get_tree_sequence()
        utils.set_interval("cryptobox.cf:765", second_interval, 1000, "second_interval")
    utils.set_time_out("cryptobox.cf:766", start_second_interval, 1000)

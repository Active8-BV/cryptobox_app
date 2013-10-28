
child_process = require("child_process")
path = require("path")
fs = require("fs")


gui = require('nw.gui')
watch = require("watch")

# Create a tray icon


# require('nw.gui').Window.get().showDevTools()


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
    print "cryptobox.cf:38", "cryptobox_ctrl"
    $scope.cba_version = 0.1
    memory.set("g_running", true)
    cba_main = null
    $scope.succesfull_kill = true
    $scope.quitting = false

    $scope.on_exit = =>
        $scope.quitting = true
        run_command("do_exit")
        gui.App.quit()

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
            run_command("get_motivation").then(
                (motivation) ->
                    $scope.motivation = motivation

                (error) ->
                    print "cryptobox.cf:136", error
            )

    #print "cryptobox.cf:135", "get_motivation not implemented"

    ping_client = ->
        run_command("ping_client", "")
        utils.force_digest($scope)
        print "cryptobox.cf:144", "ping_client"

    $scope.rpc_server_started = false

    start_process = =>
        print "cryptobox.cf:149", "start_process"
        cmd_folder = path.join(process.cwd(), "cba_commands")
        cba_main = spawn(cmd_to_run, ["-i " + cmd_folder])
        set_output_buffers(cba_main)

    start_process_once = _.once(start_process)
    print "cryptobox.cf:155", cmd_to_run
    start_process_once()
    $scope.progress_bar = 0
    $scope.progress_bar_item = 0

    $scope.get_progress_item_show = =>
        return $scope.progress_bar_item != 0

    $scope.get_progress_item = =>
        width:
            $scope.progress_bar_item + "%"

    $scope.get_progress = =>
        width:
            $scope.progress_bar + "%"

    $scope.lock_buttons = true

    $scope.get_lock_buttons = ->
        return $scope.lock_buttons

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
                warning "cryptobox.cf:240", err
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
        add_output("try_get_sync_state")

        get_sync_state().then(
            (r) ->
                pass

            (e) ->
                add_output("sync state error", e)
        )

    $scope.file_watch_started = false

    start_watch = ->
        if not $scope.file_watch_started
            if $scope.got_folder_text and $scope.got_cb_name
                watch_path = path.join($scope.cb_folder_text, $scope.cb_name)

                if fs.existsSync(watch_path)
                    $scope.file_watch_started = true
                    watch.watchTree watch_path, (f, curr, prev) ->
                        if not String(f).contains("memory.pickle")
                            if typeof f is "object" and prev is null and curr is null
                                return

                            add_output("local filechange", f)
                            if prev is null
                                try_get_sync_state()
                            else if curr.nlink is 0
                                try_get_sync_state()
                            else
                                try_get_sync_state()

    set_data_user_config = ->
        set_user_var_scope("cb_folder", "cb_folder_text").then(
            ->
                $scope.got_folder_text = true
        )

        set_user_var_scope("cb_username")
        set_user_var_scope("cb_password")

        set_user_var_scope("cb_name").then(
            ->
                if not utils.exist($scope.cb_name)
                    $scope.cb_name = "active8"

                $scope.got_cb_name = true
        )

        set_user_var_scope("cb_server").then(
            ->
                if not utils.exist($scope.cb_folder_text)
                    $scope.cb_folder_text = "https://www.cryptobox.nl/"
                    $scope.cb_folder = $scope.cb_folder_text

        )

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
                warning "cryptobox.cf:341", err
        )

    $scope.file_input_change = (f) ->
        $scope.cb_folder_text = f[0].path
        $scope.form_change()

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
        result_cnt = 0

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
                            print "cryptobox.cf:392", ex
                        p.resolve(data["result"])
                        return

            if result_cnt > 100
                print "cryptobox.cf:397", "too many result checks", name, result_cnt
            else:
                setTimeout(check_result, 100, name)
        setTimeout(check_result, 100, name)
        p.promise

    $scope.file_downloads = []
    $scope.file_uploads = []
    $scope.dir_del_server = []
    $scope.dir_make_local = []
    $scope.dir_make_server = []
    $scope.dir_del_local = []
    $scope.file_del_local = []
    $scope.file_del_server = []

    get_sync_state = ->
        p = $q.defer()
        option = 
            dir: $scope.cb_folder_text
            username: $scope.cb_username
            password: $scope.cb_password
            cryptobox: $scope.cb_name
            server: $scope.cb_server
            check: "1"

        run_command("run_cb_command", option).then(
            (res) ->
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

    $scope.working = false

    change_workingstate = (wstate) ->
        if utils.exist_truth(wstate)
            $scope.lock_buttons = true
            $scope.working = true
        else
            if $scope.lock_buttons
                try_get_sync_state()

            $scope.lock_buttons = false
            $scope.working = false

    get_all_smemory = ->
        run_command("get_all_smemory").then(
            (value) ->
                cryptobox_locked_status_change(utils.exist_truth(value.cryptobox_locked))
                change_workingstate(value.working)
                if not utils.exist_truth(value.working)
                    update_sync_state(value)
                utils.force_digest($scope)
                if utils.exist(value.tree_sequence)
                    $scope.tree_sequence = value.tree_sequence
                utils.force_digest($scope)

            (error) ->
                add_output("get_all_smemory" + " " + error)
                utils.force_digest($scope)
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

        run_command("run_cb_command", option).then(
            (res) ->
                pass

            (err) ->
                warning "cryptobox.cf:507", err
        )

    $scope.encrypt_btn = ->
        option = get_option()
        option.encrypt = true
        option.remove = true
        option.sync = false

        run_command("run_cb_command", option).then(
            (res) ->
                add_output(res)

            (err) ->
                warning "cryptobox.cf:521", err
        )

    $scope.decrypt_btn = ->
        option = get_option()
        option.decrypt = true
        option.clear = false

        run_command("run_cb_command", option).then(
            (res) ->
                add_output(res)
                add_output("done decrypting")

            (err) ->
                warning "cryptobox.cf:535", err
        )

    $scope.open_folder = ->
        run_command("do_open_folder", [$scope.cb_folder_text, $scope.cb_name])

    $scope.open_website = ->
        gui.Shell.openExternal($scope.cb_server + $scope.cb_name)

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
    winmain.menu.insert(new gui.MenuItem({label: 'Actions', submenu: actions}), 1);
    $scope.disable_encrypt_button = false
    $scope.disable_decrypt_button = false
    $scope.disable_sync_button = false
    second_counter = 0

    second_interval = =>
        if $scope.quitting
            print "cryptobox.cf:633", "quitting"
            return

        start_watch()
        second_counter += 1
        update_output()
        get_all_smemory()
        if second_counter % 10 == 0
            ping_client()

    start_after_second = =>
        get_motivation()

        try_get_sync_state()
        utils.set_interval("cryptobox.cf:647", second_interval, 1000, "second_interval")
    get_motivation()

    utils.set_time_out("cryptobox.cf:650", start_after_second, 1000)

    progress_checker = ->
        fprogress = path.join(process.cwd(), "progress")
        fitem_progress = path.join(process.cwd(), "item_progress")

        if fs.existsSync(fprogress)
            print "cryptobox.cf:657", "progress file"
            data = fs.readFileSync(fprogress)
            data = parseInt(data, 10)

            if utils.exist(data)
                add_output("progress", data)
                $scope.progress_bar = parseInt(data, 10)
                fs.unlinkSync(fprogress)

        if fs.existsSync(fitem_progress)
            print "cryptobox.cf:667", "item progress"
            data = fs.readFileSync(fitem_progress)

            if utils.exist(data)
                add_output("item_progress", data)
                $scope.progress_bar_item = parseInt(data, 10)
                fs.unlinkSync(fitem_progress)

        if $scope.progress_bar >= 100
            $scope.progress_bar = 0

        if $scope.progress_bar_item >= 100
            $scope.progress_bar_item = 0
        utils.force_digest($scope)
    utils.set_interval("cryptobox.cf:681", progress_checker, 100, "progress_checker")

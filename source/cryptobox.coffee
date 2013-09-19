child_process = require("child_process")
path = require("path")
gui = require('nw.gui')
xmlrpc = require('xmlrpc')


winmain = gui.Window.get()


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


angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"])
cryptobox_ctrl = ($scope, $q, memory, utils) ->
    print "cryptobox.cf:28", "cryptobox_ctrl"

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
            else:
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
        print "cryptobox.cf:72", "cryptobox app on_exit"
        client = get_rpc_client()
        client.methodCall "force_stop",[], (e,v) ->
            print "cryptobox.cf:75", "force_stop", e, v

            force_kill = =>
                if cba_main?
                    if cba_main.pid?
                        print "cryptobox.cf:80", "force kill!!!"
                        process.kill(cba_main.pid);

                gui.App.quit()

            _.defer(force_kill)

    set_output_buffers = (cba_main_proc) ->
        if exist(cba_main_proc.stdout)
            cba_main_proc.stdout.on "data", (data) ->
                add_output("stdout:" + data)

        if exist(cba_main_proc.stderr)
            cba_main_proc.stderr.on "data", (data) ->
                add_output("stderr:" + data)

    winmain.on('close', $scope.on_exit);
    spawn = require("child_process").spawn
    cmd_to_run = path.join(process.cwd(), "commands")
    cmd_to_run = path.join(cmd_to_run, "cba_main")
    output = []

    clear_msg_buffer = ->
        output = []
        utils.force_digest($scope)

    $scope.debug_btn = ->
        clear_msg_buffer()
        require('nw.gui').Window.get().showDevTools()

    update_output = ->
        msgs = ""

        make_stream = (msg) ->
             msgs += msg + "\n"

        _.each(output, make_stream)
        $scope.cmd_output = msgs
        utils.force_digest($scope)

    utils.set_interval("cryptobox.cf:120", update_output, 100, "update_output")

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

    ping_client = ->
        utils.force_digest($scope)
        client = get_rpc_client()
        client.methodCall "last_ping", [], (error, value) ->
            if utils.exist(error)
                cba_main = spawn(cmd_to_run, [""])
                set_output_buffers(cba_main)

    start_interval = ->
        utils.set_interval("cryptobox.cf:161", ping_client, 5000, "ping_client")

    utils.set_time_out("cryptobox.cf:163", start_interval, 1000)

    start_process = =>
        print "cryptobox.cf:166", "start_process"
        client = get_rpc_client()
        client.methodCall "force_stop",[], (e,v) ->
            print "cryptobox.cf:169", "force_stop", e, v
            if utils.exist(v)
                print "cryptobox.cf:171", "killed existing deamon"
            else
                print "cryptobox.cf:173", "starting deamon"
            cba_main = spawn(cmd_to_run, [""])
            set_output_buffers(cba_main)

    start_process_once = _.once(start_process)
    print "cryptobox.cf:178", cmd_to_run
    start_process_once()
    progress_bar = 0

    $scope.get_progress = =>
        width:
            progress_bar + "%"

    reset_progress = ->
        client = get_rpc_client()
        client.methodCall "reset_progress",[], (e,v) ->
            if utils.exist(e)
                print "cryptobox.cf:190", e

    lock_buttons = false

    $scope.lock_buttons = ->
        if parseInt(progress_bar, 10) == 0
            lock_buttons = false

        if lock_buttons
            return true
        else
            if parseInt(progress_bar, 10) == 0
                return false
            else
                return true

    get_progress = =>
        client = get_rpc_client()
        client.methodCall "get_progress",[], (e,v) ->
            if utils.exist(e)
                print "cryptobox.cf:210", e, v
            else
                progress = parseInt(v, 10)

            progress_bar = progress

            if progress_bar >= 100

                _.defer(reset_progress)

        utils.force_digest($scope)

    utils.set_interval("cryptobox.cf:222", get_progress, 1000, "get_progress")

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
                        print "cryptobox.cf:268", k, d.value
                        p.resolve(d.value)
                        utils.force_digest($scope)
                    else
                        p.reject()

                        #utils.force_digest($scope)

        return p.promise

    set_user_var_scope = (name, scope_name) ->
        get_user_var(name).then(
            (v) ->
                if exist(scope_name)
                    $scope[scope_name] = v
                else
                    $scope[name] = v

            (err) ->
                print "cryptobox.cf:287", err
        )

    set_data_user_config = ->
        set_user_var_scope("cb_folder", "cb_folder_text")
        set_user_var_scope("cb_username")
        set_user_var_scope("cb_password")
        set_user_var_scope("cb_name")
        set_user_var_scope("cb_server")
        set_user_var_scope("show_settings")

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

        $q.all([p_cb_folder, p_cb_username, p_cb_password, p_cb_name, p_cb_server, p_show_settings]).then(
            ->

                #print "cryptobox.cf:189", x
                utils.force_digest($scope)

            (err) ->
                print "cryptobox.cf:325", err
        )

    $scope.file_input_change = (f) ->
        $scope.cb_folder_text = f[0].path
        $scope.form_change()

    run_command = (command_name, command_arguments) ->
        client = get_rpc_client()
        p = $q.defer()
        print "cryptobox.cf:335", "run_command", cmd_to_run
        client.methodCall command_name, command_arguments, (error, value) ->
            if exist(error)
                p.reject(error)
                utils.force_digest($scope)
            else
                p.resolve(value)
                utils.force_digest($scope)
        p.promise

    $scope.sync_btn = ->
        clear_msg_buffer()
        add_output("syncing data")
        option = 
            dir: $scope.cb_folder_text
            username: $scope.cb_username
            password: $scope.cb_password
            cryptobox: $scope.cb_name
            server: $scope.cb_server
            encrypt: true
            clear: "0"
            sync: "1"

        run_command("cryptobox_command", [option]).then(
            (res) ->
                if not utils.exist_truth(res)
                    add_output(res)
                else
                    add_output("done syncing")

            (err) ->
                add_output(err)
        )

    $scope.check_btn = ->
        lock_buttons = true
        clear_msg_buffer()
        add_output("checking changes")
        option = 
            dir: $scope.cb_folder_text
            username: $scope.cb_username
            password: $scope.cb_password
            cryptobox: $scope.cb_name
            server: $scope.cb_server
            check: "1"

        run_command("cryptobox_command", [option]).then(
            (res) ->
                add_output(res)
                add_output("check done")

            (err) ->
                add_output(err)
        )

    $scope.encrypt_btn = ->
        clear_msg_buffer()
        add_output("sync encrypt remove data")
        option = 
            dir: $scope.cb_folder_text
            username: $scope.cb_username
            password: $scope.cb_password
            cryptobox: $scope.cb_name
            server: $scope.cb_server
            encrypt: true
            remove: true
            sync: false

        run_command("cryptobox_command", [option]).then(
            (res) ->
                add_output(res)
                add_output("done encrypting")

            (err) ->
                add_output(err)
        )

    $scope.decrypt_btn = ->
        clear_msg_buffer()
        add_output("decrypt local data")
        option = 
            dir: $scope.cb_folder_text
            username: $scope.cb_username
            password: $scope.cb_password
            cryptobox: $scope.cb_name
            server: $scope.cb_server
            decrypt: true
            clear: false

        run_command("cryptobox_command", [option]).then(
            (res) ->
                add_output(res)
                add_output("done decrypting")

            (err) ->
                add_output(err)
        )

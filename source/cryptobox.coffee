child_process = require("child_process")
path = require("path")
gui = require('nw.gui')
xmlrpc = require('xmlrpc')


winmain = gui.Window.get()


print = (msg, others...) ->
    len_others = _.size(others)

    #noinspection CoffeeScriptSwitchStatementWithNoDefaultBranch
    switch len_others
        when 0 then go console?.log msg
        when 1 then console?.log msg + " " + others[0]
        when 2 then console?.log msg + " " + others[0] + " " + others[1]
        when 3 then console?.log msg + " " + others[0] + " " + others[1] + " " + others[2]
        when 4 then console?.log msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3]
        when 5 then console?.log msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3] + " " + others[4]
        else
            console?.log others, msg


angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"])
cryptobox_ctrl = ($scope, $q, memory, utils) ->
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

    $scope.on_exit = =>
        killprocess = (child) ->
            console.error "cryptobox.cf:19", "killing" + memory.get(child)

            #memory_name = "g_process_" + utils.slugify(cmd_name)
            print "cryptobox.cf:74", "killing", child, memory.get(child)
            process.kill(memory.get(child), 'SIGINT');
        _.each(memory.all_prefix("g_process"), killprocess)

        quit = ->
            gui.App.quit()

        _.defer(quit)

    set_output_buffers = (cba_main_proc) ->
        if exist(cba_main_proc)
            memory_name = "g_process_" + utils.slugify(cmd_to_run)
            memory.set(memory_name, cba_main_proc.pid)

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

    $scope.clear_btn = ->
        clear_msg_buffer()

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
                output.push(utils.format_time(utils.get_local_time()) + ": " + msg)

        if msgs.split?
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
            output.push(utils.format_time(utils.get_local_time()) + ": " + msgs)

    update_output = ->
        msgs = ""

        make_stream = (msg) ->
             msgs += msg + "\n"

        _.each(output, make_stream)
        $scope.cmd_output = msgs
        utils.force_digest($scope)

    utils.set_interval("cryptobox.cf:147", update_output, 100, "update_output")
    starting = false
    first_start = true

    ping_client = ->
        if utils.exist_truth(starting)
            return

        client = get_rpc_client()
        client.methodCall "last_ping", [], (error, value) ->
            if exist(error)
                if not utils.exist_truth(first_start)
                    print "cryptobox.cf:159", error
                else
                    first_start = false

                starting = true
                print "cryptobox.cf:164", "starting again"
                cba_main = spawn(cmd_to_run, [""])
                set_output_buffers(cba_main)
                starting = false

    utils.set_interval("cryptobox.cf:169", ping_client, 5000, "ping_client")
    ping_client()

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
                        print "cryptobox.cf:216", k, d.value
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
                print "cryptobox.cf:235", err
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
                print "cryptobox.cf:273", err
        )

    $scope.file_input_change = (f) ->
        $scope.cb_folder_text = f[0].path
        $scope.form_change()

    run_command = (command_name, command_arguments) ->
        client = get_rpc_client()
        p = $q.defer()
        print "cryptobox.cf:283", "run_command", cmd_to_run
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
                print "cryptobox.cf:371", res
                add_output(res)

            (err) ->
                add_output(err)
        )

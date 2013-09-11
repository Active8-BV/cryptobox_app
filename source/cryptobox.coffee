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
    $scope.cba_version = 0.1
    memory.set("g_running", true)

    $scope.on_exit = =>
        killprocess = (child) ->
            console.error "cryptobox.cf:19", "killing" + memory.get(child)

            #memory_name = "g_process_" + utils.slugify(cmd_name)
            process.kill(memory.get(child));
        _.each(memory.all_prefix("g_process"), killprocess)

        quit = ->
            gui.App.quit()

        _.defer(quit)

    winmain.on('close', $scope.on_exit);

    run_command = (cmd_name) ->
        memory_name = "g_process_" + utils.slugify(cmd_name)

        if memory.has(memory_name)
            return

        cmd_to_run = path.join(process.cwd(), "commands")
        cmd_to_run = path.join(cmd_to_run, cmd_name)
        print "cryptobox.cf:55", cmd_to_run
        p = $q.defer()

        process_result = (error, stdout, stderr) =>
            if utils.exist(stderr)
                console.error console.error

            if utils.exist(error)
                console.error "cryptobox.cf:25", stderr

                p.reject(error)
            else
                p.resolve(stdout)

            memory.del(memory_name)
            utils.force_digest($scope)

        child = child_process.exec(cmd_to_run, process_result)
        memory.set(memory_name, child.pid)
        p.promise

    #$scope.python_version = run_command("cba_commander")
    #cba_commander = child_process.spawn("cba_commander")
    spawn = require("child_process").spawn
    cmd_to_run = path.join(process.cwd(), "commands")
    cmd_to_run = path.join(cmd_to_run, "cba_commander")
    cba_commander = spawn(cmd_to_run, [""])
    memory_name = "g_process_" + utils.slugify(cmd_to_run)
    memory.set(memory_name, cba_commander.pid)

    cba_commander.stdout.on "data", (data) ->
        print "cryptobox.cf:86", data

    cba_commander.stderr.on "data", (data) ->
        print "cryptobox.cf:89", data

    $scope.handle_change = ->
        $scope.yourName = handle($scope.yourName)

    $scope.file_input_change = (f) ->
        console?.log? f
        $scope.cb_folder_text = f[0].path
        print "cryptobox.cf:97", $scope.cb_folder_text
        console?.log? $scope.cb_folder_text

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

                    p.resolve("set_val -> " + k + ":" + v)
                else
                    p.reject("error set_val")

            utils.force_digest($scope)
        p.promise

    get_val = (k) ->
        p = $q.defer()
        client = get_rpc_client()
        client.methodCall "get_val", [k], (error, value) ->
            if exist(error)
                p.reject(error)
            else:
                p.resolve(value)

            utils.force_digest($scope)
        p.promise

    $scope.test_btn = ->
        set_val("my_test_var", "hello world").then(
            (value) ->
                print "cryptobox.cf:139", value

            (error) ->
                print "cryptobox.cf:142", error
        )

    $scope.sync_btn = ->
        get_val("my_test_var").then(
            (value) ->
                print "cryptobox.cf:148", value

            (error) ->
                print "cryptobox.cf:151", error
        )

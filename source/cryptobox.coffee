

child_process = require("child_process")
path = require('path')


angular.module("cryptoboxApp", ["cryptoboxApp.base"])
cryptobox_ctrl = ($scope, $q, memory, utils) ->
    memory.set("g_running", true)

    run_command = (cmd_name) ->
        console.log "cryptobox.cf:12", cmd_name
        cmd_to_run = path.join(process.cwd(), "commands")
        cmd_to_run = path.join(cmd_to_run, cmd_name)
        p = $q.defer()

        process_result = (error, stdout, stderr) ->
            if utils.exist(stderr)
                console.log "cryptobox.cf:19", stderr
            if utils.exist(error)
                p.reject(error)
            else
                console.log "cryptobox.cf:23", "resolving"
                p.resolve(stdout)
            utils.force_digest($scope)


        options = { encoding: 'utf8', timeout: 15000, maxBuffer: 200*1024, killSignal: 'SIGTERM', cwd: null, env: null }
        child_process.exec(cmd_to_run, options, process_result)
        p.promise

    $scope.python_version = run_command("pyversion")

    $scope.handle_change =  ->
        $scope.yourName =  handle($scope.yourName)

    $scope.file_input_change = ->
        py_file_input_change($scope.file_input)

    $scope.test = ->
        alert("hello")
        #cv_open_save_dialog = (e) ->
        #    console.log "cryptobox.cf:43", e.toString()
        #print "app.cf:69", Ti.UI.openFolderChooserDialog(cv_open_save_dialog)


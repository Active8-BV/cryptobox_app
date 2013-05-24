

child_process = require("child_process")
path = require("path")


angular.module("cryptoboxApp", ["cryptoboxApp.base"])
cryptobox_ctrl = ($scope, $q, memory, utils) ->
    memory.set("g_running", true)

    $scope.on_exit = =>
        console.log "cryptobox.cf:12", window.globals
    window.addEventListener("beforeunload", $scope.on_exit)

    run_command = (cmd_name) ->
        if memory.has("g_process_" + cmd_name)
            return
        console.log "cryptobox.cf:18", cmd_name
        cmd_to_run = path.join(process.cwd(), "commands")
        cmd_to_run = path.join(cmd_to_run, cmd_name)
        p = $q.defer()

        process_result = (error, stdout, stderr) ->
            if utils.exist(stderr)
                console.log "cryptobox.cf:25", stderr
            if utils.exist(error)
                p.reject(error)
            else
                console.log "cryptobox.cf:29", "resolving"
                p.resolve(stdout)
            memory.del("g_process_" + cmd_name, child)
            utils.force_digest($scope)

        child = child_process.exec(cmd_to_run, process_result)
        memory.set("g_process_" + cmd_name, child)
        p.promise

    $scope.python_version = run_command("pyversion")

    $scope.handle_change =  ->
        $scope.yourName =  handle($scope.yourName)

    $scope.file_input_change = ->
        py_file_input_change($scope.file_input)

    $scope.index = ->
        $scope.num_files = run_command("index_directory -d '/Users/rabshakeh/Desktop' -i 'mydir.dict'")
        #cv_open_save_dialog = (e) ->
        #    console.log "cryptobox.cf:49", e.toString()
        #print "app.cf:69", Ti.UI.openFolderChooserDialog(cv_open_save_dialog)
    $scope.index()


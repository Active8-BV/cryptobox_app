

angular.module("cryptoboxApp", ["cryptoboxApp.base"])
cryptobox_ctrl = ($scope, $q, memory, utils) ->
    memory.set("g_running", true)

    run_command = (cmd_name) ->
        return "command here"
        p = $q.defer()
        cmd = Ti.API.getApplication().getResourcesPath() + "/" + cmd_name
        cmd_process = Ti.Process.createProcess([cmd])

        on_read = (e) ->
            p.resolve(e.data.toString())
            utils.force_digest($scope)
        cmd_process.setOnRead(on_read)

        on_exit = (command) ->
            console.log "cryptobox.cf:19", 'exit' + command.getTarget().toString().replace(Ti.API.getApplication().getResourcesPath(), "")

        on_failure = ->
            p.reject("timeout occurred")
        set_time_out(on_failure, 5000)
        cmd_process.setOnExit(on_exit)
        cmd_process.launch()
        p.promise

    $scope.python_version = run_command("pyversion")

    $scope.handle_change =  ->
        $scope.yourName =  handle($scope.yourName)

    $scope.file_input_change = ->
        py_file_input_change($scope.file_input)

    $scope.test = ->
        alert("hello")
        #cv_open_save_dialog = (e) ->
        #    console.log "cryptobox.cf:39", e.toString()
        #print "app.cf:69", Ti.UI.openFolderChooserDialog(cv_open_save_dialog)


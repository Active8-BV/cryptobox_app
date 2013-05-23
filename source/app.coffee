

f_exit = ->
    Ti.App.exit()


add_menu = ->
    menu = Ti.UI.createMenu()
    fileItem = Ti.UI.createMenuItem("File")
    fileItem.addItem("Exit", f_exit)
    menu.appendItem fileItem
    Ti.UI.setMenu menu


add_tray = ->
    programTray = Ti.UI.addTray("tray_icon.png")
    tmenu = Ti.UI.createMenu()
    tmenu.addItem("Exit", f_exit)
    programTray.setMenu(tmenu)
add_menu()
add_tray()


angular.module("cryptoboxApp", ["cryptoboxApp.base"])
cryptobox_ctrl = ($scope, $q, memory, utils) ->
    memory.set("g_running", true)

    run_command = (cmd_name) ->
        p = $q.defer()
        cmd = Ti.API.getApplication().getResourcesPath() + "/" + cmd_name
        cmd_process = Ti.Process.createProcess([cmd])

        on_read = (e) ->
            p.resolve(e.data.toString())
            utils.force_digest($scope)
        cmd_process.setOnRead(on_read)

        on_exit = (command) ->
            console.log "app.cf:39", 'exit' + command.getTarget().toString().replace(Ti.API.getApplication().getResourcesPath(), "")

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
        #    console.log "app.cf:59", e.toString()
        #print "app.cf:69", Ti.UI.openFolderChooserDialog(cv_open_save_dialog)


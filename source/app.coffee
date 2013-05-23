

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
cryptobox_ctrl = ($scope, $q) ->
    run_command = (cmd_name) ->
        p = $q.defer()
        cmd = Ti.API.getApplication().getResourcesPath() + "/" + cmd_name
        cmd_output = Ti.Filesystem.createTempFile()
        cmd_process = Ti.Process.createProcess([cmd], stdout = cmd_output)

        on_exit = (command) ->
            console.log 'exiting', command.getTarget().toString().replace(Ti.API.getApplication().getResourcesPath(), "")
            p.resolve("succes")

        on_failure = ->
            p.reject("timeout occurred")
        set_time_out(on_failure, 5000)
        cmd_process.setOnExit(on_exit)
        cmd_process.launch()
        p.promise

    get_version = ->
        run_command("pyversion").then(
            (success) ->
                console.log success

            (error) ->
                console.log error
        )
        return "version"
    $scope.python_version = get_version()

    $scope.handle_change =  ->
        $scope.yourName =  handle($scope.yourName)

    $scope.file_input_change = ->
        py_file_input_change($scope.file_input)

    $scope.open_dialog = ->
        console.log get_version()
        return

        cv_open_save_dialog = (e) ->
            console.log e.toString()
        console.log Ti.UI.openFolderChooserDialog(cv_open_save_dialog, {"title": "Selecteer datamap Cryptobox", "path":Ti.Filesystem.getDocumentsDirectory().toString(), "default":"Cryptobox" })


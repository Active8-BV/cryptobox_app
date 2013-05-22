

f_exit = ->
    Ti.App.exit()


Ti.API.addEventListener(Ti.EXIT, ->
    console.log "bye bye"
)


add_menu = ->
    menu = Ti.UI.createMenu()
    fileItem = Ti.UI.createMenuItem("File")
    fileItem.addItem("Exit", f_exit)
    menu.appendItem fileItem
    Ti.UI.setMenu menu
add_menu()


add_tray = ->
    programTray = Ti.UI.addTray("tray_icon.png")
    tmenu = Ti.UI.createMenu()
    tmenu.addItem("Exit", f_exit)
    programTray.setMenu(tmenu)
add_tray()


angular.module("cryptoboxApp", ["cryptoboxApp.base"])
cryptobox_app = ($scope, memory) ->
    $scope.python_version = get_version()

    $scope.handle_change =  ->
        $scope.yourName =  handle($scope.yourName)

    $scope.file_input_change = ->
        py_file_input_change($scope.file_input)




# create and set menu

use_my_python_data = (data) ->
    console.log data


add_menu = ->
    menu = Ti.UI.createMenu()
    fileItem = Ti.UI.createMenuItem("File")

    f_exit = ->
        Ti.App.exit()

    exitItem = fileItem.addItem("Exit", f_exit)
    menu.appendItem fileItem
    Ti.UI.setMenu menu
add_menu()


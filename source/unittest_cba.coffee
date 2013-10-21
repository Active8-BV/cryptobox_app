
fs = require("fs")
assert = require('assert')

add_command = (name, data) ->
    cmd_folder = path.join(process.cwd(), "commands")
    cmd_path = path.join(cmd_folder, "name")
    fout = fs.openSync(cmd_path, "w")
    fs.write(fout, "hello world")

exports["test add command"] = ->
    add_command("exit", "-")

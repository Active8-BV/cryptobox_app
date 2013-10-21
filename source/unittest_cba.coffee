fs = require("fs")
assert = require('assert')
path = require("path")


add_command = (name, data) ->
    console.log name, data
    cmd_folder = path.join(process.cwd(), "cba_commands")
    if not fs.existsSync(cmd_folder)
        fs.mkdirSync(cmd_folder)
    cmd_path = path.join(cmd_folder, name)
    fout = fs.openSync(cmd_path, "w")
    fs.write(fout, data)

    
exports["test add command"] = ->
    obj = {}
    obj["a"] = 7
    obj["b"] = 9
    add_command("add", JSON.stringify(obj))

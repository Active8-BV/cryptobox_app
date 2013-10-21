fs = require("fs")
assert = require('assert')
path = require("path")

run_command = (name, data) ->
    data["id"] = new Date().getTime();
    cmd_folder = path.join(process.cwd(), "cba_commands")
    if not fs.existsSync(cmd_folder)
        fs.mkdirSync(cmd_folder)
    cmd_path = path.join(cmd_folder, name + ".cmd")
    result_path = path.join(cmd_folder, name + ".result")
    fout = fs.openSync(cmd_path, "w")
    fs.write(fout, JSON.stringify(data))
    return data["id"]

check_result = (name, id) ->
    cmd_folder = path.join(process.cwd(), "cba_commands")
    result_path = path.join(cmd_folder, name + ".result")
    if fs.existsSync(result_path)
        data = fs.readFileSync(result_path)
        data = JSON.parse(data)
        fs.unlinkSync(result_path)
        if data?
            if data["result"]? and data["id"]?
                if data["id"] == id
                    return data["result"]
    return null

run_commands = ->
    spawn = require("child_process").spawn
    proc = spawn("/Users/rabshakeh/workspace/cryptobox/cryptobox_app/source/run_commands.py", "")


exports["test add command"] = ->
    name = "add"
    cmd_folder = path.join(process.cwd(), "cba_commands")
    cmd_path = path.join(cmd_folder, name + ".cmd")
    result_path = path.join(cmd_folder, name + ".result")
    obj = {}
    obj["a"] = 7
    obj["b"] = 9
    cmd_id = run_command(name, obj)
    assert.equal(fs.existsSync(cmd_path), true)
    run_commands()

    check_results = =>
        assert.equal(fs.existsSync(result_path), true)
        assert.equal(fs.existsSync(cmd_path), false)
        result = check_result(name, cmd_id)
        assert.equal(result["result"], 16)
    setTimeout(check_results, 200)





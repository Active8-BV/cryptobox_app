fs = require("fs")
assert = require('assert')
path = require("path")
_ = require('underscore')

add_output = (msgs) ->
    console.log msgs
    return true


print = (msg, others...) ->
    len_others = _.size(others)

    #noinspection CoffeeScriptSwitchStatementWithNoDefaultBranch
    switch len_others
        when 0
            add_output(msg)
        when 1
            add_output(msg + " " + others[0])
        when 2
            add_output(msg + " " + others[0] + " " + others[1])
        when 3
            add_output(msg + " " + others[0] + " " + others[1] + " " + others[2])
        when 4
            add_output(msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3])
        when 5
            add_output(msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3] + " " + others[4])
        else
            add_output(others)
            add_output(msg)


run_cba_main = (name, options, cb, cb_stdout) ->
    if !exist(cb)
        throw "run_cba_main needs a cb parameter (callback)"

    params = option_to_array(name, options)
    cmd_to_run = path.join(process.cwd(), "commands")
    cmd_to_run = path.join(cmd_to_run, "cba_main")
    cba_main = child_process.spawn(cmd_to_run, params)
    g_cba_main = cba_main
    output = ""
    error = ""
    buffereddata = ""

    stdout_data = (data) ->
        if String(data).indexOf("error_message") >= 0
            error = parse_json(data)
            g_error_message = error?.error_message
            add_output(g_error_message)

        if cb_stdout?
            buffereddata += data
            buffereddata = String(buffereddata).split("\n")

            try_cb = (datachunk) ->
                if datachunk?
                    if _.size(datachunk) > 0
                        datachunk = parse_json(datachunk)

                        if datachunk?
                            buffereddata = ""
                            cb_stdout(datachunk)

            _.each(buffereddata, try_cb)

            #pdata = parse_json(buffereddata)
            #if pdata?
            ##    print "cryptobox.cf:206", pdata
            #    buffereddata = ""
            #    cb_stdout(pdata)
        else
            output += data
    cba_main.stdout.on "data", stdout_data

    cba_main.stderr.on "data", (data) ->
        error += data

    execution_done = (event) ->
        g_cba_main = null

        if already_running(output)
            print "cryptobox.cf:220", "already running"
            cb(false, output)
        else
            if _.size(error) > 0
                if String(error).indexOf("error_message") >= 0
                    errorm = parse_json(error)
                    g_error_message = errorm.error_message
                cb(false, error)
            else
                output = parse_json(output)

                if event > 0
                    cb(false, output)
                else
                    cb(true, output)

    cba_main.on("exit", execution_done)

print "hello"

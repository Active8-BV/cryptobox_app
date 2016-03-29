
fs = require("fs")
assert = require('assert')
path = require("path")
_ = require('underscore')
child_process = require("child_process")
path = require("path")


pass = ->
    x = 9


strEndsWith = (str, suffix) ->
    str.indexOf(suffix, str.length - suffix.length) != -1


exist_string = (value) ->
  if value?
    switch value
      when undefined, null, "null", "undefined"
        false
      else
        true
  else
    false


exist = (value) ->
  if exist_string(value)
    return false  if value is ""
    return false  if String(value) is "NaN"
    return false  if String(value) is "undefined"
    return false  if value.trim() is ""  if value.trim?
    true
  else
    false


parse_json = (data, debug) ->
    try
        output = []
        data = String(data).split("\n")

        try_cb = (datachunk) ->
            if datachunk?
                if _.size(datachunk) > 0
                    datachunk = JSON.parse(datachunk)

                    if datachunk?
                        if datachunk.error_message?
                            g_error_message = datachunk?.error_message
                            add_output(g_error_message)
                        output.push(datachunk)

        _.each(data, try_cb)
        if _.size(output) == 1
            return output[0]
        return output
    catch ex
        if debug?
            print "node_test.cf:62", "could not parse json", ex
            print "node_test.cf:63", data
    return null


already_running = (output) ->
    if output.indexOf("Another instance is already running, quitting.") >= 0
        return true
    return false


add_output = (msgs) ->
    console?.log msgs
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


cnt_char = (data, c) ->
    _.size(String(data).split(c))-1


possible_json = (data) ->
    if cnt_char(data, "{") == cnt_char(data, "}")
        try
            JSON.parse(data)
            return true
        catch ex
            return false
    return false


run_cba_main = (name, options, cb_done, cb_intermediate) ->
    if !exist(cb_done)
        throw "run_cba_main needs a cb_done parameter (callback)"

    #params = option_to_array(name, options)
    cmd_to_run = path.join(process.cwd(), "cba_main")
    cba_main = child_process.spawn(cmd_to_run, "")
    g_cba_main = cba_main
    output = ""
    error = ""
    data = ""
    intermediate_cnt = 0

    stdout_data = (data) ->
        output += data
        ssp = String(output).split("\n")

        has_data = (item) ->
            if _.size(item) > 0
                return true
            return false

        ssp = _.filter(ssp, has_data)
        nls = _.size(ssp)

        if nls > 0
            loop_cnt = 0

            call_intermediate = (data) ->
                if loop_cnt == intermediate_cnt
                    pdata = null

                    if possible_json(data)
                        pdata = parse_json(data, true)

                    if pdata
                        cb_intermediate(pdata)
                        intermediate_cnt += 1

                loop_cnt += 1
            _.each(ssp, call_intermediate)
    cba_main.stdout.on "data", stdout_data

    cba_main.stderr.on "data", (data) ->
        error += data

    execution_done = (event) ->
        g_cba_main = null

        if already_running(output)
            print "node_test.cf:164", "already running"
            cb_done(false, output)
        else
            output = parse_json(output)

            if event > 0
                cb_done(false, output)
            else
                cb_done(true, output)

    cba_main.on("exit", execution_done)


cb_done = (r, o) ->
    print "node_test.cf:178", r

    p = (d) ->
        print "node_test.cf:181", d.message
    _.each(o, p)


cb_current = (o) ->
    print "node_test.cf:186", o
run_cba_main("foo", {}, cb_done, cb_current)

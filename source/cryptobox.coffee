child_process = require("child_process")
path = require("path")
gui = require('nw.gui')
xmlrpc = require('xmlrpc')


winmain = gui.Window.get()


print = (msg, others...) ->
  switch _.size(others)
      when 0
          console?.log msg
      when 1
          console?.log msg + " " + others[0]
      when 2
          console?.log msg + " " + others[0] + " " + others[1]
      when 3
          console?.log msg + " " + others[0] + " " + others[1] + " " + others[2]
      when 4
          console?.log msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3]
      when 5
          console?.log msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3] + " " + others[4]
      else
          console?.log others, msg


angular.module("cryptoboxApp", ["cryptoboxApp.base"])
cryptobox_ctrl = ($scope, $q, memory, utils) ->
    $scope.cba_version = 0.1
    memory.set("g_running", true)

    $scope.on_exit = =>
        killprocess = (child) ->
            console.error "cryptobox.cf:19", "killing"+memory.get(child)

            #memory_name = "g_process_" + utils.slugify(cmd_name)
            process.kill(memory.get(child));
        _.each(memory.all_prefix("g_process"), killprocess)

        quit = ->
            gui.App.quit()

        _.defer(quit)

    winmain.on('close', $scope.on_exit);

    run_command = (cmd_name) ->
        memory_name = "g_process_" + utils.slugify(cmd_name)

        if memory.has(memory_name)
            return

        cmd_to_run = path.join(process.cwd(), "commands")
        cmd_to_run = path.join(cmd_to_run, cmd_name)
        print "cryptobox.cf:58", cmd_to_run
        p = $q.defer()

        process_result = (error, stdout, stderr) =>
            if utils.exist(stderr)
                console.error console.error

            if utils.exist(error)
                console.error "cryptobox.cf:25", stderr

                p.reject(error)
            else
                p.resolve(stdout)

            memory.del(memory_name)
            utils.force_digest($scope)

        child = child_process.exec(cmd_to_run, process_result)
        memory.set(memory_name, child.pid)
        p.promise

    #$scope.python_version = run_command("cba_commander")
    #cba_commander = child_process.spawn("cba_commander")
    spawn = require("child_process").spawn
    cmd_to_run = path.join(process.cwd(), "commands")
    cmd_to_run = path.join(cmd_to_run, "cba_commander")
    cba_commander = spawn(cmd_to_run, [""])
    memory_name = "g_process_" + utils.slugify(cmd_to_run)
    memory.set(memory_name, cba_commander.pid)

    cba_commander.stdout.on "data", (data) ->
      print "cryptobox.cf:89", data

    cba_commander.stderr.on "data", (data) ->
      print "cryptobox.cf:92", data

    $scope.handle_change =  ->
        $scope.yourName =  handle($scope.yourName)

    $scope.file_input_change = ->
        py_file_input_change($scope.file_input)

    $scope.run_commands = ->
        clientOptions = 
          host: "localhost"
          port: 8654
          path: "/RPC2"

        client = xmlrpc.createClient(clientOptions)
        client.methodCall "add", [2, 4], (error, value) ->
          $scope.python_version = value
          utils.force_digest($scope)

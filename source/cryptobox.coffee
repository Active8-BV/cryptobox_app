child_process = require("child_process")
path = require("path")
gui = require('nw.gui')
xmlrpc = require('xmlrpc')


winmain = gui.Window.get()


angular.module("cryptoboxApp", ["cryptoboxApp.base"])
cryptobox_ctrl = ($scope, $q, memory, utils) ->
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

    $scope.python_version = run_command("pyversion")

    $scope.handle_change =  ->
        $scope.yourName =  handle($scope.yourName)

    $scope.file_input_change = ->
        py_file_input_change($scope.file_input)

    $scope.run_commands = ->
        run_command("pyversion")
        client = xmlrpc.createClient(
          host: "localhost"
          port: 8000
          cookies: true
        )

        #client.setCookie "login", "bilbo"
        #This call will send provided cookie to the server
        client.methodCall "adder_function", [2, 4], (error, value) ->
          print "cryptobox.cf:78", error, value
          $scope.python_version = value

          #Here we may get cookie received from server if we know its name
          #print client.getCookie("session")

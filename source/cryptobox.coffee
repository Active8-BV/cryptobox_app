

child_process = require("child_process")
path = require("path")


gui = require('nw.gui')


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
        console.log "cryptobox.cf:34", cmd_name
        cmd_to_run = path.join(process.cwd(), "commands")
        cmd_to_run = path.join(cmd_to_run, cmd_name)
        p = $q.defer()

        process_result = (error, stdout, stderr) =>
            if utils.exist(stderr)
                console.log "cryptobox.cf:41", stderr
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
    $scope.num_files = run_command("index_directory -d '/Users/rabshakeh/Desktop' -i 'mydir.dict'")

    $scope.handle_change =  ->
        $scope.yourName =  handle($scope.yourName)

    $scope.file_input_change = ->
        py_file_input_change($scope.file_input)

    $scope.run_commands = ->
        $scope.python_version = run_command("pyversion")
        $scope.num_files = run_command("index_directory -d '/Users/rabshakeh/Desktop' -i 'mydir.dict'")


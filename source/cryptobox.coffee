
child_process = require("child_process") # ##^ ass1gnment on global 0
path = require("path") # ##^ ass1gnment on global 0
fs = require("fs") # ##^ ass1gnment on global 0


gui = require('nw.gui') # ##^ global method call 0
xmlrpc = require('xmlrpc') # ##^ ass1gnment on global 0


gui = require("nw.gui") # ##^ global method call 0
watch = require("watch") # ##^ ass1gnment on global 0

# Create a tray icon # ##^ comment 0


print = (msg, others...) -> # ##^ global method call 0
    len_others = _.size(others) # ##^ ass1gnment 0

    #noinspection CoffeeScriptSwitchStatementWithNoDefaultBranch # ##^ pycharm d1rect1ve keyword (not class) 1n nextl1ne 0
    switch len_others # ##^ sw1tch statement prevented by None 0
        when 0 then console?.log msg # ##^ when statement 0
        when 1 then console?.log msg + " " + others[0] # ##^ when statement 0
        when 2 then console?.log msg + " " + others[0] + " " + others[1] # ##^ when statement 0
        when 3 then console?.log msg + " " + others[0] + " " + others[1] + " " + others[2] # ##^ when statement 0
        when 4 then console?.log msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3] # ##^ when statement 0
        when 5 then console?.log msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3] + " " + others[4] # ##^ when statement 0
        else # ##^  0
            console?.log others, msg # ##^  0


tray = new gui.Tray(# ##^ ass1gnment prev scope on global on prev scope new scope 0
    icon: "images/icon-client-signed-in-idle.png" # ##^ member 1n1t1al1zat1on 0
) # ##^  0


angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"]) # ##^ global method call 0
cryptobox_ctrl = ($scope, $q, memory, utils) -> # ##^ funct1on def 0
    print "cryptobox.cf:39", "cryptobox_ctrl" # ##^ debug statement 0

    get_rpc_client = -> # ##^ funct1on def nested after keyword 0
        clientOptions = # ##^  0
            host: "localhost" # ##^ member 1n1t1al1zat1on 0
            port: 8654 # ##^ member 1n1t1al1zat1on 0
            path: "/RPC2" # ##^ member 1n1t1al1zat1on 0

        return xmlrpc.createClient(clientOptions) # ##^  wh1tespace |  0

    $scope.cba_version = 0.1 # ##^ ass1gnment prev scope on scope 0
    memory.set("g_running", true) # ##^  0
    cba_main = null # ##^ ass1gnment 0

    $scope.on_exit = => # ##^ funct1on def nested after ass1gnement on scope 0

        #print "cryptobox.cf:54", "cryptobox app on_exit" # ##^ comment -> debug statement 0
        client = get_rpc_client() # ##^ ass1gnment 0
        client.methodCall "force_stop",[], (e,v) -> # ##^ anonymousfunct1on 0
            force_kill = => # ##^ funct1on def nested after keyword after anon func 0
                if cba_main? # ##^  1f statement 1
                    if cba_main.pid? # ##^  1f statement 2
                        add_output("force kill!!!") # ##^ funct1on call 2
                        process.kill(cba_main.pid); # ##^  2
                        gui.App.quit() # ##^  2

            utils.set_time_out("cryptobox.cf:65", force_kill, 100) # ##^  scope -1

    set_output_buffers = (cba_main_proc) -> # ##^ funct1on def nested after keyword on prev1ous scope -1
        if exist(cba_main_proc.stdout) # ##^  1f statement 0
            cba_main_proc.stdout.on "data", (data) -> # ##^ anonymousfunct1on 0
                add_output("stdout:" + data) # ##^ member 1n1t1al1zat1on 0

        if exist(cba_main_proc.stderr) # ##^  1f statement scope change 1
            cba_main_proc.stderr.on "data", (data) -> # ##^ anonymousfunct1on 1
                add_output("stderr:" + data) # ##^ member 1n1t1al1zat1on 1

    winmain = gui.Window.get() # ##^  scope -2
    winmain.on('close', $scope.on_exit); # ##^  -2
    spawn = require("child_process").spawn # ##^ ass1gnment -2
    cmd_to_run = path.join(process.cwd(), "commands") # ##^ ass1gnment -2
    cmd_to_run = path.join(cmd_to_run, "cba_main") # ##^ ass1gnment -2
    output = [] # ##^ ass1gnment -2

    $scope.clear_msg_buffer = -> # ##^ funct1on def nested after ass1gnement on scope -2
        output = [] # ##^ ass1gnment -2
        utils.force_digest($scope) # ##^  -2

    $scope.debug_btn = -> # ##^ funct1on def nested after keyword on scope -2
        require('nw.gui').Window.get().showDevTools() # ##^  -2

    update_output = -> # ##^ funct1on def nested after keyword on prev1ous scope -2
        msgs = "" # ##^ ass1gnment -2

        make_stream = (msg) -> # ##^ funct1on def nested after ass1gnement -2
             msgs += msg + "\n" # ##^ ass1gnment -2
        _.each(output, make_stream) # ##^  -2
        $scope.cmd_output = msgs # ##^ ass1gnment on scope -2
        utils.force_digest($scope) # ##^  -2

    add_output = (msgs) -> # ##^ funct1on def nested after keyword on prev1ous scope -2
        add_msg = (msg) -> # ##^ funct1ondef after funct1ondef -2
            if msg.indexOf? # ##^  1f statement -1
                if msg.indexOf("Error") == -1 # ##^  1f statement 0
                    if msg.indexOf("POST /RPC2") > 0 # ##^  1f statement 1
                        return # ##^  after keyword 1

            if msg.replace? # ##^  scope -1
                msg = msg.replace("stderr:", "") # ##^ member 1n1t1al1zat1on -1
                msg.replace("\n", "") # ##^  -1
                msg = msg.trim() # ##^ ass1gnment -1

            if utils.exist(msg) # ##^  1f statement scope change 0
                output.unshift(utils.format_time(utils.get_local_time()) + ": " + msg) # ##^  0

        if msgs?.split? # ##^  1f statement scope change 1
            _.each(msgs.split("\n"), add_msg) # ##^  1
        else if msgs == "true" # ##^  1f statement scope change else 0
            pass # ##^  0
        else if msgs == "false" # ##^  1f statement scope change else 0
            pass # ##^  0
        else if msgs == true # ##^  1f statement scope change else 0
            pass # ##^  0
        else if msgs == false # ##^  1f statement scope change else 0
            pass # ##^  0
        else # ##^  0
            if msgs? # ##^  1f statement 1
                output.push(utils.format_time(utils.get_local_time()) + ": " + msgs) # ##^  1
        update_output() # ##^ funct1on call -1

    warning = (ln, w) -> # ##^ ass1gnment prev scope -1
        if w? # ##^  1f statement 0
            if w?.trim? # ##^  1f statement 1
                w = w.trim() # ##^ ass1gnment 1
        else # ##^  -1
            return # ##^  after keyword -1

        if utils.exist(w) # ##^  1f statement scope change 0
            if w.faultString? # ##^  1f statement 1
                add_output(w.faultString) # ##^  1
            else if w.message # ##^  1f statement scope change else 0
                add_output(w.message) # ##^  0
            else # ##^  0
                add_output(w) # ##^ funct1on call 0

    $scope.motivation = null # ##^  scope 0

    get_motivation = -> # ##^ funct1on def nested after ass1gnement 0
        if not utils.exist($scope.motivation) # ##^  1f statement 1
            client = get_rpc_client() # ##^ ass1gnment 1
            client.methodCall "get_motivation", [], (error, value) -> # ##^ anonymousfunct1on 1
                if utils.exist(value) # ##^  1f statement 2
                    $scope.motivation = value # ##^ ass1gnment on scope 2

                if not utils.exist($scope.motivation) # ##^  1f statement scope change 2
                    utils.set_time_out("cryptobox.cf:154", get_motivation, 100) # ##^  2

    ping_client = -> # ##^  scope -2
        utils.force_digest($scope) # ##^  -2
        client = get_rpc_client() # ##^ ass1gnment -2
        client.methodCall "last_ping", [], (error, value) -> # ##^ anonymousfunct1on -2
            if utils.exist(error) # ##^  1f statement -1
                cmd_to_run = "ls" # ##^ ass1gnment -1
                cba_main = spawn(cmd_to_run, [""]) # ##^ ass1gnment -1
                set_output_buffers(cba_main) # ##^ funct1on call -1
            else # ##^  -1
                $scope.rpc_server_started = true # ##^ ass1gnment on scope -1

    $scope.rpc_server_started = false # ##^  scope -1

    start_process = => # ##^ funct1on def nested after ass1gnement -1
        print "cryptobox.cf:170", "start_process" # ##^ debug statement -1
        client = get_rpc_client() # ##^ ass1gnment -1
        client.methodCall "force_stop",[], (e,v) -> # ##^ anonymousfunct1on -1
            if utils.exist(v) # ##^  1f statement 0
                print "cryptobox.cf:174", "killed existing deamon" # ##^ debug statement 0
            else # ##^  0
                print "cryptobox.cf:176", "starting deamon" # ##^ debug statement 0

            cmd_to_run = "ls" # ##^ ass1gnment prev scope 0
            cba_main = spawn(cmd_to_run, [""]) # ##^ ass1gnment 0
            set_output_buffers(cba_main) # ##^ funct1on call 0

    start_process_once = _.once(start_process) # ##^ ass1gnment prev scope on prev scope new scope 0
    print "cryptobox.cf:183", cmd_to_run # ##^ debug statement 0
    start_process_once() # ##^ funct1on call 0
    progress_bar = 0 # ##^ ass1gnment 0
    progress_bar_item = 0 # ##^ ass1gnment 0

    $scope.get_progress_item_show = => # ##^ funct1on def nested after ass1gnement on scope 0
        return progress_bar_item != 0 # ##^  after keyword 0

    $scope.get_progress_item = => # ##^ funct1on def nested after ass1gnement after keyword on scope 0
        width: # ##^ member 1n1t1al1zat1on 0
            progress_bar_item + "%" # ##^  0

    $scope.get_progress = => # ##^ scope change 0
        width: # ##^ member 1n1t1al1zat1on 0
            progress_bar + "%" # ##^  0

    reset_progress = -> # ##^ scope change 0
        client = get_rpc_client() # ##^ ass1gnment 0
        client.methodCall "reset_progress",[], (e,v) -> # ##^ anonymousfunct1on 0
            if utils.exist(e) # ##^  1f statement 1
                warning "cryptobox.cf:203", e # ##^  1

    reset_item_progress = -> # ##^  scope -2
        client = get_rpc_client() # ##^ ass1gnment -2
        client.methodCall "reset_item_progress",[], (e,v) -> # ##^ anonymousfunct1on -2
            if utils.exist(e) # ##^  1f statement -1
                warning "cryptobox.cf:209", e # ##^  -1

    $scope.lock_buttons = false # ##^  scope -1

    $scope.get_lock_buttons = -> # ##^ funct1on def nested after ass1gnement on scope -1
        return $scope.lock_buttons # ##^  after keyword -1

    get_working_state = -> # ##^ funct1on def nested after keyword on prev1ous scope -1
        client = get_rpc_client() # ##^ ass1gnment -1
        client.methodCall "get_smemory",["working"], (e,v) -> # ##^ anonymousfunct1on -1
            if utils.exist(e) # ##^  1f statement 0
                warning "cryptobox.cf:220", e # ##^  0
            else # ##^  0
                $scope.lock_buttons = v # ##^ ass1gnment on scope 0

    last_progress_bar = 0 # ##^  scope 0
    last_progress_bar_item = 0 # ##^ ass1gnment 0

    get_progress = (progress, progress_item) => # ##^ funct1on def nested after ass1gnement 0
        if not $scope.rpc_server_started # ##^  1f statement 1
            return # ##^  after keyword 1

        progress = parseInt(progress, 10) # ##^ ass1gnment prev scope 0
        progress_item = parseInt(progress_item, 10) # ##^ ass1gnment 0
        last_progress_bar = progress_bar # ##^ ass1gnment 0
        last_progress_bar_item = progress_bar_item # ##^ ass1gnment 0

        if progress == 0 # ##^  1f statement on same scope after ass1gnement 1
            if last_progress_bar > 10 # ##^  1f statement 2
                progress_bar = 100 # ##^ ass1gnment 2

        if progress_item == 0 # ##^  1f statement scope change 1
            if last_progress_bar_item > 10 # ##^  1f statement 2
                progress_bar_item = 100 # ##^ ass1gnment 2

        if progress > parseInt(progress_bar, 10) # ##^  1f statement scope change 1
            progress_bar = progress # ##^ ass1gnment 1

        if progress_item > parseInt(progress_bar_item, 10) # ##^  1f statement scope change 1
            progress_bar_item = progress_item # ##^ ass1gnment 1

        if progress_bar >= 100 # ##^  1f statement scope change 1

            reset_progress_bar = -> # ##^ funct1on def nested after ass1gnement after 1f or else 1
                progress_bar = 0 # ##^ ass1gnment 1
                reset_progress() # ##^ funct1on call 1
            utils.set_time_out("cryptobox.cf:255", reset_progress_bar, 500) # ##^  0

        if progress_bar_item >= 100 # ##^  1f statement scope change 1

            reset_progress_bar_item = -> # ##^ funct1on def nested after ass1gnement after 1f or else 1
                progress_bar_item = 0 # ##^ ass1gnment 1
                reset_item_progress() # ##^ funct1on call 1
            utils.set_time_out("cryptobox.cf:262", reset_progress_bar_item, 500) # ##^  0
        utils.force_digest($scope) # ##^  0

    store_user_var = (k, v) -> # ##^ funct1on def nested after keyword on prev1ous scope 0
        p = $q.defer() # ##^ ass1gnment 0
        db = new PouchDB('cb_userinfo') # ##^ ass1gnment 0

        if not exist(db) # ##^  1f statement on same scope after ass1gnement 1
            p.reject("no db") # ##^  1
        else # ##^  0
            record = # ##^  0
                _id: k # ##^ member 1n1t1al1zat1on 0
                value: v # ##^ member 1n1t1al1zat1on 0
            db.get k, (e, d) -> # ##^ anonymousfunct1on 0
                if exist(d) # ##^  1f statement 1
                    if exist(d._rev) # ##^  1f statement 2
                        record._rev = d._rev # ##^ ass1gnment 2
                db.put record, (e, r) -> # ##^ anonymousfunct1on 0
                    if exist(e) # ##^  1f statement 1
                        p.reject(e) # ##^  1
                        utils.force_digest($scope) # ##^  1

                    if exist(r) # ##^  1f statement scope change 1
                        if exist_truth(r.ok) # ##^  1f statement 2
                            p.resolve(true) # ##^  2
                            utils.force_digest($scope) # ##^  2
                        else # ##^  1
                            p.reject(r) # ##^  1
                            utils.force_digest($scope) # ##^  1
                    else # ##^  -1
                        p.reject("store_user_var generic error") # ##^  -1
                        utils.force_digest($scope) # ##^  -1

        return p.promise # ##^  scope -1

    get_user_var = (k) -> # ##^ funct1on def nested after keyword on prev1ous scope -1
        p = $q.defer() # ##^ ass1gnment -1
        db = new PouchDB('cb_userinfo') # ##^ ass1gnment -1

        if not exist(db) # ##^  1f statement on same scope after ass1gnement 0
            p.reject("no db") # ##^  0
        else # ##^  0
            db.get k, (e, d) -> # ##^ anonymousfunct1on 0
                if exist(e) # ##^  1f statement 1
                    p.reject(e) # ##^  1
                else # ##^  0
                    if exist(d) # ##^  1f statement 1
                        p.resolve(d.value) # ##^  1
                        utils.force_digest($scope) # ##^  1
                    else # ##^  0
                        p.reject() # ##^  0

                        #utils.force_digest($scope) # ##^ comment 0

        return p.promise # ##^  scope 0

    set_user_var_scope = (name, scope_name) -> # ##^ funct1on def nested after keyword on prev1ous scope 0
        p = $q.defer() # ##^ ass1gnment 0

        get_user_var(name).then(# ##^ resolve method body 0
            (v) -> # ##^ resolve result 2 0
                if exist(scope_name) # ##^  1f statement 1
                    $scope[scope_name] = v # ##^ ass1gnment 1
                else # ##^  0
                    $scope[name] = v # ##^ ass1gnment 0
                p.resolve() # ##^  0

            (err) -> # ##^ resolve func
                warning "cryptobox.cf:330", err # ##^  0
                p.reject() # ##^  0
        ) # ##^ resolve func stopped
        p.promise # ##^  0

    $scope.show_settings = false # ##^ ass1gnment prev scope on scope 0
    $scope.show_debug = false # ##^ ass1gnment on scope 0

    $scope.toggle_debug = -> # ##^ funct1on def nested after ass1gnement on scope 0
        $scope.show_debug = !$scope.show_debug # ##^ ass1gnment on scope 0
        $scope.form_change() # ##^  0

    $scope.got_folder_text = false # ##^ ass1gnment prev scope on scope 0
    $scope.got_cb_name = false # ##^ ass1gnment on scope 0

    try_get_sync_state = => # ##^ try 0
        add_output("try_get_sync_state") # ##^ funct1on call 0

        get_sync_state().then(# ##^ resolve method body 0
            (r) -> # ##^ resolve result 2 0
                print "cryptobox.cf:350", "sync state retrieved" # ##^ debug statement 0

            (e) -> # ##^ resolve func
                warning "cryptobox.cf:353", e # ##^  0
        ) # ##^ resolve func stopped

    start_watch = -> # ##^ funct1on def nested somewhere 0
        if $scope.got_folder_text and $scope.got_cb_name # ##^  1f statement 1
            if fs.exists(path.join($scope.cb_folder_text, $scope.cb_name)) # ##^  1f statement 2
                watch.watchTree path.join($scope.cb_folder_text, $scope.cb_name), (f, curr, prev) -> # ##^ anonymousfunct1on 2
                    if not String(f).contains("memory.pickle") # ##^  1f statement 3
                        if typeof f is "object" and prev is null and curr is null # ##^  1f statement 4
                            pass # ##^  4
                        else if prev is null # ##^  1f statement scope change else 3
                            try_get_sync_state() # ##^  3
                        else if curr.nlink is 0 # ##^  1f statement scope change else 2
                            try_get_sync_state() # ##^  2
                        else # ##^  1
                            try_get_sync_state() # ##^  1

    set_data_user_config = -> # ##^  scope -5
        set_user_var_scope("cb_folder", "cb_folder_text").then(# ##^ resolve method body -5
            -> # ##^ resolve result 2 -5
                $scope.got_folder_text = true # ##^ ass1gnment on scope -5
                start_watch() # ##^ funct1on call -5
        ) # ##^ resolve func stopped

        set_user_var_scope("cb_username") # ##^  new l1ne -5
        set_user_var_scope("cb_password") # ##^ funct1on call -5

        set_user_var_scope("cb_name").then(# ##^ resolve method body -5
            -> # ##^ resolve result 2 -5
                $scope.got_cb_name = true # ##^ ass1gnment on scope -5
                start_watch() # ##^ funct1on call -5
        ) # ##^ resolve func stopped

        set_user_var_scope("cb_server") # ##^  new l1ne -5
        set_user_var_scope("show_settings") # ##^ funct1on call -5
        set_user_var_scope("show_debug") # ##^ funct1on call -5
        if not utils.exist($scope.cb_username) # ##^  1f statement on same scope -4
            $scope.show_settings = true # ##^ ass1gnment on scope -4

        if not utils.exist($scope.cb_server) # ##^  1f statement scope change -3
            $scope.cb_server = "http://127.0.0.1:8000/" # ##^ ass1gnment on scope -3

    set_data_user_config_once = _.once(set_data_user_config) # ##^ ass1gnment prev scope on prev scope new scope -3
    set_data_user_config_once() # ##^ funct1on call -3

    $scope.$on "$includeContentLoaded", (event) -> # ##^ 0n event on same scope  on same scope  -3
        console?.log event # ##^  -3

    $scope.form_change = -> # ##^ funct1on def nested somewhere -3
        p_cb_folder = store_user_var("cb_folder", $scope.cb_folder_text) # ##^ ass1gnment -3
        p_cb_username = store_user_var("cb_username", $scope.cb_username) # ##^ ass1gnment -3
        p_cb_password = store_user_var("cb_password", $scope.cb_password) # ##^ ass1gnment -3
        p_cb_name = store_user_var("cb_name", $scope.cb_name) # ##^ ass1gnment -3
        p_cb_server = store_user_var("cb_server", $scope.cb_server) # ##^ ass1gnment -3
        p_show_settings = store_user_var("show_settings", $scope.show_settings) # ##^ ass1gnment -3
        p_show_debug = store_user_var("show_debug", $scope.show_debug) # ##^ ass1gnment -3

        $q.all([p_cb_folder, p_cb_username, p_cb_password, p_cb_name, p_cb_server, p_show_settings, p_show_debug]).then(# ##^ resolve method body -3
            -> # ##^ resolve result 2 -3
                utils.force_digest($scope) # ##^  -3

            (err) -> # ##^ resolve func
                warning "cryptobox.cf:415", err # ##^  -3
        ) # ##^ resolve func stopped

    $scope.file_input_change = (f) -> # ##^ funct1on def nested somewhere -3
        $scope.cb_folder_text = f[0].path # ##^ ass1gnment on scope -3
        $scope.form_change() # ##^  -3

    run_command = (command_name, command_arguments) -> # ##^ funct1on def nested after keyword on prev1ous scope -3
        client = get_rpc_client() # ##^ ass1gnment -3
        p = $q.defer() # ##^ ass1gnment -3
        client.methodCall command_name, command_arguments, (error, value) -> # ##^ anonymousfunct1on -3
            if exist(error) # ##^  1f statement -2
                ca_str = "" # ##^ ass1gnment -2

                bsca = (i) -> # ##^ funct1on def nested after ass1gnement -2
                    if _.isObject(i) # ##^  1f statement -1
                        _.each(_.keys(i), (k) -> # ##^ anonymousfunct1on -1
                            ca_str = ca_str + k + ":" + i[k] + "|" # ##^ ass1gnment -1
                        ) # ##^  -1
                    else # ##^  -1
                        ca_str = ca_str + i # ##^ ass1gnment -1
                _.each(command_arguments, bsca) # ##^  -1
                add_output(command_name + " " + ca_str + " " + error) # ##^ funct1on call -1
                p.reject(error) # ##^  -1
                utils.force_digest($scope) # ##^  -1
            else # ##^  -1
                p.resolve(value) # ##^  -1
                utils.force_digest($scope) # ##^  -1
        p.promise # ##^  -1

    $scope.file_downloads = [] # ##^ ass1gnment prev scope on scope -1
    $scope.file_uploads = [] # ##^ ass1gnment on scope -1
    $scope.dir_del_server = [] # ##^ ass1gnment on scope -1
    $scope.dir_make_local = [] # ##^ ass1gnment on scope -1
    $scope.dir_make_server = [] # ##^ ass1gnment on scope -1
    $scope.dir_del_local = [] # ##^ ass1gnment on scope -1
    $scope.file_del_local = [] # ##^ ass1gnment on scope -1
    $scope.file_del_server = [] # ##^ ass1gnment on scope -1

    cryptobox_locked_status_change = => # ##^ funct1on def nested after ass1gnement after keyword -1
        run_command("get_cryptobox_lock_status", []).then(# ##^ resolve method body -1
            (r) => # ##^ resolve result 2 -1
                $scope.cryptobox_locked = r # ##^ ass1gnment on scope -1

                if $scope.cryptobox_locked # ##^  1f statement on same scope after ass1gnement 0
                    tray.icon = "images/icon-client-signed-out.png" # ##^ ass1gnment 0
                    $scope.disable_encrypt_button = true # ##^ ass1gnment on scope 0
                    $scope.disable_decrypt_button = false # ##^ ass1gnment on scope 0
                    $scope.disable_sync_button = true # ##^ ass1gnment on scope 0
                    encrypt_tray_item.enabled = false # ##^ ass1gnment 0
                else # ##^  0
                    tray.icon = "images/icon-client-signed-in-idle.png" # ##^ ass1gnment 0
                    $scope.disable_encrypt_button = false # ##^ ass1gnment on scope 0
                    $scope.disable_decrypt_button = true # ##^ ass1gnment on scope 0
                    $scope.disable_sync_button = false # ##^ ass1gnment on scope 0
                    encrypt_tray_item.enabled = true # ##^ ass1gnment 0

            (e) -> # ##^ resolve func
                warning "cryptobox.cf:473", e # ##^  0
        ) # ##^ resolve func stopped

    get_sync_state = -> # ##^ funct1on def nested somewhere 0
        p = $q.defer() # ##^ ass1gnment 0
        option = # ##^  0
            dir: $scope.cb_folder_text # ##^ member 1n1t1al1zat1on 0
            username: $scope.cb_username # ##^ member 1n1t1al1zat1on 0
            password: $scope.cb_password # ##^  0
            cryptobox: $scope.cb_name # ##^ member 1n1t1al1zat1on 0
            server: $scope.cb_server # ##^ member 1n1t1al1zat1on 0
            check: "1" # ##^ member 1n1t1al1zat1on 0

        run_command("cryptobox_command", [option]).then(# ##^ resolve method body 0
            (res) -> # ##^ resolve result 2 0
                p.resolve() # ##^  0

            (err) -> # ##^ resolve func
                p.reject(err) # ##^  0
        ) # ##^ resolve func stopped
        p.promise # ##^  0

    update_sync_state = (smem) -> # ##^ funct1on def nested somewhere 0
        $scope.file_downloads = smem.file_downloads # ##^ ass1gnment on scope 0
        $scope.file_uploads = smem.file_uploads # ##^ ass1gnment on scope 0
        $scope.dir_del_server = smem.dir_del_server # ##^ ass1gnment on scope 0
        $scope.dir_make_local = smem.dir_make_local # ##^ ass1gnment on scope 0
        $scope.dir_make_server = smem.dir_make_server # ##^ ass1gnment on scope 0
        $scope.dir_del_local = smem.dir_del_local # ##^ ass1gnment on scope 0
        $scope.file_del_local = smem.file_del_local # ##^ ass1gnment on scope 0

    get_all_smemory = -> # ##^ funct1on def nested after ass1gnement after keyword on prev1ous scope 0
        run_command("get_all_smemory", []).then(# ##^ resolve method body 0
            (r) -> # ##^ resolve result 2 0
                get_progress(r.progress, r.item_progress) # ##^  0

                #get_working_state() # ##^ comment -> funct1on call 0
                #cryptobox_locked_status_change() # ##^ comment -> funct1on call 0
                update_sync_state(r) # ##^ funct1on call 0
                utils.force_digest($scope) # ##^  0

            (e) -> # ##^ resolve func
                warning "cryptobox.cf:515", e # ##^  0
        ) # ##^ resolve func stopped

    get_option = -> # ##^ funct1on def nested somewhere 0
        option = # ##^  0
            dir: $scope.cb_folder_text # ##^ member 1n1t1al1zat1on 0
            username: $scope.cb_username # ##^ member 1n1t1al1zat1on 0
            password: $scope.cb_password # ##^  0
            cryptobox: $scope.cb_name # ##^ member 1n1t1al1zat1on 0
            server: $scope.cb_server # ##^ member 1n1t1al1zat1on 0

        return option # ##^  wh1tespace |  0

    $scope.sync_btn = -> # ##^ funct1on def nested after keyword on scope 0
        option = get_option() # ##^ ass1gnment 0
        option.encrypt = true # ##^ ass1gnment 0
        option.clear = "0" # ##^ ass1gnment 0
        option.sync = "0" # ##^ ass1gnment 0

        run_command("cryptobox_command", [option]).then(# ##^ resolve method body 0
            (res) -> # ##^ resolve result 2 0
                pass # ##^  0

            (err) -> # ##^ resolve func
                warning "cryptobox.cf:539", err # ##^  0
        ) # ##^ resolve func stopped

    $scope.encrypt_btn = -> # ##^ funct1on def nested somewhere 0
        option = get_option() # ##^ ass1gnment 0
        option.encrypt = true # ##^ ass1gnment 0
        option.remove = true # ##^ ass1gnment 0
        option.sync = false # ##^ ass1gnment 0

        run_command("cryptobox_command", [option]).then(# ##^ resolve method body 0
            (res) -> # ##^ resolve result 2 0
                add_output(res) # ##^ funct1on call 0

            (err) -> # ##^ resolve func
                warning "cryptobox.cf:553", err # ##^  0
        ) # ##^ resolve func stopped

    $scope.decrypt_btn = -> # ##^ funct1on def nested somewhere 0
        option = get_option() # ##^ ass1gnment 0
        option.decrypt = true # ##^ ass1gnment 0
        option.clear = false # ##^ ass1gnment 0

        run_command("cryptobox_command", [option]).then(# ##^ resolve method body 0
            (res) -> # ##^ resolve result 2 0
                add_output(res) # ##^ funct1on call 0
                add_output("done decrypting") # ##^ funct1on call 0

            (err) -> # ##^ resolve func
                warning "cryptobox.cf:567", err # ##^  0
        ) # ##^ resolve func stopped

    $scope.tree_sequence = null # ##^ ass1gnment prev scope on scope 0

    get_tree_sequence = -> # ##^ funct1on def nested after ass1gnement 0
        option = get_option() # ##^ ass1gnment 0
        option.treeseq = true # ##^ ass1gnment 0

        run_command("cryptobox_command", [option]).then(# ##^ resolve method body 0
            (res) -> # ##^ resolve result 2 0
                add_output("tree_seq", res) # ##^ funct1on call 0
                $scope.tree_sequence = res # ##^ ass1gnment on scope 0

            (err) -> # ##^ resolve func
                warning "cryptobox.cf:582", err # ##^  0
        ) # ##^ resolve func stopped

    $scope.open_folder = -> # ##^ funct1on def nested somewhere 0
        run_command("do_open_folder", [$scope.cb_folder_text, $scope.cb_name]) # ##^  0

    $scope.open_website = -> # ##^ funct1on def nested somewhere 0
        gui.Shell.openExternal($scope.cb_server+$scope.cb_name) # ##^  0

    trayactions = new gui.Menu() # ##^ ass1gnment prev scope 0
    tray.menu = trayactions # ##^ ass1gnment 0

    add_traymenu_item = (label, icon, method) => # ##^ funct1on def nested after ass1gnement 0
        trayitem = new gui.MenuItem(# ##^ ass1gnment 0
            type: "normal" # ##^ member 1n1t1al1zat1on 0
            label: label # ##^ member 1n1t1al1zat1on 0
            icon: icon # ##^ member 1n1t1al1zat1on 0
            click: method # ##^ member 1n1t1al1zat1on 0
        ) # ##^  0
        trayactions.append trayitem # ##^  0
        return trayitem # ##^ retrn |  0

    add_checkbox_traymenu_item = (label, icon, method, enabled) => # ##^ funct1on def nested after keyword on prev1ous scope 0
        trayitem_cb = new gui.MenuItem(# ##^ ass1gnment 0
            type: "checkbox" # ##^ member 1n1t1al1zat1on 0
            label: label # ##^ member 1n1t1al1zat1on 0
            icon: icon # ##^ member 1n1t1al1zat1on 0
            click: method # ##^ member 1n1t1al1zat1on 0
            checked: enabled # ##^ member 1n1t1al1zat1on 0
        ) # ##^  0
        trayactions.append trayitem_cb # ##^  0
        return trayitem_cb # ##^ retrn |  0

    add_traymenu_seperator = () => # ##^ funct1on def nested after keyword on prev1ous scope 0
        traymenubaritem = new gui.MenuItem(# ##^ ass1gnment 0
            type: "separator" # ##^ member 1n1t1al1zat1on 0
        ) # ##^  0
        trayactions.append traymenubaritem # ##^  0
        return traymenubaritem # ##^ retrn |  0

    menubar = new gui.Menu(# ##^ ass1gnment prev scope 0
        type: 'menubar' # ##^ member 1n1t1al1zat1on 0
    ) # ##^  0
    actions = new gui.Menu() # ##^ ass1gnment 0

    add_menu_item = (label, icon, method) => # ##^ funct1on def nested after ass1gnement 0
        menubaritem = new gui.MenuItem(# ##^ ass1gnment 0
            type: "normal" # ##^ member 1n1t1al1zat1on 0
            label: label # ##^ member 1n1t1al1zat1on 0
            icon: icon # ##^ member 1n1t1al1zat1on 0
            click: method # ##^ member 1n1t1al1zat1on 0
        ) # ##^  0
        actions.append menubaritem # ##^  0
        return menubaritem # ##^ retrn |  0

    add_checkbox_menu_item = (label, icon, method, enabled) => # ##^ funct1on def nested after keyword on prev1ous scope 0
        menubaritem_cb = new gui.MenuItem(# ##^ ass1gnment 0
            type: "checkbox" # ##^ member 1n1t1al1zat1on 0
            label: label # ##^ member 1n1t1al1zat1on 0
            icon: icon # ##^ member 1n1t1al1zat1on 0
            click: method # ##^ member 1n1t1al1zat1on 0
            checked: enabled # ##^ member 1n1t1al1zat1on 0
        ) # ##^  0
        actions.append menubaritem_cb # ##^  0
        return menubaritem_cb # ##^ retrn |  0

    add_menu_seperator = () => # ##^ funct1on def nested after keyword on prev1ous scope 0
        menubaritem = new gui.MenuItem(# ##^ ass1gnment 0
            type: "separator" # ##^ member 1n1t1al1zat1on 0
        ) # ##^  0
        actions.append menubaritem # ##^  0

    $scope.toggle_settings = -> # ##^ funct1on def nested somewhere 0
        $scope.show_settings = !$scope.show_settings # ##^ ass1gnment on scope 0
        $scope.form_change() # ##^  0

    settings_menubaritem = add_checkbox_menu_item("Settings", "images/cog.png", $scope.toggle_settings, $scope.show_settings) # ##^ ass1gnment prev scope 0
    settings_menubar_tray = add_checkbox_traymenu_item("Settings", "images/cog.png", $scope.toggle_settings, $scope.show_settings) # ##^ ass1gnment 0

    update_menu_checks = => # ##^ funct1on def nested after ass1gnement 0
        settings_menubaritem.checked = $scope.show_settings # ##^ ass1gnment 0
        settings_menubar_tray.checked = $scope.show_settings # ##^ ass1gnment 0
    $scope.$watch "show_settings", update_menu_checks # ##^ watch def 0
    add_menu_seperator() # ##^ funct1on call 0
    add_traymenu_seperator() # ##^ funct1on call 0
    add_menu_item("Encrypt local", "images/lock.png", $scope.encrypt_btn) # ##^  0
    encrypt_tray_item = add_traymenu_item("Encrypt local", "images/lock.png", $scope.encrypt_btn) # ##^ ass1gnment 0
    add_menu_item("Decrypt local", "images/unlock.png", $scope.decrypt_btn) # ##^  0
    add_traymenu_item("Decrypt local", "images/unlock.png", $scope.decrypt_btn) # ##^  0
    winmain.menu = menubar # ##^ ass1gnment 0
    winmain.menu.insert(new gui.MenuItem({ label: 'Actions', submenu: actions}), 1); # ##^  0
    $scope.disable_encrypt_button = false # ##^ ass1gnment on scope 0
    $scope.disable_decrypt_button = false # ##^ ass1gnment on scope 0
    $scope.disable_sync_button = false # ##^ ass1gnment on scope 0
    second_counter = 0 # ##^ ass1gnment 0

    second_interval = => # ##^ funct1on def nested after ass1gnement 0
        second_counter += 1 # ##^ ass1gnment 0

        _.defer(update_output) # ##^ deferred call 0

        _.defer(get_all_smemory) # ##^ deferred call 0
        if second_counter % 10 == 0 # ##^  1f statement on same scope 1
            _.defer(ping_client) # ##^ deferred call 1

        if second_counter % 30 == 0 # ##^  1f statement scope change 1
            _.defer(get_tree_sequence) # ##^ deferred call 1

    start_after_second = => # ##^ scope change -1
        utils.set_interval("cryptobox.cf:691", second_interval, 1000, "second_intervalADDTYPES") # ##^  -1

        _.defer(get_motivation) # ##^ deferred call -1

        _.defer(get_tree_sequence) # ##^ deferred call -1

        _.defer(start_watch) # ##^ deferred call -1

        _.defer(try_get_sync_state) # ##^ deferred call -1
    utils.set_time_out("cryptobox.cf:700", start_after_second, 1000) # ##^  -1

 # ##^ global_class_declare -1

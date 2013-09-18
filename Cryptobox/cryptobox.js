// Generated by CoffeeScript 1.6.3
var child_process, cryptobox_ctrl, gui, path, print, winmain, xmlrpc,
  __slice = [].slice;

child_process = require("child_process");

path = require("path");

gui = require('nw.gui');

xmlrpc = require('xmlrpc');

winmain = gui.Window.get();

print = function() {
  var len_others, msg, others;
  msg = arguments[0], others = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
  len_others = _.size(others);
  switch (len_others) {
    case 0:
      return typeof console !== "undefined" && console !== null ? console.log(msg) : void 0;
    case 1:
      return typeof console !== "undefined" && console !== null ? console.log(msg + " " + others[0]) : void 0;
    case 2:
      return typeof console !== "undefined" && console !== null ? console.log(msg + " " + others[0] + " " + others[1]) : void 0;
    case 3:
      return typeof console !== "undefined" && console !== null ? console.log(msg + " " + others[0] + " " + others[1] + " " + others[2]) : void 0;
    case 4:
      return typeof console !== "undefined" && console !== null ? console.log(msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3]) : void 0;
    case 5:
      return typeof console !== "undefined" && console !== null ? console.log(msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3] + " " + others[4]) : void 0;
    default:
      return typeof console !== "undefined" && console !== null ? console.log(others, msg) : void 0;
  }
};

angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"]);

cryptobox_ctrl = function($scope, $q, memory, utils) {
  var add_output, cba_main, clear_msg_buffer, cmd_to_run, get_progress, get_rpc_client, get_user_var, get_val, output, ping_client, progress_bar, reset_progress, run_command, set_data_user_config, set_data_user_config_once, set_output_buffers, set_user_var_scope, set_val, spawn, start_interval, start_process, start_process_once, store_user_var, update_output,
    _this = this;
  print("cryptobox.cf:28", "cryptobox_ctrl");
  get_rpc_client = function() {
    var clientOptions;
    clientOptions = {
      host: "localhost",
      port: 8654,
      path: "/RPC2"
    };
    return xmlrpc.createClient(clientOptions);
  };
  set_val = function(k, v) {
    var client, p;
    p = $q.defer();
    client = get_rpc_client();
    client.methodCall("set_val", [k, v], function(error, value) {
      if (exist(error)) {
        p.reject(error);
      }
      ({
        "else": utils.exist_truth(value) ? (p.resolve("set_val " + k + ":" + v), utils.force_digest($scope)) : (p.reject("error set_val"), utils.force_digest($scope))
      });
      return utils.force_digest($scope);
    });
    return p.promise;
  };
  get_val = function(k) {
    var client, p;
    p = $q.defer();
    client = get_rpc_client();
    client.methodCall("get_val", [k], function(error, value) {
      if (exist(error)) {
        p.reject(error);
        return utils.force_digest($scope);
      } else {
        p.resolve(value);
        return utils.force_digest($scope);
      }
    });
    return p.promise;
  };
  $scope.cba_version = 0.1;
  memory.set("g_running", true);
  cba_main = null;
  set_output_buffers = function(cba_main_proc) {
    if (exist(cba_main_proc.stdout)) {
      cba_main_proc.stdout.on("data", function(data) {
        return add_output("stdout:" + data);
      });
    }
    if (exist(cba_main_proc.stderr)) {
      return cba_main_proc.stderr.on("data", function(data) {
        return add_output("stderr:" + data);
      });
    }
  };
  winmain.on('close', $scope.on_exit);
  spawn = require("child_process").spawn;
  cmd_to_run = path.join(process.cwd(), "commands");
  cmd_to_run = path.join(cmd_to_run, "cba_main");
  output = [];
  clear_msg_buffer = function() {
    output = [];
    return utils.force_digest($scope);
  };
  $scope.debug_btn = function() {
    clear_msg_buffer();
    return require('nw.gui').Window.get().showDevTools();
  };
  update_output = function() {
    var make_stream, msgs;
    msgs = "";
    make_stream = function(msg) {
      return msgs += msg + "\n";
    };
    _.each(output, make_stream);
    $scope.cmd_output = msgs;
    return utils.force_digest($scope);
  };
  utils.set_interval("cryptobox.cf:120", update_output, 100, "update_output");
  add_output = function(msgs) {
    var add_msg;
    add_msg = function(msg) {
      if (msg.indexOf != null) {
        if (msg.indexOf("Error") === -1) {
          if (msg.indexOf("POST /RPC2") > 0) {
            return;
          }
        }
      }
      if (msg.replace != null) {
        msg = msg.replace("stderr:", "");
        msg.replace("\n", "");
        msg = msg.trim();
      }
      if (utils.exist(msg)) {
        return output.unshift(utils.format_time(utils.get_local_time()) + ": " + msg);
      }
    };
    if ((msgs != null ? msgs.split : void 0) != null) {
      _.each(msgs.split("\n"), add_msg);
    } else if (msgs === "true") {
      pass;
    } else if (msgs === "false") {
      pass;
    } else if (msgs === true) {
      pass;
    } else if (msgs === false) {
      pass;
    } else {
      if (msgs != null) {
        output.push(utils.format_time(utils.get_local_time()) + ": " + msgs);
      }
    }
    return update_output();
  };
  ping_client = function() {
    var client;
    utils.force_digest($scope);
    client = get_rpc_client();
    return client.methodCall("last_ping", [], function(error, value) {
      if (utils.exist(error)) {
        cba_main = spawn(cmd_to_run, [""]);
        return set_output_buffers(cba_main);
      }
    });
  };
  start_interval = function() {
    return utils.set_interval("cryptobox.cf:161", ping_client, 5000, "ping_client");
  };
  utils.set_time_out("cryptobox.cf:163", start_interval, 1000);
  start_process = function() {
    var client;
    print("cryptobox.cf:166", "start_process");
    client = get_rpc_client();
    return client.methodCall("force_stop", [], function(e, v) {
      print("cryptobox.cf:169", "force_stop", e, v);
      if (utils.exist(v)) {
        print("cryptobox.cf:171", "killed existing deamon");
      } else {
        print("cryptobox.cf:173", "starting deamon");
      }
      cba_main = spawn(cmd_to_run, [""]);
      return set_output_buffers(cba_main);
    });
  };
  start_process_once = _.once(start_process);
  start_process_once();
  progress_bar = 0;
  $scope.get_progress = function() {
    return {
      width: progress_bar + "%"
    };
  };
  reset_progress = function() {
    var client;
    client = get_rpc_client();
    return client.methodCall("reset_progress", [], function(e, v) {
      if (utils.exist(e)) {
        return print("cryptobox.cf:189", e);
      }
    });
  };
  get_progress = function() {
    var client;
    client = get_rpc_client();
    client.methodCall("get_progress", [], function(e, v) {
      if (utils.exist(e)) {
        print("cryptobox.cf:195", e, v);
      } else {
        progress_bar = parseInt(v, 10);
      }
      if (progress_bar > 0) {
        print("cryptobox.cf:200", "progress", e, v);
      }
      if (progress_bar >= 100) {
        return utils.set_time_out("cryptobox.cf:203", reset_progress, 1);
      }
    });
    return utils.force_digest($scope);
  };
  utils.set_interval("cryptobox.cf:207", get_progress, 1000, "get_progress");
  store_user_var = function(k, v) {
    var db, p, record;
    p = $q.defer();
    db = new PouchDB('cb_userinfo');
    if (!exist(db)) {
      p.reject("no db");
    } else {
      record = {
        _id: k,
        value: v
      };
      db.get(k, function(e, d) {
        if (exist(d)) {
          if (exist(d._rev)) {
            record._rev = d._rev;
          }
        }
        return db.put(record, function(e, r) {
          if (exist(e)) {
            p.reject(e);
            utils.force_digest($scope);
          }
          if (exist(r)) {
            if (exist_truth(r.ok)) {
              p.resolve(true);
              return utils.force_digest($scope);
            } else {
              p.reject(r);
              return utils.force_digest($scope);
            }
          } else {
            p.reject("store_user_var generic error");
            return utils.force_digest($scope);
          }
        });
      });
    }
    return p.promise;
  };
  get_user_var = function(k) {
    var db, p;
    p = $q.defer();
    db = new PouchDB('cb_userinfo');
    if (!exist(db)) {
      p.reject("no db");
    } else {
      db.get(k, function(e, d) {
        if (exist(e)) {
          return p.reject(e);
        } else {
          if (exist(d)) {
            print("cryptobox.cf:253", k, d.value);
            p.resolve(d.value);
            return utils.force_digest($scope);
          } else {
            return p.reject();
          }
        }
      });
    }
    return p.promise;
  };
  set_user_var_scope = function(name, scope_name) {
    return get_user_var(name).then(function(v) {
      if (exist(scope_name)) {
        return $scope[scope_name] = v;
      } else {
        return $scope[name] = v;
      }
    }, function(err) {
      return print("cryptobox.cf:272", err);
    });
  };
  set_data_user_config = function() {
    set_user_var_scope("cb_folder", "cb_folder_text");
    set_user_var_scope("cb_username");
    set_user_var_scope("cb_password");
    set_user_var_scope("cb_name");
    set_user_var_scope("cb_server");
    set_user_var_scope("show_settings");
    if (!utils.exist($scope.cb_username)) {
      $scope.show_settings = true;
    }
    if (!utils.exist($scope.cb_server)) {
      return $scope.cb_server = "http://127.0.0.1:8000/";
    }
  };
  set_data_user_config_once = _.once(set_data_user_config);
  set_data_user_config_once();
  $scope.$on("$includeContentLoaded", function(event) {
    return typeof console !== "undefined" && console !== null ? console.log(event) : void 0;
  });
  $scope.form_change = function() {
    var p_cb_folder, p_cb_name, p_cb_password, p_cb_server, p_cb_username, p_show_settings;
    p_cb_folder = store_user_var("cb_folder", $scope.cb_folder_text);
    p_cb_username = store_user_var("cb_username", $scope.cb_username);
    p_cb_password = store_user_var("cb_password", $scope.cb_password);
    p_cb_name = store_user_var("cb_name", $scope.cb_name);
    p_cb_server = store_user_var("cb_server", $scope.cb_server);
    p_show_settings = store_user_var("show_settings", $scope.show_settings);
    return $q.all([p_cb_folder, p_cb_username, p_cb_password, p_cb_name, p_cb_server, p_show_settings]).then(function() {
      return utils.force_digest($scope);
    }, function(err) {
      return print("cryptobox.cf:310", err);
    });
  };
  $scope.file_input_change = function(f) {
    $scope.cb_folder_text = f[0].path;
    return $scope.form_change();
  };
  run_command = function(command_name, command_arguments) {
    var client, p;
    client = get_rpc_client();
    p = $q.defer();
    print("cryptobox.cf:320", "run_command", cmd_to_run);
    client.methodCall(command_name, command_arguments, function(error, value) {
      if (exist(error)) {
        p.reject(error);
        return utils.force_digest($scope);
      } else {
        p.resolve(value);
        return utils.force_digest($scope);
      }
    });
    return p.promise;
  };
  $scope.sync_btn = function() {
    var option;
    clear_msg_buffer();
    add_output("syncing data");
    option = {
      dir: $scope.cb_folder_text,
      username: $scope.cb_username,
      password: $scope.cb_password,
      cryptobox: $scope.cb_name,
      server: $scope.cb_server,
      encrypt: true,
      clear: "0",
      sync: "1"
    };
    return run_command("cryptobox_command", [option]).then(function(res) {
      if (!utils.exist_truth(res)) {
        return add_output(res);
      } else {
        return add_output("done syncing");
      }
    }, function(err) {
      return add_output(err);
    });
  };
  $scope.check_btn = function() {
    var option;
    clear_msg_buffer();
    add_output("checking changes");
    option = {
      dir: $scope.cb_folder_text,
      username: $scope.cb_username,
      password: $scope.cb_password,
      cryptobox: $scope.cb_name,
      server: $scope.cb_server,
      check: "1"
    };
    return run_command("cryptobox_command", [option]).then(function(res) {
      add_output(res);
      return add_output("check done");
    }, function(err) {
      return add_output(err);
    });
  };
  $scope.encrypt_btn = function() {
    var option;
    clear_msg_buffer();
    add_output("sync encrypt remove data");
    option = {
      dir: $scope.cb_folder_text,
      username: $scope.cb_username,
      password: $scope.cb_password,
      cryptobox: $scope.cb_name,
      server: $scope.cb_server,
      encrypt: true,
      remove: true,
      sync: false
    };
    return run_command("cryptobox_command", [option]).then(function(res) {
      add_output(res);
      return add_output("done encrypting");
    }, function(err) {
      return add_output(err);
    });
  };
  return $scope.decrypt_btn = function() {
    var option;
    clear_msg_buffer();
    add_output("decrypt local data");
    option = {
      dir: $scope.cb_folder_text,
      username: $scope.cb_username,
      password: $scope.cb_password,
      cryptobox: $scope.cb_name,
      server: $scope.cb_server,
      decrypt: true,
      clear: false
    };
    return run_command("cryptobox_command", [option]).then(function(res) {
      add_output(res);
      return add_output("done decrypting");
    }, function(err) {
      return add_output(err);
    });
  };
};

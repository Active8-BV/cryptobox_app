// Generated by CoffeeScript 1.6.3
var child_process, cryptobox_ctrl, fs, gui, path, print, tray, watch,
  __slice = [].slice;

child_process = require("child_process");

path = require("path");

fs = require("fs");

gui = require('nw.gui');

watch = require("watch");

require('nw.gui').Window.get().showDevTools();

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

tray = new gui.Tray({
  icon: "images/icon-client-signed-in-idle.png"
});

angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"]);

cryptobox_ctrl = function($scope, $q, memory, utils) {
  var actions, add_checkbox_menu_item, add_checkbox_traymenu_item, add_menu_item, add_menu_seperator, add_output, add_traymenu_item, add_traymenu_seperator, cba_main, change_workingstate, check_result, cmd_to_run, cryptobox_locked_status_change, encrypt_tray_item, get_all_smemory, get_motivation, get_option, get_sync_state, get_user_var, getting_sync_state_false, last_progress_bar, last_progress_bar_item, loop_for_results, menubar, output, ping_client, progress_checker, run_command, second_counter, second_interval, set_data_user_config, set_data_user_config_once, set_output_buffers, set_user_var_scope, settings_menubar_tray, settings_menubaritem, spawn, start_after_second, start_process, start_process_once, start_watch, store_user_var, trayactions, try_get_sync_state, update_menu_checks, update_output, update_sync_state, warning, winmain,
    _this = this;
  print("cryptobox.cf:38", "cryptobox_ctrl");
  $scope.cba_version = 0.1;
  memory.set("g_running", true);
  cba_main = null;
  $scope.succesfull_kill = true;
  $scope.quitting = false;
  $scope.on_exit = function() {
    $scope.quitting = true;
    return gui.App.quit();
  };
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
  winmain = gui.Window.get();
  winmain.on('close', $scope.on_exit);
  spawn = require("child_process").spawn;
  cmd_to_run = path.join(process.cwd(), "commands");
  cmd_to_run = path.join(cmd_to_run, "cba_main");
  cmd_to_run = "/bin/date";
  output = [];
  $scope.clear_msg_buffer = function() {
    output = [];
    return utils.force_digest($scope);
  };
  $scope.debug_btn = function() {
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
  warning = function(ln, w) {
    if (w != null) {
      if ((w != null ? w.trim : void 0) != null) {
        w = w.trim();
      }
    } else {
      return;
    }
    if (utils.exist(w)) {
      if (w.faultString != null) {
        return add_output(w.faultString);
      } else if (w.message) {
        return add_output(w.message);
      } else {
        return add_output(w);
      }
    }
  };
  $scope.motivation = null;
  get_motivation = function() {
    if (!utils.exist($scope.motivation)) {
      return run_command("get_motivation", "").then(function(motivation) {
        print("cryptobox.cf:133", motivation);
        return $scope.motivation = motivation;
      }, function(error) {
        return print("cryptobox.cf:137", error);
      });
    }
  };
  ping_client = function() {
    run_command("ping_client", "").then(function(res) {
      return print("cryptobox.cf:145", res);
    }, function(err) {
      return print("cryptobox.cf:148", err);
    });
    utils.force_digest($scope);
    return print("cryptobox.cf:151", "ping_client");
  };
  $scope.rpc_server_started = false;
  start_process = function() {
    print("cryptobox.cf:156", "start_process");
    cba_main = spawn(cmd_to_run, [""]);
    return set_output_buffers(cba_main);
  };
  start_process_once = _.once(start_process);
  print("cryptobox.cf:161", cmd_to_run);
  start_process_once();
  $scope.progress_bar = 0;
  $scope.progress_bar_item = 0;
  $scope.get_progress_item_show = function() {
    return $scope.progress_bar_item !== 0;
  };
  $scope.get_progress_item = function() {
    return {
      width: $scope.progress_bar_item + "%"
    };
  };
  $scope.get_progress = function() {
    return {
      width: $scope.progress_bar + "%"
    };
  };
  $scope.lock_buttons = true;
  $scope.get_lock_buttons = function() {
    return $scope.lock_buttons;
  };
  last_progress_bar = 0;
  last_progress_bar_item = 0;
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
    var p;
    p = $q.defer();
    get_user_var(name).then(function(v) {
      if (exist(scope_name)) {
        $scope[scope_name] = v;
      } else {
        $scope[name] = v;
      }
      return p.resolve();
    }, function(err) {
      warning("cryptobox.cf:249", err);
      return p.reject();
    });
    return p.promise;
  };
  $scope.show_settings = false;
  $scope.show_debug = false;
  $scope.toggle_debug = function() {
    $scope.show_debug = !$scope.show_debug;
    return $scope.form_change();
  };
  $scope.got_folder_text = false;
  $scope.got_cb_name = false;
  $scope.getting_sync_state = false;
  getting_sync_state_false = function() {
    add_output("sync state retrieved");
    return $scope.getting_sync_state = false;
  };
  try_get_sync_state = function() {
    if ($scope.working) {
      add_output("try_get_sync_state denied, working");
      return;
    }
    if (!$scope.getting_sync_state) {
      $scope.getting_sync_state = true;
      add_output("try_get_sync_state");
      return get_sync_state().then(function(r) {
        return utils.set_time_out("cryptobox.cf:281", getting_sync_state_false, 1000);
      }, function(e) {
        add_output("sync state error", e);
        utils.set_time_out("cryptobox.cf:286", getting_sync_state_false, 1000);
        return warning("cryptobox.cf:287", e);
      });
    } else {
      return add_output("sync state in progress");
    }
  };
  $scope.file_watch_started = false;
  start_watch = function() {
    var watch_path;
    if (!$scope.file_watch_started) {
      if ($scope.got_folder_text && $scope.got_cb_name) {
        watch_path = path.join($scope.cb_folder_text, $scope.cb_name);
        if (fs.existsSync(watch_path)) {
          $scope.file_watch_started = true;
          return watch.watchTree(watch_path, function(f, curr, prev) {
            if (!String(f).contains("memory.pickle")) {
              if (typeof f === "object" && prev === null && curr === null) {
                return;
              }
              add_output("local filechange", f);
              if (prev === null) {
                return try_get_sync_state();
              } else if (curr.nlink === 0) {
                return try_get_sync_state();
              } else {
                return try_get_sync_state();
              }
            }
          });
        }
      }
    }
  };
  set_data_user_config = function() {
    set_user_var_scope("cb_folder", "cb_folder_text").then(function() {
      return $scope.got_folder_text = true;
    });
    set_user_var_scope("cb_username");
    set_user_var_scope("cb_password");
    set_user_var_scope("cb_name").then(function() {
      if (!utils.exist($scope.cb_name)) {
        $scope.cb_name = "active8";
      }
      return $scope.got_cb_name = true;
    });
    set_user_var_scope("cb_server").then(function() {
      if (!utils.exist($scope.cb_folder_text)) {
        $scope.cb_folder_text = "https://www.cryptobox.nl/";
        return $scope.cb_folder = $scope.cb_folder_text;
      }
    });
    set_user_var_scope("show_settings");
    set_user_var_scope("show_debug");
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
    var p_cb_folder, p_cb_name, p_cb_password, p_cb_server, p_cb_username, p_show_debug, p_show_settings;
    p_cb_folder = store_user_var("cb_folder", $scope.cb_folder_text);
    p_cb_username = store_user_var("cb_username", $scope.cb_username);
    p_cb_password = store_user_var("cb_password", $scope.cb_password);
    p_cb_name = store_user_var("cb_name", $scope.cb_name);
    p_cb_server = store_user_var("cb_server", $scope.cb_server);
    p_show_settings = store_user_var("show_settings", $scope.show_settings);
    p_show_debug = store_user_var("show_debug", $scope.show_debug);
    return $q.all([p_cb_folder, p_cb_username, p_cb_password, p_cb_name, p_cb_server, p_show_settings, p_show_debug]).then(function() {
      return utils.force_digest($scope);
    }, function(err) {
      return warning("cryptobox.cf:367", err);
    });
  };
  $scope.file_input_change = function(f) {
    $scope.cb_folder_text = f[0].path;
    return $scope.form_change();
  };
  check_result = function(name) {
    var cmd_folder, data, result_path;
    cmd_folder = path.join(process.cwd(), "cba_commands");
    result_path = path.join(cmd_folder, name + ".result");
    if (fs.existsSync(result_path)) {
      data = fs.readFileSync(result_path);
      data = JSON.parse(data);
      if (data != null) {
        if (data["result"] != null) {
          return data["result"];
        }
      }
    }
    return null;
  };
  loop_for_results = function(name) {
    var p, res;
    p = $q.defer();
    print("cryptobox.cf:390", "loop results");
    res = check_result(name);
    if (!res) {
      setTimeout(loop_for_results, 1000, name);
    } else {
      p.resolve(res);
    }
    return p.promise;
  };
  run_command = function(name, data) {
    var cmd_folder, cmd_path, fout, p, result_path;
    if ("name" !== "get_motivation") {
      p = $q.defer();
      p.resolve(name);
      return p.promise;
    }
    cmd_folder = path.join(process.cwd(), "cba_commands");
    if (!fs.existsSync(cmd_folder)) {
      fs.mkdirSync(cmd_folder);
    }
    cmd_path = path.join(cmd_folder, name + ".cmd");
    result_path = path.join(cmd_folder, name + ".result");
    if (fs.existsSync(result_path)) {
      fs.unlinkSync(result_path);
    }
    fout = fs.openSync(cmd_path, "w");
    fs.write(fout, JSON.stringify(data));
    return loop_for_results(name);
  };
  $scope.file_downloads = [];
  $scope.file_uploads = [];
  $scope.dir_del_server = [];
  $scope.dir_make_local = [];
  $scope.dir_make_server = [];
  $scope.dir_del_local = [];
  $scope.file_del_local = [];
  $scope.file_del_server = [];
  get_sync_state = function() {
    var option, p;
    p = $q.defer();
    option = {
      dir: $scope.cb_folder_text,
      username: $scope.cb_username,
      password: $scope.cb_password,
      cryptobox: $scope.cb_name,
      server: $scope.cb_server,
      check: "1"
    };
    run_command("cryptobox_command", option).then(function(res) {
      return p.resolve();
    }, function(err) {
      return p.reject(err);
    });
    return p.promise;
  };
  update_sync_state = function(smem) {
    $scope.file_downloads = smem.file_downloads;
    $scope.file_uploads = smem.file_uploads;
    $scope.dir_del_server = smem.dir_del_server;
    $scope.dir_make_local = smem.dir_make_local;
    $scope.dir_make_server = smem.dir_make_server;
    $scope.dir_del_local = smem.dir_del_local;
    return $scope.file_del_local = smem.file_del_local;
  };
  cryptobox_locked_status_change = function(locked) {
    $scope.cryptobox_locked = locked;
    if ($scope.cryptobox_locked) {
      tray.icon = "images/icon-client-signed-out.png";
      $scope.disable_encrypt_button = true;
      $scope.disable_decrypt_button = false;
      $scope.disable_sync_button = true;
      return encrypt_tray_item.enabled = false;
    } else {
      tray.icon = "images/icon-client-signed-in-idle.png";
      $scope.disable_encrypt_button = false;
      $scope.disable_decrypt_button = true;
      $scope.disable_sync_button = false;
      return encrypt_tray_item.enabled = true;
    }
  };
  $scope.working = false;
  change_workingstate = function(wstate) {
    if (utils.exist_truth(wstate)) {
      $scope.lock_buttons = true;
      return $scope.working = true;
    } else {
      if ($scope.lock_buttons) {
        try_get_sync_state();
      }
      $scope.lock_buttons = false;
      return $scope.working = false;
    }
  };
  get_all_smemory = function() {
    var handle_smemory;
    return;
    handle_smemory = function(error, value) {
      if (exist(error)) {
        add_output("get_all_smemory" + " " + error);
        return utils.force_digest($scope);
      } else {
        cryptobox_locked_status_change(utils.exist_truth(value.cryptobox_locked));
        change_workingstate(value.working);
        if (!utils.exist_truth(value.working)) {
          update_sync_state(value);
        }
        utils.force_digest($scope);
        if (utils.exist(value.tree_sequence)) {
          $scope.tree_sequence = value.tree_sequence;
        }
        return utils.force_digest($scope);
      }
    };
    return client.methodCall("get_all_smemory", [], handle_smemory);
  };
  get_option = function() {
    var option;
    option = {
      dir: $scope.cb_folder_text,
      username: $scope.cb_username,
      password: $scope.cb_password,
      cryptobox: $scope.cb_name,
      server: $scope.cb_server
    };
    return option;
  };
  $scope.sync_btn = function() {
    var option;
    option = get_option();
    option.encrypt = true;
    option.clear = "0";
    option.sync = "0";
    return run_command("cryptobox_command", option).then(function(res) {
      return pass;
    }, function(err) {
      return warning("cryptobox.cf:525", err);
    });
  };
  $scope.encrypt_btn = function() {
    var option;
    option = get_option();
    option.encrypt = true;
    option.remove = true;
    option.sync = false;
    return run_command("cryptobox_command", option).then(function(res) {
      return add_output(res);
    }, function(err) {
      return warning("cryptobox.cf:539", err);
    });
  };
  $scope.decrypt_btn = function() {
    var option;
    option = get_option();
    option.decrypt = true;
    option.clear = false;
    return run_command("cryptobox_command", option).then(function(res) {
      add_output(res);
      return add_output("done decrypting");
    }, function(err) {
      return warning("cryptobox.cf:553", err);
    });
  };
  $scope.open_folder = function() {
    return run_command("do_open_folder", [$scope.cb_folder_text, $scope.cb_name]);
  };
  $scope.open_website = function() {
    return gui.Shell.openExternal($scope.cb_server + $scope.cb_name);
  };
  trayactions = new gui.Menu();
  tray.menu = trayactions;
  add_traymenu_item = function(label, icon, method) {
    var trayitem;
    trayitem = new gui.MenuItem({
      type: "normal",
      label: label,
      icon: icon,
      click: method
    });
    trayactions.append(trayitem);
    return trayitem;
  };
  add_checkbox_traymenu_item = function(label, icon, method, enabled) {
    var trayitem_cb;
    trayitem_cb = new gui.MenuItem({
      type: "checkbox",
      label: label,
      icon: icon,
      click: method,
      checked: enabled
    });
    trayactions.append(trayitem_cb);
    return trayitem_cb;
  };
  add_traymenu_seperator = function() {
    var traymenubaritem;
    traymenubaritem = new gui.MenuItem({
      type: "separator"
    });
    trayactions.append(traymenubaritem);
    return traymenubaritem;
  };
  menubar = new gui.Menu({
    type: 'menubar'
  });
  actions = new gui.Menu();
  add_menu_item = function(label, icon, method) {
    var menubaritem;
    menubaritem = new gui.MenuItem({
      type: "normal",
      label: label,
      icon: icon,
      click: method
    });
    actions.append(menubaritem);
    return menubaritem;
  };
  add_checkbox_menu_item = function(label, icon, method, enabled) {
    var menubaritem_cb;
    menubaritem_cb = new gui.MenuItem({
      type: "checkbox",
      label: label,
      icon: icon,
      click: method,
      checked: enabled
    });
    actions.append(menubaritem_cb);
    return menubaritem_cb;
  };
  add_menu_seperator = function() {
    var menubaritem;
    menubaritem = new gui.MenuItem({
      type: "separator"
    });
    return actions.append(menubaritem);
  };
  $scope.toggle_settings = function() {
    $scope.show_settings = !$scope.show_settings;
    return $scope.form_change();
  };
  settings_menubaritem = add_checkbox_menu_item("Settings", "images/cog.png", $scope.toggle_settings, $scope.show_settings);
  settings_menubar_tray = add_checkbox_traymenu_item("Settings", "images/cog.png", $scope.toggle_settings, $scope.show_settings);
  update_menu_checks = function() {
    settings_menubaritem.checked = $scope.show_settings;
    return settings_menubar_tray.checked = $scope.show_settings;
  };
  $scope.$watch("show_settings", update_menu_checks);
  add_menu_seperator();
  add_traymenu_seperator();
  add_menu_item("Encrypt local", "images/lock.png", $scope.encrypt_btn);
  encrypt_tray_item = add_traymenu_item("Encrypt local", "images/lock.png", $scope.encrypt_btn);
  add_menu_item("Decrypt local", "images/unlock.png", $scope.decrypt_btn);
  add_traymenu_item("Decrypt local", "images/unlock.png", $scope.decrypt_btn);
  winmain.menu = menubar;
  winmain.menu.insert(new gui.MenuItem({
    label: 'Actions',
    submenu: actions
  }), 1);
  $scope.disable_encrypt_button = false;
  $scope.disable_decrypt_button = false;
  $scope.disable_sync_button = false;
  second_counter = 0;
  second_interval = function() {
    if ($scope.quitting) {
      print("cryptobox.cf:651", "quitting");
      return;
    }
    start_watch();
    second_counter += 1;
    update_output();
    get_all_smemory();
    if (second_counter % 10 === 0) {
      return ping_client();
    }
  };
  start_after_second = function() {
    get_motivation();
    try_get_sync_state();
    return utils.set_interval("cryptobox.cf:665", second_interval, 1000, "second_interval");
  };
  utils.set_time_out("cryptobox.cf:667", start_after_second, 5000);
  progress_checker = function() {
    var data, fitem_progress, fprogress;
    fprogress = path.join(process.cwd(), "progress");
    fitem_progress = path.join(process.cwd(), "item_progress");
    if (fs.existsSync(fprogress)) {
      data = fs.readFileSync(fprogress);
      data = parseInt(data, 10);
      if (utils.exist(data)) {
        $scope.progress_bar = parseInt(data, 10);
        fs.unlinkSync(fprogress);
      }
    }
    if (fs.existsSync(fitem_progress)) {
      data = fs.readFileSync(fitem_progress);
      if (utils.exist(data)) {
        $scope.progress_bar_item = parseInt(data, 10);
        fs.unlinkSync(fitem_progress);
      }
    }
    if ($scope.progress_bar >= 100) {
      $scope.progress_bar = 0;
    }
    if ($scope.progress_bar_item >= 100) {
      $scope.progress_bar_item = 0;
    }
    return utils.force_digest($scope);
  };
  return utils.set_interval("cryptobox.cf:694", progress_checker, 100, "progress_checker");
};

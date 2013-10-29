// Generated by CoffeeScript 1.6.3
var add_checkbox_g_traymenu_item, add_checkbox_menu_item, add_g_traymenu_item, add_g_traymenu_seperator, add_menu_item, add_menu_seperator, add_output, cb_server_url, change_workingstate, check_all_progress, check_result, child_process, cryptobox_ctrl, cryptobox_locked_status_change, fs, g_menu, g_menuactions, g_output, g_second_counter, g_tray, g_trayactions, g_winmain, get_all_smemory, get_motivation, get_option, get_sync_state, get_user_var, gui, on_exit, path, print, progress_checker, run_command, second_interval, set_data_user_config, set_menus_and_g_tray_icon, set_output_buffers, set_user_var_scope, spawn, start_process, start_watch, store_user_var, update_output, update_sync_state, warning, watch,
  __slice = [].slice;

child_process = require("child_process");

path = require("path");

fs = require("fs");

watch = require("watch");

spawn = require("child_process");

gui = require('nw.gui');

g_output = [];

g_second_counter = 0;

cb_server_url = "http://127.0.0.1:8000/";

g_winmain = gui.Window.get();

g_tray = new gui.Tray({
  icon: "images/icon-client-signed-in-idle.png"
});

g_menu = new gui.Menu({
  type: 'menubar'
});

g_trayactions = new gui.Menu();

g_tray.menu = g_trayactions;

g_menuactions = new gui.Menu();

g_winmain.menu = g_menuactions;

gui.Window.get().showDevTools();

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

warning = function(ln, w) {
  if (w != null) {
    if ((w != null ? w.trim : void 0) != null) {
      w = w.trim();
    }
  } else {
    return;
  }
  if (exist(w)) {
    if (w.faultString != null) {
      return add_output(w.faultString);
    } else if (w.message) {
      return add_output(w.message);
    } else {
      return add_output(w);
    }
  }
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

update_output = function(scope) {
  var make_stream, msgs;
  msgs = "";
  make_stream = function(msg) {
    return msgs += msg + "\n";
  };
  _.each(g_output, make_stream);
  return scope.cmd_output = msgs;
};

add_output = function(msgs, scope) {
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
    if (exist(msg)) {
      return g_output.unshift(msg);
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
      g_output.push(msgs);
    }
  }
  return update_output(scope);
};

warning = function(ln, w) {
  if (w != null) {
    if ((w != null ? w.trim : void 0) != null) {
      w = w.trim();
    }
  } else {
    return;
  }
  if (exist(w)) {
    if (w.faultString != null) {
      return add_output(w.faultString);
    } else if (w.message) {
      return add_output(w.message);
    } else {
      return add_output(w);
    }
  }
};

start_process = function() {
  var cba_main, cmd_folder, cmd_to_run;
  print("cryptobox.cf:123", "start_process");
  cmd_to_run = path.join(process.cwd(), "commands");
  cmd_to_run = path.join(cmd_to_run, "cba_main");
  cmd_folder = path.join(process.cwd(), "cba_commands");
  cba_main = spawn.spawn(cmd_to_run, ["-i " + cmd_folder]);
  return set_output_buffers(cba_main);
};

check_result = function(name) {
  var data, ex, result_path;
  result_path = path.join(cmd_folder, name + ".result");
  if (fs.existSync(result_path)) {
    data = null;
    try {
      data = fs.readFileSync(result_path);
    } catch (_error) {
      ex = _error;
      pass;
    }
    if (data != null) {
      try {
        data = JSON.parse(data);
      } catch (_error) {
        ex = _error;
        pass;
      }
    }
    if (data != null) {
      if (data["result"] != null) {
        try {
          fs.unlinkSync(result_path);
        } catch (_error) {
          ex = _error;
          print("cryptobox.cf:153", ex);
        }
        p.resolve(data["result"]);
        return;
      }
    }
  }
  if (result_cnt > 100) {
    return print("cryptobox.cf:158", "too many result checks", name, result_cnt);
  } else {
    return setTimeout(check_result, 100, name);
  }
};

run_command = function(name, data, scope) {
  var cmd_folder, cmd_path, fout, result_path;
  try {
    scope.running_command = true;
    if (!exist(data)) {
      data = "";
    }
    cmd_folder = path.join(process.cwd(), "cba_commands");
    if (!fs.existSync(cmd_folder)) {
      fs.mkdirSync(cmd_folder);
    }
    cmd_path = path.join(cmd_folder, name + ".cmd");
    result_path = path.join(cmd_folder, name + ".result");
    if (fs.existSync(result_path)) {
      fs.unlinkSync(result_path);
    }
    fout = fs.openSync(cmd_path, "w");
    fs.writeSync(fout, JSON.stringify(data));
    return fs.closeSync(fout);
  } finally {
    scope.running_command = false;
  }
};

get_motivation = function(scope) {
  if (scope.motivation == null) {
    return scope.motivation = run_command("get_motivation", "", scope);
  } else {
    return setTimeout(get_motivation, scope, 200);
  }
};

on_exit = function() {
  return gui.App.quit();
};

store_user_var = function(k, v) {
  var db, record;
  db = new PouchDB('cb_userinfo');
  if (!exist(db)) {
    throw "no db";
  } else {
    record = {
      _id: k,
      value: v
    };
    return db.get(k, function(e, d) {
      if (exist(d)) {
        if (exist(d._rev)) {
          record._rev = d._rev;
        }
      }
      return db.put(record, function(e, r) {
        if (exist(e)) {
          throw e;
        }
        if (exist(r)) {
          if (exist_truth(r.ok)) {
            return true;
          } else {
            throw e;
          }
        } else {
          throw "store_user_var generic error";
        }
      });
    });
  }
};

get_user_var = function(k) {
  var db;
  db = new PouchDB('cb_userinfo');
  if (!exist(db)) {
    throw "no db, get_user_var";
  } else {
    return db.get(k, function(e, d) {
      if (exist(e)) {
        throw e;
      } else {
        if (exist(d)) {
          return d.value;
        } else {
          throw "error, get_user_var";
        }
      }
    });
  }
};

set_user_var_scope = function(name, scope_name, scope) {
  var v;
  v = get_user_var(name);
  if (exist(scope_name)) {
    scope[scope_name] = v;
  } else {
    scope[name] = v;
  }
  return true;
};

set_data_user_config = function(scope) {
  if (set_user_var_scope("cb_folder", "cb_folder_text", scope)) {
    scope.got_folder_text = true;
  }
  set_user_var_scope("cb_username", null, scope);
  set_user_var_scope("cb_password", null, scope);
  if (set_user_var_scope("cb_name", null, scope)) {
    if (!exist(scope.cb_name)) {
      scope.cb_name = "active8";
      scope.got_cb_name = true;
    }
  }
  if (set_user_var_scope("cb_server", null, scope)) {
    if (!exist(scope.cb_folder_text)) {
      scope.cb_folder_text = "https://www.cryptobox.nl/";
      scope.cb_folder = scope.cb_folder_text;
    }
  }
  set_user_var_scope("show_settings", null, scope);
  set_user_var_scope("show_debug", null, scope);
  if (!exist(scope.cb_username)) {
    scope.show_settings = true;
  }
  if (!exist(scope.cb_server)) {
    return scope.cb_server = cb_server_url;
  }
};

get_sync_state = function(scope) {
  var option;
  option = {
    dir: scope.cb_folder_text,
    username: scope.cb_username,
    password: scope.cb_password,
    cryptobox: scope.cb_name,
    server: scope.cb_server,
    check: "1"
  };
  return run_command("run_cb_command", option, scope);
};

start_watch = function(scope) {
  var watch_path;
  if (!scope.file_watch_started) {
    watch_path = path.join(scope.cb_folder_text, scope.cb_name);
    if (fs.existSync(watch_path)) {
      scope.file_watch_started = true;
      return watch.watchTree(watch_path, function(f, curr, prev) {
        if (!String(f).contains("memory.pickle")) {
          if (typeof f === "object" && prev === null && curr === null) {
            return;
          }
          if (scope.running_command) {
            return;
          }
          add_output("local filechange", f);
          if (prev === null) {
            return get_sync_state(scope);
          } else if (curr.nlink === 0) {
            return get_sync_state(scope);
          } else {
            return get_sync_state(scope);
          }
        }
      });
    }
  }
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
    g_tray.icon = "images/icon-client-signed-out.png";
    $scope.disable_encrypt_button = true;
    $scope.disable_decrypt_button = false;
    $scope.disable_sync_button = true;
    return encrypt_g_tray_item.enabled = false;
  } else {
    g_tray.icon = "images/icon-client-signed-in-idle.png";
    $scope.disable_encrypt_button = false;
    $scope.disable_decrypt_button = true;
    $scope.disable_sync_button = false;
    return encrypt_g_tray_item.enabled = true;
  }
};

change_workingstate = function(wstate, scope) {
  if (exist_truth(wstate)) {
    scope.lock_buttons = true;
    return scope.working = true;
  } else {
    scope.lock_buttons = false;
    return scope.working = false;
  }
};

get_all_smemory = function(scope) {
  var value;
  value = run_command("get_all_smemory", "", scope);
  cryptobox_locked_status_change(exist_truth(value.cryptobox_locked));
  change_workingstate(value.working);
  if (!exist_truth(value.working)) {
    update_sync_state(value);
  }
  force_digest(scope);
  if (exist(value.tree_sequence)) {
    scope.tree_sequence = value.tree_sequence;
  }
  return force_digest(scope);
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

add_g_traymenu_item = function(label, icon, method) {
  var g_trayitem;
  g_trayitem = new gui.MenuItem({
    type: "normal",
    label: label,
    icon: icon,
    click: method
  });
  g_trayactions.append(g_trayitem);
  return g_trayitem;
};

add_checkbox_g_traymenu_item = function(label, icon, method, enabled) {
  var g_trayitem_cb;
  g_trayitem_cb = new gui.MenuItem({
    type: "checkbox",
    label: label,
    icon: icon,
    click: method,
    checked: enabled
  });
  g_trayactions.append(g_trayitem_cb);
  return g_trayitem_cb;
};

add_g_traymenu_seperator = function() {
  var g_traymenubaritem;
  g_traymenubaritem = new gui.MenuItem({
    type: "separator"
  });
  g_trayactions.append(g_traymenubaritem);
  return g_traymenubaritem;
};

add_menu_item = function(label, icon, method) {
  var menubaritem;
  menubaritem = new gui.MenuItem({
    type: "normal",
    label: label,
    icon: icon,
    click: method
  });
  g_menuactions.append(menubaritem);
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
  g_menuactions.append(menubaritem_cb);
  return menubaritem_cb;
};

add_menu_seperator = function() {
  var menubaritem;
  menubaritem = new gui.MenuItem({
    type: "separator"
  });
  return g_menuactions.append(menubaritem);
};

set_menus_and_g_tray_icon = function(scope) {
  add_menu_seperator();
  add_g_traymenu_seperator();
  add_menu_item("Encrypt local", "images/lock.png", $scope.encrypt_btn);
  add_g_traymenu_item("Encrypt local", "images/lock.png", $scope.encrypt_btn);
  add_menu_item("Decrypt local", "images/unlock.png", $scope.decrypt_btn);
  add_g_traymenu_item("Decrypt local", "images/unlock.png", $scope.decrypt_btn);
  g_winmain.menu.insert(new gui.MenuItem({
    label: 'Actions',
    submenu: g_menuactions
  }), 1);
  scope.settings_menubaritem = add_checkbox_menu_item("Settings", "images/cog.png", scope.toggle_settings, scope.show_settings);
  scope.settings_menubar_g_tray = add_checkbox_g_traymenu_item("Settings", "images/cog.png", scope.toggle_settings, scope.show_settings);
  scope.update_menu_checks = function() {
    scope.settings_menubaritem.checked = scope.show_settings;
    return scope.settings_menubar_g_tray.checked = scope.show_settings;
  };
  return scope.$watch("show_settings", scope.update_menu_checks);
};

progress_checker = function(fname, scope) {
  var data, fprogress;
  fprogress = path.join(process.cwd(), fname);
  if (fs.existSync(fprogress)) {
    data = fs.readFileSync(fprogress);
    data = parseInt(data, 10);
    if (exist(data)) {
      add_output(fname, data);
      scope[fname] = parseInt(data, 10);
      fs.unlinkSync(fprogress);
    }
  }
  if (scope[fname] >= 100) {
    scope[fname] = 100;
  }
  return utils.force_digest(scope);
};

check_all_progress = function(scope) {
  progress_checker("progress", scope);
  return progress_checker("item_progress", scope);
};

second_interval = function(scope) {
  if (scope.quitting) {
    print("cryptobox.cf:470", "quitting");
    return;
  }
  g_second_counter += 1;
  start_watch();
  check_all_progress(scope);
  update_output(scope);
  get_all_smemory();
  if (g_second_counter % 10 === 0) {
    return ping_client();
  }
};

angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"]);

cryptobox_ctrl = function($scope, memory, utils) {
  var set_data_user_config_once, start_process_once;
  $scope.cba_version = 0.1;
  $scope.cba_main = null;
  $scope.quitting = false;
  $scope.motivation = null;
  $scope.rpc_server_started = false;
  $scope.progress_bar = 0;
  $scope.progress_bar_item = 0;
  $scope.lock_buttons = true;
  $scope.show_settings = false;
  $scope.show_debug = false;
  $scope.got_folder_text = false;
  $scope.got_cb_name = false;
  $scope.working = false;
  $scope.file_downloads = [];
  $scope.file_uploads = [];
  $scope.dir_del_server = [];
  $scope.dir_make_local = [];
  $scope.dir_make_server = [];
  $scope.dir_del_local = [];
  $scope.file_del_local = [];
  $scope.file_del_server = [];
  $scope.disable_encrypt_button = false;
  $scope.disable_decrypt_button = false;
  $scope.disable_sync_button = false;
  $scope.file_watch_started = false;
  $scope.running_command = false;
  g_winmain.on('close', on_exit);
  $scope.debug_btn = function() {
    return require('nw.gui').Window.get().showDevTools();
  };
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
  $scope.get_lock_buttons = function() {
    return $scope.lock_buttons;
  };
  $scope.toggle_debug = function() {
    $scope.show_debug = !$scope.show_debug;
    return $scope.form_change();
  };
  $scope.form_change = function() {
    store_user_var("cb_folder", $scope.cb_folder_text);
    store_user_var("cb_username", $scope.cb_username);
    store_user_var("cb_password", $scope.cb_password);
    store_user_var("cb_name", $scope.cb_name);
    store_user_var("cb_server", $scope.cb_server);
    store_user_var("show_settings", $scope.show_settings);
    store_user_var("show_debug", $scope.show_debug);
    return utils.force_digest($scope);
  };
  $scope.file_input_change = function(f) {
    $scope.cb_folder_text = f[0].path;
    return $scope.form_change();
  };
  $scope.sync_btn = function() {
    var option;
    option = get_option();
    option.encrypt = true;
    option.clear = "0";
    option.sync = "0";
    return run_command("run_cb_command", option, $scope);
  };
  $scope.encrypt_btn = function() {
    var option;
    option = get_option();
    option.encrypt = true;
    option.remove = true;
    option.sync = false;
    return run_command("run_cb_command", option, $scope);
  };
  $scope.decrypt_btn = function() {
    var option;
    option = get_option();
    option.decrypt = true;
    option.clear = false;
    return run_command("run_cb_command", option, $scope);
  };
  $scope.open_folder = function() {
    return run_command("do_open_folder", [$scope.cb_folder_text, $scope.cb_name], $scope);
  };
  $scope.open_website = function() {
    return gui.Shell.openExternal($scope.cb_server + $scope.cb_name);
  };
  $scope.toggle_settings = function() {
    $scope.show_settings = !$scope.show_settings;
    return $scope.form_change();
  };
  set_data_user_config_once = _.once(set_data_user_config);
  start_process_once = _.once(start_process);
  set_data_user_config_once($scope);
  start_process_once();
  set_menus_and_g_tray_icon($scope);
  return setInterval(second_interval, [scope], 1000);
};

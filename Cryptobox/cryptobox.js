// Generated by CoffeeScript 1.6.3
var add_checkbox_g_traymenu_item, add_checkbox_menu_item, add_g_traymenu_item, add_g_traymenu_seperator, add_menu_seperator, add_output, already_running, cb_server_url, check_for_new_release, child_process, cnt_char, cryptobox_ctrl, cryptobox_locked_status_change, delete_blobs, fs, g_about_tray_item, g_cba_main, g_decrypt_g_tray_item, g_encrypt_g_tray_item, g_error_message, g_info_message, g_menu, g_menuactions, g_output, g_pref_tray_item, g_progress_callback, g_second_counter, g_tray, g_trayactions, g_winmain, get_option, get_user_var, gui, on_exit, option_to_array, outofsync, parse_json, path, possible_json, print, reset_bars, reset_bars_timer, run_cba_main, set_data_user_config, set_menus_and_g_tray_icon, set_motivation, set_sync_check_on_scope, set_user_var_scope, store_user_var, update_sync_state, warning,
  __slice = [].slice;

child_process = require("child_process");

path = require("path");

fs = require("fs");

gui = require('nw.gui');

g_output = [];

g_cba_main = [];

g_second_counter = 0;

g_error_message = null;

g_info_message = null;

g_encrypt_g_tray_item = null;

g_decrypt_g_tray_item = null;

g_pref_tray_item = null;

g_about_tray_item = null;

cb_server_url = "http://127.0.0.1:8000/";

g_winmain = gui.Window.get();

g_tray = new gui.Tray({
  icon: "images/cryptoboxstatus-idle-lep.tiff",
  alticon: "images/cryptoboxstatus-idle-lep-inv.tiff"
});

g_tray.on('click', function() {
  return alert;
});

g_menu = new gui.Menu({
  type: 'menubar'
});

g_trayactions = new gui.Menu();

g_tray.menu = g_trayactions;

g_menuactions = new gui.Menu();

g_winmain.menu = g_menu;

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
    if (exist(msg)) {
      return g_output.push(msg);
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
  console.log(msgs.trim());
  return true;
};

print = function() {
  var len_others, msg, others;
  msg = arguments[0], others = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
  len_others = _.size(others);
  switch (len_others) {
    case 0:
      return add_output(msg);
    case 1:
      return add_output(msg + " " + others[0]);
    case 2:
      return add_output(msg + " " + others[0] + " " + others[1]);
    case 3:
      return add_output(msg + " " + others[0] + " " + others[1] + " " + others[2]);
    case 4:
      return add_output(msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3]);
    case 5:
      return add_output(msg + " " + others[0] + " " + others[1] + " " + others[2] + " " + others[3] + " " + others[4]);
    default:
      add_output(others);
      return add_output(msg);
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

option_to_array = function(name, option) {
  var cmd_str, k, param_array, push_param_array, _i, _len, _ref;
  _ref = _.keys(option);
  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
    k = _ref[_i];
    if (option[k] === true) {
      option[k] = "1";
    }
    if (option[k] === false) {
      option[k] = "0";
    }
  }
  cmd_str = "";
  if (option.acommand != null) {
    cmd_str += " --acommand " + option.acommand;
  }
  if (option.cryptobox != null) {
    cmd_str += " --cryptobox " + option.cryptobox;
  }
  if (option.clear != null) {
    cmd_str += " --clear " + option.clear;
  }
  if (option.decrypt != null) {
    cmd_str += " --decrypt " + option.decrypt;
  }
  if (option.encrypt != null) {
    cmd_str += " --encrypt " + option.encrypt;
  }
  if (option.dir != null) {
    cmd_str += " --dir " + option.dir;
  }
  if (option.logout != null) {
    cmd_str += " --logout " + option.logout;
  }
  if (option.motivation != null) {
    cmd_str += " --motivation " + option.motivation;
  }
  if (option.numdownloadthreads != null) {
    cmd_str += " --numdownloadthreads " + option.numdownloadthreads;
  }
  if (option.check != null) {
    cmd_str += " --check " + option.check;
  }
  if (option.password != null) {
    cmd_str += " --password " + option.password;
  }
  if (option.remove != null) {
    cmd_str += " --remove " + option.remove;
  }
  if (option.sync != null) {
    cmd_str += " --sync " + option.sync;
  }
  if (option.treeseq != null) {
    cmd_str += " --treeseq " + option.treeseq;
  }
  if (option.username != null) {
    cmd_str += " --username " + option.username;
  }
  if (option.version != null) {
    cmd_str += " --version " + option.version;
  }
  if (option.server != null) {
    cmd_str += " --server " + option.server;
  }
  if (option.compiled != null) {
    cmd_str += " --compiled " + option.compiled;
  }
  param_array = [];
  push_param_array = function(i) {
    if (_.size(i.trim()) > 0) {
      return param_array.push(i);
    }
  };
  _.each(cmd_str.split(" "), push_param_array);
  return param_array;
};

already_running = function(output) {
  if (output.indexOf("Another instance is already running, quitting.") >= 0) {
    return true;
  }
  return false;
};

cnt_char = function(data, c) {
  return _.size(String(data).split(c)) - 1;
};

possible_json = function(data) {
  var ex;
  if (cnt_char(data, "{") === cnt_char(data, "}")) {
    try {
      JSON.parse(data);
      return true;
    } catch (_error) {
      ex = _error;
      return false;
    }
  }
  return false;
};

parse_json = function(method, data, givelist, debug) {
  var datacopy, ex, output, try_cb;
  try {
    output = [];
    datacopy = data;
    data = String(data).split("\n");
    try_cb = function(datachunk) {
      if (datachunk != null) {
        if (_.size(datachunk) > 0) {
          datachunk = JSON.parse(datachunk);
          if (datachunk != null) {
            if (datachunk.error_message != null) {
              g_error_message = datachunk != null ? datachunk.error_message : void 0;
              return add_output("error> " + g_error_message);
            } else if (datachunk.log != null) {
              return typeof console !== "undefined" && console !== null ? typeof console.log === "function" ? console.log(datachunk.log) : void 0 : void 0;
            } else if (datachunk.message != null) {
              g_info_message = datachunk.message;
              return add_output("info> " + g_info_message);
            } else {
              return output.push(datachunk);
            }
          }
        }
      }
    };
    _.each(data, try_cb);
  } catch (_error) {
    ex = _error;
    if (debug != null) {
      print("cryptobox.cf:203", method, "could not parse json", ex);
      if (typeof console !== "undefined" && console !== null) {
        if (typeof console.log === "function") {
          console.log(datacopy);
        }
      }
      return null;
    }
  }
  if (!givelist) {
    if (_.size(output) === 1) {
      return output[0];
    } else {
      return output[_.size(output) - 1];
    }
  }
  return output;
};

run_cba_main = function(name, options, cb_done, cb_intermediate, give_list) {
  var cba_main, cmd_to_run, data, error, execution_done, intermediate_cnt, output, params, stdout_data;
  cmd_to_run = path.join(process.cwd(), "commands");
  cmd_to_run = path.join(cmd_to_run, "cba_main");
  options.compiled = cmd_to_run;
  params = option_to_array(name, options);
  cba_main = child_process.spawn(cmd_to_run, params);
  g_cba_main.push(cba_main);
  output = "";
  error = "";
  data = "";
  intermediate_cnt = 0;
  if (give_list == null) {
    print("cryptobox.cf:228", name, "forcing give list");
    give_list = true;
  }
  stdout_data = function(data) {
    var call_intermediate, has_data, loop_cnt, nls, ssp;
    output += data;
    if (!exist(cb_intermediate)) {
      return;
    }
    ssp = String(output).split("\n");
    has_data = function(item) {
      if (_.size(item) > 0) {
        return true;
      }
      return false;
    };
    ssp = _.filter(ssp, has_data);
    nls = _.size(ssp);
    if (nls > 0) {
      loop_cnt = 0;
      call_intermediate = function(data) {
        var pdata;
        if (loop_cnt === intermediate_cnt) {
          pdata = null;
          if (possible_json(data)) {
            pdata = parse_json(name, data, give_list, true);
          }
          if (pdata) {
            cb_intermediate(pdata);
            data = "";
            intermediate_cnt += 1;
          }
        }
        return loop_cnt += 1;
      };
      return _.each(ssp, call_intermediate);
    }
  };
  cba_main.stdout.on("data", stdout_data);
  cba_main.stderr.on("data", function(data) {
    return error += data;
  });
  execution_done = function(event) {
    g_cba_main.remove(g_cba_main.indexOf(cba_main));
    if (already_running(output)) {
      print("cryptobox.cf:272", "already running");
      if (cb_done != null) {
        return cb_done(false, output);
      }
    } else {
      if (cb_done != null) {
        output = parse_json(name, output, give_list, true);
        if (event > 0) {
          return cb_done(false, output);
        } else {
          return cb_done(true, output);
        }
      }
    }
  };
  return cba_main.on("exit", execution_done);
};

on_exit = function() {
  var killcba;
  killcba = function(cba) {
    if (cba != null) {
      print("cryptobox.cf:290", "kill");
      return typeof cba.kill === "function" ? cba.kill() : void 0;
    }
  };
  _.each(g_cba_main, killcba);
  return gui.App.quit();
};

store_user_var = function(k, v, $q) {
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
        }
        if (exist(r)) {
          if (exist_truth(r.ok)) {
            return p.resolve(true);
          } else {
            return p.reject(r);
          }
        } else {
          return p.reject("store_user_var generic error");
        }
      });
    });
  }
  return p.promise;
};

get_user_var = function(k, $q) {
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
          return p.resolve(d.value);
        } else {
          return p.reject();
        }
      }
    });
  }
  return p.promise;
};

set_user_var_scope = function(name, scope_name, scope, $q) {
  var p;
  p = $q.defer();
  get_user_var(name, $q).then(function(v) {
    if (exist(scope_name)) {
      scope[scope_name] = v;
    } else {
      scope[name] = v;
    }
    return p.resolve();
  }, function(err) {
    warning("cryptobox.cf:356", err);
    return p.reject(err);
  });
  return p.promise;
};

set_data_user_config = function(scope, $q) {
  var p, promises;
  p = $q.defer();
  promises = [];
  promises.push(set_user_var_scope("cb_folder", "cb_folder_text", scope, $q));
  promises.push(set_user_var_scope("cb_username", null, scope, $q));
  promises.push(set_user_var_scope("cb_password", null, scope, $q));
  promises.push(set_user_var_scope("cb_name", null, scope, $q));
  promises.push(set_user_var_scope("cb_server", null, scope, $q));
  promises.push(set_user_var_scope("show_debug", null, scope, $q));
  $q.all(promises).then(function() {
    if (!exist(scope.cb_server)) {
      scope.cb_server = cb_server_url;
    }
    if (exist(scope.cb_username) && exist(scope.cb_password) && exist(scope.cb_name)) {
      return p.resolve();
    } else {
      scope.show_settings = true;
      return p.reject("not all data");
    }
  }, function(err) {
    scope.cb_name = "test";
    scope.show_settings = true;
    return p.reject(err);
  });
  return p.promise;
};

outofsync = function(scope, items) {
  var ioos;
  if (items != null) {
    ioos = _.size(items);
    if (ioos > 0) {
      scope.outofsync = true;
      return ioos;
    }
  }
  return 0;
};

set_sync_check_on_scope = function(scope, sync_results) {
  var human_readable_size, human_readable_size2, items_out_of_sync;
  scope.outofsync = false;
  items_out_of_sync = 0;
  human_readable_size = function(item) {
    return item.doc.m_size_p64s = g_format_file_size(item.doc.m_size_p64s);
  };
  human_readable_size2 = function(item) {
    return item.size = g_format_file_size(item.size);
  };
  if (sync_results.file_downloads != null) {
    items_out_of_sync += outofsync(scope, sync_results.file_downloads);
    scope.file_downloads = sync_results.file_downloads;
    _.each(scope.file_downloads, human_readable_size);
  }
  if (sync_results.file_uploads != null) {
    items_out_of_sync += outofsync(scope, sync_results.file_uploads);
    scope.file_uploads = sync_results.file_uploads;
    _.each(scope.file_uploads, human_readable_size2);
  }
  if (sync_results.dir_del_server != null) {
    items_out_of_sync += outofsync(scope, sync_results.dir_del_server);
    scope.dir_del_server = sync_results.dir_del_server;
  }
  if (sync_results.dir_make_local != null) {
    items_out_of_sync += outofsync(scope, sync_results.dir_make_local);
    scope.dir_make_local = sync_results.dir_make_local;
  }
  if (sync_results.dir_make_server != null) {
    items_out_of_sync += outofsync(scope, sync_results.dir_make_server);
    scope.dir_make_server = sync_results.dir_make_server;
  }
  if (sync_results.dir_del_local != null) {
    items_out_of_sync += outofsync(scope, sync_results.dir_del_local);
    scope.dir_del_local = sync_results.dir_del_local;
  }
  if (sync_results.file_del_local != null) {
    items_out_of_sync += outofsync(scope, sync_results.file_del_local);
    scope.file_del_local = sync_results.file_del_local;
  }
  if (sync_results.file_del_server != null) {
    items_out_of_sync += outofsync(scope, sync_results.file_del_server);
    scope.file_del_server = sync_results.file_del_server;
  }
  if (sync_results.rename_file_server != null) {
    items_out_of_sync += outofsync(scope, sync_results.rename_file_server);
    scope.rename_file_server = sync_results.rename_file_server;
  }
  if (sync_results.rename_folder_server != null) {
    items_out_of_sync += outofsync(scope, sync_results.rename_folder_server);
    scope.rename_folder_server = sync_results.rename_folder_server;
  }
  if (sync_results.rename_local_dirs != null) {
    items_out_of_sync += outofsync(scope, sync_results.rename_local_dirs);
    scope.rename_local_dirs = sync_results.rename_local_dirs;
  }
  scope.items_out_of_sync = items_out_of_sync;
  if (scope.items_out_of_sync > 0) {
    scope.progress_message = scope.items_out_of_sync + " items out of sync";
    return scope.sync_requested = true;
  }
};

update_sync_state = function(scope) {
  var option, result_sync_state;
  option = {
    dir: scope.cb_folder_text,
    username: scope.cb_username,
    password: scope.cb_password,
    cryptobox: scope.cb_name,
    server: scope.cb_server,
    check: true
  };
  result_sync_state = function(result, sync_result_list) {
    var process_sync_result;
    if (scope.disable_check_button) {
      print("cryptobox.cf:475", "check done");
      scope.disable_check_button = false;
      scope.disable_sync_button = false;
    }
    if (result) {
      process_sync_result = function(sync_results) {
        var ex;
        if (sync_results.instruction != null) {
          if (sync_results.instruction === "lock_buttons_password_wrong") {
            print("cryptobox.cf:483", sync_results.instruction);
            return scope.lock_buttons_password_wrong = true;
          }
        } else {
          scope.request_update_sync_state = false;
          try {
            if (sync_results != null) {
              if (sync_results.locked != null) {
                if (sync_results.locked) {
                  return cryptobox_locked_status_change(true, scope);
                }
              } else {
                cryptobox_locked_status_change(false, scope);
                set_sync_check_on_scope(scope, sync_results);
                if (sync_results.all_synced) {
                  return scope.disable_sync_button = false;
                } else {
                  return scope.disable_sync_button = false;
                }
              }
            }
          } catch (_error) {
            ex = _error;
            print("cryptobox.cf:502", ex);
            return print("cryptobox.cf:503", sync_results);
          }
        }
      };
      _.each(sync_result_list, process_sync_result);
    }
    return result;
  };
  return run_cba_main("update_sync_state", option, result_sync_state, null, true);
};

cryptobox_locked_status_change = function(locked, scope) {
  scope.cryptobox_locked = locked;
  if (scope.cryptobox_locked) {
    g_tray.icon = "images/icon-client-signed-out.png";
    scope.disable_folder_button = true;
    scope.disable_encrypt_button = true;
    scope.disable_decrypt_button = false;
    scope.disable_sync_button = true;
    if (g_encrypt_g_tray_item != null) {
      g_encrypt_g_tray_item.label = "Unlock Cryptobox folder";
      return g_encrypt_g_tray_item.click = scope.decrypt_btn;
    }
  } else {
    g_tray.icon = "images/cryptoboxstatus-idle-lep.tiff";
    scope.disable_folder_button = false;
    scope.disable_encrypt_button = false;
    scope.disable_decrypt_button = true;
    return scope.disable_sync_button = false;
  }
};

get_option = function(scope) {
  var option;
  option = {
    dir: scope.cb_folder_text,
    username: scope.cb_username,
    password: scope.cb_password,
    cryptobox: scope.cb_name,
    server: scope.cb_server
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
  add_g_traymenu_item("Start Sync", "", scope.sync_btn);
  add_g_traymenu_seperator();
  add_g_traymenu_item("Open Cryptobox folder", "", scope.open_folder);
  add_g_traymenu_item("Visit Cryptobox on the web", "", scope.open_website);
  add_g_traymenu_seperator();
  g_encrypt_g_tray_item = add_g_traymenu_item("Lock Cryptobox folder", "", scope.encrypt_btn);
  add_g_traymenu_seperator();
  g_pref_tray_item = add_g_traymenu_item("Preferences", "", scope.pref_window);
  g_about_tray_item = add_g_traymenu_item("About", "", scope.about);
  add_g_traymenu_seperator();
  add_g_traymenu_item("Debug Console", "", scope.debug_btn);
  return add_g_traymenu_item("Quit Cryptobox", "", scope.close_window_menu);
};

set_motivation = function($scope) {
  var motivation_cb;
  motivation_cb = function(result, output) {
    print("cryptobox.cf:616", output);
    if (result) {
      $scope.motivation = output != null ? output.motivation.replace("\n", "<br/>") : void 0;
      return $scope.progress_message = $scope.motivation + "<br/><br/>";
    }
  };
  return run_cba_main("motivation", {
    "motivation": true
  }, motivation_cb, null, false);
};

g_progress_callback = function(scope, output) {
  var err;
  try {
    if (output.global_progress != null) {
      scope.progress_bar = output.global_progress;
    }
    if (output.item_progress != null) {
      scope.progress_bar_item = output.item_progress;
    }
    if (output.msg != null) {
      scope.progress_message = output.msg;
    }
    if (!scope.$$phase) {
      return scope.$apply();
    }
  } catch (_error) {
    err = _error;
    return print("cryptobox.cf:638", "g_progress_callback", err);
  }
};

reset_bars_timer = null;

reset_bars = function(scope) {
  var reset_bar, reset_bar_item;
  return;
  if (scope.progress_bar_item >= 100) {
    if (scope.progress_bar > 0) {
      if (scope.progress_bar_item >= 100) {
        reset_bar_item = function() {
          return scope.progress_bar_item = 0;
        };
        setTimeout(reset_bar_item, 2000);
      }
    }
  }
  if (scope.progress_bar >= 100) {
    if (scope.progress_bar_item === 0) {
      reset_bar = function() {
        if (scope.progress_bar_item === 0) {
          return scope.progress_bar = 0;
        }
      };
      return setTimeout(reset_bar, 750);
    }
  }
};

delete_blobs = function(scope) {
  var cb_delete_blobs, option;
  option = get_option(scope);
  option.acommand = "delete_blobs";
  cb_delete_blobs = function(result, output) {
    return print("cryptobox.cf:667", "blobs deleted", result, output);
  };
  return run_cba_main("delete_blobs", option, cb_delete_blobs, null, false);
};

check_for_new_release = function(scope) {
  var cb_check_new_release, option;
  option = get_option(scope);
  option.acommand = "check_new_release";
  cb_check_new_release = function(result, output) {
    var check_output;
    if (result) {
      check_output = function(o) {
        if ((o != null ? o.new_release : void 0) != null) {
          if (o.new_release) {
            return scope.show_new_release_download_dialog = true;
          }
        }
      };
      return _.each(output, check_output);
    }
  };
  return run_cba_main("check_new_release", option, cb_check_new_release, null, true);
};

angular.module("cryptoboxApp", ["cryptoboxApp.base", "angularFileUpload"]);

cryptobox_ctrl = function($scope, memory, utils, $q) {
  var check_feedback_progress_callback, digester, do_sync, g_window_width, icon_busy, icon_update, once_motivation, progress_callback, ten_second_interval, two_second_interval;
  $scope.cba_version = 0.1;
  $scope.cba_main = null;
  $scope.quitting = false;
  $scope.motivation = null;
  $scope.progress_bar = 0;
  $scope.progress_bar_item = 0;
  $scope.progress_message = "";
  $scope.show_settings = true;
  $scope.show_debug = false;
  $scope.got_cb_name = false;
  $scope.file_downloads = [];
  $scope.file_uploads = [];
  $scope.dir_del_server = [];
  $scope.dir_make_local = [];
  $scope.dir_make_server = [];
  $scope.dir_del_local = [];
  $scope.file_del_local = [];
  $scope.file_del_server = [];
  $scope.disable_encrypt_button = true;
  $scope.disable_decrypt_button = true;
  $scope.disable_check_button = false;
  $scope.disable_sync_button = false;
  $scope.file_watch_started = false;
  $scope.request_update_sync_state = false;
  $scope.state_syncing = false;
  $scope.tree_sequence = null;
  $scope.sync_requested = false;
  $scope.error_message = null;
  $scope.info_message = null;
  $scope.disable_folder_button = false;
  $scope.lock_buttons_password_wrong = false;
  $scope.show_new_release_download_dialog = false;
  $scope.show_new_release_download_dialog_message = "A new release of this app is available, click here to download";
  g_winmain.on("close", on_exit);
  $scope.about = function() {
    return window.open("about.html", "", "width=390,height=160");
  };
  $scope.download_new_release = function() {
    var option;
    option = get_option($scope);
    option.acommand = "download_new_release";
    return run_cba_main("download_new_release", option, null, progress_callback, false);
  };
  $scope.close_window_menu = function() {
    return g_winmain.close();
  };
  $scope.close_window = function() {
    var close_callback;
    close_callback = function(result) {
      if (result) {
        return g_winmain.close();
      }
    };
    return bootbox.confirm("Exit application, are you sure?", close_callback);
  };
  $scope.pref_window = function() {
    g_pref_tray_item.label = "Preferences";
    g_pref_tray_item.click = $scope.pref_window;
    g_winmain.show();
    return $scope.set_window_size_settings();
  };
  $scope.hide_window = function() {
    g_winmain.hide();
    return $scope.set_window_size_settings();
  };
  $scope.debug_btn = function() {
    return require("nw.gui").Window.get().showDevTools();
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
  $scope.form_changed = false;
  $scope.form_change = function() {
    return $scope.form_changed = true;
  };
  $scope.reset_cache = function() {
    var option;
    option = get_option($scope);
    option.encrypt = true;
    option.clear = true;
    return run_cba_main("reset_cache", option, null, progress_callback, false);
  };
  $scope.form_save = function() {
    store_user_var("cb_folder", $scope.cb_folder_text, $q);
    store_user_var("cb_username", $scope.cb_username, $q);
    store_user_var("cb_name", $scope.cb_name, $q);
    store_user_var("cb_server", $scope.cb_server, $q);
    store_user_var("show_debug", $scope.show_debug, $q);
    get_user_var("cb_password", $q).then(function(oldpassword) {
      if (oldpassword !== $scope.cb_password) {
        delete_blobs($scope);
        $scope.lock_buttons_password_wrong = false;
      }
      return store_user_var("cb_password", $scope.cb_password, $q);
    }, function(err) {
      return print("cryptobox.cf:788", "error setting password", err);
    });
    $scope.form_changed = false;
    return $scope.request_update_sync_state = true;
  };
  $scope.file_input_change = function(f) {
    $scope.cb_folder_text = f[0].path;
    return $scope.form_save();
  };
  $scope.check_btn = function() {
    $scope.disable_check_button = true;
    return $scope.request_update_sync_state = true;
  };
  $scope.sync_btn = function() {
    return $scope.sync_requested = true;
  };
  progress_callback = function(output) {
    return g_progress_callback($scope, output);
  };
  check_feedback_progress_callback = function(output) {
    g_progress_callback($scope, output);
    if (output.file_uploads != null) {
      return set_sync_check_on_scope($scope, output);
    }
  };
  do_sync = function() {
    var option, sync_cb;
    option = get_option($scope);
    option.clear = false;
    option.sync = true;
    $scope.state_syncing = true;
    $scope.disable_encrypt_button = true;
    $scope.disable_sync_button = true;
    sync_cb = function(result, output) {
      var po;
      po = function(o) {
        return typeof console !== "undefined" && console !== null ? typeof console.log === "function" ? console.log(o) : void 0 : void 0;
      };
      _.each(output, po);
      if (result) {
        $scope.disable_sync_button = false;
        $scope.state_syncing = false;
        $scope.disable_encrypt_button = false;
        return $scope.request_update_sync_state = true;
      }
    };
    return run_cba_main("sync_cb", option, sync_cb, check_feedback_progress_callback, false);
  };
  $scope.encrypt_btn = function() {
    var option, sync_cb;
    option = get_option($scope);
    option.encrypt = true;
    option.remove = true;
    $scope.disable_encrypt_button = true;
    $scope.disable_sync_button = true;
    sync_cb = function(result, output) {
      if (result) {
        g_encrypt_g_tray_item.label = "Unlock Cryptobox folder";
        g_encrypt_g_tray_item.click = $scope.decrypt_btn;
        return $scope.request_update_sync_state = true;
      }
    };
    return run_cba_main("encrypt", option, sync_cb, progress_callback, false);
  };
  $scope.decrypt_btn = function() {
    var decrypt_cb, option;
    option = get_option($scope);
    option.decrypt = true;
    $scope.disable_sync_button = true;
    $scope.disable_decrypt_button = true;
    decrypt_cb = function(result, output) {
      if (result) {
        print("cryptobox.cf:853", "decrypted");
        g_encrypt_g_tray_item.label = "Lock Cryptobox folder";
        g_encrypt_g_tray_item.click = $scope.encrypt_btn;
        $scope.disable_sync_button = false;
        return $scope.request_update_sync_state = true;
      }
    };
    return run_cba_main("decrypt", option, decrypt_cb, progress_callback, false);
  };
  $scope.open_folder = function() {
    var option;
    option = get_option($scope);
    option.acommand = "open_folder";
    return run_cba_main("open_folder", option, null, null, false);
  };
  $scope.open_website = function() {
    var option;
    option = get_option($scope);
    option.acommand = "open_website";
    return run_cba_main("open_website", option, null, null, false);
  };
  g_window_width = 300;
  $scope.set_window_size_settings = function() {
    g_winmain.moveTo(screen.width - 900, 32);
    return g_winmain.resizeTo(800, 700);
  };
  $scope.toggle_settings = function() {
    g_winmain.show();
    $scope.set_window_size_settings();
    return $scope.form_save();
  };
  $scope.toggle_debug = function() {
    $scope.show_debug = !$scope.show_debug;
    return print("cryptobox.cf:883", $scope.show_debug);
  };
  $scope.clear_msg_buffer = function() {
    g_output = [];
    return utils.force_digest($scope);
  };
  set_data_user_config($scope, $q).then(function() {
    update_sync_state($scope);
    $scope.set_window_size_settings();
    return check_for_new_release($scope);
  }, function(err) {
    print("cryptobox.cf:896", err);
    throw "set data user config error";
  });
  once_motivation = _.once(set_motivation);
  set_menus_and_g_tray_icon($scope);
  icon_busy = 1;
  icon_update = get_local_time();
  digester = function() {
    var clear_info, error, make_stream, now, output_msg;
    now = get_local_time();
    $scope.progress_message = utils.capfirst($scope.progress_message);
    output_msg = "";
    if (utils.exist_truth($scope.lock_buttons_password_wrong)) {
      $scope.disable_encrypt_button = true;
      $scope.disable_decrypt_button = true;
      $scope.disable_sync_button = true;
    }
    make_stream = function(msg) {
      return output_msg += msg + "\n";
    };
    _.each(g_output, make_stream);
    $scope.cmd_output = output_msg;
    reset_bars($scope);
    $scope.error_message = g_error_message;
    if (g_error_message != null) {
      try {
        $scope.subject_message_mail = String(g_error_message).split("> ---------------------------")[2].split(">")[3].trim();
        $scope.error_message_mail = String(g_error_message).replace(/\n/g, "%0A");
      } catch (_error) {
        error = _error;
        $scope.error_message_mail = null;
      }
    }
    if ($scope.sync_requested) {
      $scope.sync_requested = false;
      icon_busy = 1;
      icon_update = get_local_time();
      do_sync();
    }
    utils.force_digest($scope);
    if (g_info_message != null) {
      $scope.info_message = g_info_message;
      g_info_message = null;
      clear_info = function() {
        return $scope.info_message = "";
      };
      setTimeout(clear_info, 5000);
    }
    if (now - icon_update > 400) {
      icon_busy += 1;
      icon_update = now;
    }
    if (icon_busy > 4) {
      icon_busy = 1;
    }
    if ($scope.state_syncing) {
      return g_tray.icon = "images/icon-client-busy-" + icon_busy + ".png";
    } else {
      if (!$scope.cryptobox_locked) {
        return g_tray.icon = "images/cryptoboxstatus-idle-lep.tiff";
      }
    }
  };
  setInterval(digester, 100);
  two_second_interval = function() {
    if ($scope.request_update_sync_state) {
      if ($scope.progress_bar === 0) {
        if (!$scope.lock_buttons_password_wrong) {
          return update_sync_state($scope);
        }
      }
    }
  };
  setInterval(two_second_interval, 2000);
  ten_second_interval = function() {
    var option, tree_sequence_cb;
    option = get_option($scope);
    option.treeseq = true;
    $scope.request_update_sync_state = true;
    if ($scope.lock_buttons_password_wrong) {
      update_sync_state($scope);
    }
    tree_sequence_cb = function(result, output) {
      var ts;
      if (result) {
        ts = output;
        if (ts !== $scope.tree_sequence) {
          if ($scope.tree_sequence != null) {
            $scope.request_update_sync_state = true;
          }
        }
        return $scope.tree_sequence = ts;
      }
    };
    if ($scope.progress_bar === 0) {
      return run_cba_main("treeseq", option, tree_sequence_cb, null, false);
    }
  };
  setInterval(ten_second_interval, 10000);
  return g_winmain.hide();
};

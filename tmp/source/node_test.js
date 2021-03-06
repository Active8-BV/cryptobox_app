// Generated by CoffeeScript 1.8.0
var add_output, already_running, assert, cb_current, cb_done, child_process, cnt_char, exist, exist_string, fs, parse_json, pass, path, possible_json, print, run_cba_main, strEndsWith, _,
  __slice = [].slice;

fs = require("fs");

assert = require('assert');

path = require("path");

_ = require('underscore');

child_process = require("child_process");

path = require("path");

pass = function() {
  var x;
  return x = 9;
};

strEndsWith = function(str, suffix) {
  return str.indexOf(suffix, str.length - suffix.length) !== -1;
};

exist_string = function(value) {
  if (value != null) {
    switch (value) {
      case void 0:
      case null:
      case "null":
      case "undefined":
        return false;
      default:
        return true;
    }
  } else {
    return false;
  }
};

exist = function(value) {
  if (exist_string(value)) {
    if (value === "") {
      return false;
    }
    if (String(value) === "NaN") {
      return false;
    }
    if (String(value) === "undefined") {
      return false;
    }
    if (value.trim != null) {
      if (value.trim() === "") {
        return false;
      }
    }
    return true;
  } else {
    return false;
  }
};

parse_json = function(data, debug) {
  var ex, output, try_cb;
  try {
    output = [];
    data = String(data).split("\n");
    try_cb = function(datachunk) {
      var g_error_message;
      if (datachunk != null) {
        if (_.size(datachunk) > 0) {
          datachunk = JSON.parse(datachunk);
          if (datachunk != null) {
            if (datachunk.error_message != null) {
              g_error_message = datachunk != null ? datachunk.error_message : void 0;
              add_output(g_error_message);
            }
            return output.push(datachunk);
          }
        }
      }
    };
    _.each(data, try_cb);
    if (_.size(output) === 1) {
      return output[0];
    }
    return output;
  } catch (_error) {
    ex = _error;
    if (debug != null) {
      print("node_test.cf:62", "could not parse json", ex);
      print("node_test.cf:63", data);
    }
  }
  return null;
};

already_running = function(output) {
  if (output.indexOf("Another instance is already running, quitting.") >= 0) {
    return true;
  }
  return false;
};

add_output = function(msgs) {
  if (typeof console !== "undefined" && console !== null) {
    console.log(msgs);
  }
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

run_cba_main = function(name, options, cb_done, cb_intermediate) {
  var cba_main, cmd_to_run, data, error, execution_done, g_cba_main, intermediate_cnt, output, stdout_data;
  if (!exist(cb_done)) {
    throw "run_cba_main needs a cb_done parameter (callback)";
  }
  cmd_to_run = path.join(process.cwd(), "cba_main");
  cba_main = child_process.spawn(cmd_to_run, "");
  g_cba_main = cba_main;
  output = "";
  error = "";
  data = "";
  intermediate_cnt = 0;
  stdout_data = function(data) {
    var call_intermediate, has_data, loop_cnt, nls, ssp;
    output += data;
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
            pdata = parse_json(data, true);
          }
          if (pdata) {
            cb_intermediate(pdata);
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
    g_cba_main = null;
    if (already_running(output)) {
      print("node_test.cf:164", "already running");
      return cb_done(false, output);
    } else {
      output = parse_json(output);
      if (event > 0) {
        return cb_done(false, output);
      } else {
        return cb_done(true, output);
      }
    }
  };
  return cba_main.on("exit", execution_done);
};

cb_done = function(r, o) {
  var p;
  print("node_test.cf:178", r);
  p = function(d) {
    return print("node_test.cf:181", d.message);
  };
  return _.each(o, p);
};

cb_current = function(o) {
  return print("node_test.cf:186", o);
};

run_cba_main("foo", {}, cb_done, cb_current);

//# sourceMappingURL=node_test.js.map

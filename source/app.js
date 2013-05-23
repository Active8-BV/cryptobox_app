// Generated by CoffeeScript 1.6.2
var add_menu, add_tray, cryptobox_ctrl, f_exit;

f_exit = function() {
  return Ti.App.exit();
};

add_menu = function() {
  var fileItem, menu;

  menu = Ti.UI.createMenu();
  fileItem = Ti.UI.createMenuItem("File");
  fileItem.addItem("Exit", f_exit);
  menu.appendItem(fileItem);
  return Ti.UI.setMenu(menu);
};

add_tray = function() {
  var programTray, tmenu;

  programTray = Ti.UI.addTray("tray_icon.png");
  tmenu = Ti.UI.createMenu();
  tmenu.addItem("Exit", f_exit);
  return programTray.setMenu(tmenu);
};

add_menu();

add_tray();

angular.module("cryptoboxApp", ["cryptoboxApp.base"]);

cryptobox_ctrl = function($scope, $q, memory, utils) {
  var run_command;

  memory.set("g_running", true);
  run_command = function(cmd_name) {
    var cmd, cmd_process, on_exit, on_failure, on_read, p;

    p = $q.defer();
    cmd = Ti.API.getApplication().getResourcesPath() + "/" + cmd_name;
    cmd_process = Ti.Process.createProcess([cmd]);
    on_read = function(e) {
      p.resolve(e.data.toString());
      return utils.force_digest($scope);
    };
    cmd_process.setOnRead(on_read);
    on_exit = function(command) {
      return console.log("app.cf:40", 'exit' + command.getTarget().toString().replace(Ti.API.getApplication().getResourcesPath(), ""));
    };
    on_failure = function() {
      return p.reject("timeout occurred");
    };
    set_time_out(on_failure, 5000);
    cmd_process.setOnExit(on_exit);
    cmd_process.launch();
    return p.promise;
  };
  $scope.python_version = run_command("pyversion");
  $scope.handle_change = function() {
    return $scope.yourName = handle($scope.yourName);
  };
  $scope.file_input_change = function() {
    return py_file_input_change($scope.file_input);
  };
  return $scope.open_dialog = function() {
    utils.force_digest($scope);
    return document.location = "https://www.cryptobox.nl/active8";
  };
};

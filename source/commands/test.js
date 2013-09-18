_ = require('underscore');

child_process = require("child_process");

path = require("path");
xmlrpc = require('xmlrpc');

cmd_to_run = path.join(process.cwd(), "cba_main");

get_rpc_client = function () {
    clientOptions = {
        host: "localhost",
        port: 8654,
        path: "/RPC2"
    };
    return xmlrpc.createClient(clientOptions);
};

var client;
client = get_rpc_client();


set_output_buffers = function (cba_main_proc) {
    var memory_name;
    if (cba_main_proc.stdout) {
        cba_main_proc.stdout.on("data", function (data) {
            console.log("stdout:" + data);
        });
    }
    if (cba_main_proc.stderr) {
        return cba_main_proc.stderr.on("data", function (data) {
            console.log("stderr:" + data);
        });
    }
};

on_exit = function () {
    var client;

    client = get_rpc_client();
    return client.methodCall("force_stop", [], function (e, v) {
        var force_kill,
            _this = this;
        console.log(e, v);
        force_kill = function () {
            console.log("gui exit")
            return
        };
        return _.defer(force_kill);
    });
};

spawn = require("child_process").spawn;

on_exit()
//cba_main = spawn(cmd_to_run, [""]);
//set_output_buffers(cba_main);

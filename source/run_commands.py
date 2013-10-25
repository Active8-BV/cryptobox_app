#!/usr/local/bin/python
# coding=utf-8

from commands.cba_utils import *


def main():
    """
    main
    """
    cmd_folder_path = os.path.join(os.getcwd(), "cba_commands")

    commands = check_command_folder(cmd_folder_path)

    for cmd in commands:
        if cmd["name"] == "add":
            cmd["result"] = {"params": (cmd["a"], cmd["b"]), "result": cmd["a"] + cmd["b"]}
            add_command_result_to_folder(cmd_folder_path, cmd)


if __name__ == '__main__':
    main()

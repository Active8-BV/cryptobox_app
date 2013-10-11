function build_commands {
    python -OO when_changed.py ./source/commands/cba_main.py -c "./buildcommands.sh cba_main" &
    python -OO when_changed.py ./source/commands/cba_sync.py -c "./buildcommands.sh cba_main" &
    python -OO when_changed.py ./source/commands/cba_network.py -c "./buildcommands.sh cba_main" &
    python -OO when_changed.py ./source/commands/cba_utils.py -c "./buildcommands.sh cba_main" &
    python -OO when_changed.py ./source/commands/cba_blobs.py -c "./buildcommands.sh cba_main" &
    python -OO when_changed.py ./source/commands/cba_crypto.py -c "./buildcommands.sh cba_main" &
    python -OO when_changed.py ./source/commands/cba_file.py -c "./buildcommands.sh cba_main" &
    python -OO when_changed.py ./source/commands/cba_index.py -c "./buildcommands.sh cba_main" &
}
build_commands

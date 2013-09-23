

rm -Rf ./Cryptobox/packages

function wait_bit {
    sleep 0.2
}

function on_change_path_cmd {
    python -OO when_changed.py $1 -c "$2; " &
    wait_bit
}

on_change_path_cmd ./source/cryptobox.coffee 'python -OO cp.py -r 0 -f ./source/cryptobox.coffee; coffee -c -b ./source/cryptobox.coffee; mv ./source/cryptobox.js ./Cryptobox'

./run_cp.sh

python -OO when_changed.py ./source/commands/cba_main.py -c "./buildcommands.sh cba_main" &
python -OO when_changed.py ./source/commands/cba_sync.py -c "./buildcommands.sh cba_main" &
python -OO when_changed.py ./source/commands/cba_network.py -c "./buildcommands.sh cba_main" &
python -OO when_changed.py ./source/commands/cba_utils.py -c "./buildcommands.sh cba_main" &
python -OO when_changed.py ./source/commands/cba_blobs.py -c "./buildcommands.sh cba_main" &
python -OO when_changed.py ./source/commands/cba_crypto.py -c "./buildcommands.sh cba_main" &
python -OO when_changed.py ./source/commands/cba_file.py -c "./buildcommands.sh cba_main" &
python -OO when_changed.py ./source/commands/cba_index.py -c "./buildcommands.sh cba_main" &


python kill_restart.py &
python -OO kill_on_change_procs.py
rm app.running
killall Python
killall python


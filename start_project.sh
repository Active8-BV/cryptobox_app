

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

python kill_restart_cba_app.py &
python -OO kill_on_change_procs.py
rm app.running

ps aux | grep -ie cryptobox.coffee | awk '{print $2}' | xargs kill -9
ps aux | grep -ie kill_restart_cba_app | awk '{print $2}' | xargs kill -9
ps aux | grep -ie cba_main | awk '{print $2}' | xargs kill -9


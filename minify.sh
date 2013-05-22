

function wait_bit {
    sleep 0.2
}

function on_change_path_cmd {
    python -OO when_changed.py $1 -c "$2; " &    
    wait_bit
}

on_change_path_cmd ./source/app.coffee 'python -OO cp.py  -r "0" -f ./source/app.coffee; coffee -c -l -b ./source/app.coffee; python combinejs.py'
python -OO kill_on_change_procs.py



function wait_bit {
    sleep 0.2
}

function on_change_path_cmd {
    python275 -OO when_changed.py $1 -c "$2; " &
    python275 -OO when_changed.py $1 -c "python275 kill_restart.py" &
    wait_bit
}
on_change_path_cmd ./source/app.py 'python275 -OO cp.py  -r "0" -f ./source/app.coffee; coffee -c -l -b ./source/app.coffee; python275 combinejs.py'
on_change_path_cmd ./source/app.coffee 'python275 -OO cp.py  -r "0" -f ./source/app.coffee; coffee -c -l -b ./source/app.coffee; python275 combinejs.py'
on_change_path_cmd ./Cryptobox/Resources/index.html 'python275 -OO cp.py  -r "0" -f ./source/app.coffee; coffee -c -l -b ./source/app.coffee; python275 combinejs.py'
python275 -OO kill_on_change_procs.py

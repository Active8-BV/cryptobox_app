
function on_change_path {
    python -OO cp.py -f $1
    #python when_changed.py $1 "python -OO cp.py -f $1"
}

on_change_path cba_main.py
on_change_path cba_utils.py
on_change_path cba_crypto.py
on_change_path cba_blobs.py
on_change_path cba_index.py
on_change_path cba_network.py
on_change_path cba_sync.py
on_change_path cba_file.py
on_change_path tests.py
python -OO cp.py -r 0 -f ../cryptobox.coffee
coffee -c -b ../cryptobox.coffee;
mv ../cryptobox.js ../../Cryptobox/

echo "done"



function on_change_path {
    python -OO cp.py -f $1
    #python when_changed.py $1 "python -OO cp.py -f $1"
}

on_change_path cba_main.py 
on_change_path cba_utils.py 
on_change_path cba_crypto.py 
on_change_path cba_memory.py 
on_change_path cba_feedback.py 
on_change_path cba_blobs.py 
on_change_path cba_index.py 
on_change_path cba_tree.py 
on_change_path cba_network.py 
on_change_path cba_sync.py 
on_change_path cba_file.py 
on_change_path tests.py

#killall Python

echo "done"


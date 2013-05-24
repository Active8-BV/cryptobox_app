import os
import time
from multiprocessing import Pool

def bring_to_front():
    time.sleep(0.3)
    os.system("osascript node_webkit_to_foreground.scpt")

if __name__ == '__main__':
    pool = Pool(processes=1)              # Start a worker processes.
    
        
    if os.path.exists("app.running"):
        exit(1)
    try:
        while True:
            if not os.path.exists("app.running"):            
                os.system("killall node-webkit")
                open("app.running", "w").write(".")
                pool.apply_async(bring_to_front)
                os.system("make run")            
                os.remove("app.running")
            print "restarting app"  
    finally:
        os.remove("app.running")

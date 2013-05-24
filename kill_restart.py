import os
import time
if os.path.exists("app.running"):
    exit(1)
try:
    while True:
        if not os.path.exists("app.running"):            
            os.system("killall node-webkit")
            open("app.running", "w").write(".")
            os.system("make run")
            os.remove("app.running")
        print "restarting app"  
finally:
    os.remove("app.running")

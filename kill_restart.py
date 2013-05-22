import os
import time
if os.path.exists("app.running"):
    exit(1)
try:
    while True:
        if not os.path.exists("app.running"):            
            os.system("killall Cryptobox")
            open("app.running", "w").write(".")
            os.system("./build.sh")
            os.remove("app.running")
        time.sleep(0.5)
finally:
    os.remove("app.running")

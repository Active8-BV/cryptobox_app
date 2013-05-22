import os
import time
if os.path.exists("app.running"):
    exit(1)
os.system("killall Cryptobox")
open("app.running", "w").write(".")
os.system("./build.sh")
os.remove("app.running")

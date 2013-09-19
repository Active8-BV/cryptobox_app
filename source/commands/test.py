# coding=utf-8

import requests

url = "http://upload.wikimedia.org/wikipedia/commons/4/4e/Pleiades_large.jpg"
#url = "http://download.thinkbroadband.com/1MB.zip"
#url = "http://download.thinkbroadband.com/"

def print_url(r, *args, **kwargs):
    pass

r = requests.get(url, hooks=dict(response=print_url), stream=True)
print r.headers
size = int(r.headers['Content-Length'].strip())

bytes = 0
fileb = []
for buf in r.iter_content(1024):
    if buf:
        fileb.append(buf)
        bytes += len(buf)
        print bytes, size, int(float(bytes) / float(size/100))

open("file.jpg", "w").write(b"".join(fileb))
import os
print size
print os.stat("file.jpg").st_size

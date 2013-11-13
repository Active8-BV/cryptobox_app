# coding=utf-8
import urllib
import BeautifulSoup
l = []
for i in range(1, 21):
    break
    #u = "http://www.searchquotes.com/search/Privacy/"+str(i)+"/"
    #c = urllib.urlopen(u).read()

    c = open("./searchquotes/"+str(i)+".html").read()
    b = BeautifulSoup.BeautifulSoup(c)
    item = {}

    for a in b.findAll("a"):

        try:
            if a["class"] == "mainquote":
                item["text"] = a["title"]
            if a["class"] == "authorlink":
                item["author"] = a.text.replace("&nbsp;", "")

                l.append(item)
                item = {}


        except:
            pass
import pickle
open("list.pickle", "w").write(pickle.dumps(l))


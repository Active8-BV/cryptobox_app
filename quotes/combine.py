# coding=utf-8

import pickle
l = pickle.load(open("quotes.list"))

l2 = pickle.load(open("list.pickle"))
print len(l)

for i in l2:
    l.append((i["text"], i["author"]))
print len(l)
l = list(set(l))
print len(l)
pickle.dump(l, open("quotes2.list", "w"))

# coding=utf-8

def foo():
    x = 4
    l = [x]
    def bar():
        l[0] = 1
    bar()
    x = l[0]
    return x

if __name__=="__main__":
    print foo()

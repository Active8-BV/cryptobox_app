# coding=utf-8
import os

def get_code(flist, header="", footer=""):
    code = header
    for i in flist:
        if not os.path.exists(i):
            raise Exception("file not found "+str(i))
        code += open(i, "r").read()
    code += footer 
    return code 


def main():

    flist = list()
    flist.append("./source/lib/angular.min.js")
    flist.append("./source/app.js")
    code = get_code(flist)
    open("./Cryptobox/Resources/cryptobox_app.js", "w").write(code)

    flist = list()
    flist.append("./source/app.py")
    code = get_code(flist)    
    open("./Cryptobox/Resources/cryptobox_app.py", "w").write(code)
    
if __name__ == "__main__":
    main()


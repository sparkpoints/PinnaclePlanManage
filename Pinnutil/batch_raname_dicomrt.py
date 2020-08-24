# coding:utf-8

import os
import shutil

if __name__ == "__main__":
    tgt = "/media/PinnSETemp/DICOM/PA0/ST0/SE1"
    dst = "/media/PinnSETemp/DICOM/PA0/ST0/SE0"

    for file in os.listdir(tgt):
        oldname = file
        newname = oldname + '.dcm'
        shutil.copy2(os.path.join(tgt,oldname),os.path.join(dst,newname))
        print oldname,newname

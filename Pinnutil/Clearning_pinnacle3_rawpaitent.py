#! /usr/bin/env python
# coding=utf-8
# using a logfile (findedfile) finded parsed file in sourcepath, then copy it to target path

import os
import re
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='myapp.log',
                    filemode='w')
# 定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def CleaningPatientPool(poolpath):
    MatchRegList = ['^.auto.plan*',
                    '.ErrorLog$',
                    '.Transcript$',
                    '.defaults$',
                    '.pinnbackup$',
                    '^Institution.\d+',
                    '^Patient.\d+',
                    '\s*~\s*',
                    '.json$']

    for dirpath, dirname, filenames in os.walk(poolpath):
        for file in filenames:
            filepath = os.path.join(dirpath, file)
            if os.path.islink(filepath):
                os.remove(filepath)
                continue
            for currentReg in MatchRegList:
                if re.findall(currentReg, file):
                    os.remove(filepath)
                    print('del:%s\n' % filepath)
        if dirname:
            for currendir in dirname:
                CleaningPatientPool(os.path.join(dirpath,currendir))


if __name__ == "__main__":

    work_path = '/home/peter/PinnWork/'
    targetpath = os.path.join(work_path, 'Accuracy','Mount_Lung12')
    if os.path.isdir(targetpath):
        CleaningPatientPool(targetpath)
    else:
        logging.debug("not fined %s", targetpath)

    logging.info('End of Program!')

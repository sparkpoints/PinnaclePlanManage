#! /usr/bin/env python
# coding=utf-8
# 2010-2017.12 all Patients tars in one place
# this scripts used to batch find and restore to remote server1(10.36.126.101)
import os
import logging
import FTP_Module

PINN_TRA_PATH = '/media/peter/BACKUP/Pinnacle_Backup2010-2017/'
WORKING_PATH = '/home/peter/PinnWork'
LOCAL_DIR_PATH = os.path.join(WORKING_PATH, 'export')
WANTED_LIST = os.path.join(WORKING_PATH, 'WantedList')

FTP_IP = '10.36.126.101'
FTP_USER = 'p3rtp'
FTP_PASSWD = 'p3rtp123'
FTP_REMOTE_PATH = '/home/p3rtp/Pinnacle_Server1'


def RetorePinnPatients(localDirPath, wantedFile, targetDirPath, loggerHand, ftpMode=True,):
    wantedList = []
    if ftpMode:
        ftpHandle = FTP_Module.myFtp(FTP_IP)
        ftpHandle.Login(FTP_USER, FTP_PASSWD)
        targetDirPath = os.path.basename(FTP_REMOTE_PATH)
        ftpHandle.changePath(targetDirPath)
    try:
        fileHand = open(wantedFile, 'r')
        for mrn in fileHand.readlines():
            wantedList.append(mrn.strip())
    except IOError:
        raise
    localFileList = os.listdir(localDirPath)
    ind = 1
    for tarFile in localFileList:
        curMRN = tarFile.split('_')[1]
        if curMRN in wantedList:
            loggerHand.info(tarFile)
            if ftpHandle and not ftpHandle.isExist(tarFile, '.'):
                #print("upload file %s", ind, tarFile)
                loggerHand.info("uploadFile(%d of %d):%s",
                                (ind, len(wantedList), tarFile))
                ind += 1
                ftpHandle.UpLoadFile(os.path.join(
                    localDirPath, tarFile), tarFile)


if __name__ == "__main__":
    logger = logging.getLogger('batch restoe pinnalce')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info('begin!')
    RetorePinnPatients(PINN_TRA_PATH, WANTED_LIST,
                       LOCAL_DIR_PATH, logger, True)

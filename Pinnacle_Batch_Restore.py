#! /usr/bin/env python
# coding=utf-8

import os
import re
import shutil
import time


# 删除Pinnacle 3 TPS native file，匹配的规则如下（删除），同时检测link文件（删除）
# 输入参数，rootpath，和logobject文件指针
def CleaningPatientPool(poolpath, logfile):
    MatchRegList = ['^.auto.plan*',
                    '.ErrorLog$',
                    '.Transcript$',
                    '.defaults$',
                    '.pinnbackup$',
                    '^Institution.\d+',
                    '^Patient.\d+',
                    '\s*~\s*']
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
                    logfile.write('del:%s\n' % filepath)
# serachpat是Pinnacle文件的root目录\
# PatientListFile是一个csv文件，记录整个数据库中病例基本信息
# Wantedfiel 是需要查找并列的病例好列表，每个MRN一列
# logobj，log文件指针


def GetPatientPath(searchPath1, searchPath2, PatientListFile, WantedFile, logobj):
    wantedList = []
    PatientList = open(PatientListFile, 'r').read().split('\n')
    WantedList = open(WantedFile, 'r').read().split('\n')

    for wantedPatient in WantedList:
        if wantedPatient == '':
            continue
        for PatientInfo in PatientList:
            patientInfoList = PatientInfo.split(',')
            wantedPatientList = wantedPatient.split(',')
            if wantedPatientList[0] is None:
                continue
            elif len(patientInfoList) < 4:
                continue
            else:
                if wantedPatientList[0] == patientInfoList[0]:
                    if re.findall('tar', patientInfoList[3]):
                        #path = os.path.join(searchPath1,patientInfoList[3])
                        path = searchPath1 + patientInfoList[3]
                    else:
                        #path = os.path.join(searchPath2,patientInfoList[3])
                        path = searchPath2 + patientInfoList[3]
                    logobj.write('%s,%s\n' %
                                 (patientInfoList[0], patientInfoList[3]))
                    wantedList.append(path)
                    print PatientInfo
    return wantedList

# 对比2个CSV文件，
# 在logobj文件中列出2着差异：in 2 not 1：XXXX；in 1 not 2：XXXX


def compareTwoCSVfile(firstfile, secendfile, logobj):
    firstlist = open(firstfile, 'r').read().split('\n')
    seconlist = open(secendfile, 'r').read().split('\n')

    # create_difference log files
    basepath = os.path.split(firstfile)[0]
    differences = os.path.join(basepath, 'differences.cvs')
    diffObj = open(differences, 'w+')

    diffObj.write('In %s Not In %s' % (firstfile, secendfile))
    for line1 in firstlist:
        if line1 in seconlist:
            continue
        else:
            diffObj.write('%s\n' % line1)
            logobj.write('%s\n' % line1)

    diffObj.write('In %s Not In %s' % (secendfile, firstfile))
    for line2 in seconlist:
        if line2 in firstlist:
            continue
        else:
            diffObj.write('%s\n' % line2)
            logobj.write('%s\n' % line2)

    diffObj.close()
    return differences
# PatientPathList,需要恢复的病例的位置（abs——path）
# targetDirpath，如果ftp模式，是remote的machine上的目录；否则是本机上的目录
# ftpobj，ftp实例，
# logobj，logfile


def RetorePinnPatients(PatientPathList, targetDirPath, ftpObj, logobj):
    RestoredList = []
    totallist = len(PatientPathList)
    i = 0
    for line in PatientPathList:
        i = i + 1
        print("Total %d, Current:%d,oriloca%s" % (totallist, i, line))
        localfile = os.path.basename(line)
        remotedirname = ''
        if localfile in RestoredList:
            print("Dir %s, already upload" % localfile)
            continue

        if ftpObj is None:
            remotedirname = os.path.basename(line)
            remotedirname = os.path.join(remoteDirPath, remotedirname)
            print('copy file: %s ....\n' % remotedirname)
            if os.path.isfile(line):
                shutil.copy(line, remotedirname)
            elif os.path.isdir(line):
                # CleaningPatientPool(line, logobj)  # remove unuseful files like .auto.save....
                try:
                    shutil.copytree(line, remotedirname,
                                    symlinks=True, ignore=None)
                except IOError, os.error:
                    continue
            RestoredList.append(os.path.basename(line))
            logobj.write("copy:%s \n" % line)
        else:

            remotefiles = ftpObj.listDir(targetDirPath)  # get remote file list
            if localfile in remotefiles:
                print('remote dir %s exist, skip!\n' % localfile)
                logobj.write('remote dir %s exist, skip!\n' % localfile)
            elif os.path.isfile(line):
                ftpObj.UpLoadFile(line, targetDirPath)
            elif os.path.isdir(lien):
                print('FTP file: %s...\n' % locafile)
                # CleaningPatientPool(line, logobj)  # remove unuseful files like .auto.save....
                ftpObj.UpLoadFileTree(line, targetDirPath)
            RestoredList.append(os.path.basename(line))
            logobj.write("copy:%s \n" % line)

    return True


if __name__ == "__main__":
    #sourcepath = "/Volumes/PinnSETemp/NewPatients/"
    PinnPatientPool = '/media/PinnSETemp/NewPatients/'
    PinnPatientTars = '/media/peter/BACKUP'
    basepath = "/home/peter/python/"
    #remoteDirPath   = '/PrimaryPatientData/BetaPatients/import/'
    remoteDirPath = "/home/peter/export/"
    PatientsRecordListFile = os.path.join(basepath, 'PPP_ 2017_final.csv')
    PatientWantedListFile = os.path.join(basepath, 'WantedList.csv')
    FirstRecord = os.path.join(basepath, 'first.csv')
    secendRecord = os.path.join(basepath, 'secend.csv')

    filename = time.asctime() + '.csv'
    listfile = os.path.join(basepath, filename)
    outobj = open(listfile, 'w+')

    # CleaningPatientPool('/media/PinnSETemp/NewPatients/',outobj)
    ftpobj = None
    # ftpobj = FTP_Module.myFtp('10.36.126.101')
    # ftpobj.Login('p3rtp','p3rtp123')
    #
    #
    #
    # #FTP2Pinnacle('/home/peter/Python/cron',remoteDirPath)
    # compareTwoCSVfile(FirstRecord,secendRecord,outobj)
    PatientPathList = GetPatientPath(
        PinnPatientTars, PinnPatientPool, PatientsRecordListFile, PatientWantedListFile, outobj)
    StatesIndex = RetorePinnPatients(
        PatientPathList, remoteDirPath, ftpobj, outobj)
    # ftpobj.close()
    outobj.close()
    print "end"

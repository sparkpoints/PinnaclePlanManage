# coding:utf-8
from ctypes import *
import os
import sys
import ftplib

class ftpExt(object):
    ftp = ftplib.FTP()
    bIsDir = False
    path = ""

    def __init__(self, host, port='21'):
        # self.ftp.set_debuglevel(2) #打开调试级别2，显示详细信息
        # self.ftp.set_pasv(0)      #0主动模式 1 #被动模式
        self.ftp.connect(host, port)

    def Login(self, user, passwd):
        self.ftp.login(user, passwd)
        print(self.ftp.welcome)

    def DownLoadFile(self, LocalFile, RemoteFile):
        file_handler = open(LocalFile, 'w')
        self.ftp.retrlines("RETR %s" % (RemoteFile), file_handler.write)
        file_handler.close()
        return True

    def UpLoadFile(self, LocalFile, RemoteFile):
        if os.path.islink(LocalFile):
            return False
        if not os.path.isfile(LocalFile):
            return False
        file_handler = open(LocalFile, "rb")
        self.ftp.storbinary('STOR %s' % RemoteFile, file_handler, 4096)
        file_handler.close()
        return True

    def UpLoadFileTree(self, LocalDir, RemoteDir):
        if not os.path.isdir(LocalDir):
            return False
        # print "LocalDir:", LocalDir
        LocalNames = os.listdir(LocalDir)
        basename = os.path.basename(LocalDir)
        oldpath = self.ftp.pwd()
        # self.ftp.cwd("/")
        self.ftp.cwd(RemoteDir)
        filelist = self.ftp.nlst()
        if basename in filelist:
            print("%s exist" % basename)
            return
        else:
            self.ftp.mkd(os.path.basename(LocalDir))
        # self.ftp.mkd(os.path.basename(LocalDir))
        remotedirs = os.path.join(RemoteDir, os.path.basename(LocalDir))
        self.ftp.cwd(remotedirs)
        for Local in LocalNames:
            src = os.path.join(LocalDir, Local)
            if os.path.isdir(src):
                self.UpLoadFileTree(src, remotedirs)
            else:
                self.UpLoadFile(src, Local)
        self.ftp.cwd(oldpath)
        return

    def DownLoadFileTree(self, LocalDir, RemoteDir):
        print("remoteDir:", RemoteDir)
        if not os.path.isdir(LocalDir):
            os.makedirs(LocalDir)
        self.ftp.cwd(RemoteDir)
        RemoteNames = self.ftp.nlst()
        print("RemoteNames", RemoteNames)
        print(self.ftp.nlst("/del1"))
        for file in RemoteNames:
            Local = os.path.join(LocalDir, file)
            if self.isDir(file):
                self.DownLoadFileTree(Local, file)
            else:
                self.DownLoadFile(Local, file)
        self.ftp.cwd("..")
        return

    def show(self, list):
        result = list.lower().split(" ")
        if self.path in result and "<dir>" in result:
            self.bIsDir = True

    def isDir(self, path):
        self.bIsDir = False
        self.path = path
        # this ues callback function ,that will change bIsDir value
        self.ftp.retrlines('LIST', self.show)
        return self.bIsDir

    def listDir(self, path):
        self.path = path
        self.ftp.cwd(path)
        return self.ftp.nlst()

    def isExist(self, fileName, dirName):
        filelist = self.listDir(dirName)
        if fileName in filelist:
            return True
        else:
            return False

    def close(self):
        self.ftp.quit()

    def changePath(self, path):
        self.ftp.cwd(path)


if __name__ == "__main__":
    ftp = ftpExt('*****')
    ftp.Login('***', '***')

    ftp.DownLoadFileTree('del', '/del1')  # ok
    ftp.UpLoadFileTree('del', "/del1")
    ftp.close()
    print('end\n')

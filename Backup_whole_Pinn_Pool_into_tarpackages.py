#!/usr/bin/env python
# coding=utf-8
# usage:
# tar whole pinnacle Database into seperated tar packages
#
import os
import re
import time
import shutil
import csv
#from Pinnutil.untar_old_pinnacle_backup_file import untar_old_pinnacle_backup_file
from Pinnutil.parse_single_pinn_file import parse_single_pinn_file
from Pinnutil.tar_one_pinn_patient import tar_one_pinn_patient
from Pinnutil.scan_standard_pinn_DB import scan_standard_pinn_DB
DEBUG = 0

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


                    # logfile.write('del:%s\n'%filepath)
if __name__ == "__main__":
    # 工作路径
    work_path = "/home/peter/PinnWork"
    # 头文件模板
    inst_template = os.path.join(work_path, 'institution_template')
    # 源文件夹，旧病例存储
    old_Pinn_pool = '/media/PinnSETemp/tarPatients/'
    #old_Pinn_pool = '/media/peter/BACKUP/PinnX86/test/'
    # 新生成压缩包的归档文件夹
    new_Pinn_pool = '/media/peter/BACKUP2/Pinn2018/'

    # log
    #filename = time.asctime() + '.log'
    listfile = os.path.join(work_path, 'PPP' + time.asctime() + '.csv')

    logobj = open(listfile, 'w+')
    #csvobj = csv.writer(logobj,)

    report_file = os.path.join(work_path, 'PPP' + time.asctime() + '.report')

    i = 1
    obj1 = scan_standard_pinn_DB(old_Pinn_pool, report_file)
    finished_list = os.listdir(new_Pinn_pool)
    inst_lists = obj1.get_institution_list()
    for inst in inst_lists:
        for data_dir in obj1.get_patient_list_in_inst(inst):
            print i
            i = i + 1
            if data_dir:
                # Step1: 生成新的文件压缩包，targzip打包压缩，返回压缩包的绝对路径
                patient_obj = parse_single_pinn_file(
                    os.path.join(data_dir, 'Patient'))
                if patient_obj:
                    patient_info = patient_obj.get_patient_data()
                    if not patient_info:
                        print "not a validate patient dir, next"
                        continue
                    finished = 0
                    for line in finished_list:
                        tar_id = patient_info['PatientID'] + \
                            '_' + patient_info['MedicalRecordNumber']
                        if re.search(tar_id, line):
                            finished = 1
                            break
                    if finished:
                        print "tar file exist! just skip to next file"
                    else:
                        new_tar_file = tar_one_pinn_patient(
                            inst_template, data_dir).get_tar_gzip_file()
                        if new_tar_file:
                            print '    Get New TarFile:', os.path.basename(
                                new_tar_file)
                            if not os.path.isfile(os.path.join(new_Pinn_pool, os.path.basename(new_tar_file))):
                                try:
                                    # Step4：移动到归档文件夹中
                                    shutil.move(new_tar_file, new_Pinn_pool)
                                except IOError or OSError:
                                    print "move fail!"
    logobj.close()
    print "finish"

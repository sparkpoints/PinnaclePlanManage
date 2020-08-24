#!/usr/bin/env python
# coding=utf-8
# usage:
# 早期Pinnacle3 TPS的压缩包，没有添加Institution头文件，Restore时，TPS无法直接识别
# 此程序的功能是：批量的将就压缩包，转换成TPS可以识别的新压缩包;1,增加Institution头文件，2,删除病例中无用的临时文件
#
import os
import re
import time
import shutil
from Pinnutil.untar_old_pinnacle_backup_file import untar_old_pinnacle_backup_file
from Pinnutil.tar_one_pinn_patient import tar_one_pinn_patient
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
    old_Pinn_pool = '/media/peter/BACKUP/PinnX86/PinnV80/'
    #old_Pinn_pool = '/media/peter/BACKUP/PinnX86/test/'
    # 新生成压缩包的归档文件夹
    new_Pinn_pool = '/media/peter/BACKUP/PinnX86/NewPinn/'

    # log
    filename = time.asctime() + '.log'
    listfile = os.path.join(work_path, filename)
    logobj = open(listfile, 'w+')

    i = 1
    for tar_file in os.listdir(old_Pinn_pool):
        print i
        i = i + 1
        current_tar_file = os.path.join(old_Pinn_pool, tar_file)

        if os.path.isfile(current_tar_file):
            # Step1:解压就压缩包,得到病例数据文件夹绝对路径
            data_dir = untar_old_pinnacle_backup_file(
                work_path, current_tar_file).untar_gzip_file()
            if data_dir:
                # 删除旧压缩包
                os.remove(current_tar_file)
                # Step2：删除病例数据中的临时文件
                CleaningPatientPool(data_dir, logobj)
                # Step3: 生成新的文件压缩包，targzip打包压缩，返回压缩包的绝对路径
                new_tar_file = tar_one_pinn_patient(
                    inst_template, data_dir).get_tar_gzip_file()
                if new_tar_file:
                    print '    Get New TarFile:', os.path.basename(new_tar_file)
                    logobj.write("convert:%s to %s\n" %
                                 (tar_file, new_tar_file))
                    # 删除临时临时病例文件夹
                    shutil.rmtree(data_dir)
                    if not os.path.isfile(os.path.join(new_Pinn_pool, os.path.basename(new_tar_file))):
                        # Step4：移动到归档文件夹中
                        try:
                            shutil.move(new_tar_file, new_Pinn_pool)
                        except IOError, OSError:
                            print "move fail!"
                    else:
                        print "file already exists"

    logobj.close()
    print "finish"

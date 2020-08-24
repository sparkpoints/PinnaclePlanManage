#! /usr/bin/env python
# coding = utf-8
import os
import re
import tarfile
import zlib

class untar_old_pinnacle_backup_file(object):
    def __init__(self, working_dir,backup_file):
        if not os.path.isfile(backup_file):
            print("No such file %s\n",backup_file)
        elif tarfile.is_tarfile(backup_file):
            print '  tar file is ok'
        self.working_dir = working_dir
        self.untar_file = backup_file
            # file_extension = filetype.guess(backup_file)
            # print file_extension.extension
    def untar_gzip_file(self):
        patient_dir_name = None
        gzip_file = self.untar_file
        if os.path.isfile(gzip_file) and tarfile.is_tarfile(gzip_file):
            print '  untar file:', os.path.basename(gzip_file), '....'
            try:
                Tar_obj = tarfile.open(gzip_file,'r:gz')
            except IOError or tarfile.ReadError:
                print "tar package broken"
                return None
            if Tar_obj:
                try:
                    name_list = Tar_obj.getnames()
                except IOError or zlib.error:
                    print "tar package broken"
                    return None
                for member_name in name_list:
                    if re.search('^Patient_\d+$',member_name):
                        patient_dir_name = os.path.join(self.working_dir,member_name)
                        try:
                            Tar_obj.extractall(self.working_dir)
                        except IOError or tarfile.ReadError:
                            print"extractfile Faile:", os.path.basename(gzip_file)
                            return None
                        break
                print '  output dir:',os.path.basename(patient_dir_name)
            return patient_dir_name

    def get_untar_package(self):
        print "sss"

if __name__ == "__main__":
    work_path = "/home/peter/PinnWork"
    backup_dir_path = "/media/peter/BACKUP/PinnX86/NewPinn/"
    for file in os.listdir(backup_dir_path):
        untar_old_pinnacle_backup_file(work_path,os.path.join(backup_dir_path,file)).untar_gzip_file()
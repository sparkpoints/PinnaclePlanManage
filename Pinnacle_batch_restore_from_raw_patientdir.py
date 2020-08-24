# /usr/bin/env python

import os
import re
from Pinnutil.parse_single_pinn_file import parse_single_pinn_file
from Pinnutil.scan_standard_pinn_DB import scan_standard_pinn_DB
from Pinnutil.tar_one_pinn_patient import tar_one_pinn_patient

DEBUG = 0
MKDIR = '/bin/mkdir'
TAR = '/bin/tar'
COPY = '/bin/cp'
GZIP = '/bin/gzip'
MOVE = '/bin/mv'
DELETE = '/bin/rm'


def tar_one_institution(inst_base_path, patient_list_in_inst):
    i = 1
    for target_patient in patient_list_in_inst:
        print("Number:%d" % i)
        tar_one_pinn_patient(inst_base_path, target_patient).creat_tar_file()
        i = i + 1


def batch_build_restore_tarfiles(work_dir, backup_dir):
    root_path = work_dir
    inst_template = os.path.join(root_path, 'institution_template')
    #tar_obj = tar_one_pinn_patient(root_path,inst_template)
    list_dir = os.listdir(backup_dir)
    #work_base = os.path.split(backup)
    for dir_target in list_dir:
        if re.match('Patient_\d+', dir_target):
            # tar_obj.creat_tar_file(os.path.join(backup_dir,dir_target))
            target_dir = os.path.join(backup_dir, dir_target)
            print tar_one_pinn_patient(inst_template, target_dir).get_tar_gzip_file()
        else:
            print("Not Pinnacle3 fiel%s" % dir_target)


if __name__ == "__main__":
    #patientfile =  "/home/peter/Patient_30942/Patient"
    # obj1 = parse_single_pinn_file(patientfile)
    # print(obj1.get_patient_data())
    #root_path = "/PrimaryPatientData/BetaPatients"
    root_path = "/home/peter/PinnWork"
    import_dir = "/media/peter/BACKUP/PinnX86/NewPinn/"
    inst_template = os.path.join(root_path, 'institution_template')
    record_file = "/home/peter/testlog"

    batch_build_restore_tarfiles(root_path, import_dir)
    #patientfile = "/PrimaryPatientData/BetaPatients/Patient_23615"
    #obj3 = tar_one_pinn_patient(root_path,inst_template)
    # obj3.creat_tar_file(patientfile)
    #obj2 = scan_standard_pinn_DB(root_path,record_file)
    #institution_list = obj2.get_inistitution_list()
    # if 'Institution_3781' in institution_list:
    #    tar_one_institution(root_path,obj2.get_patient_ref_path_in_inst('Institution_3781'))
    # obj2.print_whole_patients_in_DB()
    # obj2.create_patient_list_record()
    print "finish"

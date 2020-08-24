#! /usr/bin/env python
# coding=utf-8
# input: 1: PinnaclePool_dir"/PrimaryPatient/NewPatient",2:logfile
# output：a inst_list = obj.get_institution_list
import os
import re
from Pinnutil.parse_single_pinn_file import parse_single_pinn_file


class scan_standard_pinn_DB(object):
    def __init__(self, root_path, record_file):
        self.root_path = root_path
        self.record_file = record_file
        self.inst_list = []
        self.pat_list = []

    def get_institution_list(self):
        temp_list = os.listdir(self.root_path)
        for line in temp_list:
            if re.match('Institution_\d+', line):
                self.inst_list.append(line)
        return self.inst_list
    # full path of Patient dir

    def get_patient_list_in_inst(self, institution_name):
        current_pat_list = []
        current_inst_pat_pool_path = os.path.join(
            self.root_path, institution_name, 'Mount_0')
        if os.path.isdir(current_inst_pat_pool_path):
            temp_list = os.listdir(current_inst_pat_pool_path)
            for patient in temp_list:
                if re.match('Patient_\d+', patient):
                    current_pat_list.append(os.path.join(
                        current_inst_pat_pool_path, patient))
        return current_pat_list
    # related path to PinnaclePoolBaseDir like "/PrimaryPatient/NewPatient" + RefPath = absPath

    def get_patient_ref_path_in_inst(self, institution_name):
        patient_path_list = []
        current_inst_pat_pool_path = os.path.join(
            self.root_path, institution_name, 'Mount_0')
        if os.path.isdir(current_inst_pat_pool_path):
            temp_list = os.listdir(current_inst_pat_pool_path)
            for patient in temp_list:
                if re.match('Patient_\d+', patient):
                    ref_path = institution_name + '/Mount_0/' + patient
                    patient_path_list.append(ref_path)
        return patient_path_list

    def print_insts(self):
        if self.inst_list is None:
            self.get_inistitution_list()
        print(self.inst_list)

    def print_whole_patients_in_DB(self):
        for list in self.inst_list:
            i = 1
            # patient_list = obj2.get_patient_list_in_inst(list)
            patient_list = obj2.get_patient_ref_path_in_inst(list)
            total_patients = len(patient_list)
            print("Institution:%s, TotalPaitents:%d" % (list, total_patients))
            # for patient in patient_list:
            #     # print ("%d of Total %d Patients, PatientName:%s"%(i,total_patients,patient))
            #     i = i + 1

    def get_number_patients(self, institution_name):
        current_pat_list = []
        current_inst_pat_pool_path = os.path.join(
            self.root_path, institution_name, 'Mount_0')
        if os.path.isdir(current_inst_pat_pool_path):
            temp_list = os.listdir(current_inst_pat_pool_path)
            number_patients = len(temp_list)
        return number_patients

    def create_patient_list_record(self):
        record_obj = open(self.record_file, 'w+')
        for list in self.inst_list:
            print("working inst:", list)
            for patient in obj2.get_patient_ref_path_in_inst(list):
                current_pat_path = os.path.join(self.root_path, patient)
                if os.path.isdir(current_pat_path):
                    patient_info = os.path.join(current_pat_path, 'Patient')
                    print patient_info
                    if os.path.isfile(patient_info):
                        data = parse_single_pinn_file(
                            patient_info).get_patient_data()
                        record_obj.write("%s,%s%s,%s,%s\n" % (data['MedicalRecordNumber'],
                                                              data['LastName'],
                                                              data['FirstName'],
                                                              data['PatientID'],
                                                              data['MiddleName']))
        record_obj.close()


if __name__ == "__main__":
    root_path = "/media/PinnSETemp/NewPatients"
    record_file = "/home/peter/testlog"
    obj2 = scan_standard_pinn_DB(root_path, record_file)
    institution_list = obj2.get_institution_list()
    i = 0
    for inst in institution_list:
        i = i + obj2.get_number_patients(inst)
        print i
    #     tar_one_institution(root_path,obj2.get_patient_ref_path_in_inst('Institution_3781'))
    # obj2.print_whole_patients_in_DB()
    # obj2.create_patient_list_record()
    print "finish"

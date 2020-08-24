#! /usr/bin/env python
# coding=utf-8
import os
import re
import subprocess

MKDIR = '/usr/bin/mkdir'
TAR = '/usr/sfw/bin/gtar'
COPY = '/usr/bin/cp'
GZIP = '/usr/bin/gzip'
MOVE = '/usr/bin/mv'


class parse_single_pinn_file(object):
    '''parse simple pinnacle TPS raw data file,
    like:"patient" text format file
    return a dict object:dict[var_name] = value'''

    def __init__(self, file_path):
        self.file = file_path
        if os.path.isfile(self.file):
            self.file_obj = open(self.file)
            self.patient_data = self.readsinglefile(self.file_obj)
            self.file_obj.close()

    def get_patient_data(self):
        return self.patient_data

    def readsinglefile(self, file_obj):
        PatientData = {}
        if file_obj:
            for line in file_obj.readlines():
                if not re.search('\=', line):
                    '''only parse line in style "var_name = value;",
                    escape all other lines'''
                    continue
                elif re.search('CreateTimeStamp', line):
                    continue
                elif re.search('^DirSize*', line):
                    '''sub_function exit port
                    DirSize is the final line of Pinn Patient file'''
                    (key, value) = self.readSingleValue(line)
                    PatientData[key] = value
                    return PatientData
                elif re.search('^  CreateTimeStamp*', line):
                    '''there many createTimestamp,only record this line'''
                    (key, value) = readSingleValue(line)
                    PatientData[key] = value
                else:
                    (key, value) = self.readSingleValue(line)
                    PatientData[key] = value

    def readSingleValue(self, str):
        ''' parse one line "var_name = value;",
        return (var_name, value)'''
        str = str.strip()
        if re.search('\;', str):
            str = str[0:-1]
        str = str.replace("\"", '')
        data = str.split('=')
        return (data[0].strip(), data[1].strip())


class scan_standard_pinn_DB(object):
    def __init__(self, root_path, record_file):
        self.root_path = root_path
        self.record_file = record_file
        self.inst_list = []
        self.pat_list = []

    def get_inistitution_list(self):
        temp_list = os.listdir(self.root_path)
        for line in temp_list:
            if re.match('Institution_\d+', line):
                self.inst_list.append(line)
        return self.inst_list

    def get_patient_list_in_inst(self, institution_name):
        current_pat_list = []
        current_inst_pat_pool_path = os.path.join(
            self.root_path, institution_name, 'Mount_0')
        if os.path.isdir(current_inst_pat_pool_path):
            temp_list = os.listdir(current_inst_pat_pool_path)
            for patient in temp_list:
                if re.match('Patient_\d+', patient):
                    current_pat_list.append(patient)
        return current_pat_list

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
            #patient_list = obj2.get_patient_list_in_inst(list)
            patient_list = obj2.get_patient_ref_path_in_inst(list)
            total_patients = len(patient_list)
            print("Institution:%s, TotalPaitents:%d" % (list, total_patients))
            for patient in patient_list:
                #print ("%d of Total %d Patients, PatientName:%s"%(i,total_patients,patient))
                i = i + 1

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


class tar_one_pinn_patient(object):
    def __init__(self, working_dir, target_dir):
        self.working_basedir = working_dir
        self.data_dir = target_dir
        patient_obj = parse_single_pinn_file(
            os.path.join(working_dir, target_dir, 'Patient'))
        self.patient_info = patient_obj.get_patient_data()
        self.relative_path = self.patient_info['PatientPath']

    def get_inst_header_template(self, patient_info):
        template_pool = '/home/p3rtp/document/'
        PatientPath = patient_info['PatientPath']
        inst_name = PatientPath.split('/')[0]
        temp_path = os.path.join(template_pool, inst_name)
        return temp_path

    def create_inst_header(self, inst_template, patient_info):
        patientData = patient_info
        source_file = inst_template
        #base_dir  = os.path.base(source_file)
        target_file = os.path.join(self.working_basedir, 'Institution')
        sourceObj = open(source_file, 'r')
        headerObj = open(target_file, 'w+')

        PatientPath = patientData['PatientPath']
        inst_name = PatientPath.split('/')[0]
        inst_number = inst_name.split('_')[-1]
        formatted_str = patientData['LastName'] + '&&' \
            + patientData['FirstName'] + '&&' \
            + patientData['MedicalRecordNumber'] + '&&' \
            + patientData['RadiationOncologist'] + '&&' \
            + patientData['WriteTimeStamp']
        for line in sourceObj.readlines():
            if re.search('^InstitutionID*', line):
                headerObj.write("InstitutionID = %s;\n" % inst_number)
                continue
            elif re.search('^InstitutionPath*', line):
                headerObj.write("InstitutionPath = \"%s\";\n" % inst_name)
                continue
            elif re.search('^PinnInstitutionPath*', line):
                headerObj.write("PinnInsitutionPath = \"%s\";\n" % inst_name)
                continue
            elif re.search('^    PatientID*', line):
                headerObj.write('    ')
                headerObj.write("PatientID = %s;\n" % patientData['PatientID'])
                continue
            elif re.search('^    PatientPath*', line):
                headerObj.write('    ')
                headerObj.write("PatientPath = \"%s\";\n" %
                                patientData['PatientPath'])
                continue
            elif re.search('^    FormattedDescription*', line):
                headerObj.write('    ')
                headerObj.write(
                    "FormattedDescription = \"%s\";\n" % formatted_str)
                continue
            elif re.search('^    DirSize*', line):
                headerObj.write('    ')
                headerObj.write("DirSize = %s;\n" % patientData['DirSize'])
                continue
            else:
                headerObj.write(line)
        headerObj.close()
        return target_file

    def creat_tar_file(self):
        patientData = self.patient_info
        refpath = self.relative_path
        #inst_template = self.get_inst_header_template(patientData)
        inst_template = "/home/p3rtp/document/institution_template"
        inst_header = self.create_inst_header(inst_template, patientData)

        tarFile = patientData['MedicalRecordNumber'] + \
            patientData['LastName'] + patientData['FirstName'] + '.tar.gz'
        tarName = ''.join(tarFile.split())
        os.chdir(self.working_basedir)
        command = ' --add-file=' + refpath
        command = TAR + ' -czf ' + tarName + ' Institution ' + command
        print("tar....%s\n" % tarName)
        # print command
        os.system(command)
        subprocess.call([MOVE, tarName, '/home/p3rtp/document'])


def tar_one_institution(inst_base_path, patient_list_in_inst):
    i = 1
    for target_patient in patient_list_in_inst:
        print("Number:%d" % i)
        tar_one_pinn_patient(inst_base_path, target_patient).creat_tar_file()
        i = i + 1


if __name__ == "__main__":
    #patientfile =  "/home/peter/Patient_30942/Patient"
    # obj1 = parse_single_pinn_file(patientfile)
    # print(obj1.get_patient_data())

    #patientfile = "/PrimaryPatientData/NewPatients/Institution_2941/Mount_0/Patient_15296"
    #obj3 = tar_one_pinn_patient('/PrimaryPatientData/NewPatients',patientfile)
    # obj3.creat_tar_file()

    root_path = "/PrimaryPatientData/NewPatients"
    record_file = "/home/p3rtp/document/testlog"
    obj2 = scan_standard_pinn_DB(root_path, record_file)
    institution_list = obj2.get_inistitution_list()
    if 'Institution_3781' in institution_list:
        tar_one_institution(
            root_path, obj2.get_patient_ref_path_in_inst('Institution_3781'))
    # obj2.print_whole_patients_in_DB()
    # obj2.create_patient_list_record()
    print "finish"

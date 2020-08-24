#! /usr/bin/env python
# coding=utf-8
# input: file "/home/peter/Patient_6527/Patient"
# output：a dict = obj.get_patient_data
import os
import re


class parse_single_pinn_file(object):
    '''parse simple pinnacle TPS raw data file,
    like:"patient" text format file
    return a dict object:dict[var_name] = value'''

    def __init__(self, file_path):
        self.file = file_path
        self.patient_data = None

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


if __name__ == "__main__":
    patientfile = "/home/peter/Patient_6527/Patient"
    obj1 = parse_single_pinn_file(patientfile)
    print(obj1.get_patient_data())

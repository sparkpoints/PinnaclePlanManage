#! /usr/bin/env python
# coding=utf-8
import os
import re
import time
import subprocess
import shutil

MKDIR = '/bin/mkdir'
TAR = '/usr/bin/tar'
COPY = '/bin/cp'
GZIP = '/usr/bin/gzip'


def readsinglefile(file):

    fobj = open(file, 'r')

    PatientData = {}
    for line in fobj.readlines():
        if not re.search('\=', line):
            continue
        elif re.search('^DirSize*', line):
            (key, value) = readSingleValue(line)
            PatientData[key] = value
            return PatientData
        elif re.search('^PatientID*', line):
            (key, value) = readSingleValue(line)
            PatientData[key] = value
        elif re.search('^PatientPath*', line):
            (key, value) = readSingleValue(line)
            PatientData[key] = value
        elif re.search('^LastName*', line):
            (key, value) = readSingleValue(line)
            PatientData[key] = value
        elif re.search('^FirstName*', line):
            (key, value) = readSingleValue(line)
            PatientData[key] = value
        elif re.search('^MiddleName*', line):
            (key, value) = readSingleValue(line)
            PatientData[key] = value
        elif re.search('^MedicalRecordNumber*', line):
            (key, value) = readSingleValue(line)
            PatientData[key] = value
        elif re.search('^RadiationOncologist*', line):
            (key, value) = readSingleValue(line)
            PatientData[key] = value
        elif re.search('^  CreateTimeStamp*', line):
            (key, value) = readSingleValue(line)
            PatientData[key] = value
        else:
            continue

# return one line


def readSingleValue(str):
    str = str.strip()
    if re.search('\;', str):
        str = str[0:-1]
    str = str.replace("\"", '')
    data = str.split('=')
    return (data[0].strip(), data[1].strip())


def TarOnePinnPatientDir(workPath, templateFile, targetDir, LogFileObj):
    oldPath = os.getcwd()
    os.chdir(workPath)
    headerFile = '/Users/yang/python/Institution.template'
    InstitutionPath = ""
    if os.path.isdir(targetDir):
        patientInfo = os.path.join(targetDir, 'patient')
        patientData = readsinglefile(patientInfo)
        if os.path.isfile(templateFile):
            PatPath = patientData['PatientPath']
            pathList = PatPath.split('/')
            InstitutionPath = pathList[0]
            patientData['InstitutionPath'] = InstitutionPath
            PatientRefPath = pathList[-1]
            InstitutionID = InstitutionPath.split('_')[-1]
            patientData['InstitutionID'] = InstitutionID

            stringFormat = patientData['LastName'] + '&&' + patientData['FirstName'] + '&&' \
                + patientData['MiddleName'] + '&&' + patientData['MedicalRecordNumber'] + '&&' \
                + patientData['RadiationOncologist'] + '&&'
            patientData['FormattedDescription'] = stringFormat
            headerFile = CreateInstitutionHeader(
                workPath, templateFile, patientData)
    if headerFile is not None:
        if not os.path.isdir(os.path.join(os.getcwd(), InstitutionPath)):
            subprocess.call([MKDIR, InstitutionPath])
            oldPaht2 = os.getcwd()
            os.chdir(InstitutionPath)
            subprocess.call([MKDIR, 'Mount_0'])
            os.chdir(oldPaht2)
        tarFile = patientData['MedicalRecordNumber'] + \
            patientData['LastName'] + patientData['FirstName'] + '.tar'
        tarName = ''.join(tarFile.split())
        InstitutionName = os.path.basename(headerFile)
        subprocess.call([TAR, '-cvf', tarName, InstitutionName])

        refpath = InstitutionPath + '/Mount_0'
        subprocess.call(
            [COPY, '-rf', targetDir, os.path.join(os.getcwd(), refpath, PatientRefPath)])
        refpath2 = refpath + '/' + PatientRefPath

        subprocess.call([TAR, '-rvf', tarName, refpath2])
        subprocess.call([GZIP, tarName])
        tmpInsti = os.path.join(workPath, InstitutionPath)
        shutil.rmtree(tmpInsti)
    os.chdir(oldPath)


def CreateInstitutionHeader(workpath, tempFile, patientData):
    headerfile = os.path.join(workpath, 'Institution')
    headerObj = open(headerfile, 'w+')
    space4 = '   '
    sourceObj = open(tempFile, 'r')
    for line in sourceObj.readlines():
        if re.search('^InstitutionID*', line):
            headerObj.write("InstitutionID = %s;\n" %
                            patientData['InstitutionID'])
            continue
        elif re.search('^InstitutionPath*', line):
            headerObj.write("InstitutionPath = %s;\n" %
                            patientData['InstitutionPath'])
            continue
        elif re.search('^PinnInstitutionPath*', line):
            headerObj.write("PinnInsitutionPath = %s;\n" %
                            patientData['InstitutionPath'])
            continue
        elif re.search('^    PatientID*', line):
            headerObj.write('    ')
            headerObj.write("PatientID = %s;\n" % patientData['PatientID'])
            continue
        elif re.search('^    PatientPath*', line):
            headerObj.write('    ')
            headerObj.write("PatientPath = %s;\n" % patientData['PatientPath'])
            continue
        elif re.search('^    FormattedDescription*', line):
            headerObj.write('    ')
            headerObj.write("FormattedDescription = %s;\n" %
                            patientData['FormattedDescription'])
            continue
        elif re.search('^    DirSize*', line):
            headerObj.write('    ')
            headerObj.write("DirSize = %s;\n" % patientData['DirSize'])
            continue
        else:
            headerObj.write(line)
    headerObj.close()
    return headerfile


if __name__ == "__main__":
    patientDir = "/Users/yang/Downloads/ESO/Patient_31113/"
    workDir = "/Users/yang/python/"
    InstitutionTemplate = os.path.join(workDir, "Institution.template")

    logFileName = time.asctime() + '.log'
    logFile = os.path.join(workDir, logFileName)
    logObj = open(logFile, 'w+')

    data = TarOnePinnPatientDir(
        workDir, InstitutionTemplate, patientDir, logObj)
    logObj.close()
    print(data)

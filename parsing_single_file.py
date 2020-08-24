#!/usr/bin/env python
# coding=utf-8
import os
import pinn
import pickle


def readPlanTrial(patientPlanDir):
    """
    Read all the information out of a plan.Trial file for a given patient plan directory.
    """


# planTrialFile = os.path.join(patientPlanDir,'Plan_0/plan.Trial')
    pinnFile = os.path.join(patientPlanDir, 'Patient')
    f = open(pinnFile)
    fileTxt = pinn.pinn2Json(f.read())
    f.close()

    f = open(pinnFile + '.json', 'w')
    f.write(fileTxt)
    f.close()
    data = pickle.loads(fileTxt)
    # planTrial = pinn.read(planTrialFile)
    # return planTrial


if __name__ == '__main__':
    patientPlanDir = '/Users/yang/Downloads/ESO/Patient_9122'
    planTrial = readPlanTrial(patientPlanDir)

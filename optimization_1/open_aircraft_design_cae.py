# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 15:07:59 2023

@author: jplilly25
"""

with open('inputs.txt', 'r') as fileObj:
    lines = fileObj.readlines()

skin_thickness = float(lines[0].split()[0])

allowable_strain = 4000e-6 # 4000 microstrain

model_name = 'Model-1'
segment_names = ['Segment-1', 'Segment-2']

numCpus = 4

# skin_thickness = 0.5

n_ply = 3.0 # NEEDS TO MATCH N-PLY IN "example_1_wing.py"
ply_thickness = skin_thickness / n_ply

#--------------------------------------------------
# LIBRARY IMPORT
#--------------------------------------------------
from abaqus import *
from abaqusConstants import *
from caeModules import *
from odbAccess import *

from odb_readout import odbPostProcess

#--------------------------------------------------
# HOUSEKEEPING LINES 
#--------------------------------------------------
# Line to save findAts instead of masks 
session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)
    
cae_name = 'aircraft_design_5.cae'

openMdb(pathName='C:/Users/jplilly25/Documents/SPARRO (Dec 2022 - Mar 2023)/Geometry Generation/Example 1/' + cae_name)

for segment_name in segment_names:
    layupOrientation = None
    p = mdb.models[model_name].parts[segment_name]
    region1 = p.sets['Skin']
    p = mdb.models[model_name].parts[segment_name]
    region2 = p.sets['Skin']
    p = mdb.models[model_name].parts[segment_name]
    region3 = p.sets['Skin']
    compositeLayup = mdb.models[model_name].parts[segment_name].compositeLayups['CompositeLayup-1']
    compositeLayup.orientation.setValues(additionalRotationType=ROTATION_NONE, 
        angle=0.0)
    compositeLayup.deletePlies()
    compositeLayup.suppress()
    compositeLayup.CompositePly(suppressed=False, plyName='Ply-0', region=region1, 
        material='Toray-T700G', thicknessType=SPECIFY_THICKNESS, thickness=ply_thickness, 
        orientationType=SPECIFY_ORIENT, orientationValue=0.0, 
        additionalRotationType=ROTATION_NONE, additionalRotationField='', 
        axis=AXIS_3, angle=0.0, numIntPoints=3)
    compositeLayup.CompositePly(suppressed=False, plyName='Ply-1', region=region2, 
        material='Toray-T700G', thicknessType=SPECIFY_THICKNESS, thickness=ply_thickness, 
        orientationType=SPECIFY_ORIENT, orientationValue=0.0, 
        additionalRotationType=ROTATION_NONE, additionalRotationField='', 
        axis=AXIS_3, angle=0.0, numIntPoints=3)
    compositeLayup.CompositePly(suppressed=False, plyName='Ply-2', region=region3, 
        material='Toray-T700G', thicknessType=SPECIFY_THICKNESS, thickness=ply_thickness, 
        orientationType=SPECIFY_ORIENT, orientationValue=0.0, 
        additionalRotationType=ROTATION_NONE, additionalRotationField='', 
        axis=AXIS_3, angle=0.0, numIntPoints=3)
    compositeLayup.resume()

job_name = model_name + '-job'

## Create the job and run it on N CPUs
mdb.Job(name=job_name, model=model_name, description='', type=ANALYSIS, 
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
    memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
    explicitPrecision=SINGLE, nodalOutputPrecision=FULL, echoPrint=OFF, 
    modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
    scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=numCpus, 
    numDomains=numCpus, numGPUs=0)

## Submit and wait for the job to complete
job = mdb.jobs[job_name]
job.submit()
job.waitForCompletion()

## Post-processing
elsetNames = ['SEGMENT-1', 'SEGMENT-2']

results = odbPostProcess(JobName=job_name, elsetNames=elsetNames)

max_strain = results['stress']['SEGMENT-1']['Max_Strain'][-1]
min_strain = abs(results['stress']['SEGMENT-1']['Min_Strain'][-1])

critical_strain = max([min_strain, max_strain])

## Calculat the objective (want to minimize the difference in strain value)
U = abs(1.025 * critical_strain - allowable_strain)

with open('outputs.txt', 'w') as fileObj:
    fileObj.write(str(U))

with open('all_outputs.txt', 'a') as fileObj:
    fileObj.write('\t'.join([str(critical_strain), str(allowable_strain), str(U)]) + '\n')
    
    
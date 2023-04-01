"""
Description:
This script...

Skeleton script by:
Darren Hartl
Dept. of Aerospace Engineering
Texas A&M University
February 2013
"""

from abaqus import *
from abaqusConstants import *
import __main__
import section
import odbSection
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import job
import sketch
import visualization
import xyPlot
import connectorBehavior
import displayGroupOdbToolset as dgo

from math import atan, sin, cos, tan, sqrt
from Post_P_Script import getResults

session.journalOptions.setValues(replayGeometry=COORDINATE,recoverGeometry=COORDINATE)

##########################################
### Using Post-P Script to Get Results ###
##########################################

failure = False # represents if model has reach yield stress for either load 1 or 2

for loadn in range(1, 3): # Models/Loads 1 and 2
	ModelName = 'Model-%s' % (loadn)
	stepName = 'Load-%s' % (loadn)
	
	print 'Pulling data from ODB'
	results = getResults(ModelName, stepName, loadn)
	S = results[0]
	U = results[1]
	E = results[2]
	Un1 = results[3]
	Un2 = results[4]

	# Query Surface Area
	p = mdb.models[ModelName].parts['Fork-cm']
	SA = p.getArea(p.faces)

	# Query Volume
	a = mdb.models[ModelName].rootAssembly
	prop = a.getMassProperties()
	V = prop['volume']
	V *= 10**6 # converting to cm^3

	# DataFile = open('PostData.txt','a')
	# DataFile.write('%1.0f, %1.0f, ' % (modelNum, loadn)) 
	# for val in varValues:
		# DataFile.write('%s, ' % (val)) 
	# DataFile.write('%1.3f, %1.1f, %1.3f, %1.4f, %1.3f, %1.3f\n' % (SA/V, S/1000000, U*100, E, Un1*100, Un2*100)) 
	# DataFile.close()

	# writing outputs for optimization
	yield_stress = 60e6 # Source: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6926899/
	safety_factor = 1.2
	if S <= yield_stress*safety_factor and not failure:
		score = -SA/V # this is negative in order to maximize using scipy minimize
	else:
		failure = True
		score = 0
		
	with open('outputs.txt', 'w') as fileObj:
		fileObj.write(str(score))
	with open('all_outputs.txt', 'a') as fileObj:
		fileObj.write('%1.3f, %1.1f, %1.3f, %1.4f, %1.3f, %1.3f\n' % (SA/V, S/1000000, U*100, E, Un1*100, Un2*100)) 
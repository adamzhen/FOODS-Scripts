"""
...
"""

from abaqus import *
from abaqusConstants import *
import visualization
from viewerModules import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getResults(ModelName):

	"""
	This ODB reading script does the following:
	-Retrieves the displacement at TIPNODE
	-Scans for max. Mises stress in a part (if set exists)
	"""

	# Open the output database.
	print 'Made it in'
	odbName = ModelName+'.odb'
	print odbName
	odb = visualization.openOdb(odbName)
	lastFrame = odb.steps['Load-1'].frames[-1]
	print 'odb open'


	# # Selecting the node(s) to be queried
	# # pTip = odb.rootAssembly.nodeSets['TIPNODE']
		
	# # # Retrieve Y-displacements at the splines/connectors
	# # print 'Retrieving ALL final displacements at ALL points'
	# # dispField = lastFrame.fieldOutputs['U']

	# # print 'Retrieving ALL displacements at TIPNODE'
	# # dFieldpTip = dispField.getSubset(region=pTip)

	# # print 'Retrieving only U2 at TIPNODE'
	# # #Note, U1=data[0], U2=data[1], U3=data[2]
	# # disppTip = dFieldpTip.values[0].data[1]


	## The following is left for use in later probems/projects
	print 'Scanning the PART for maximum VM STRESS'
	elsetName=' ALL ELEMENTS'
	elset = elemset = None
	region = "over the entire model"
	assembly = odb.rootAssembly

	#Check to see if the element set exists
	#in the assembly

	if elsetName:
		try:
			elemset = assembly.elementSets[elsetName]
			region = " in the element set : " + elsetName;
		except KeyError:
			print 'An assembly level elset named %s does' \
					'not exist in the output database %s' \
					% (elsetName, odbName)
			odb.close()
			exit(0)
	""" Initialize maximum values """
	Stress = 'S'
	maxMises = -0.1
	maxVMElem = 0
	maxStep = "_None_"
	maxFrame = -1
	isStressPresent = 0
	
	Strain = 'E'
	maxStrain = -0.1
	isStrainPresent = 0
	
	Displacement = 'U'
	maxDisp = -0.1
	maxVMElem = 0
	maxStep = "_None_"
	maxFrame = -1
	isDisplacementPresent = 0
	
	for step in odb.steps.values():
		print 'Processing Step:', step.name
		for frame in step.frames:
			allFields = frame.fieldOutputs
			print(allFields.keys())
			if (allFields.has_key(Stress)):
				isStressPresent = 1
				stressSet = allFields[Stress]  
				misesValues = []
				for stressValue in stressSet.values: 
					# misesValues.append(stressValue.mises)
					if (stressValue.mises > maxMises):
						maxMises = stressValue.mises
						maxVMElem = stressValue.elementLabel
						maxStep = step.name
						maxFrame = frame.incrementNumber
			if (allFields.has_key(Displacement)):
				isDisplacementPresent = 1
				dispSet = allFields[Displacement]  
				dispValues = []
				# print("Displacement present")
				for dispValue in dispSet.values: 
					if (dispValue.magnitude > maxDisp):
						maxDisp = dispValue.magnitude
			if (allFields.has_key(Strain)):
				isStrainPresent = 1
				strainSet = allFields[Strain]  
				strainValues = []
				# print("Strain present")
				# for strainValue in strainSet.values: 
					# if (strainValue.maxprincipal > maxStrain):
						# maxStrain = strainValue.maxprincipal				
			
	# if(isStressPresent):
		# print 'Maximum von Mises stress %s is %f in element %d'%(
			# region, maxMises, maxVMElem)
		# print 'Location: frame # %d  step:  %s '%(maxFrame,maxStep)
	# else:
		# print 'Stress output is not available in' \
				# 'the output database : %s\n' %(odb.name)     

	odb.close()
	return maxMises, maxDisp

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def createXYPlot(vpOrigin, vpName, plotName, data):

	##NOTE: I have never used this but it might be interesting in some problems
    
    """
    Display curves of theoretical and computed results in
    a new viewport.
    """
    print 'In plotter'
    from visualization import  USER_DEFINED
    
    vp = session.Viewport(name=vpName, origin=vpOrigin, 
        width=150, height=100)
    print 'Viewport created'
    xyPlot = session.XYPlot(plotName)
    chart = xyPlot.charts.values()[0]
    curveList = []
    for elemName, xyValues in sorted(data.items()):
        xyData = session.XYData(elemName, xyValues)
        curve = session.Curve(xyData)
        curveList.append(curve)

    print 'Curves created'
    chart.setValues(curvesToPlot=curveList)
    chart.axes1[0].axisData.setValues(useSystemTitle=False,title='Arc Height')
    chart.axes2[0].axisData.setValues(useSystemTitle=False,title=plotName)
    vp.setValues(displayedObject=xyPlot)
    print 'Plot displayed'
    return


def findEigenValue(ModelName,StepName):
    odbName = ModelName+'.odb'
    odb = visualization.openOdb(odbName)

    lastFrameM = odb.steps[StepName].frames[-1]
    print lastFrameM.description
##The following string is from the description of the frame; contains the eigenvalue
    descString=lastFrameM.description
    print lastFrameM.mode
##Now we split the string at the = sign
    pattern2 = re.compile('\s*=\s*')
    print pattern2.split(descString)
    print pattern2.split(descString)[1]
##Convert the second string (index=1) to floating point number
    eigenVal1=float(pattern2.split(descString)[1])
##Test that it is a number and not a string
#    print eigenVal1/20.
    odb.close()

    return eigenVal1

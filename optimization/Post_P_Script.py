"""
...
"""

from abaqus import *
from abaqusConstants import *
import visualization
from viewerModules import *

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getResults(ModelName, stepName, loadn, dispNodes):

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
	lastFrame = odb.steps[stepName].frames[-1]
	print 'odb open'
	
	# Retrieve Y-displacements at the splines/connectors
	print 'Retrieving ALL final displacements at ALL points'
	dispField = lastFrame.fieldOutputs['U']
	
	dispNode1 = 0
	dispNode2 = 0
	if dispNodes:
		# Selecting the node(s) to be queried
		if loadn==1:
			NODE1 = odb.rootAssembly.nodeSets['ASSEMBLY_CONSTRAINT-%1.0f-1_REFERENCE_POINT' % (loadn)]
			NODE2 = odb.rootAssembly.nodeSets['ASSEMBLY_CONSTRAINT-%1.0f-2_REFERENCE_POINT' % (loadn)]
		elif loadn==2:
			NODE1 = odb.rootAssembly.nodeSets['M_SET-NODE-1']
			NODE2 = odb.rootAssembly.nodeSets['M_SET-NODE-2']
		
		print 'Retrieving ALL displacements at nodes'
		dFieldNode1 = dispField.getSubset(region=NODE1)
		dFieldNode2 = dispField.getSubset(region=NODE2)
	
		#Note, U1=data[0], U2=data[1], U3=data[2]
		dispNode1 = dFieldNode1.values[0].magnitude
		dispNode2 = dFieldNode2.values[0].magnitude

	
	## The following is left for use in later probems/projects
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
			print 'Scanning for max VM STRESS, max strain, max displacement, and displacement at 2 nodes'
			if (allFields.has_key(Stress)):
				#print 'Scanning for max VM STRESS, max strain, max displacement, and displacement at 2 nodes'
				isStressPresent = 1
				if loadn==1:
					targetset = assembly.elementSets["WITHOUT-TIPS"]
					stressSet = allFields[Stress].getSubset(region=targetset)
				elif loadn==2:
					stressSet = allFields[Stress]
				misesValues = []
				for stressValue in stressSet.values: 
					# misesValues.append(stressValue.mises)
					if (stressValue.mises > maxMises):
						maxMises = stressValue.mises
						maxVMElem = stressValue.elementLabel
						maxStep = step.name
						maxFrame = frame.incrementNumber
			# if (allFields.has_key(Displacement)):
				# #print 'Scanning for maximum displacement magnitude'
				# isDisplacementPresent = 1
				# dispSet = allFields[Displacement]  
				# dispValues = []
				# # print("Displacement present")
				# for dispValue in dispSet.values: 
					# if (dispValue.magnitude > maxDisp):
						# maxDisp = dispValue.magnitude
			# if (allFields.has_key(Strain)):
				# #print 'Scanning for maximum strain'
				# isStrainPresent = 1
				# strainSet = allFields[Strain]  
				# strainValues = []
				# for strainValue in strainSet.values:
					# if (strainValue.maxPrincipal > maxStrain):
						# maxStrain = strainValue.maxPrincipal		
						
	if(isStressPresent):
		print 'Maximum von Mises stress %s is %f in element %d'%(
			region, maxMises, maxVMElem)
		#print 'Location: frame # %d  step:  %s '%(maxFrame,maxStep)
	else:
		print 'Stress output is not available in' \
				'the output database : %s\n' %(odb.name)     

	odb.close()
	return maxMises, maxDisp, maxStrain, dispNode1, dispNode2

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

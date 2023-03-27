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
from math import atan, sin, cos, tan
from Post_P_Script import getResults

###############################
### Generation of FEA Model ###
###############################

### Note: If you create a loop, START it here
### (i.e., the contents of the loop below are intended)
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)

with open('RunInfo.txt', 'w') as f:
	f.write("a, b, c, score\n")

def abaqusFcn(value):
	print(value)
	h0 = 1
	h1 = (0.1*h0)+(0.9*h0*value[0])
	fd1 = 0.1 + value[1]*0.7
	fd2 = 0.1 + value[2]*0.7
	thk = 2.0*h0 + 6.0*h0*0.1 #value[3]


	hL4 = h0 + (h1-h0)*0.25
	h3L4 = h0 + (h1-h0)*0.75

	### Scripting the entire model allows its entire
	### contents to be packaged into this single file.
	Mdb()

	# Sketch Geometry and Create Parts
	print 'Sketching/Creating the part'

	s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=2.0)
	g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
	s.setPrimaryObject(option=STANDALONE)
	s.Line(point1=(0.0, 0.0), point2=(0.0, h0))
	s.Line(point1=(0.0, h0), point2=(1.0, h1))
	s.Line(point1=(1.0, h1), point2=(1.0, 0.0))
	s.Line(point1=(1.0, 0.0), point2=(0.0, 0.0))
	s.CircleByCenterPerimeter(center=(0.25, hL4/2), point1=(0.25,
		(1-fd1)*(hL4/2)))
	s.CircleByCenterPerimeter(center=(0.75, h3L4/2), point1=(0.75,
		(1-fd2)*(h3L4/2)))
	p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=TWO_D_PLANAR,
		type=DEFORMABLE_BODY)
	p = mdb.models['Model-1'].parts['Part-1']
	p.BaseShell(sketch=s)
	s.unsetPrimaryObject()
	p = mdb.models['Model-1'].parts['Part-1']
	del mdb.models['Model-1'].sketches['__profile__']


	#Defining the face partitions
	print 'Partitioning part'

	p = mdb.models['Model-1'].parts['Part-1']
	f, e, d2 = p.faces, p.edges, p.datums
	t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(0.0, 0.0,
		0.0), normal=(0.0, 0.0, 1.0)), sketchPlaneSide=SIDE1, origin=(0.0,
		0.0, 0.0))
	s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
		sheetSize=2.0, gridSpacing=0.05, transform=t)
	g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
	s1.setPrimaryObject(option=SUPERIMPOSE)
	p = mdb.models['Model-1'].parts['Part-1']
	p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
	s1.Line(point1=(0.0, 0.25), point2=(1.0, h1/2))
	s1.Line(point1=(0.25, 0.0), point2=(0.25, hL4))
	s1.Line(point1=(0.5, 0.0), point2=(0.5, (hL4+h3L4)/2))
	s1.Line(point1=(0.75, 0.0), point2=(0.75, h3L4))
	p = mdb.models['Model-1'].parts['Part-1']
	f = p.faces
	pickedFaces = f.findAt(((0.0, 0.0, 0.0), ))
	e1, d1 = p.edges, p.datums
	p.PartitionFaceBySketch(faces=pickedFaces, sketch=s1)
	s1.unsetPrimaryObject()
	del mdb.models['Model-1'].sketches['__profile__']


	# Create Material
	print 'Creating the Materials'

	mdb.models['Model-1'].Material(name='Aluminum')
	mdb.models['Model-1'].materials['Aluminum'].Elastic(table=((70000000000.0,
		0.3), ))
	mdb.models['Model-1'].materials['Aluminum'].Density(table=((2720.0, ), ))

	#Create/Assign Section
	print 'Creating the Sections'

	mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1',
		material='Aluminum', thickness=thk)

	print 'Assigning the Sections'

	region = p.Set(faces=p.faces, name='Set-1')
	p = mdb.models['Model-1'].parts['Part-1']
	p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0,
		offsetType=MIDDLE_SURFACE, offsetField='',
		thicknessAssignment=FROM_SECTION)



	#Assemble Parts
	print 'Placing Parts in Space'
	#Create Instances here

	a = mdb.models['Model-1'].rootAssembly
	a.DatumCsysByDefault(CARTESIAN)
	p = mdb.models['Model-1'].parts['Part-1']
	a.Instance(name='Part-1-1', part=p, dependent=ON)

	#Define Steps
	print 'Defining the Steps'

	mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
	session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')

	#Create Loads
	print 'Defining Loads'
	
	a = mdb.models['Model-1'].rootAssembly
	s1 = a.instances['Part-1-1'].edges
	side1Edges1 = s1.findAt(((1.0, h1/4, 0.0), ), ((1.0, 3*(h1/4), 0.0), ))
	region = a.Surface(side1Edges=side1Edges1, name='Surf-2')
	mdb.models['Model-1'].SurfaceTraction(name='Load-1', createStepName='Step-1',
		region=region, magnitude=F/(thk*h1), directionVector=((0.0, 1.0, 0.0), (0.0, 0.0,
		0.0)), distributionType=UNIFORM, field='', localCsys=None)

	#Define BCs
	print 'Defining all BCs'

	a = mdb.models['Model-1'].rootAssembly
	e1 = a.instances['Part-1-1'].edges
	edges1 = e1.findAt(((0.0, h0/4, 0.0), ), ((0.0, 3*(h0/4), 0.0), ))
	region = a.Set(edges=edges1, name='Set-1')
	mdb.models['Model-1'].EncastreBC(name='BC-1', createStepName='Step-1',
		region=region, localCsys=None)

	#Define Sets
	print 'Defining Sets'

	a = mdb.models['Model-1'].rootAssembly
	v1 = a.instances['Part-1-1'].vertices
	verts1 = v1.findAt(((1.0, h1/2, 0.0), ))
	a.Set(vertices=verts1, name='TIPNODE')


	# Note: Create "TIPNODE" here
	# Create it from the Assembly Module (not Part)

	#Mesh Parts
	print 'Meshing the Part'
	
	p = mdb.models['Model-1'].parts['Part-1']
	p.setMeshControls(regions=p.faces, elemShape=QUAD, technique=FREE)
	p.seedPart(size=seedSize, deviationFactor=0.1, minSizeFactor=0.1)
	elemType1 = mesh.ElemType(elemCode=CPS4R, elemLibrary=STANDARD)
	#elemType1 = mesh.ElemType(elemCode=C3D2OR, elemLibrary=STANDARD) #elemType
	p = mdb.models['Model-1'].parts['Part-1']
	pickedRegions =(p.faces, )
	p.setElementType(regions=pickedRegions, elemTypes=(elemType1, ))
	p = mdb.models['Model-1'].parts['Part-1']
	p.generateMesh()

	#####################################
	### Creation/Execution of the Job ###
	#####################################
	print 'Creating/Running Job'

	ModelName='Model-1'

	mdb.Job(name=ModelName, model=ModelName, description='', type=ANALYSIS,
		atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
		memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
		explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
		modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
		scratch='', multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)

	job=mdb.jobs[ModelName]

	# delete lock file, which for some reason tends to hang around, if it exists
	if os.access('%s.lck'%ModelName,os.F_OK):
		os.remove('%s.lck'%ModelName)

	# Run the job, then process the results.
	job.submit()
	job.waitForCompletion()
	print 'Completed job'

	score = getResults(ModelName)
	
	valuestr = ""
	for v in value:
		valuestr += str(v) + ", "
	with open('RunInfo.txt', 'a') as f:
		f.write("%s%1.1f \n" % (valuestr, score))
		
	return score

F = 10
seedSize = 0.038

from math import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize 

# Set the bounds
bounds = [(0, 2), (0, 0.75), (0, 0.75)]

# Set the initial guess for the optimizer
xy0 = np.array([1, 0, 0])

# Use the minimize function to optimize the function
result = minimize(abaqusFcn, xy0, bounds=bounds)

# Plot the function and the optimized point
print(result)

# print(abaqusFcn([0.2,0.3,0.7,0.1])) # height of right side, radius of 1st circle, radius of 2nd circle, thickness
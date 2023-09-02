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

######################################
# Variable and Fixed Design Parameters
######################################

##########################
# FEA Modeling Parameters
# (e.g., mesh seeds, step times, etc)
##########################

####################################
### Calculated Properties/Values ###
####################################


### Write data file column headings
  
#####################################
### Generation of SOLID FEA Model ###
#####################################

#[14.0, 20.0], #L = 17.0 # TOTAL LENGTH (cm)
#[0.32, 0.44], #L1 = 0.38 * L #Length from neck to point
#[0.4, 0.56], #L11 = 0.53 * L1 #Length from root to point
#[0.55, 0.95], #L2 = 0.75 * (L-L1)
#[2.0, 3.0], #W = 2.5 # MAXIMUM WIDTH (cm)
#[0.2, 0.4], #W3 = 0.3 * W
#[0.2, 0.5], #W4 = 0.35 * W #Width of the bottom of the handle
#[0.86, 0.94], #W21 = 0.9 * (W-W3) + W3
#[0.5, 0.56], #W22 = 0.53 * (W-W3) + W3
#[0.02, 0.08], #W23 = 0.05 * (W-W3) + W3
#[0.2, 0.4], #T = 0.4 # MAXIMUM THICKNESS (cm)
#[0.1, 0.4], #T1 = T * 0.25 #Thickness of the overall surface
#[1.2, 1.8], #h4 = 1.5 # heights expressed in terms of h4, since it's the max height
#[0.0, 0.6], #h7 = 0.3 * h4 # height of tine tip from plane
#[0.45, 0.55], #h2 = 0.5 * h4
#[0.5, 0.7], #h6 = h5 + (T + T1) * 0.6
#[0.15, 0.35], #T2 = T * 0.3 #Thickness of outer ridges
#[0.15, 0.35] #T3 = T * 0.3 #Thickness of middle ridges

### Note: If you create a loop, start it here

### Scripting the entire model allows its entire
### contents to be packaged into this single file.

VERSION = 1.0
RUNJOB = True
cutTips = True
modelNum = 1
#loadn = 1
failure = False # represents if model has reach yield stress for either load 1 or 2
varParameters = []
meanParameters = []
rangeParameters = [ 	# Min, Max
[0.2, 0.4], #T = 0.3 # MAXIMUM THICKNESS (cm)
[0.1, 0.4], #T1 = T * 0.25 #Thickness of the overall surface
[0.15, 0.35], #T2 = T * 0.3 #Thickness of outer ridges
[14.0, 20.0], #L = 17.0 # TOTAL LENGTH (cm)
[1.2, 1.8], #h4 = 1.5 # heights expressed in terms of h4, since it's the max height
[0.2, 0.4], #W3 = 0.3 * W
]
alphabet = ['a','b','c','d','e','f','g','h','i'] # used for treatment combinations
paramNames = ['T', 'T1', 'T2', 'L', 'h4', 'W3']
nParams = len(paramNames) # number of parameters
treatmentNames = alphabet[:nParams] # used for treatment combinations (i.e. d, ab, acde, etc.)

for p in rangeParameters:
	varParameters.append([p[0], (p[0]+p[1])/2, p[1]])
	meanParameters.append((p[0]+p[1])/2)

# Open data file and write column headings
DataFile = open('PostData.txt','w')
#DataFile.write('%s\n\n' % (', '.join(paramNames)))
DataFile.write('Load, ')
for name in paramNames:
	DataFile.write(name + ", ")
DataFile.write('SAV (1/cm), Max Mises Stress (MPa), Node 1 Displacement (cm), Node 2 Displacement (cm)\n')
DataFile.close()

Mdb()

vars = meanParameters[:] # stores 0 for min and 1 for max values
score = 0 # initializes score of objective function

for loadn in range(1, 3): # Loads 1 and 2
	with open('inputs.txt', 'r') as fileObj:
		varValues = [float(v) for v in fileObj.read().split(',')]
	#vars = [1, 0, 0, 0, 0, 0]
	print("Model %1.0f, Load Case %1.0f" % (modelNum, loadn))

	if modelNum <= 2: # CHANGE THIS TO RUN CERTAIN PARTS OF THE FULL FACTORIAL
		print varValues
			
		# Top View
		L = varValues[3] # TOTAL LENGTH (cm)
		L1 = 0.38 * L
		L11 = 0.53 * L1 #Length from root to point
		L2 = 0.75 * (L1-L11)
		L12 = L1 - L11 - L2
		L3 = L - L1

		W = 2.5 # MAXIMUM WIDTH (cm)
		W1 = 0.83 * W
		Wtip = 0.04 * W
		W12 = L11/(L11+L12) * (W-W1) + W1
		Wt1 = 0.16 * W12 # 2 outer tines
		Wt2 = 0.16 * W12 # 2 inner tines
		Ws = (W12 - 2*Wt1 - 2*Wt2) / 3 # 3 slots
		W3 = varValues[5] * W
		W4 = 0.35 * W
		W21 = 0.94 * (W-W3) + W3
		l21 = 0.85 * L2
		W22 = 0.56 * (W-W3) + W3
		l22 = 0.65 * L2
		W23 = 0.05 * (W-W3) + W3
		l23 = 0.3 * L2
		fr1 = Wtip / 3
		fr2 = Ws / 2

		# Side View 

		T = varValues[0] # MAXIMUM THICKNESS (cm)
		T1 = T * varValues[1]

		l4 = L2
		h4 = varValues[4] # heights expressed in terms of h4, since it's the max height
		h7 = 0.3 * h4 # height of tine tip from plane
		l1 = 0.27 * l4
		h1 = 0.1 * h4
		l2 = 0.54 * l4
		h2 = 0.45 * h4
		l3 = 0.75 * l4
		h3 = 0.95 * h4
		l5 = L1 - (L11+L12)/2
		h5 = (h4 + h7) * 0.55
		l6 = l5 + L11/100
		h6 = h5 + (T + T1) * 0.5

		# Bottom View

		T2 = T * varValues[2]
		T3 = T2 # T * vars[10]

		# X Support

		Lx = 0.1 * L3
		L4 = L3 - Lx
		Tx1 = T * 0.5
		Tx2 = T * 0.3
		rx = W3 * 0.2

		# Seed Size
		seedSize = 0.001 # sqrt( (((W4-W3)/2)**2) + (L3**2) ) / seedScale / 100 # calculating seed size and converting from cm to m
		handleSeedSize = 0.002
		localHandle = True
		
		ModelName = 'Model-%s' % (modelNum)
		mdb.Model(name=ModelName, modelType=STANDARD_EXPLICIT)
		
		# Recreate the model using the current parameter values
			
		# Sketch Geometry and Create Parts

		print 'Sketching/Creating the Baffle'

		# TopSketch
		s = mdb.models[ModelName].ConstrainedSketch(name='__profile__', sheetSize=50.0)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=STANDALONE)
		# Handle
		s.Line(point1=(0.0, L-L11), point2=(0.0, 0.0))
		s.VerticalConstraint(entity=g[2], addUndoState=False)
		s.Line(point1=(0.0, 0.0), point2=(W4/2, 0.0))
		s.HorizontalConstraint(entity=g[3], addUndoState=False)
		s.PerpendicularConstraint(entity1=g[2], entity2=g[3], addUndoState=False)
		s.Line(point1=(W4/2, 0.0), point2=(W3/2, L3))
		for e in range(len(v)):
			s.FixedConstraint(entity=v[e])
		# Curve
		s.Arc3Points(point1=(W3/2, L3), point2=(W22/2, L3+l22), point3=(W23/2, L3+l23))
		s.Arc3Points(point1=(W22/2, L3+l22), point2=(W/2, L3+L2), point3=(W21/2, L3+l21)) # 3 points cannot be collinear
		# print('(%f, %f), (%f, %f), (%f, %f)') % (W22/2, L3+l22, W/2, L3+L2, W21/2, L3+l21)
		s.Line(point1=(W/2, L3+L2), point2=(W1/2, L))
		s.FixedConstraint(entity=v.findAt((W/2, L3+L2)))
		# s.FixedConstraint(entity=v[4])
		s.FixedConstraint(entity=v.findAt((W1/2, L)))
		s.TangentConstraint(entity1=g[5], entity2=g[6])
		s.TangentConstraint(entity1=g[4], entity2=g[5])
		s.TangentConstraint(entity1=g[6], entity2=g[7])
		#s.EqualDistanceConstraint(entity1=v[3], entity2=v[4], midpoint=v[6])
		# Tines
		x = Ws/2
		s.Line(point1=(0.0, L-L11), point2=(x, L-L11))
		prevx = x
		x += (Wt2-Wtip)/2
		s.Line(point1=(prevx, L-L11), point2=(x, L))
		prevx = x
		x += Wtip
		s.Line(point1=(prevx, L), point2=(x, L))
		prevx = x
		x += (Wt2-Wtip)/2
		s.Line(point1=(prevx, L), point2=(x, L-L11))
		prevx = x
		x += Ws
		s.Line(point1=(prevx, L-L11), point2=(x, L-L11))
		prevx = x
		x = W1/2-Wtip
		s.Line(point1=(prevx, L-L11), point2=(x, L))
		prevx = x
		s.Line(point1=(prevx, L), point2=(W1/2, L))
		# Fillets
		s.FilletByRadius(radius=fr2, curve1=g[8], nearPoint1=(0,L), curve2=g[9], nearPoint2=(0,L))
		s.FilletByRadius(radius=fr1, curve1=g[9], nearPoint1=(W4/2,0), curve2=g[10], nearPoint2=(W4/2,0))
		s.FilletByRadius(radius=fr1, curve1=g[10], nearPoint1=(0,0), curve2=g[11], nearPoint2=(0,0))
		s.FilletByRadius(radius=fr2, curve1=g[11], nearPoint1=(W1/2,L), curve2=g[12], nearPoint2=(W1/2,L))
		s.FilletByRadius(radius=fr2, curve1=g[12], nearPoint1=(0,L), curve2=g[13], nearPoint2=(0,L))
		s.FilletByRadius(radius=fr1, curve1=g[13], nearPoint1=(W/2,0), curve2=g[14], nearPoint2=(W/2,0))
		s.FilletByRadius(radius=fr1, curve1=g[14], nearPoint1=(0,0), curve2=g[7], nearPoint2=(0,0))
		mdb.models[ModelName].sketches.changeKey(fromName='__profile__', 
			toName='TopSketch')
		s.unsetPrimaryObject()

		# SideSketch
		s = mdb.models[ModelName].ConstrainedSketch(name='__profile__', sheetSize=50.0)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=STANDALONE)
		s.Line(point1=(0.0, T), point2=(0.0, 0.0))
		s.Line(point1=(0.0, 0), point2=(-L3, 0.0))
		s.Arc3Points(point1=(-L3, 0.0), point2=(-L3-l2, h2), point3=(-L3-l1, h1))
		s.Arc3Points(point1=(-L3-l2, h2), point2=(-L3-l4, h4), point3=(-L3-l3, h3))
		s.Arc3Points(point1=(-L3-l4, h4), point2=(-L, h7), point3=(-L3-l5, h5))
		s.FixedConstraint(entity=v[1])
		s.FixedConstraint(entity=v[2])
		#s.FixedConstraint(entity=v[3])
		s.FixedConstraint(entity=v[5])
		s.FixedConstraint(entity=v[7])
		s.FixedConstraint(entity=v[8])
		s.TangentConstraint(entity1=g[4], entity2=g[5])
		#s.TangentConstraint(entity1=g[3], entity2=g[4])
		#s.TangentConstraint(entity1=g[5], entity2=g[6])
		s.offset(distance=T, objectList=(g[3], g[4], g[5]), side=RIGHT)
		s.Spot(point=(-L3-l4, h4+T))
		s.FixedConstraint(entity=v[14])
		s.CoincidentConstraint(entity1=v[14], entity2=v[12])
		s.Line(point1=(-L, h7), point2=(-L, h7+T1))
		s.Arc3Points(point1=(-L, h7+T1), point2=(-L3-l4, h4+T), point3=(-L3-l6, h6))
		mdb.models[ModelName].sketches.changeKey(fromName='__profile__', 
			toName='SideSketch')
		s.unsetPrimaryObject()
			
		# Part-1
		s1 = mdb.models[ModelName].ConstrainedSketch(name='__profile__', 
			sheetSize=200.0)
		g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
		s1.setPrimaryObject(option=STANDALONE)
		s1.sketchOptions.setValues(gridOrigin=(0,0))
		s1.retrieveSketch(sketch=mdb.models[ModelName].sketches['TopSketch'])
		session.viewports['Viewport: 1'].view.fitView()
		#: Info: 20 entities copied from TopSketch.
		s1.move(vector=(0,0), objectList=(g[4], g[5], 
			g[6], g[7], g[8], g[9], g[10], g[11], g[12], g[13], g[14], g[15], g[16], 
			g[17], g[18], g[19], g[20], g[21], g[22], g[23]))
		p = mdb.models[ModelName].Part(name='Part-1', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models[ModelName].parts['Part-1']
		p.BaseSolidExtrude(sketch=s1, depth=h4*2)
		s1.unsetPrimaryObject()
		p = mdb.models[ModelName].parts['Part-1']
		session.viewports['Viewport: 1'].setValues(displayedObject=p)
		del mdb.models[ModelName].sketches['__profile__']

		# Cut-1
		# Creating Block
		s = mdb.models[ModelName].ConstrainedSketch(name='__profile__', sheetSize=50.0)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=STANDALONE)
		s.Line(point1=(0.0, 0.0), point2=(W*2, 0.0))
		s.Line(point1=(W*2, 0.0), point2=(W*2, L+0.5))
		s.Line(point1=(W*2, L+0.5), point2=(0, L+0.5))
		s.Line(point1=(0, L+0.5), point2=(0, 0))
		p = mdb.models[ModelName].Part(name='Cut-1', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models[ModelName].parts['Cut-1']
		p.BaseSolidExtrude(sketch=s, depth=h4*2)
		s.unsetPrimaryObject()
		p = mdb.models[ModelName].parts['Cut-1']
		del mdb.models[ModelName].sketches['__profile__']
		# Cut
		p = mdb.models[ModelName].parts['Cut-1']
		f1, e1 = p.faces, p.edges
		t = p.MakeSketchTransform(sketchPlane=f1[3], sketchUpEdge=e1[8], 
			sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
		s1 = mdb.models[ModelName].ConstrainedSketch(name='__profile__', 
			sheetSize=37.54, gridSpacing=0.93, transform=t)
		g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
		#s1.setPrimaryObject(option=SUPERIMPOSE)
		p = mdb.models[ModelName].parts['Cut-1']
		p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
		s1.retrieveSketch(sketch=mdb.models[ModelName].sketches['SideSketch'])
		session.viewports['Viewport: 1'].view.fitView()
		#: Info: 10 entities copied from SideSketch.
		p = mdb.models[ModelName].parts['Cut-1']
		f, e = p.faces, p.edges
		p.CutExtrude(sketchPlane=f[3], sketchUpEdge=e[8], sketchPlaneSide=SIDE1, 
			sketchOrientation=RIGHT, sketch=s1, flipExtrudeDirection=OFF)
		s1.unsetPrimaryObject()
		del mdb.models[ModelName].sketches['__profile__']

		# Part-2
		a = mdb.models[ModelName].rootAssembly
		a.DatumCsysByDefault(CARTESIAN)
		p = mdb.models[ModelName].parts['Cut-1']
		a.Instance(name='Cut-1-1', part=p, dependent=ON)
		p = mdb.models[ModelName].parts['Part-1']
		a.Instance(name='Part-1-1', part=p, dependent=ON)
		a = mdb.models[ModelName].rootAssembly
		a.InstanceFromBooleanCut(name='Part-2', 
			instanceToBeCut=mdb.models[ModelName].rootAssembly.instances['Part-1-1'], 
			cuttingInstances=(a.instances['Cut-1-1'], ), originalInstances=DELETE)

		# Cut-2-1
		p1 = mdb.models[ModelName].parts['Part-2']
		p = mdb.models[ModelName].Part(name='Cut-2-1', 
			objectToCopy=mdb.models[ModelName].parts['Part-2'])
		p = mdb.models[ModelName].parts['Cut-2-1']
		f, e = p.faces, p.edges
		t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(W4/10, L3/10, 0.0)), 
			sketchUpEdge=e.findAt(coordinates=(0.0, L3/2, 0.0)), sketchPlaneSide=SIDE1, 
			sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
		s = mdb.models[ModelName].ConstrainedSketch(name='__profile__', 
			sheetSize=25, gridSpacing=0.5, transform=t)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		#s.setPrimaryObject(option=SUPERIMPOSE)
		p = mdb.models[ModelName].parts['Cut-2-1']
		p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
		s.Line(point1=(0.0, 0.0), point2=(W4, 0.0))
		s.Line(point1=(W4, 0.0), point2=(W4, -T2))
		s.Line(point1=(W4, -T2), point2=(0.0, -T2))
		s.Line(point1=(0.0, -T2), point2=(0.0, 0.0))
		p = mdb.models[ModelName].parts['Cut-2-1']
		f1, e1 = p.faces, p.edges
		p.CutExtrude(sketchPlane=f1.findAt(coordinates=(W4/10, L3/10, 0.0)), 
			sketchUpEdge=e1.findAt(coordinates=(0.0, L3/2, 0.0)), sketchPlaneSide=SIDE1, 
			sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
		s.unsetPrimaryObject()
		del mdb.models[ModelName].sketches['__profile__']

		# SideCutSketch
		mdb.models[ModelName].ConstrainedSketch(name='SideCutSketch', 
			objectToCopy=mdb.models[ModelName].sketches['SideSketch'])
		s = mdb.models[ModelName].ConstrainedSketch(name='__edit__', 
			objectToCopy=mdb.models[ModelName].sketches['SideCutSketch'])
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=STANDALONE)
		s.delete(objectList=(g[2], g[3], g[4], g[5], g[7], g[8], g[9]))
		s.delete(objectList=(g[11], v[14]))
		s.Line(point1=(-L, h7+T1), point2=(-L, h4*2))
		s.Line(point1=(-L, h4*2), point2=(-L3-L2, h4*2))
		s.Line(point1=(-L3-L2, h4*2), point2=(-L3-L2, h4))
		mdb.models[ModelName].sketches.changeKey(fromName='__edit__', 
			toName='SideCutSketch')
		s.unsetPrimaryObject()

		# Cut-2-2
		s1 = mdb.models[ModelName].ConstrainedSketch(name='__profile__', 
			sheetSize=50.0)
		g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
		s1.setPrimaryObject(option=STANDALONE)
		s1.sketchOptions.setValues(gridOrigin=(0,0))
		s1.retrieveSketch(sketch=mdb.models[ModelName].sketches['SideCutSketch'])
		session.viewports['Viewport: 1'].view.fitView()
		#: Info: 7 entities copied from SideCutSketch.
		p = mdb.models[ModelName].Part(name='Cut-2-2', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models[ModelName].parts['Cut-2-2']
		p.BaseSolidExtrude(sketch=s1, depth=(W1)/2+1) # +1 is to create extra depth that will later be mostly cut to properly cut fork while keeping a tip buffer
		s1.unsetPrimaryObject()
		p = mdb.models[ModelName].parts['Cut-2-2']
		session.viewports['Viewport: 1'].setValues(displayedObject=p)
		del mdb.models[ModelName].sketches['__profile__']
		# Extrude Cut (cut to correct while leaving a small sliver for tip buffer)
		if cutTips:
			tipBuffer = Wtip
		else:
			tipBuffer = 0 # partitions off inner tine ridges a certain distance before the tip, to allow for more accurate meshing
		p = mdb.models[ModelName].parts['Cut-2-2']
		f1, e1 = p.faces, p.edges
		t = p.MakeSketchTransform(sketchPlane=f1.findAt(coordinates=(-(L-Wtip), 
			h6, 0.0)), sketchUpEdge=e1.findAt(coordinates=(-L3-L2, h4*3/2, 0.0)), 
			sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
		s = mdb.models[ModelName].ConstrainedSketch(name='__profile__', sheetSize=28.4, 
			gridSpacing=0.71, transform=t)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=SUPERIMPOSE)
		p = mdb.models[ModelName].parts['Cut-2-2']
		p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
		s.rectangle(point1=(L3+L2, h4*2), point2=(L-tipBuffer, h7))
		p = mdb.models[ModelName].parts['Cut-2-2']
		f, e = p.faces, p.edges
		p.CutExtrude(sketchPlane=f.findAt(coordinates=(-(L-Wtip), h6, 0.0)), 
			sketchUpEdge=e.findAt(coordinates=(-L3-L2, h4*3/2, 0.0)), 
			sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, depth=1.0, 
			flipExtrudeDirection=OFF)
		s.unsetPrimaryObject()
		del mdb.models[ModelName].sketches['__profile__']

		# Cut-2-3
		a = mdb.models[ModelName].rootAssembly
		del a.features['Part-2-1']
		a1 = mdb.models[ModelName].rootAssembly
		p = mdb.models[ModelName].parts['Cut-2-1']
		a1.Instance(name='Cut-2-1-1', part=p, dependent=ON)
		p = mdb.models[ModelName].parts['Cut-2-2']
		a1.Instance(name='Cut-2-2-1', part=p, dependent=ON)
		a1 = mdb.models[ModelName].rootAssembly
		a1.rotate(instanceList=('Cut-2-2-1', ), axisPoint=(0.0, 0.0, 0.0), 
			axisDirection=(0.0, 0.0, -1.0), angle=90.0)
		#: The instance Cut-2-2-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 0., -1.
		a1 = mdb.models[ModelName].rootAssembly
		a1.rotate(instanceList=('Cut-2-2-1', ), axisPoint=(0.0, 0.0, 0.0), 
			axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
		#: The instance Cut-2-2-1 was rotated by -90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 1., 0.
		a1 = mdb.models[ModelName].rootAssembly
		a1.translate(instanceList=('Cut-2-2-1', ), vector=((W1)/2+1, 0.0, 0.0)) # corresponds to depth of Cut-2-2 extrude
		a1 = mdb.models[ModelName].rootAssembly
		# Merging Cut-2-1 and Cut-2-2
		a1.InstanceFromBooleanMerge(name='Cut-2-3', instances=(
			a1.instances['Cut-2-1-1'], a1.instances['Cut-2-2-1'], ), 
			originalInstances=DELETE, domain=GEOMETRY)
		# Extrude Cut (cut that will create ridges for inner tines)
		p = mdb.models[ModelName].parts['Cut-2-3']
		f, e = p.faces, p.edges
		t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(W1/4, 
			L-L11, h4*2)), sketchUpEdge=e.findAt(coordinates=(W1/4, L, h4*2)), 
			sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
		s = mdb.models[ModelName].ConstrainedSketch(name='__profile__', 
			sheetSize=34.05, gridSpacing=0.85, transform=t)
		#s.setPrimaryObject(option=SUPERIMPOSE)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		p = mdb.models[ModelName].parts['Cut-2-3']
		p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
		tineY = (Ws+Wt2)/2 + T2
		s.Line(point1=(L-tipBuffer, -tineY - T3/2), point2=(L-tipBuffer, -tineY + T3/2))
		s.Line(point1=(L-tipBuffer, -tineY + T3/2), point2=(L-L1, -tineY + T3/2))
		s.Line(point1=(L-L1, -tineY + T3/2), point2=(L-L1, -tineY - T3/2))
		s.Line(point1=(L-L1, -tineY - T3/2), point2=(L-tipBuffer, -tineY - T3/2))
		p = mdb.models[ModelName].parts['Cut-2-3']
		f1, e1 = p.faces, p.edges
		p.CutExtrude(sketchPlane=f.findAt(coordinates=(W1/4, L-L11, h4*2)), 
			sketchUpEdge=e.findAt(coordinates=(W1/4, L, h4*2)), 
			sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, 
			flipExtrudeDirection=OFF)
		s.unsetPrimaryObject()
		del mdb.models[ModelName].sketches['__profile__']
		

		# X-Support
		cy = L4+Lx/2 # y-coordinate of circle center
		def getX(n): # returns X-value for diagonal parts when given y-value
			return ((L3-n)/L3 * (W4-W3) + W3) / 2 - T2
		# Circle
		s1 = mdb.models[ModelName].ConstrainedSketch(name='__profile__', 
			sheetSize=50.0)
		g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
		s1.setPrimaryObject(option=STANDALONE)
		s1.CircleByCenterPerimeter(center=(0.0, cy), point1=(0.0, cy+rx))
		p = mdb.models[ModelName].Part(name='X-Circle', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models[ModelName].parts['X-Circle']
		p.BaseSolidExtrude(sketch=s1, depth=Tx1)
		s1.unsetPrimaryObject()
		p = mdb.models[ModelName].parts['X-Circle']
		del mdb.models[ModelName].sketches['__profile__']
		# Diagonal 1
		s = mdb.models[ModelName].ConstrainedSketch(name='__profile__', sheetSize=50.0)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=STANDALONE)
		y1 = L3
		y2 = L4+Tx2
		s.Line(point1=(-getX(y1), y1), point2=(getX(y2), y2))
		y1 = y2
		y2 = L4
		s.Line(point1=(getX(y1), y1), point2=(getX(y2), y2))
		y1 = y2
		y2 = L3-Tx2
		s.Line(point1=(getX(y1), y1), point2=(-getX(y2), y2))
		y1 = y2
		y2 = L3
		s.Line(point1=(-getX(y1), y1), point2=(-getX(y2), y2))
		p = mdb.models[ModelName].Part(name='X-Diagonal-1', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models[ModelName].parts['X-Diagonal-1']
		p.BaseSolidExtrude(sketch=s, depth=Tx1)
		s.unsetPrimaryObject()
		p = mdb.models[ModelName].parts['X-Diagonal-1']
		del mdb.models[ModelName].sketches['__profile__']
		# Diagonal 2
		s = mdb.models[ModelName].ConstrainedSketch(name='__profile__', sheetSize=50.0)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=STANDALONE)
		y1 = L3
		y2 = L4+Tx2
		s.Line(point1=(getX(y1), y1), point2=(-getX(y2), y2))
		y1 = y2
		y2 = L4
		s.Line(point1=(-getX(y1), y1), point2=(-getX(y2), y2))
		y1 = y2
		y2 = L3-Tx2
		s.Line(point1=(-getX(y1), y1), point2=(getX(y2), y2))
		y1 = y2
		y2 = L3
		s.Line(point1=(getX(y1), y1), point2=(getX(y2), y2))
		p = mdb.models[ModelName].Part(name='X-Diagonal-2', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models[ModelName].parts['X-Diagonal-2']
		p.BaseSolidExtrude(sketch=s, depth=Tx1)
		s.unsetPrimaryObject()
		p = mdb.models[ModelName].parts['X-Diagonal-2']
		del mdb.models[ModelName].sketches['__profile__']
		# Assemble X-Support Parts
		a = mdb.models[ModelName].rootAssembly
		p = mdb.models[ModelName].parts['X-Circle']
		a.Instance(name='X-Circle-1', part=p, dependent=ON)
		p = mdb.models[ModelName].parts['X-Diagonal-1']
		a.Instance(name='X-Diagonal-1-1', part=p, dependent=ON)
		p = mdb.models[ModelName].parts['X-Diagonal-2']
		a.Instance(name='X-Diagonal-2-1', part=p, dependent=ON)
		a = mdb.models[ModelName].rootAssembly
		a.InstanceFromBooleanMerge(name='X-Support', instances=(
			a.instances['X-Diagonal-1-1'], a.instances['X-Circle-1'], 
			a.instances['X-Diagonal-2-1'], ), originalInstances=DELETE, 
			domain=GEOMETRY)
		# Partition Circle in X-Support by sketch
		p = mdb.models[ModelName].parts['X-Support']
		f, e, d = p.faces, p.edges, p.datums
		t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(0, 
			L3-Lx/2, Tx1)), sketchUpEdge=e.findAt(coordinates=(rx, 
			L3-Lx/2, Tx1)), sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0.0))
		s = mdb.models[ModelName].ConstrainedSketch(name='__profile__', 
			sheetSize=21.63, gridSpacing=0.54, transform=t)
		g, v, d1, c = s.geometry, s.vertices, s.dimensions, s.constraints
		#s.setPrimaryObject(option=SUPERIMPOSE)
		p = mdb.models[ModelName].parts['X-Support']
		p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
		s.CircleByCenterPerimeter(center=(0.0, L3-Lx/2), point1=(0.0, L3-Lx/2+rx))
		p = mdb.models[ModelName].parts['X-Support']
		f = p.faces
		pickedFaces = f.findAt(((0, L3-Lx/2, Tx1), ))
		e1, d2 = p.edges, p.datums
		p.PartitionFaceBySketch(faces=pickedFaces, sketch=s)
		s.unsetPrimaryObject()
		del mdb.models[ModelName].sketches['__profile__']
		
		# Fork-1 (without X-Support)
		a = mdb.models[ModelName].rootAssembly
		del a.features['Cut-2-3-1']
		a1 = mdb.models[ModelName].rootAssembly
		p = mdb.models[ModelName].parts['Part-2']
		a1.Instance(name='Part-2-1', part=p, dependent=ON)
		a1 = mdb.models[ModelName].rootAssembly
		p = mdb.models[ModelName].parts['Cut-2-3']
		a1.Instance(name='Cut-2-3-1', part=p, dependent=ON)
		a1.translate(instanceList=('Cut-2-3-1', ), vector=(-T2, 0.0, T1))
		a1 = mdb.models[ModelName].rootAssembly
		a1.InstanceFromBooleanCut(name='Fork-1', 
			instanceToBeCut=mdb.models[ModelName].rootAssembly.instances['Part-2-1'], 
			cuttingInstances=(a1.instances['Cut-2-3-1'], ), originalInstances=DELETE)
		p = mdb.models[ModelName].parts['Fork-1']
		f = p.faces
		p.Mirror(mirrorPlane=f.findAt(coordinates=(0.0, L3/2, T1/4.0)), keepOriginal=ON)

		# Fork-cm
		a = mdb.models[ModelName].rootAssembly
		a.translate(instanceList=('X-Support-1', ), vector=(0.0, 0.0, T1))
		a = mdb.models[ModelName].rootAssembly
		a.InstanceFromBooleanMerge(name='Fork-cm', instances=(
			a.instances['X-Support-1'], a.instances['Fork-1-1'], ), 
			keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)

		# Fork-m
		p1 = mdb.models[ModelName].parts['Fork-cm']
		p = mdb.models[ModelName].Part(name='Fork-m', 
			objectToCopy=mdb.models[ModelName].parts['Fork-cm'], 
			compressFeatureList=ON, scale=0.01)
		
		# Fork-cm-SA
		a = mdb.models[ModelName].rootAssembly
		p = mdb.models[ModelName].parts['X-Support']
		a.Instance(name='X-Support-1', part=p, dependent=ON)
		a.translate(instanceList=('X-Support-1', ), vector=(0.0, 0.0, T1))
		a = mdb.models[ModelName].rootAssembly
		a.InstanceFromBooleanMerge(name='Fork-cm-SA', instances=(
			a.instances['X-Support-1'], a.instances['Fork-cm-1'], ), 
			originalInstances=DELETE, domain=GEOMETRY)

		# Partitioning
		p = mdb.models[ModelName].parts['Fork-m']
		c = p.cells
		pickedCells = c.findAt(((0.0, L3/2/100, 0.0), ))
		v1, e1, d1 = p.vertices, p.edges, p.datums
		p.PartitionCellByPlaneThreePoints(point1=(W3/2/100, L3/100, 0), point2=(-W3/2/100, L3/100, 0), 
			point3=(W3/2/100, L3/100, T), cells=pickedCells) # Partition handle from part above neck
		p = mdb.models[ModelName].parts['Fork-m']
		p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=(L-tipBuffer)/100)
		if cutTips:
			p = mdb.models[ModelName].parts['Fork-m']
			c = p.cells
			pickedCells = c.findAt((((Ws+Wt2)/2/100, (L3+l5)/100, (h5)/100), ))
			d = p.datums
			p.PartitionCellByDatumPlane(datumPlane=d[3], cells=pickedCells) # Partition tips of fork tines
		seedBuffer = handleSeedSize*4
		# if localHandle: # if seeding handle locally with larger seed sizes
			# p = mdb.models[ModelName].parts['Fork-m']
			# p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=(L3/100-seedBuffer))
			# p = mdb.models[ModelName].parts['Fork-m']
			# c = p.cells
			# pickedCells = c.findAt(((0.0, L3/2/100, 0.0), ))
			# d = p.datums
			# p.PartitionCellByDatumPlane(datumPlane=d[5], cells=pickedCells) # Partition handle
		p = mdb.models[ModelName].parts['Fork-m']
		c = p.cells
		pickedCells = c.findAt(((0.0, L3/2/100, 0.0), ))
		v, e, d = p.vertices, p.edges, p.datums
		# p.PartitionCellByPlaneThreePoints(point1=((W3/2-T2)/100, L3/100, T1/100), point2=(-(W3/2-T2)/100, L3/100, T1/100), point3=((W3/2-T2)/100, T2/100, T1/100), 
			# cells=pickedCells) # Partition main handle thickness from outer ridges

			
		# Create Material
		print 'Creating the Materials'
		mdb.models[ModelName].Material(name='PLA')
		mdb.models[ModelName].materials['PLA'].Elastic(table=((3986000000.0, 0.332), ))

		#Create/Assign Section
		print 'Creating the Sections'
		mdb.models[ModelName].HomogeneousSolidSection(name='PLA-Section', 
			material='PLA', thickness=None)

		print 'Assigning the Sections'
		p = mdb.models[ModelName].parts['Fork-m']
		c = p.cells
		# cells = c.findAt(((0.0, (L3+L2)/100, h4/100), ), ((0.0, (L3/2)/100, 0.0), ), # Above neck & Main handle
			# ((0.0, (L3-Lx/2)/100, (T1+Tx1)/100), ), ((0, (T2/2)/100, T/100), ), # X-Support & Handle ridges
			# (((W1-Wtip)/2/100, L/100, (h7)/100), ), ((-(W1-Wtip)/2/100, L/100, (h7)/100), ), # Outer tine tips
			# (((Ws+Wt2)/2/100, L/100, (h7)/100), ), ((-(Ws+Wt2)/2/100, L/100, (h7)/100), )) # Inner tine tips
		region = p.Set(cells=p.cells, name='Fork-Set')
		p = mdb.models[ModelName].parts['Fork-m']
		p.SectionAssignment(region=region, sectionName='PLA-Section', offset=0.0, 
			offsetType=MIDDLE_SURFACE, offsetField='', 
			thicknessAssignment=FROM_SECTION)

		#Assemble Parts
		print 'Placing Parts in Space'
		a = mdb.models[ModelName].rootAssembly
		session.viewports['Viewport: 1'].setValues(displayedObject=a)
		del a.features['Fork-cm-SA-1'] # Deleting Fork-cm-SA from assembly
		a1 = mdb.models[ModelName].rootAssembly
		p = mdb.models[ModelName].parts['Fork-m']
		a1.Instance(name='Fork-m-1', part=p, dependent=ON) # Adding Fork-m to assembly
		
		loadName = 'Load-%s' % (loadn)
		stepName = 'Load-%s' % (loadn)
		if loadn==1:
			#Define Steps
			print 'Defining the Steps'
			mdb.models[ModelName].StaticStep(name=stepName, previous='Initial', 
				initialInc=0.1)
			session.viewports['Viewport: 1'].assemblyDisplay.setValues(step=stepName)
			
			# Create Sets
			a = mdb.models[ModelName].rootAssembly
			c1 = a.instances['Fork-m-1'].cells
			cells1 = c1.findAt(((0.0, (L3+L2)/100, h4/100), ), ((0.0, (L3/2)/100, 0.0), ), # Above neck & Main handle
				((0.0, (L3-Lx/2)/100, (T1+Tx1)/100), )) # X-Support
				# Handle Partition = ((0.0, L3/100-seedBuffer/2, 0.0), )
			a.Set(cells=cells1,name='Without-Tips')
		
			#Define Loads
			print 'Defining Loads'

			# Load-1 (Vertical)
			F1 = 15.0 # Newtons
			a = mdb.models[ModelName].rootAssembly
			s1 = a.instances['Fork-m-1'].faces
			surfFace1 = s1.findAt((0, L3/2/100, 0))
			#surfFace2 = s1.findAt((0.0, L3/100-seedBuffer/2, 0.0))
			Asurf1 = surfFace1.getSize() # + surfFace2.getSize()
			side1Faces1 = s1.findAt(((0, L3/2/100, 0), ))
			region = a.Surface(side1Faces=side1Faces1, name='Surf-1')
			mdb.models[ModelName].SurfaceTraction(name=loadName, createStepName=stepName, 
				region=region, magnitude=(F1 / Asurf1), directionVector=((0.0, 0.0, 0.0), (0.0, 
				1.0, 0.0)), distributionType=UNIFORM, field='', localCsys=None)
				
			a.regenerate()
			
			#Define BCs
			print 'Defining all BCs'
			# Food-Surface [Analytical Surface for BC-1-1 on tips]
			s1 = mdb.models[ModelName].ConstrainedSketch(name='__profile__', 
			sheetSize=20.0)
			g, v, d1, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
			s1.setPrimaryObject(option=STANDALONE)
			s1.Line(point1=(-W/100, L/100), point2=(W/100, L/100))
			p = mdb.models[ModelName].Part(name='Food-Surface', dimensionality=THREE_D, 
				type=DISCRETE_RIGID_SURFACE)
			p = mdb.models[ModelName].parts['Food-Surface']
			p.BaseShellExtrude(sketch=s1, depth=W/100)
			s1.unsetPrimaryObject()
			p = mdb.models[ModelName].parts['Food-Surface']
			p.ReferencePoint(point=(0.0, L/100, W/2/100))
			del mdb.models[ModelName].sketches['__profile__']
			# Constraining Fork-m and Food-Surface
			a = mdb.models[ModelName].rootAssembly
			p = mdb.models[ModelName].parts['Food-Surface']
			a.Instance(name='Food-Surface-1', part=p, dependent=ON)
			a.translate(instanceList=('Food-Surface-1', ), vector=(0.0, 0.0, -W/2/100))
			a = mdb.models[ModelName].rootAssembly
			s1 = a.instances['Food-Surface-1'].faces
			side1Faces1 = s1.findAt(((0.0, L/100, W/2/100), )) # Master Surface
			region1=a.Surface(side1Faces=side1Faces1, name='m_Surf-2')
			a = mdb.models[ModelName].rootAssembly
			s1 = a.instances['Fork-m-1'].faces
			tipZ = (h7+T1/2)/100
			side1Faces1 = s1.findAt(((-(W1-Wtip)/2/100, L/100, tipZ), ), ((-(Ws+Wt2)/2/100, L/100, 
				tipZ), ), (((Ws+Wt2)/2/100, L/100, tipZ), ), (((W1-Wtip)/2/100, L/100, tipZ), 
				)) # Slave Surface
			region2=a.Surface(side1Faces=side1Faces1, name='s_Surf-2')
			mdb.models[ModelName].Tie(name='Constraint-1', master=region1, slave=region2, 
				positionToleranceMethod=COMPUTED, adjust=OFF, tieRotations=ON, 
				thickness=ON)
			# BC-1-1
			a = mdb.models[ModelName].rootAssembly
			r1 = a.instances['Food-Surface-1'].referencePoints
			refPoints1=(r1[2], )
			region = a.Set(referencePoints=refPoints1, name='Set-1-1')
			mdb.models[ModelName].EncastreBC(name='BC-1-1', createStepName=stepName, 
				region=region, localCsys=None)
			# BC-1-2
			a = mdb.models[ModelName].rootAssembly
			f1 = a.instances['Fork-m-1'].faces
			faces1 = f1.findAt(((0, L3/2/100, 0), ), ((0, 0.0, (T1+(T-T1))/2/100), ))
			region = a.Set(faces=faces1, name='Set-1-2')
			mdb.models[ModelName].DisplacementBC(name='BC-1-2', createStepName=stepName, 
				region=region, u1=0.0, u2=UNSET, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
				amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
				localCsys=None)

			# Field Output Request for Model
			#Define Sets
			print 'Defining Sets'
			
			# Create reference points
			a = mdb.models[ModelName].rootAssembly
			v1 = a.instances['Fork-m-1'].vertices
			a.ReferencePoint(point=v1.findAt(coordinates=((Ws+Wt2-T3)/2/100, (L3+L2)/100, (h4+T)/100)))
			a = mdb.models[ModelName].rootAssembly
			v1 = a.instances['Fork-m-1'].vertices
			a.ReferencePoint(point=v1.findAt(coordinates=(0.0, 0.0, 0.0)))
			a = mdb.models[ModelName].rootAssembly
			
			# Create coupling constraints
			a = mdb.models[ModelName].rootAssembly
			r1 = a.referencePoints
			refPoints1=(r1[44], )
			region1=a.Set(referencePoints=refPoints1, name='m_Set-5')
			a = mdb.models[ModelName].rootAssembly
			v1 = a.instances['Fork-m-1'].vertices
			verts1 = v1.findAt((((Ws+Wt2-T3)/2/100, (L3+L2)/100, (h4+T)/100), ))
			region2=a.Set(vertices=verts1, name='s_Set-5')
			mdb.models[ModelName].Coupling(name='Constraint-1-1', controlPoint=region1, 
				surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, 
				localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
			a = mdb.models[ModelName].rootAssembly
			r1 = a.referencePoints
			refPoints1=(r1[45], )
			region1=a.Set(referencePoints=refPoints1, name='m_Set-6')
			a = mdb.models[ModelName].rootAssembly
			v1 = a.instances['Fork-m-1'].vertices
			verts1 = v1.findAt(((0.0, 0.0, 0.0), ))
			region2=a.Set(vertices=verts1, name='s_Set-6')
			mdb.models[ModelName].Coupling(name='Constraint-1-2', controlPoint=region1, 
				surface=region2, influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC, 
				localCsys=None, u1=ON, u2=ON, u3=ON, ur1=ON, ur2=ON, ur3=ON)
				
		if loadn==2:
			#Define Steps
			print 'Defining the Steps'
			mdb.models[ModelName].StaticStep(name=stepName, previous='Initial', 
				initialInc=0.1)
			session.viewports['Viewport: 1'].assemblyDisplay.setValues(step=stepName)

			#Define Loads
			print 'Defining Loads'

			# Load-2 (Horizontal)
			a = mdb.models[ModelName].rootAssembly
			s1 = a.instances['Fork-m-1'].faces
			side1Faces1 = s1.findAt((((Ws+Wt2)/2/100, (L3+l5)/100, (h5)/100), ))
			region = a.Surface(side1Faces=side1Faces1, name='Surf-2')
			# calculating area and pressure
			F2 = 5.0 # Newtons
			surf2Face = s1.findAt(((Ws+Wt2)/2/100, (L3+l5)/100, (h5)/100))
			Asurf2 = surf2Face.getSize()
			mdb.models[ModelName].SurfaceTraction(name=loadName, createStepName=stepName, 
				region=region, magnitude=(F2 / Asurf2), directionVector=((0.0, 0.0, 0.0), (0.0, 0.0, 
				1.0)), distributionType=UNIFORM, field='', localCsys=None, 
				traction=GENERAL, follower=OFF) # follow rotation off
			a = mdb.models[ModelName].rootAssembly
			a.regenerate()
			
			#Define BCs
			print 'Defining all BCs'
			# BC-2-1
			a = mdb.models[ModelName].rootAssembly
			f1 = a.instances['Fork-m-1'].faces
			faces1 = f1.findAt(((0.0, L3/2/100, 0), )) # (0.0, T2/2/100, T/100)
			region = a.Set(faces=faces1, name='Set-2-1')
			mdb.models[ModelName].DisplacementBC(name='BC-2-1', createStepName=stepName, 
				region=region, u1=0.0, u2=UNSET, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
				amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
				localCsys=None)
			# BC-2-2
			a = mdb.models[ModelName].rootAssembly
			f1 = a.instances['Fork-m-1'].faces
			faces1 = f1.findAt(((0.0, 0.0, T/2/100), )) # (0.0, T2/2/100, T/100)
			region = a.Set(faces=faces1, name='Set-2-2')
			mdb.models[ModelName].DisplacementBC(name='BC-2-2', createStepName=stepName, 
				region=region, u1=0.0, u2=0.0, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET, 
				amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', 
				localCsys=None)
			
			# Field Output Request for Model
			#Define Sets
			print 'Defining Sets'
			
			flattip1 = Wtip - (2*fr1 - fr1/L11 * 2*((W1/2-Wtip) - (1.5*Ws+Wt2))) # width of flat part of outer tip in cm
			flattip2 = Wtip - (2*fr1 - fr1/L11 * (Wt2-Wtip)) # width of flat part of inner tip in cm
			# Create reference points
			a = mdb.models[ModelName].rootAssembly
			e1 = a.instances['Fork-m-1'].edges
			a.ReferencePoint(point=a.instances['Fork-m-1'].InterestingPoint(edge=e1.findAt(
				coordinates=((Ws+Wt2-flattip2)/2/100, L/100, (h7)/100)), rule=MIDDLE))
			a = mdb.models[ModelName].rootAssembly
			e1 = a.instances['Fork-m-1'].edges
			a.ReferencePoint(point=a.instances['Fork-m-1'].InterestingPoint(edge=e1.findAt(
				coordinates=((W1-Wtip-flattip1)/2/100, L/100, (h7)/100)), rule=MIDDLE))
			a = mdb.models[ModelName].rootAssembly
			
			# Create tie constraints
			a = mdb.models[ModelName].rootAssembly
			v1 = a.instances['Fork-m-1'].vertices
			verts1 = v1.findAt((((Ws+Wt2-flattip2)/2/100, L/100, (h7)/100), ))
			region1=a.Set(vertices=verts1, name='m_Set-Node-1')
			a = mdb.models[ModelName].rootAssembly
			r1 = a.referencePoints
			refPoints1=(r1[39], )
			region2=a.Set(referencePoints=refPoints1, name='s_Set-Node-1')
			mdb.models[ModelName].Tie(name='Tie-2-1', master=region1, slave=region2, 
				positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)
				
			a = mdb.models[ModelName].rootAssembly
			v1 = a.instances['Fork-m-1'].vertices
			verts1 = v1.findAt((((W1-Wtip-flattip1)/2/100, L/100, (h7)/100), ))
			region1=a.Set(vertices=verts1, name='m_Set-Node-2')
			a = mdb.models[ModelName].rootAssembly
			r1 = a.referencePoints
			refPoints1=(r1[40], )
			region2=a.Set(referencePoints=refPoints1, name='s_Set-Node-2')
			mdb.models[ModelName].Tie(name='Tie-2-2', master=region1, slave=region2, 
				positionToleranceMethod=COMPUTED, adjust=ON, tieRotations=ON, thickness=ON)
			
		#Mesh Parts
		print 'Meshing the Baffle'
		# set mesh controls
		p = mdb.models[ModelName].parts['Fork-m']
		c = p.cells
		# pickedRegions = c.findAt(((0.0, (L3+L2)/100, h4/100), ), ((0.0, (L3/2)/100, 0.0), ), # Above neck & Main handle
			# ((0.0, (L3-Lx/2)/100, (T1+Tx1)/100), ), ((0, (T2/2)/100, T/100), ), # X-Support & Handle ridges
			# (((W1-Wtip)/2/100, L/100, (h7)/100), ), ((-(W1-Wtip)/2/100, L/100, (h7)/100), )) # Tine tips
		# pickedRegions =(cells, )
		p.setMeshControls(regions=p.cells, elemShape=TET, technique=FREE)
		elemType1 = mesh.ElemType(elemCode=C3D20R)
		elemType2 = mesh.ElemType(elemCode=C3D15)
		elemType3 = mesh.ElemType(elemCode=C3D10)
		p = mdb.models[ModelName].parts['Fork-m']
		c = p.cells
		# pickedRegions = c.findAt(((0.0, (L3+L2)/100, h4/100), ), ((0.0, (L3/2)/100, 0.0), ), # Above neck & Main handle
			# ((0.0, (L3-Lx/2)/100, (T1+Tx1)/100), ), ((0, (T2/2)/100, T/100), ), # X-Support & Handle ridges
			# (((W1-Wtip)/2/100, L/100, (h7)/100), ), ((-(W1-Wtip)/2/100, L/100, (h7)/100), )) # Tine tips
		# pickedRegions =(cells, )
		pickedRegions =(c, )
		p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, 
			elemType3))
		# seed part
		p = mdb.models[ModelName].parts['Fork-m']
		p.seedPart(size=seedSize, deviationFactor=0.1, minSizeFactor=0.1)
		# local seed handle
		if localHandle: # if seeding handle locally with larger seed sizes
			p = mdb.models[ModelName].parts['Fork-m']
			e = p.edges
			midHandleX = (W3 + (W4-W3)/2) / 2 # X-coordinate of handle edge whe Y = L3/2
			lowHandleX = W3/2 + (W4-W3)/2 * (L3-T2)/L3 - T2 # X-coordinate of inner handle edge whe Y = T2
			pickedEdges = e.findAt(((0,0,0), ), ((0,0,T/100), ), ((0,T2/100,T1/100), ), ((0,T2/100,T/100), ), 
				((-W4/4/100,0,0), ), ((-W4/4/100,0,T/100), ), ((-W4/4/100,T2/100,T1/100), ), ((-W4/4/100,T2/100,T/100), ), 
				((W4/2/100, 0, T/2/100), ), ((-W4/2/100, 0, T/2/100), ), ((lowHandleX/100, T2/100, T/2/100), ), ((-lowHandleX/100, T2/100, T/2/100), ))
			p.seedEdgeBySize(edges=pickedEdges, size=handleSeedSize, deviationFactor=0.1, 
				minSizeFactor=0.1, constraint=FINER)
			p = mdb.models[ModelName].parts['Fork-m']
			e = p.edges 
			pickedEdges1 = e.findAt(((midHandleX/100, L3/2/100, T/100), ), ((-midHandleX/100, L3/2/100, T/100), ), (((midHandleX-T2)/100, L3/2/100, T/100), ), ((-(midHandleX-T2)/100, L3/2/100, T/100), ))
			pickedEdges2 = e.findAt(((midHandleX/100, L3/2/100, 0.0), ), ((-midHandleX/100, L3/2/100, 0.0), ), (((midHandleX-T2)/100, L3/2/100, T1/100), ), ((-(midHandleX-T2)/100, L3/2/100, T1/100), ))
			p.seedEdgeByBias(biasMethod=SINGLE, end1Edges=pickedEdges1, 
				end2Edges=pickedEdges2, minSize=seedSize, maxSize=handleSeedSize, constraint=FINER)
		# mesh Fork-m
		p = mdb.models[ModelName].parts['Fork-m']
		p.generateMesh()
		if loadn==1:
			# mesh Food-Surface
			p = mdb.models[ModelName].parts['Food-Surface']
			p.seedPart(size=1.0, deviationFactor=0.1, minSizeFactor=0.1)
			p = mdb.models[ModelName].parts['Food-Surface']
			p.generateMesh()
			a.regenerate()

		#####################################
		### Creation/Execution of the Job ###
		#####################################
		print 'Creating/Running Job'

		ModelName = 'Model-%s' % (modelNum)

		mdb.Job(name=ModelName, model=ModelName, description='', 
				type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
				memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
				explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
				modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, 
				userSubroutine='', 
				scratch='', multiprocessingMode=DEFAULT, numCpus=4, numDomains=4)

		job=mdb.jobs[ModelName]

		# delete lock file, which for some reason tends to hang around, if it exists
		if os.access('%s.lck'%ModelName,os.F_OK):
			os.remove('%s.lck'%ModelName)
			# print 'lck file removed'

		# Runs job and extracts ODB data if RUNJOB is True
		if RUNJOB:
			# Run the job, then process the results.        
			job.submit()
			job.waitForCompletion()
			print 'Completed job'
		
		##########################################
		### Using Post-P Script to Get Results ###
		##########################################
		
		print 'Pulling data from ODB'
		results = getResults(ModelName, stepName, loadn)
		S = results[0]
		U = results[1]
		E = results[2]
		Un1 = results[3]
		Un2 = results[4]

		# Query Surface Area
		p = mdb.models[ModelName].parts['Fork-cm-SA']
		SA = p.getArea(p.faces)
		
		# Query Volume
		a = mdb.models[ModelName].rootAssembly
		prop = a.getMassProperties()
		V = prop['volume']
		V *= 10**6 # converting to cm^3

		# DataFile = open('PostData.txt','a')
		# DataFile.write('%1.0f, %1.0f, ' % (modelNum, n)) 
		# for val in varValues:
			# DataFile.write('%s, ' % (val)) 
		# DataFile.write('%1.3f, %1.1f, %1.3f, %1.4f, %1.3f, %1.3f\n' % (SA/V, S/1000000, U*100, E, Un1*100, Un2*100)) 
		# DataFile.close()

		# writing outputs for optimization
		yield_stress = 60e6 # 60 MPa, Source: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6926899/
		safety_factor = 1.1
		stress_threshold = yield_stress / safety_factor
		success_ind = '' # represents if both loads get executed successfully
		if loadn == 1:
			if S <= stress_threshold: # load 1 success
				score = -SA/V # this is negative in order to maximize using scipy minimize
			else:
				failure = True
				score += S / stress_threshold
			with open('all_run_data.txt', 'a') as fileObj:
				fileObj.write('%1.3f, %1.1f, ' % (SA/V, S/1000000)) 
		elif loadn == 2:
			if S > yield_stress/safety_factor: # load 2 failure
				if score < 0:
					score = 0
				score += S / stress_threshold
			with open('all_run_data.txt', 'a') as fileObj:
				fileObj.write('%1.3f, %1.1f, %1.3f \n' % (SA/V, S/1000000, score)) 
			success_ind += '\n1'
				
		with open('all_outputs.txt', 'a') as fileObj:
			fileObj.write('%d, %1.3f, %1.3f, %1.1f, %1.3f, %1.3f\n' % (loadn, score, SA/V, S/1000000, Un1*100, Un2*100)) 
		
	modelNum += 1

###END LOOP (i.e., end indentation)

with open('outputs.txt', 'w') as fileObj:
	fileObj.write(str(score) + success_ind)
with open('fork_script_metadata.txt', 'w') as fileObj:
	fileObj.write('VERSION, yield_stress, safety_factor, stress_threshold\n')
	fileObj.write('%1.1f, %1.1f, %1.2f, %1.3f \n\n' % (VERSION, yield_stress, safety_factor, stress_threshold)) 
		
print 'DONE!!'
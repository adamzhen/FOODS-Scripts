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

# Top View

L = 17.0 # TOTAL LENGTH (cm)
L1 = 0.38 * L
L11 = 0.5 * L1
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
W3 = 0.35 * W
W4 = 0.35 * W
W21 = 0.9 * (W-W3) + W3
l21 = 0.85 * L2
W22 = 0.53 * (W-W3) + W3
l22 = 0.65 * L2
W23 = 0.05 * (W-W3) + W3
l23 = 0.3 * L2

fr1 = Wtip / 3
fr2 = Ws / 2

# Side View

T = 0.4 # MAXIMUM THICKNESS (cm)
T1 = T * 0.25

l4 = L2
h4 = 1.6 # heights expressed in terms of h4, since it's the max height
h7 = 0.3 * h4 # height of tine tip from plane
l2 = 0.54 * l4
h2 = 0.55 * h4
l1 = 0.27 * l4
h1 = 0.15 * h4
l3 = 0.75 * l4
h3 = 0.8 * h4
l5 = L1 - (L11+L12)/2
h5 = (h4 + h7) * 0.55
l6 = l5 + L11/100
h6 = h5 + (T + T1) * 0.6

# Bottom View

T2 = T * 0.3
T3 = T * 0.25

# X Support

Lx = 0.1 * L3
L4 = L3 - Lx
Tx1 = T * 0.5
Tx2 = T * 0.5
rx = W3 * 0.25

# Seed Size
seedScale = 100 # number of elements that will fit across one diagonal of the fork handle
seedSize = sqrt( (((W4-W3)/2)**2) + (L3**2) ) / seedScale / 100 # calculating seed size and converting from cm to m

####################################
### Calculated Properties/Values ###
####################################

  
#####################################
### Generation of SOLID FEA Model ###
#####################################

### Note: If you create a loop, start it here

### Scripting the entire model allows its entire
### contents to be packaged into this single file.

modelNum = 1
meanParameters = []
rangeParameters = [ 	# Min, Max
[14.0, 20.0], #L = 17.0 # TOTAL LENGTH (cm)
[0.32, 0.44], #L1 = 0.38 * L #Length from neck to point
[0.4, 0.6], #L11 = 0.5 * L1 #Length from root to point
[0.55, 0.95], #L2 = 0.75 * (L-L1)
[2.0, 3.0], #W = 2.5 # MAXIMUM WIDTH (cm)
[0.25, 0.45], #W3 = 0.35 * W
[0.2, 0.5], #W4 = 0.35 * W #Width of the bottom of the handle
[0.86, 0.94], #W21 = 0.9 * (W-W3) + W3
[0.5, 0.56], #W22 = 0.53 * (W-W3) + W3
[0.02, 0.08], #W23 = 0.05 * (W-W3) + W3
[0.3, 0.5], #T = 0.4 # MAXIMUM THICKNESS (cm)
[0.1, 0.4], #T1 = T * 0.25 #Thickness of the overall surface
[1.2, 2.0], #h4 = 1.6 # heights expressed in terms of h4, since it's the max height
[0.0, 0.6], #h7 = 0.3 * h4 # height of tine tip from plane
[0.45, 0.55], #h2 = 0.5 * h4
[0.5, 0.7], #h6 = h5 + (T + T1) * 0.6
[0.15, 0.35], #T2 = T * 0.3 #Thickness of outer ridges
[0.15, 0.35] #T3 = T * 0.3 #Thickness of middle ridges
]
paramNames = ['L', 'L1', 'L11', 'L2', 'W', 'W3', 'W4', 'W21', 'W22', 'W23', 'T', 'T1', 'h4', 'h7', 'h2', 'h6', 'T2', 'T3']
curveIndices = [5,6,7,14]
varScale = 0.1
varParameters = []
# for i in range(len(meanParameters)):
	# p = meanParameters[i]
	# if i in curveIndices:
		# varParameters.append([p*(1-varScale/2), p, p*(1+varScale/2)])
	# else:
		# varParameters.append([p*(1-varScale), p, p*(1+varScale)])
for p in rangeParameters:
	varParameters.append([p[0], (p[0]+p[1])/2, p[1]])
	meanParameters.append((p[0]+p[1])/2)
print varParameters

DataFile = open('VaryingParametersFormatted.txt','w')
DataFile.write('Min, Max\n')
DataFile.write('%s\n\n' % (', '.join(paramNames)))
# DataFile.write('normal scale = %1.2f\n' % (varScale))
# DataFile.write('curve scale = %1.2f (' % (varScale/2))
# for i in range(len(curveIndices)):
	# ind = curveIndices[i]
	# if i == len(curveIndices)-1:
		# DataFile.write('%s)' % (paramNames[ind]))
	# else:
		# DataFile.write('%s, ' % (paramNames[ind]))
# DataFile.write('\n\n')
DataFile.close()
RawDataFile = open('VaryingParametersCSV.txt', 'w')
RawDataFile.write('name, val, j, V, SA, SA:V\n')
RawDataFile.close()

for vari in range(len(varParameters)):
	param = varParameters[vari]
	for j in range(0, 3, 2):
		vars = meanParameters[:]
		vars[vari] = param[j]
		print vari
		print j
		print vars
		# Top View
		
		L = vars[0] # TOTAL LENGTH (cm)
		L1 = vars[1] * L
		L11 = vars[2] * L1
		L2 = vars[3] * (L1-L11)
		L12 = L1 - L11 - L2
		L3 = L - L1

		W = vars[4] # MAXIMUM WIDTH (cm)
		W1 = 0.83 * W
		Wtip = 0.04 * W
		W12 = L11/(L11+L12) * (W-W1) + W1
		Wt1 = 0.16 * W12 # 2 outer tines
		Wt2 = 0.16 * W12 # 2 inner tines
		Ws = (W12 - 2*Wt1 - 2*Wt2) / 3 # 3 slots
		W3 = vars[5] * W
		W4 = vars[6] * W
		W21 = vars[7] * (W-W3) + W3
		l21 = 0.85 * L2
		W22 = vars[8] * (W-W3) + W3
		l22 = 0.65 * L2
		W23 = vars[9] * (W-W3) + W3
		l23 = 0.3 * L2

		fr1 = Wtip / 3
		fr2 = Ws / 2

		# Side View

		T = vars[10] # MAXIMUM THICKNESS (cm)
		T1 = T * vars[11]

		l4 = L2
		h4 = vars[12] # heights expressed in terms of h4, since it's the max height
		h7 = vars[13] * h4 # height of tine tip from plane
		l1 = 0.27 * l4
		h1 = 0.15 * h4
		l2 = 0.54 * l4
		h2 = vars[14] * h4
		l3 = 0.75 * l4
		h3 = 0.8 * h4
		l5 = L1 - (L11+L12)/2
		h5 = (h4 + h7) * 0.55
		l6 = l5 + L11/100
		h6 = h5 + (T + T1) * vars[15]

		# Bottom View

		T2 = T * vars[16]
		T3 = T * vars[17]

		# X Support

		Lx = 0.1 * L3
		L4 = L3 - Lx
		Tx1 = T * 0.5
		Tx2 = T * 0.5
		rx = W3 * 0.25

		Mdb()   

		# Recreate the model using the current parameter values
			
		# Sketch Geometry and Create Parts

		print 'Sketching/Creating the Baffle'

		# TopSketch
		s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=50.0)
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
		mdb.models['Model-1'].sketches.changeKey(fromName='__profile__', 
			toName='TopSketch')
		s.unsetPrimaryObject()

		# SideSketch
		s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=50.0)
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
		s.TangentConstraint(entity1=g[4], entity2=g[5])
		s.TangentConstraint(entity1=g[3], entity2=g[4])
		s.TangentConstraint(entity1=g[5], entity2=g[6])
		s.offset(distance=T, objectList=(g[3], g[4], g[5]), side=RIGHT)
		s.Spot(point=(-L3-l4, h4+T))
		s.FixedConstraint(entity=v[14])
		s.CoincidentConstraint(entity1=v[14], entity2=v[12])
		s.Line(point1=(-L, h7), point2=(-L, h7+T1))
		s.Arc3Points(point1=(-L, h7+T1), point2=(-L3-l4, h4+T), point3=(-L3-l6, h6))
		mdb.models['Model-1'].sketches.changeKey(fromName='__profile__', 
			toName='SideSketch')
		s.unsetPrimaryObject()

		# Part-1
		s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
			sheetSize=200.0)
		g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
		s1.setPrimaryObject(option=STANDALONE)
		s1.sketchOptions.setValues(gridOrigin=(0,0))
		s1.retrieveSketch(sketch=mdb.models['Model-1'].sketches['TopSketch'])
		session.viewports['Viewport: 1'].view.fitView()
		#: Info: 20 entities copied from TopSketch.
		s1.move(vector=(0,0), objectList=(g[4], g[5], 
			g[6], g[7], g[8], g[9], g[10], g[11], g[12], g[13], g[14], g[15], g[16], 
			g[17], g[18], g[19], g[20], g[21], g[22], g[23]))
		p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models['Model-1'].parts['Part-1']
		p.BaseSolidExtrude(sketch=s1, depth=h4*2)
		s1.unsetPrimaryObject()
		p = mdb.models['Model-1'].parts['Part-1']
		session.viewports['Viewport: 1'].setValues(displayedObject=p)
		del mdb.models['Model-1'].sketches['__profile__']

		# Cut-1
		# Creating Block
		s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=50.0)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=STANDALONE)
		s.Line(point1=(0.0, 0.0), point2=(W*2, 0.0))
		s.Line(point1=(W*2, 0.0), point2=(W*2, L+0.5))
		s.Line(point1=(W*2, L+0.5), point2=(0, L+0.5))
		s.Line(point1=(0, L+0.5), point2=(0, 0))
		p = mdb.models['Model-1'].Part(name='Cut-1', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models['Model-1'].parts['Cut-1']
		p.BaseSolidExtrude(sketch=s, depth=h4*2)
		s.unsetPrimaryObject()
		p = mdb.models['Model-1'].parts['Cut-1']
		del mdb.models['Model-1'].sketches['__profile__']
		# Cut
		p = mdb.models['Model-1'].parts['Cut-1']
		f1, e1 = p.faces, p.edges
		t = p.MakeSketchTransform(sketchPlane=f1[3], sketchUpEdge=e1[8], 
			sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
		s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
			sheetSize=37.54, gridSpacing=0.93, transform=t)
		g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
		#s1.setPrimaryObject(option=SUPERIMPOSE)
		p = mdb.models['Model-1'].parts['Cut-1']
		p.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
		s1.retrieveSketch(sketch=mdb.models['Model-1'].sketches['SideSketch'])
		session.viewports['Viewport: 1'].view.fitView()
		#: Info: 10 entities copied from SideSketch.
		p = mdb.models['Model-1'].parts['Cut-1']
		f, e = p.faces, p.edges
		p.CutExtrude(sketchPlane=f[3], sketchUpEdge=e[8], sketchPlaneSide=SIDE1, 
			sketchOrientation=RIGHT, sketch=s1, flipExtrudeDirection=OFF)
		s1.unsetPrimaryObject()
		del mdb.models['Model-1'].sketches['__profile__']

		# Part-2
		a = mdb.models['Model-1'].rootAssembly
		a.DatumCsysByDefault(CARTESIAN)
		p = mdb.models['Model-1'].parts['Cut-1']
		a.Instance(name='Cut-1-1', part=p, dependent=ON)
		p = mdb.models['Model-1'].parts['Part-1']
		a.Instance(name='Part-1-1', part=p, dependent=ON)
		a = mdb.models['Model-1'].rootAssembly
		a.InstanceFromBooleanCut(name='Part-2', 
			instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['Part-1-1'], 
			cuttingInstances=(a.instances['Cut-1-1'], ), originalInstances=DELETE)

		# Cut-2-1
		p1 = mdb.models['Model-1'].parts['Part-2']
		p = mdb.models['Model-1'].Part(name='Cut-2-1', 
			objectToCopy=mdb.models['Model-1'].parts['Part-2'])
		p = mdb.models['Model-1'].parts['Cut-2-1']
		f, e = p.faces, p.edges
		t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(W4/10, L3/10, 0.0)), 
			sketchUpEdge=e.findAt(coordinates=(0.0, L3/2, 0.0)), sketchPlaneSide=SIDE1, 
			sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
		s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
			sheetSize=25, gridSpacing=0.5, transform=t)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		#s.setPrimaryObject(option=SUPERIMPOSE)
		p = mdb.models['Model-1'].parts['Cut-2-1']
		p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
		s.Line(point1=(0.0, 0.0), point2=(W4/2, 0.0))
		s.Line(point1=(W4/2, 0.0), point2=(W4/2, -T2))
		s.Line(point1=(W4/2, -T2), point2=(0.0, -T2))
		s.Line(point1=(0.0, -T2), point2=(0.0, 0.0))
		p = mdb.models['Model-1'].parts['Cut-2-1']
		f1, e1 = p.faces, p.edges
		p.CutExtrude(sketchPlane=f1.findAt(coordinates=(W4/10, L3/10, 0.0)), 
			sketchUpEdge=e1.findAt(coordinates=(0.0, L3/2, 0.0)), sketchPlaneSide=SIDE1, 
			sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
		s.unsetPrimaryObject()
		del mdb.models['Model-1'].sketches['__profile__']

		# SideCutSketch
		mdb.models['Model-1'].ConstrainedSketch(name='SideCutSketch', 
			objectToCopy=mdb.models['Model-1'].sketches['SideSketch'])
		s = mdb.models['Model-1'].ConstrainedSketch(name='__edit__', 
			objectToCopy=mdb.models['Model-1'].sketches['SideCutSketch'])
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=STANDALONE)
		s.delete(objectList=(g[2], g[3], g[4], g[5], g[7], g[8], g[9]))
		s.delete(objectList=(g[11], v[14]))
		s.Line(point1=(-L, h7+T1), point2=(-L, h4*2))
		s.Line(point1=(-L, h4*2), point2=(-L3-L2, h4*2))
		s.Line(point1=(-L3-L2, h4*2), point2=(-L3-L2, h4))
		mdb.models['Model-1'].sketches.changeKey(fromName='__edit__', 
			toName='SideCutSketch')
		s.unsetPrimaryObject()

		# Cut-2-2
		s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
			sheetSize=50.0)
		g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
		s1.setPrimaryObject(option=STANDALONE)
		s1.sketchOptions.setValues(gridOrigin=(0,0))
		s1.retrieveSketch(sketch=mdb.models['Model-1'].sketches['SideCutSketch'])
		session.viewports['Viewport: 1'].view.fitView()
		#: Info: 7 entities copied from SideCutSketch.
		p = mdb.models['Model-1'].Part(name='Cut-2-2', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models['Model-1'].parts['Cut-2-2']
		p.BaseSolidExtrude(sketch=s1, depth=(W1-Wtip)/2)
		s1.unsetPrimaryObject()
		p = mdb.models['Model-1'].parts['Cut-2-2']
		session.viewports['Viewport: 1'].setValues(displayedObject=p)
		del mdb.models['Model-1'].sketches['__profile__']

		# Cut-2-3
		a = mdb.models['Model-1'].rootAssembly
		del a.features['Part-2-1']
		a1 = mdb.models['Model-1'].rootAssembly
		p = mdb.models['Model-1'].parts['Cut-2-1']
		a1.Instance(name='Cut-2-1-1', part=p, dependent=ON)
		p = mdb.models['Model-1'].parts['Cut-2-2']
		a1.Instance(name='Cut-2-2-1', part=p, dependent=ON)
		a1 = mdb.models['Model-1'].rootAssembly
		a1.rotate(instanceList=('Cut-2-2-1', ), axisPoint=(0.0, 0.0, 0.0), 
			axisDirection=(0.0, 0.0, -1.0), angle=90.0)
		#: The instance Cut-2-2-1 was rotated by 90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 0., -1.
		a1 = mdb.models['Model-1'].rootAssembly
		a1.rotate(instanceList=('Cut-2-2-1', ), axisPoint=(0.0, 0.0, 0.0), 
			axisDirection=(0.0, 1.0, 0.0), angle=-90.0)
		#: The instance Cut-2-2-1 was rotated by -90. degrees about the axis defined by the point 0., 0., 0. and the vector 0., 1., 0.
		a1 = mdb.models['Model-1'].rootAssembly
		a1.translate(instanceList=('Cut-2-2-1', ), vector=((W1-Wtip)/2, 0.0, 0.0))
		a1 = mdb.models['Model-1'].rootAssembly
		# Merging Cut-2-1 and Cut-2-2
		a1.InstanceFromBooleanMerge(name='Cut-2-3', instances=(
			a1.instances['Cut-2-1-1'], a1.instances['Cut-2-2-1'], ), 
			originalInstances=DELETE, domain=GEOMETRY)
		# Extrude Cut (cut that will create ridges for inner tines)
		p = mdb.models['Model-1'].parts['Cut-2-3']
		f, e = p.faces, p.edges
		t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(W1/4, 
			L-L11, h4*2)), sketchUpEdge=e.findAt(coordinates=(W1/4, L, h4*2)), 
			sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0))
		s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
			sheetSize=34.05, gridSpacing=0.85, transform=t)
		#s.setPrimaryObject(option=SUPERIMPOSE)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		p = mdb.models['Model-1'].parts['Cut-2-3']
		p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
		tineY = (Ws+Wt2)/2 + T2
		tipBuffer = Wtip # cuts off inner tine ridges a certain distance before the tip, to allow for more accurate meshing
		s.Line(point1=(L-tipBuffer, -tineY - T3/2), point2=(L-tipBuffer, -tineY + T3/2))
		s.Line(point1=(L-tipBuffer, -tineY + T3/2), point2=(L-L1, -tineY + T3/2))
		s.Line(point1=(L-L1, -tineY + T3/2), point2=(L-L1, -tineY - T3/2))
		s.Line(point1=(L-L1, -tineY - T3/2), point2=(L-tipBuffer, -tineY - T3/2))
		p = mdb.models['Model-1'].parts['Cut-2-3']
		f1, e1 = p.faces, p.edges
		p.CutExtrude(sketchPlane=f.findAt(coordinates=(W1/4, L-L11, h4*2)), 
			sketchUpEdge=e.findAt(coordinates=(W1/4, L, h4*2)), 
			sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, 
			flipExtrudeDirection=OFF)
		s.unsetPrimaryObject()
		del mdb.models['Model-1'].sketches['__profile__']

		# X-Support
		cy = L4+Lx/2 # y-coordinate of circle center
		def getX(n): # returns X-value for diagonal parts when given y-value
			return ((L3-n)/L3 * (W4-W3) + W3) / 2 - T2
		# Circle
		s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
			sheetSize=50.0)
		g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
		s1.setPrimaryObject(option=STANDALONE)
		s1.CircleByCenterPerimeter(center=(0.0, cy), point1=(0.0, cy+rx))
		p = mdb.models['Model-1'].Part(name='X-Circle', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models['Model-1'].parts['X-Circle']
		p.BaseSolidExtrude(sketch=s1, depth=Tx1)
		s1.unsetPrimaryObject()
		p = mdb.models['Model-1'].parts['X-Circle']
		del mdb.models['Model-1'].sketches['__profile__']
		# Diagonal 1
		s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=50.0)
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
		p = mdb.models['Model-1'].Part(name='X-Diagonal-1', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models['Model-1'].parts['X-Diagonal-1']
		p.BaseSolidExtrude(sketch=s, depth=Tx1)
		s.unsetPrimaryObject()
		p = mdb.models['Model-1'].parts['X-Diagonal-1']
		del mdb.models['Model-1'].sketches['__profile__']
		# Diagonal 2
		s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=50.0)
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
		p = mdb.models['Model-1'].Part(name='X-Diagonal-2', dimensionality=THREE_D, 
			type=DEFORMABLE_BODY)
		p = mdb.models['Model-1'].parts['X-Diagonal-2']
		p.BaseSolidExtrude(sketch=s, depth=Tx1)
		s.unsetPrimaryObject()
		p = mdb.models['Model-1'].parts['X-Diagonal-2']
		del mdb.models['Model-1'].sketches['__profile__']
		# Assemble X-Support Parts
		a = mdb.models['Model-1'].rootAssembly
		p = mdb.models['Model-1'].parts['X-Circle']
		a.Instance(name='X-Circle-1', part=p, dependent=ON)
		p = mdb.models['Model-1'].parts['X-Diagonal-1']
		a.Instance(name='X-Diagonal-1-1', part=p, dependent=ON)
		p = mdb.models['Model-1'].parts['X-Diagonal-2']
		a.Instance(name='X-Diagonal-2-1', part=p, dependent=ON)
		a = mdb.models['Model-1'].rootAssembly
		a.InstanceFromBooleanMerge(name='X-Support', instances=(
			a.instances['X-Diagonal-1-1'], a.instances['X-Circle-1'], 
			a.instances['X-Diagonal-2-1'], ), originalInstances=DELETE, 
			domain=GEOMETRY)
		# Partition Circle in X-Support by sketch
		p = mdb.models['Model-1'].parts['X-Support']
		f, e, d = p.faces, p.edges, p.datums
		t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(0, 
			L3-Lx/2, Tx1)), sketchUpEdge=e.findAt(coordinates=(rx, 
			L3-Lx/2, Tx1)), sketchPlaneSide=SIDE1, origin=(0.0, 0.0, 0.0))
		s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
			sheetSize=21.63, gridSpacing=0.54, transform=t)
		g, v, d1, c = s.geometry, s.vertices, s.dimensions, s.constraints
		#s.setPrimaryObject(option=SUPERIMPOSE)
		p = mdb.models['Model-1'].parts['X-Support']
		p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
		s.CircleByCenterPerimeter(center=(0.0, L3-Lx/2), point1=(0.0, L3-Lx/2+rx))
		p = mdb.models['Model-1'].parts['X-Support']
		f = p.faces
		pickedFaces = f.findAt(((0, L3-Lx/2, Tx1), ))
		e1, d2 = p.edges, p.datums
		p.PartitionFaceBySketch(faces=pickedFaces, sketch=s)
		s.unsetPrimaryObject()
		del mdb.models['Model-1'].sketches['__profile__']
		
		# Fork-1 (without X-Support)
		a = mdb.models['Model-1'].rootAssembly
		del a.features['Cut-2-3-1']
		a1 = mdb.models['Model-1'].rootAssembly
		p = mdb.models['Model-1'].parts['Part-2']
		a1.Instance(name='Part-2-1', part=p, dependent=ON)
		a1 = mdb.models['Model-1'].rootAssembly
		p = mdb.models['Model-1'].parts['Cut-2-3']
		a1.Instance(name='Cut-2-3-1', part=p, dependent=ON)
		a1.translate(instanceList=('Cut-2-3-1', ), vector=(-T2, 0.0, T2))
		a1 = mdb.models['Model-1'].rootAssembly
		a1.InstanceFromBooleanCut(name='Fork-1', 
			instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['Part-2-1'], 
			cuttingInstances=(a1.instances['Cut-2-3-1'], ), originalInstances=DELETE)
		p = mdb.models['Model-1'].parts['Fork-1']
		f = p.faces
		p.Mirror(mirrorPlane=f.findAt(coordinates=(0.0, L3/2, T1/4.0)), keepOriginal=ON)

		# Fork-cm
		a = mdb.models['Model-1'].rootAssembly
		a.translate(instanceList=('X-Support-1', ), vector=(0.0, 0.0, T1))
		a = mdb.models['Model-1'].rootAssembly
		a.InstanceFromBooleanMerge(name='Fork-cm', instances=(
			a.instances['X-Support-1'], a.instances['Fork-1-1'], ), 
			keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)

		# Fork-m
		p1 = mdb.models['Model-1'].parts['Fork-cm']
		p = mdb.models['Model-1'].Part(name='Fork-m', 
			objectToCopy=mdb.models['Model-1'].parts['Fork-cm'], 
			compressFeatureList=ON, scale=0.01)

		# Partitioning
		p = mdb.models['Model-1'].parts['Fork-m']
		c = p.cells
		pickedCells = c.findAt(((0.0, L3/2/100, 0.0), ))
		v1, e1, d1 = p.vertices, p.edges, p.datums
		p.PartitionCellByPlaneThreePoints(point1=(W3/2/100, L3/100, 0), point2=(-W3/2/100, L3/100, 0), 
			point3=(W3/2/100, L3/100, T), cells=pickedCells) # Partition handle from part above neck
		p = mdb.models['Model-1'].parts['Fork-m']
		c = p.cells
		pickedCells = c.findAt(((0.0, L3/2/100, 0.0), ))
		v, e, d = p.vertices, p.edges, p.datums
		p.PartitionCellByPlaneThreePoints(point1=((W3/2-T2)/100, L3/100, T1/100), point2=(-(W3/2-T2)/100, L3/100, T1/100), point3=((W3/2-T2)/100, T2/100, T1/100), 
			cells=pickedCells) # Partition main handle thickness from outer ridges
		# p = mdb.models['Model-1'].parts['Fork-m']
		# c = p.cells
		# pickedCells = c.findAt(((0.0, 0.0, (T1+(T+T1)/2)/100), ))
		# v1, e1, d1 = p.vertices, p.edges, p.datums
		# p.PartitionCellByPlaneThreePoints(point1=((W4/2-T2)/2/100, T2/100, T1/100), point2=(-(W4/2-T2)/2/100, T2/100, T1/100), point3=((W4/2-T2)/2/100, T2/100, T/100), 
			# cells=pickedCells) # Partition side & bottom ridges apart, allows for hex meshing but unnecessary for tet
		# p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=(L-fr1)/100)
		# p = mdb.models['Model-1'].parts['Fork-m']
		# c = p.cells
		# pickedCells = c.findAt(((0.0, (L3+L2)/100, h4/100), ))
		# d2 = p.datums
		# p.PartitionCellByDatumPlane(datumPlane=d2[5], cells=pickedCells)

			
		# Create Material
		print 'Creating the Materials'
		mdb.models['Model-1'].Material(name='PLA')
		mdb.models['Model-1'].materials['PLA'].Elastic(table=((3986000000.0, 0.332), ))

		#Create/Assign Section
		print 'Creating the Sections'
		mdb.models['Model-1'].HomogeneousSolidSection(name='PLA-Section', 
			material='PLA', thickness=None)

		print 'Assigning the Sections'
		p = mdb.models['Model-1'].parts['Fork-m']
		c = p.cells
		cells = c.getSequenceFromMask(mask=('[#3ffff ]', ), )
		region = p.Set(cells=cells, name='Fork-Set')
		p = mdb.models['Model-1'].parts['Fork-m']
		p.SectionAssignment(region=region, sectionName='PLA-Section', offset=0.0, 
			offsetType=MIDDLE_SURFACE, offsetField='', 
			thicknessAssignment=FROM_SECTION)

		#Assemble Parts
		print 'Placing Parts in Space'
		a = mdb.models['Model-1'].rootAssembly
		session.viewports['Viewport: 1'].setValues(displayedObject=a)
		del a.features['Fork-cm-1'] # Deleting Fork-cm from assembly
		a1 = mdb.models['Model-1'].rootAssembly
		p = mdb.models['Model-1'].parts['Fork-m']
		a1.Instance(name='Fork-m-1', part=p, dependent=ON) # Adding Fork-m to assembly

		##########################################
		### Using Post-P Script to Get Results ###
		##########################################

		# Query Surface Area
		p = mdb.models['Model-1'].parts['Fork-cm']
		SA = p.getArea(p.faces)

		# Query Volume
		a = mdb.models['Model-1'].rootAssembly
		prop = a.getMassProperties()
		V = prop['volume']
		V *= 10**6 # converting to cm^3

		#Calculations (if needed)

		DataFile = open('VaryingParametersFormatted.txt','a')
		DataFile.write('%s = %1.3f\n' % (paramNames[vari], param[j])) 
		DataFile.write('j = %1.0f\n' % (j)) 
		DataFile.write('V = %1.3f\n' % (V)) # Volume in cm^3
		DataFile.write('SA = %1.3f\n' % (SA)) # Surface Area in cm^2
		DataFile.write('SA:V = %1.5f\n' % (SA/V)) # Volume in cm^3
		DataFile.write('\n')
		DataFile.close()
		
		RawDataFile = open('VaryingParametersCSV.txt', 'a')
		RawDataFile.write('%s, %1.3f, %1.0f, %1.3f, %1.3f, %1.5f\n' % (paramNames[vari], param[j], j, V, SA, SA/V))
		RawDataFile.close()
		
		modelNum += 1
###END LOOP (i.e., end indentation)

print 'DONE!!'
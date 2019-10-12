from mathutils import Vector
from math import sqrt
from random import uniform

def frameOffset(cont):
	own = cont.owner
	for act in cont.actuators:
		if hasattr(act, "frame"):
			act.frameStart = uniform(0, 0.75)

		cont.activate(act)

def lyprint(s, x=18):
	print( "\n" + "#//" + "--%s"%(s) + ("-" * (21-len(s)) ) )

def calcDistance(x1,y1,x2,y2):
	dist = sqrt((x2 - x1)**2 + (y2 - y1)**2)
	return dist

def coneRay(obj, target, r, doBool=False, z_adjust=False):
	l = [ [0, r], [r/2, r/2], [r, 0],
	[r/2, -r/2], [0, -r], [-r/2, -r/2],
	[-r, 0], [-r/2, r/2] ]

	cone = [False for i in range(8)]
	for i in range(8):
		offset = l[i]
		point = target.worldPosition.copy()
		point.y += offset[0]; point.z += offset[1]
		if z_adjust: point.z += z_adjust
		
		ray = obj.rayCast(point, mask=1, xray=True)[0]
		cone[i] = bool(ray) if doBool else ray

	return cone

def chunkIt(l, size):
	return [l[pos:pos+size] for pos in range(0, len(l), size+1)]

def floatApprox(f1, f2, fac=0.1):
	return f2-fac <= f1 <= f2+fac

def iLerp(i1, i2, l, p):
	abs_diff = abs(i1 - i2)
	real_diff = abs_diff/l
	s = 1 if i1 < i2 else -1
	return i1 + real_diff*(p*s)

def boneTrack(arma, bone):
	bone = arma.channels[bone]

	pos = bone.pose_head
	axisfix = Vector(bone.channel_matrix.to_euler())

	tgx = bone.rotation_euler[0] + axisfix[0]
	tgy = bone.rotation_euler[1] + axisfix[2]
	tgz = bone.rotation_euler[2]*-1  + axisfix[1]

	#pos += bone.pose_head
	#pos += Vector([tgx, tgz, tgy])

	return pos

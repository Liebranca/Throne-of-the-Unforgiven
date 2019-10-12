import bpy
import numpy as np
from blendInit import cwd
vert_cache = {}

actorBodyParts = ({"ds_torso":0, "ds_pelvis":1, "ds_head":2, "ds_neck":3, "ds_face":4,
				   "ds_upArm.L":5, "ds_upArm.R":6, "ds_foArm.L":7, "ds_foArm.R":8,
				   "ds_hand.L":9, "ds_hand.R":10, "ds_thigh.L":11, "ds_thigh.R":12,
				   "ds_calf.L":13, "ds_calf.R":14, "ds_foot.L":15, "ds_foot.R":16,
				})

def getCharData():
	ob = bpy.context.active_object
	for groupName in actorBodyParts:
		if groupName not in ob.vertex_groups: ob.vertex_groups.new(groupName)

	names = {g.index:g.name for g in ob.vertex_groups if "ds_" in g.name}
	getVertsInGroup_ufunc(ob.data.vertices, names)

def getVertsInGroup(v, names):
	posKey = ( str(v.co[0])+","+str(v.co[1])+","+str(v.co[2]) )
	vert_cache[posKey] = [names[g.group] for g in v.groups if g.group in names]

getVertsInGroup_ufunc = np.frompyfunc(getVertsInGroup, 2, 0)


def buildCharMesh(cont):
	getCharData()
	own = cont.owner; m = own.meshes[0]

	a = np.full(m.getVertexArrayLength(0), False, dtype=object)
	vi = np.arange(0, m.getVertexArrayLength(0), dtype=int)

	a = dumpCache_ufunc( a, vi, m )
	a = a[a != False]
	b = np.full( 17, None, dtype=object )

	keys = list(actorBodyParts.keys())
	i = 0

	for slot in b:
		index = keys[i]
		slot = {index:[]}
		result = genBodyArray_ufunc(a, slot, index)
		b[i] = result[0] if len(result) else []
		i += 1

	b = sortBodyArray_ufunc(b)
	np.save(cwd+"\\meshdata\\%s.npy"%(m.name), b )

def sortBodyArray(b):
	return [b[slot] for slot in b][0] if len(b) else []

sortBodyArray_ufunc = np.frompyfunc( sortBodyArray, 1, 1 )

def genBodyArray(a, slot, index):
	if a[1] == index: slot[index].append(a[0])
	return slot

genBodyArray_ufunc = np.frompyfunc( genBodyArray, 3, 1 )

def dumpCache(a, vi, m):
	v = m.getVertex( 0, vi )
	posKey = ( str(v.x)+","+str(v.y)+","+str(v.z) )

	if vert_cache[posKey]:
		a = [vi, vert_cache[posKey][0]]		

	return a

dumpCache_ufunc = np.frompyfunc(dumpCache, 3, 1)

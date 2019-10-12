#// 000. IMPORTS & NAMING
from bge.types import KX_GameObject, KX_VertexProxy
from mathutils import Vector, kdtree
from math import sqrt, radians
from random import uniform, randint
import numpy as np
from dsm import gamepath, color_ops, waterLevel, showDebug
from dsm.utils.lymath import chunkIt
import struct
import os

grass = Vector([0.0,0.25,0.0,1])
stone = Vector([1.75,0.0,0.0,1])
dirt = Vector([0.0,0.0,0.0,0])
sand = Vector([1.0,1.0, 0.0, 1])

i_list = [ (y, x) for y in range(41) for x in range(41) ]
terra_i = [ i for i in range(41*41) ]
ps = [(x, y) for y in range(-100, 101, 5) for x in range(-100, 101, 5) ]

core = None

defStatic = {"generic":True, "team":1, "kls":"statics"}

def batchAdd(obj_id, a):
	a = core.objSuspended[obj_id]
	del core.objSuspended[obj_id]

	return a

batchAdd_ufunc = np.frompyfunc(batchAdd, 2, 1)

#// 001. CLASS DEFINITION
class Landmass(KX_GameObject):
	def __init__(self, old_owner, pos, **kwargs):
		for key, value in kwargs.items():
			self.__dict__[key] = value

		if core.terra["reserved"]:
			self.id = core.terra["reserved"].pop(0)
			core.registerReserved(self)
		else:
			self.id = core.genID(self, "terra")

		cellDict = core.world["cellDict"]
		core.grid["cells"][(self.cell[0], self.cell[1])] = self.id

		cellIndex = (core.wOrigin[0]+self.cell[0], core.wOrigin[1]+self.cell[1])
		self.regions = (core.world["cellGen"][cellIndex]
					if cellIndex in core.world["cellGen"] else [])

		if cellIndex not in cellDict:
			cellDict[cellIndex] = {"heightMap":[], "objects":[], "natr":{}, "init":False}
		
		for key, value in cellDict[cellIndex].items():
			self.__dict__[key] = value

		if self.objects:
			for spawn in chunkIt(self.objects, 12):

				if not cellDict[cellIndex]["init"]:
					for obj in spawn: obj["d"]["worldKey"] = cellIndex

				core.queues["addObject_mainScene"].append(spawn)

		cellDict[cellIndex]["objects"] = []

		if core.genVerts:
			self.gridSetup()
			core.genVerts = False

		if not cellDict[cellIndex]["init"]:
			prng = self.getRandomState(cellIndex)
			r = prng.rand(self.size[0], self.size[1])
			rf = prng.randint(1, 275, r.shape)
			rs = prng.randint(9, 21, r.shape)

			cellDict[cellIndex]["init"] = [r, rf, rs]

		self.genArrs = cellDict[cellIndex]["init"]
		r = self.genArrs[0]

		self.worldPosition.xy = (self.cell[0]*200, self.cell[1]*200)

		wx = core.wOrigin[0]+self.cell[0]
		wy = core.wOrigin[1]+self.cell[1]
		ripMesh = "%s_%dx%d"%(core.worldName, wx, wy)
		self.ripMesh = ripMesh if ripMesh in self.scene.objectsInactive else ""
		core.grid["meshes"][self.id] = self.meshes[0]

		if not self.ripMesh:
			m = self.meshes[0]		
			self.stdSetup(m, r, cellIndex)

		else:
			self.onHeightModEnd()


	def onTectonicsEnd(self):
		cellIndex = (core.wOrigin[0]+self.cell[0], core.wOrigin[1]+self.cell[1])
		r = self.genArrs[0]; m = core.grid["meshes"][self.id]
		self.stdSetup(m, r, cellIndex)

	def getRandomState(self, cellIndex):
		ci = ( int(cellIndex[0]/200), int(cellIndex[1]/200) )
		return np.random.RandomState(abs(sum(ci)))

	def gridSetup(self):
		m = self.meshes[0]
		for vi in range( m.getVertexArrayLength(0) ):
			v = m.getVertex(0, vi)
			pos = self.getVertPos(v)
			gridY, gridX = self.getGridXY(v)

			xb = abs(pos[0]) == 100; yb = abs(pos[1]) == 100
			isEdge = (0 if not xb else -1 if pos[0] < 0 else 1,
				0 if not yb else -1 if pos[1] < 0 else 1)

			core.grid["verts"][ gridY, gridX ] = (vi, isEdge)

		print( "\nWriting file: %s" %("\\dsm\\cache\\landmass\\verts.npy") )
		np.save(gamepath+"\\dsm\\cache\\landmass\\verts.npy", core.grid["verts"])
		print("Done\n")

	def stdSetup(self, m, r, cellIndex):
		core.queues["landmass_heightMod"][self.id] = []
		for terraformHeight in self.heightMap:
			self.heightMod(m, r, *terraformHeight)

	def onHeightModEnd(self):
		
		if self.ripMesh:
			m = self.meshes[0]
			cellDict = core.world["cellDict"]
			wx = core.wOrigin[0]+self.cell[0]
			wy = core.wOrigin[1]+self.cell[1]			
			
			cellIndex = ( int(self.worldPosition.x), int(self.worldPosition.y) )
			if not cellDict[(wx, wy)]["natr"]:
				d = dict(defStatic)
				d["worldKey"] = (wx, wy)
				
				spawns = np.full( core.grid["verts"].shape, False )
				r, rf, rs = self.genArrs

				spawns = colorMod_ufunc( core.grid["verts"], r, rf, rs,
				 m, str(cellIndex), spawns, d )

			else: spawns = np.asarray(list(cellDict[(wx, wy)]["natr"].values()))

			if len(spawns[spawns != False]):
				spawns = chunkIt(spawns[spawns != False], 24)
				for spawn in spawns:
					core.queues["addObject_mainScene"].append(spawn)

	def getVertPos(self, v):
		return v.getXYZ()[0:2]

	def getGridXY(self, v):
		pos = self.getVertPos(v)
		return int( (pos[1]+100)/5 ), int( (pos[0]+100)/5 )

	#// 001.0 STANDARD METHODS: OVERRIDE INHERITED
	def endObject(self):
		if self.children:
			chunks = chunkIt(self.children, 18)
			for chunk in chunks:
				core.queues["endObject_mainScene"].append(chunk)

			core.queues["endObject_mainScene"].append(self)

		elif self not in core.queues["endObject_mainScene"]:
			core.reserveID(self)
			KX_GameObject.endObject(self)


	#// 001.1 STANDARD METHODS: TERRAFORM
	def Tectonics(self, startY, startX, level, lenY,
	 lenX, falloff, vertY, vertX, m, worldY, worldX, terraKey):
		x, y = divmod(lenX, self.size[0]), divmod(lenY, self.size[1])

		indexes = [str( (h, w) ) for h in range(y[0]+1) for w in range(x[0]+1)]
		startY = min(startY, y[0]); startX = min(startX, x[0])
		radius = max(lenX, lenY)

		if not os.path.exists(gamepath+"\\dsm\\cache\\landmass\\"+terraKey):
			os.mkdir(gamepath+"\\dsm\\cache\\landmass\\"+terraKey)

		file = gamepath+"\\dsm\\cache\\landmass\\%s\\exclude.txt"%( terraKey )
		if os.path.exists(file):
			exclude = [line.rstrip('\n') for line in open(file)]
			exclude = str(exclude)

		else:
			open(file,"w+")
			exclude = "[]"

		for chunk in chunkIt(indexes, 12):
			l = [chunk, startY, startX,
			y[0], x[0], y[1], x[1], level, radius, lenY, lenX, falloff,
			vertY, vertX, worldY, worldX, m, terraKey, exclude]

			core.queues["terraform"].append(l)

	def heightMod(self, m, r, startY, startX, radius, level, falloff, e, length):
		lenX, lenY = int(length[0]/2), int(length[1]/2)
		lenX = min(lenX, self.size[0]+1); lenY = min(lenY, self.size[1]+1)	

		endY = min( self.size[1], startY+lenY )
		endX = min( self.size[0], startX+lenX )
		startY = max(0, min( self.size[1]-1, startY-lenY ))
		startX = max(0, min( self.size[0]-1, startX-lenX ))

		startX = int(startX); endX = int(endX)
		startY = int(startY); endY = int(endY)		

		sec = core.grid["verts"][startY:endY, startX:endX]
		r = r[startY:endY, startX:endX]
		e = e[startY:endY, startX:endX]

		for i in range( divmod(len(sec), 10)[0]+1 ):
			start = i*10; end = start+11
			argList = [sec[start:end], radius, level, r[start:end],
			 m, falloff, e[start:end]]

			core.queues["landmass_heightMod"][self.id].append(argList)

	def heightMod_queued(self, sec, radius, level, r, m, falloff, e):
		worldKey = str((core.wOrigin[0]+self.cell[0], core.wOrigin[1]+self.cell[1]))
		adjVerts = heightMod_ufunc(sec, radius, level, r, m, falloff, e, worldKey)
		heightMod_ufunc(adjVerts[adjVerts != False], 0,
			-level, 0, m, falloff, "PLUCK", worldKey)

#// 003. MODULE HANDLE

def terraLoop1(kd, i, worldPosX, worldPosY):
	x, y = ps[i]
	p = Vector([x+worldPosX, y+worldPosY, 0])

	kd.insert(p, i)

terraLoop1_ufunc = np.frompyfunc(terraLoop1, 4, 0)

def Tectonics_queued(indexes, startY, startX, ym, xm, yp, xp,
	level, radius, lenY, lenX, falloff, vertY, vertX, worldY,
	worldX, m, terraKey, exclude):

	terraform_ufunc(indexes, startY, startX,
	ym, xm, yp, xp, level, radius, lenY, lenX, falloff,
	vertY, vertX, worldY, worldX, m, terraKey, exclude)
		

def Terraform(index, startY, startX, distY,
	distX, endY, endX, level, radius, lenY, lenX, falloff,
		 vertY, vertX, realY, realX, m, terraKey, exclude):
	
	index = eval(index)
	dy = index[0]-startY; dx = index[1]-startX
	localPos = (200*dy, 200*dx)
	worldPos = Vector([realX+localPos[1], realY+localPos[0], 0])
	cellDict = core.world["cellDict"]
	
	worldKey = (dx+realX,dy+realY)
	if worldKey not in cellDict:
		cellDict[worldKey] = {"heightMap":[], "objects":[], "init":False}

	file = gamepath+"\\dsm\\cache\\landmass\\%s\\exclude.txt"%( terraKey )
	exclude = eval(exclude)
	if str(index) in exclude:
		return False
	
	cvi = core.grid["verts"][vertY, vertX][0]
	origin = Vector(m.getVertex(0, cvi).getXYZ()[0:2]) + Vector([realX, realY])

	try:
		f = np.load(gamepath+"\\dsm\\cache\\landmass\\%s\\%s.npy"%(
		 terraKey, str(index) ))

	except:

		kd = kdtree.KDTree(41*41)
		f = np.full( (41, 41), abs(radius*level) )
		terraLoop1_ufunc(kd, terra_i, worldPos.x, worldPos.y)

		kd.balance()
		near = kd.find_range( Vector([realX, realY, 0]), radius**2 )

		doLenAdjust = lenX != lenY
		
		for n in near:
			co, kd_index, dist = n
			point = ps[kd_index]

			if doLenAdjust:

				if min(lenX, lenY) == lenX:
					distX = np.linalg.norm( Vector([co.x,0,0])
					 - Vector([origin.x, 0, 0]) )
					dist += distX*(16*falloff)

				elif min(lenX, lenY) == lenY:
					distY = np.linalg.norm( Vector([0,co.y,0])
					 - Vector([0, origin.y, 0]) )
					dist += distY*(16*falloff)

			e = max(0, dist)
			new_f = getHeightFactor(level, radius, falloff, e)
			if abs(new_f) > 0: f[ i_list[kd_index] ] = e

		if len( f[ f != abs(radius*level) ].tolist() ) > 0:
			np.save(gamepath+"\\dsm\\cache\\landmass\\%s\\%s.npy"%( terraKey,
			 str(index) ), f)
		else:
			exclude = open(file,"a")
			exclude.write(str(index)+"\n")
		
	if len( f[ f != abs(radius*level) ].tolist() ) > 0:
		cellDict[worldKey]["heightMap"].append([vertY, vertX,
		 radius, level, falloff, f, (lenX, lenY)])

	return True

terraform_ufunc = np.frompyfunc(Terraform, 19, 1)

def colorMod(vi, r, rf, rs, m, pos, spawns, d):
	
	d = dict(d)
	v = m.getVertex(0, vi[0])		
	fertile = v.color[1] > 0.1 and v.color[0] < 0.1
	rocky = v.color[0] > 0.1 and v.color[1] < 0.1
	#treees <= r < grass
	if (0.4925 <= r <= 0.55) and fertile:
		pos = eval(pos)
		spawnX = v.x; spawnY = v.y
		spawnObj = "grass_a" if r > 0.5 else "tree_a"

		rot = [ 0,0, radians(rf) ]
		scale = [rs*0.1 for i in range(3)]
		d["vi"] = vi[0]

		spawns = ({"obj":spawnObj, "pos":[spawnX,spawnY,v.z],
		"rot":rot, "scale":scale, "d":d, "kls":"statics"})

	#gold <= r < rock
	if (0.4975 <= r <= 0.502) and rocky:
		pos = eval(pos)
		spawnX = v.x; spawnY = v.y
		spawnObj = "rocks_a0" if r > 0.5 else "goldrocks_a0"

		rot = Vector([ 0,0, radians(rf) ])
		scale = [rs*0.1 for i in range(3)]
		d["vi"] = vi[0]

		spawns = ({"obj":spawnObj, "pos":[spawnX,spawnY,v.z],
		"rot":rot, "scale":scale, "d":d, "kls":"statics"})

	return spawns
	

colorMod_ufunc = np.frompyfunc( colorMod, 8, 1 )

def getHeightFactor(level, radius, falloff, e):
	
	if e >= abs(level*radius): return False
	dist = (e/radius)*falloff

	if level > 0:
		f = max( 0, level - 3*(dist**2) - 2*(dist**3) )
		f = min(level, f)
	else:
		f = -max( 0, abs(level) - 3*(dist**2) - 2*(dist**3) )
		f = max(level, f)

	return f
	

def heightModVec(vi, radius, level, r, m, falloff, e, worldKey):

	v = m.getVertex(0, vi[0])

	if e == "PLUCK":
		v.setXYZ( [v.x,v.y, 0] )
		return False

	else:
		f = getHeightFactor(level, radius, falloff, e)
		if v.z != 0: f = min(f, v.z)
		v.setXYZ( [v.x,v.y, f] )

		if vi[1] == (0,0):
			
			col = grass
			"""
			if v.z < waterLevel/4:
				col = sand
				col[1] = max(0.666, col[1]*(r/level))
				col[0] = max(0.75, col[0]*(r/level))

			else:
				col = Vector([1*(r/level), 1*(r/level),0, 1])
				col[1] = max(1.0, col[1])
				col[0] = max(0.25, col[0])
			"""
			
			#if abs(f) > 0.5:
			#	v.color = col
	
		else:

			if v.z < waterLevel/4:
				col = sand
			else:
				col = grass

			#v.color = col

			worldKey = tuple(eval(worldKey))
			neighbor = ( worldKey[0]+(vi[1][0]), worldKey[1]+(vi[1][1]) )
			
			if neighbor not in core.world["cellDict"]: return vi
	
	return False

		
heightMod_ufunc = np.frompyfunc( heightModVec, 8, 1 )

def onTreeAdd(cont):
	own = cont.owner

	if own.parent and "init" not in own:
		

		cell = own.parent.cell
		cellDict = core.world["cellDict"]
		cellIndex = (core.wOrigin[0]+cell[0], core.wOrigin[1]+cell[1])

		if cellIndex in cellDict:
			own["init"] = True
			cancel = False
			try:
				cancel = cellDict[cellIndex]["natr"][tuple(own.localPosition)]

			except:
				vecTo = own.worldPosition.copy()+Vector([0, 0, 4])
				vecFrom = own.worldPosition.copy()-Vector([0, 0, -1])
				ray = own.rayCast(vecTo, vecFrom, prop="natr", xray=True, mask=1)
				if ray[0]:
					own.endObject()
					cancel = True						

				if not cancel:
					dd = {"generic":True, "worldKey":own.worldKey,
					 "team":own.team, "kls":"statics"}

					own_d = ({"obj":own.name, "pos":own.localPosition.copy(),
					"rot":own.localOrientation.copy(), "scale":own.localScale.copy(),
					 "d":dd, "kls":"statics"})

					cellDict[cellIndex]["natr"][tuple(own.localPosition)] = own_d

					if not hasattr(own, "noReproduction"):
						rr, rf, rs = cellDict[cellIndex]["init"]
						spawns = np.full( (12*12), False, dtype=object )
						q = -1 if "grass" in own else -2
						i = 0

						for x in range(q,-q+1,2):
							if x == 0: x += 1
							for y in range(q,-q+1,2):
								if y == 0: y += 1
								r = rr[y, x]; f = rs[y, x]
								dist = f*r

								vecTo = ( own.worldPosition.copy()
								+Vector([x*dist, y*dist, -1]) )
								vecFrom = ( own.worldPosition.copy()
								+Vector([x*dist, y*dist, 5]) )

								ray = own.rayCast(vecTo, vecFrom,
								 prop="ground", xray=True, mask=1)

								if ray[1]:
									pos = ray[1]-own.parent.worldPosition

									rot = own.worldOrientation.copy()
									own.applyRotation([0,0,x*dist])
									scale = own.worldScale.copy() * 0.9
									d = {"cell":cell, "worldKey":own.worldKey,
										"generic":True, "team":1,
										"noReproduction":True,
										"kls":"statics"}

									spawns[i] = ({"obj":own.name, "pos":pos,
									"rot":rot, "scale":scale, "d":d, "kls":"statics"})

									i += 1

						if len(spawns[spawns != False]):
							spawns = chunkIt(spawns[spawns != False], 24)
							for spawn in spawns:
								core.queues["addObject_mainScene"].append(spawn)

		own.state = 2

def new(old_owner, pos, rot, scale, d):
	setDefaults(d)
	return Landmass(old_owner, pos, **d)

def setDefaults(d):
	for key, value in landmassDefaults.items():
		if key not in d: d[key] = value

landmassDefaults = {
				"kls":"terra", "size":[41,41], "cell":(0,0)
			}
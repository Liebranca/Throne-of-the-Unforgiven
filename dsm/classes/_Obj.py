#// 000. IMPORTS & NAMING
from bge.types import KX_GameObject
from bge.logic import getTimeScale
from mathutils import Vector
from math import radians
from dsm import lymath, physRate, physClamp, camTurn, waterLevel, showDebug, actorColMask
import numpy as np
core = None
Stat = None

saveAttrs = ["kls", "weight", "solid", "alignToSurface",
			"behaviour", "id", "worldKey", "ripMesh"]

#// 001.0 BASE CLASS DEFINITION
class BaseObj(KX_GameObject):
	def __init__(self, old_owner, ci, **kwargs):
		for key, value in kwargs.items():
			if key not in ["id", "c_active"]: self.__dict__[key] = value

		if "c_active" in kwargs:
			if kwargs["c_active"][ci]: self["active"] = True

		self.id = core.reuseID(self)

	def endObject(self):
		if self.children:
			if not self.children.invalid:
				for child in self.children: child.endObject()

		core.discardID(self)
		KX_GameObject.endObject(self)


class Generic(KX_GameObject):
	def __init__(self, old_owner, pos, rot, scale, **kwargs):
		for key, value in kwargs.items():
			self.__dict__[key] = value

		for prop in ["pain", "resist"]:
			if prop in self:
				if isinstance(self[prop], float):
					value  = self[prop]
					setattr(self, prop, Stat(value, **{"max":value}))
					del self[prop]				

		self.id = core.reuseID(self)

		ground = core.getCellAtWorldKey(self.worldKey)
		if ground:
			self.worldPosition = ground.worldPosition
			self.setParent(ground)
			
			self.localPosition = pos
			self.localScale = scale
			self.localOrientation = rot
		else:
			self.endObject()

	def endObject(self):
		core.discardID(self)
		KX_GameObject.endObject(self)

	def onDeath(self):
		cell = self.parent.cell
		cellDict = core.world["cellDict"]
		cellIndex = (core.wOrigin[0]+cell[0], core.wOrigin[1]+cell[1])
		del cellDict[cellIndex]["natr"][tuple(self.localPosition)]

		if "drop" in self:
			newPickUp = self.scene.addObject(self["drop"], life=1200)
			newPickUp.worldPosition = self.worldPosition
			if self.parent: newPickUp.setParent(self.parent)

			if "size" in newPickUp:
				newPickUp["size"] = self.localScale.x

			if "value" in newPickUp:
				newPickUp["value"] *= self.localScale.x

		if "deathFX" in self:
			newFX = self.scene.addObject(self["deathFX"],
			 life=self.scene.objectsInactive[self["deathFX"]]["dur"])

			newFX.worldPosition = self.worldPosition
			newFX.worldScale = self.worldScale
			newFX.worldOrientation = self.worldOrientation

		self.endObject()

#// 001.1 CLASS DEFINITION
class Obj(KX_GameObject):

	def __init__(self, old_owner, pos, rot, scale, **kwargs):
		for key, value in kwargs.items():
			if key != "c_active": self.__dict__[key] = value

		if "id" not in kwargs: self.id = core.genID(self, self.kls)
		else: core.registerReserved(self)

		for i, child in enumerate(self.children):
			child = BaseObj(child, i, **kwargs)

		self.worldPosition = pos
		self.localScale = scale
		self.localOrientation = rot

		self.accel = Vector([0,0,0])

		self.isOnGround = True
		self.isJumping = False
		self.jumpForce = 0.0

		if not core.player:
			if self.kls == "actors":
				if self.behaviour == "player":
					self.name = "player"
					self.worldKey = core.wOrigin

		else:
			if "worldKey" not in kwargs:
				g = self.groundCheck()
				if g:
					x, y = [int(v) for v in g]
					self.worldKey = (x,y)

			ground = core.getCellAtWorldKey(self.worldKey)
		
			if self.kls == "statics" and ground:
				self.worldPosition = ground.worldPosition
				self.setParent(ground)
				self.localPosition = pos

			if not ground and showDebug:
				core.GUI.logEntry(str(self.worldKey)+" not found.")

		self.getIsUnderwater()

		if self.ripMesh: self.replaceMesh(self.ripMesh, 1, 1)

	def groundCheck(self):
		groundCheck = self.rayCast([self.worldPosition.x,
		 self.worldPosition.y, self.worldPosition.z-10000],
		 [self.worldPosition.x, self.worldPosition.y,
		  self.worldPosition.z+0.025], prop="ground")

		if groundCheck[0]:
			if self.worldPosition.z >= 999: self.worldPosition.z = groundCheck[1][2]
			if self.alignToSurface: self.worldOrientation *= groundCheck[2]
			return groundCheck[0].meshes[0].name.replace("cruelty_","").split("x")

		return False

	def checkInFrustum(self):
		inFrusX = core.actFrustum[0][0] < self.worldPosition.x < core.actFrustum[0][1]
		inFrusY = core.actFrustum[1][0] < self.worldPosition.y < core.actFrustum[1][1]

		if not inFrusX or not inFrusY:
			if self != core.player: self.endObject()
			return False

		return True

	def onCollision(obj, point, normal, points):
		for point in points:
			pass

	def getIsUnderwater(self):
		up = Vector(self.worldPosition)
		up.z += 200
		origin = Vector(self.worldPosition)
		origin.z += (self.cullingBox.max[2]/1.25)
		
		return self.rayCast(up, origin, xray=True, prop="water")[0]

	#// 001.1 STANDARD METHODS: OVERRIDE INHERITED
	def __setitem__(self, key, value):
		if isinstance(value, KX_GameObject):
			try: value = [value.id, value.kls]
			except: None
			if "OBJ:" not in key: key = "OBJ:" + key

		KX_GameObject.__setitem__(self, key, value)

	def __getitem__(self, key):
		if "OBJ:" + key in self: key = "OBJ:" + key
		value = KX_GameObject.__getitem__(self, key)

		if "OBJ:" in key:
			try:
				_id, kls = value
				return core.find(_id, kls)
			except: None

		return value

	def killObject(self):
		core.discardID(self)
		KX_GameObject.endObject(self)

	def endObject(self):
		active = []
		if self.children:
			if not self.children.invalid:
				active = [i for i in range( len(self.children) )]
				for i, child in enumerate(self.children):
					if "active" in child: active[i] = child["active"]
					else: active[i] = False
					child.endObject()

		core.reserveID(self)
		obj_dict = {k:getattr(self, k) for k in saveAttrs if hasattr(self, k)}
		obj_dict["c_active"] = active
		
		if self.parent:
			pos = Vector(self.localPosition)

		else:
			pos = Vector(self.worldPosition)
			
		rot = Vector( self.localOrientation.to_euler() )
		scale = Vector(self.localScale)
		
		core.objSuspended[self.id] = { "obj":str(self.name), "pos":pos,
		 "rot":rot, "scale":scale, "d":obj_dict, "kls":str(self.kls) }

		core.world["cellDict"][self.worldKey]["objects"].append(self.id)
		KX_GameObject.endObject(self)

	def applyMovement(self, vec, local=False, prop="", reloc=False):
		if not (self.solid or reloc): self.clipMove(vec, prop)
		KX_GameObject.applyMovement(self, vec, local)


	#// 001.2 STANDARD METHODS: SPATIAL MATH
	def clipMove(self, vec, prop=""):
		
		vol = self.cullingBox.max
		
		xdirn = -1 if vec[0] < 0 else 1 if vec[0] > 0 else 0
		ydirn = -1 if vec[1] < 0 else 1 if vec[1] > 0 else 0
		zdirn = -1 if vec[2] <= 0 else 1

		f = 3
		groundCheck = False if self.isJumping < 0 else not self.isOnGround

		if vec[0]:

			for y_offset in [ vol[1], -vol[1], 0 ]:

				lpos = self.worldPosition + (self.worldOrientation.col[0]
					*(vol[0]*f*xdirn))
				lpos = lpos + (self.worldOrientation.col[1]*(vol[1]*f*y_offset))
				
				xclip_ray = self.rayCast( objto=[ lpos[0], lpos[1],
				 self.worldPosition.z+vol[2]/2 ], objfrom=[ self.worldPosition.x,
				 self.worldPosition.y,self.worldPosition.z+vol[2]/1.25 ],
				 prop=prop, mask=actorColMask-2**8)

				if xclip_ray[0]:
					vec[0] = 0
					self.accel.x = 0
					break

		if vec[1]:
			obsDirn = {vol[0]:0, -vol[0]:0, 0:0}
			checkObs = False
			for x_offset in [ vol[0], -vol[0], 0 ]:

				lpos = self.worldPosition + (self.worldOrientation.col[1]
					*(vol[1]*f*ydirn))
				lpos = lpos + (self.worldOrientation.col[0]*(vol[0]*f*x_offset))

				yclip_ray = self.rayCast( objto=[ lpos[0], lpos[1],
				 self.worldPosition.z+vol[2]/2 ],
				 objfrom=[ self.worldPosition.x, self.worldPosition.y,
				 self.worldPosition.z+vol[2]/2 ], prop=prop, mask=actorColMask-2**8)

				if yclip_ray[0]:
					vec[1] = 0
					self.accel.y = 0
					if self.behaviour != "player":
						if "ground" not in yclip_ray[0] and "pathPoint" in self:
							obsDirn[x_offset] = np.linalg.norm(
								Vector(yclip_ray[1]) - Vector(self["pathPoint"]) )

							checkObs = True

						else:
							self.accel.z = 10
							self.isJumping = True

					if not checkObs: break

			if checkObs:
				ss = min(obsDirn, key=obsDirn.get)
				self.accel.x = 10*ss

		if ((vec[2] or not groundCheck)
		and (not self.isJumping or self.isJumping < 0)):
			l = [ [ vol[0], 0 ],
			 [ -vol[0], 0 ], [ 0, vol[1] ], [ 0, -vol[1] ], [0,0] ]
			f = self.accel.z if not self.isOnGround else f
			for xy_offset in l:

				lpos = self.worldPosition + (self.worldOrientation.col[0]
					*(vol[0]*xy_offset[0] ))

				lpos = lpos + ( self.worldOrientation.col[1]*(vol[1]*xy_offset[1] ))
				
				zclip_ray = self.rayCast( objto=[ lpos[0], lpos[1],
				 lpos[2]-( (vol[2]*f)*zdirn ) ], objfrom=[ self.worldPosition.x,
				 self.worldPosition.y, self.worldPosition.z+1.5 ], xray=True,
				 prop=prop, mask=actorColMask-2**8)

				if zclip_ray[0]:
					vol2 = zclip_ray[0].cullingBox.max[2]
					dist = self.getDistanceTo(zclip_ray[1])

					if dist <= vol[2]*0.1 or self.accel.z > 0:
						if not self.accel.z > 0:
							self.landing = True
							self.jumpForce = 0.0
							self.isOnGround = True

						self.accel.z = vec[2] = 0

					else:
						vec[2] /= 1.05
						self.accel.z /= 1.05
					
					break

		return vec


	#// 002.0 PHYSICS UPDATE
	def physicsUpdate(self):
		vec = Vector([self.accel.x/physRate, self.accel.y/physRate, 0])
		self.accel.xy -= (self.accel.xy/physRate)*getTimeScale()

		for axis in range(0, 2):
			
			if abs(self.accel[axis]) <= physClamp:
				self.accel[axis] = 0.0

		if not self.solid:
			isMoving = self.accel.x or self.accel.y
			fallBreak = self.jumpForce/3 if isMoving else 0
			f = max(0.5, (self.weight-fallBreak)*0.5 )*getTimeScale()
			if self.accel.z > 0:
				vec[2] = self.accel.z/physRate
				self.accel.z -= f
				

			elif not self.isOnGround:
				self.isJumping = False

				if not self.getIsUnderwater():
					vec[2] = self.accel.z/physRate
					self.accel.z -= f

		self.applyMovement(vec*getTimeScale(), local=True)


#// 003. MODULE HANDLE
def new(old_owner, pos, rot, scale, d):
	if "generic" in d: return Generic(old_owner, pos, rot, scale, **d)
	setDefaults(d)

	return Obj(old_owner, pos, rot, scale, **d)

def setDefaults(d):
	for key, value in objDefaults.items():
		if key not in d: d[key] = value

def spawners(cont):
	spawnPoint = cont.owner
	spawnDict = eval(spawnPoint["spawnDict"])
	spawnDict["pos"] = spawnPoint.worldPosition
	spawnDict["rot"] = spawnPoint.worldOrientation
	spawnDict["scale"] = spawnPoint.worldScale
	
	return spawnPoint.scene.addObject(**spawnDict)


objDefaults = {
				"kls":"statics", "weight":1.0, "ripMesh":None,
				 "solid":False, "alignToSurface":False,
				 "landing":False, "team":0
			}

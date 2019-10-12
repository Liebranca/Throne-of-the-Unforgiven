#// 000. IMPORTS & NAMING
from mathutils import Vector
terraMeshes = [ "TE" + ( "0"*( 9 - len(str(i) )) ) + str(i) for i in range(1, 26) ]

from dsm import Time, showDebug, worlds, camFOV, camFOV_fp

#// 001. CLASS DEFINITION
class Manager:
	def __init__(self):
		self.scenes = {"reserved":[], "reuse":[]}
		self.statics = {"reserved":[], "reuse":[]}
		self.actors = {"reserved":[], "reuse":[]}
		self.proj = {"reserved":[], "reuse":[]}

		self.terra = {"reserved":terraMeshes, "reuse":[]}
		self.grid = { "meshes":{}, "cells":{} }

		self.joyIndex = 0
		self.joyLastFrame = []
		self.joyPlugged = False
		self.cont = None
		self.genVerts = False

		self.actFrustum = []
		self.relocTresh = 100; self.lastReloc = [0,0]
		self.wOrigin = [155, 53]
		self.getActFrustum()

		self.queues = {"addObject_mainScene":[], "terraform":[],
			"endObject_mainScene":[], "landmass_heightMod":{},
			"tasks":[]}

		self.taskTimer = 0.0

		self.objSuspended = {}
		self.worldTime = Time("up")
		self.worldTime.hour = 6
		self.worldTime.min = 59
		self.worldTime.subdiv = 60

		self.worldName = "cruelty"
		self.world = worlds.__dict__[self.worldName]

		self.GUI = None
		self.player = False
		self.firstPerson = False

		self.playerLog = False
		self.fMapGen = 1

		self.settings = {"fx_volume":0.425, "mu_volume":0.75}
		self.teams = {0:{}, 1:{}}

		for team in self.teams:
			self.teams[team]["resources"] = {"wood":0,"stone":0,"gold":0,"food":50}

	#// 001.0 STANDARD METHODS: ID HANDLING
	def genID(self, obj, cath):
		group = self.__dict__[cath]
		reserve = group["reserved"]; reuse = group["reuse"]

		if len(reuse):
			newID = reuse.pop(0)

		else:
			group_count = len(group) + len(reserve)
			newID = (cath[0:2].upper() + str(0)
			 * (9 - len( str(group_count) )) + str(group_count))

		group[newID] = obj
		return newID

	def find(self, _id, cath):
		group = self.__dict__[cath]
		if _id in group: return group[_id]

		return False

	def reserveID(self, obj):
		_id = obj.id; cath = obj.kls
		group = self.__dict__[cath]
		reserve = group["reserved"]

		reserve.append(_id)
		if _id in group: del group[_id]

	def reuseID(self, obj):
		cath = obj.kls
		group = self.__dict__[cath]
		reuse = group["reuse"]

		if not len(reuse):
			return self.genID(obj, cath)

		else:
			_id = reuse.pop(0)
			group[_id] = obj
			return _id

	def discardID(self, obj):
		_id = obj.id; cath = obj.kls
		group = self.__dict__[cath]
		reuse = group["reuse"]

		reuse.append(_id)
		if _id in group: del group[_id]

	def registerReserved(self, obj):
		_id = obj.id; cath = obj.kls
		group = self.__dict__[cath]
		reserve = group["reserved"]

		group[_id] = obj
		if _id in reserve: reserve.remove(_id)
		if _id in self.objSuspended: del self.objSuspended[_id]


	def toggleView(self):
		self.firstPerson = not self.firstPerson
		cam = self.cont.scene.active_camera
		cam["frame"] = cam.parent["frame"] = self.firstPerson
		newfov = camFOV_fp if self.firstPerson else camFOV
		oldfov = cam.fov

		newTask = ([
			["own.scene.active_camera", "fov"],
			["iLerp",
			oldfov, newfov, "1", "core.taskTimer" ],
			"own.scene.active_camera.fov == %f"%newfov
			 ])

		self.queues["tasks"].append(newTask)

	def modRes(self, team, res, value):
		self.teams[team]["resources"][res] += value
		self.GUI.resbar.children["resbar.%scount"%res].text = str(
			max(0, self.teams[team]["resources"][res]))

	#// 002.0 LANDMASS METHODS
	def getCellAtWorldKey(self, worldKey):
		for co in self.grid["cells"]:
			cellIndex = self.grid["cells"][co]
			cell = self.find(str(cellIndex), "terra")
			if cell:
				key = (self.wOrigin[0]+cell.cell[0], self.wOrigin[1]+cell.cell[1])
				if worldKey == key:
					return cell

		return False

	def cellReloc(self, r):
		self.lastReloc = [ int((-r[0]*self.relocTresh*2)),
		 int((-r[1]*self.relocTresh*2)) ]
		
		self.wOrigin = [self.wOrigin[0]+r[0], self.wOrigin[1]+r[1]]

		if abs(r[0]) == 1:
			moveCenter = (-r[0],0)
			moveUp = (-r[0],1); moveDown = (-r[0],-1)
			moveRight = (-r[0],2); moveLeft = (-r[0],-2)
			
			newCenter = (r[0],0)
			newUp = (r[0],1); newDown = (r[0],-1)
			newRight = (r[0],2); newLeft = (r[0],-2)

			farCenter = (-r[0]*2,0)
			farUp = (-r[0]*2,1); farDown = (-r[0]*2,-1)
			farRight = (-r[0]*2,2); farLeft = (-r[0]*2,-2)

			fwdCenter = (r[0]*2,0)
			fwdUp = (r[0]*2,1); fwdDown = (r[0]*2,-1)
			fwdRight = (r[0]*2,2); fwdLeft = (r[0]*2,-2)

			oldUp = (0,1); oldDown = (0,-1)
			oldRight = (0,2); oldLeft = (0,-2)

		else:
			moveCenter = (0,-r[1])
			moveUp = (1,-r[1]); moveDown = (-1,-r[1])
			moveRight = (2,-r[1]); moveLeft = (-2,-r[1])
			
			newCenter = (0,r[1])
			newUp = (1,r[1]); newDown = (-1,r[1])
			newRight = (2,r[1]); newLeft = (-2,r[1])

			farCenter = (0,-r[1]*2)
			farUp = (1,-r[1]*2); farDown = (-1,-r[1]*2)
			farRight = (2,-r[1]*2); farLeft = (-2,-r[1]*2)

			fwdCenter = (0,r[1]*2)
			fwdUp = (1,r[1]*2); fwdDown = (-1,r[1]*2)
			fwdRight = (2,r[1]*2); fwdLeft = (-2,r[1]*2)
			
			oldUp = (1,0); oldDown = (-1,0)
			oldRight = (2,0); oldLeft = (-2,0)

		fwdCells = [fwdCenter, fwdUp, fwdDown, fwdRight, fwdLeft]
		newCells = [newCenter, newUp, newDown, newRight, newLeft]
		oldCells = [(0,0), oldUp, oldDown, oldRight, oldLeft]
		moveCells = [moveCenter, moveUp, moveDown, moveRight, moveLeft]
		farCells = [farCenter, farUp, farDown, farRight, farLeft]
		removeCells = []

		for i in range(5):
			newCell = newCells[i]; oldCell = oldCells[i]; moveCell = moveCells[i]
			farCell = farCells[i]; fwdCell = fwdCells[i]

			oldIndex = self.grid["cells"][oldCell]
			moveIndex = self.grid["cells"][moveCell]
			newIndex = self.grid["cells"][newCell]
			farIndex = self.grid["cells"][farCell]
			fwdIndex = self.grid["cells"][fwdCell]

			oldRef = self.find(oldIndex, "terra")
			moveRef = self.find(moveIndex, "terra")
			newRef = self.find(newIndex, "terra")
			farRef = self.find(farIndex, "terra")
			fwdRef = self.find(fwdIndex, "terra")
			
			fwd = fwdRef.cell
			fwdRef.cell = newRef.cell
			newRef.cell = oldRef.cell
			oldRef.cell = moveRef.cell
			moveRef.cell = farRef.cell
			farRef.cell = fwd

			self.grid["cells"][fwdRef.cell] = fwdRef.id
			self.grid["cells"][newRef.cell] = newRef.id
			self.grid["cells"][oldRef.cell] = oldRef.id
			self.grid["cells"][moveRef.cell] = moveRef.id

			newRef.worldPosition.xy = (newRef.cell[0]*(200),
			 newRef.cell[1]*(200))

			oldRef.worldPosition.xy = (oldRef.cell[0]*(200),
			 oldRef.cell[1]*(200))

			moveRef.worldPosition.xy = (moveRef.cell[0]*(200),
			 moveRef.cell[1]*(200))

			fwdRef.worldPosition.xy = (fwdRef.cell[0]*(200),
			 fwdRef.cell[1]*(200))

			removeCells.append(farRef)

		nx, ny = r[0], r[1]

		for i in range(5):
			cell = removeCells[i]
			cellCoor = fwdCells[i]
			
			newCell_d={"cell":cellCoor}

			self.queues["addObject_mainScene"].append( {"obj":"",
			 "d":newCell_d, "kls":"Terra"} )

			cell.applyMovement([nx*-200,ny*-200,0])
			cell.endObject()

		oldOffset = float(self.player.scene.active_camera.timeOffset)
		self.player.scene.active_camera.timeOffset = 0.0		
		self.player.applyMovement([nx*-200,ny*-200,0], reloc=True)
		self.player.scene.active_camera.timeOffset = oldOffset
		if showDebug: self.GUI.logEntry(str(tuple(self.wOrigin)))

	def getActFrustum(self):
		x = ( -int(self.relocTresh), int(self.relocTresh) )
		y = ( -int(self.relocTresh), int(self.relocTresh) )

		self.actFrustum = [x, y]

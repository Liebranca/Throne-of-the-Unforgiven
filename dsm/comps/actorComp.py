import bge
from math import radians
from mathutils import Vector

if not hasattr(bge, "__component__"):
	from dsm.gamekeys import getEventStatus, getJoyInput
	from dsm import physRate, skyColor, waterLevel, displayStrings, lang, strFromId
	from dsm import actorColMask


class Actor(bge.types.KX_PythonComponent):

	args = {}
	def start(self, args):
		arma = self.object.scene.addObject("Biped", pos=self.object.worldPosition,
		 kls="armatures")
		arma.setParent(self.object)

		wep = arma.children[self.object.activeWeapon]
		try:
			wepMod = self.object.scene.objectsInactive[wep.meshes[0].name]["ansMod"]
		except:
			wepMod = ".def"

		arma.ansModArms = wepMod+"_in"

	def update(self):

		#self.object.checkInFrustum()

		self.object["X"], self.object["Y"] = self.object.worldPosition.xy
		core = bge.logic.getCurrentScene().objects["Manager"]["core"]

		ground_vec1 = [self.object.worldPosition.x, self.object.worldPosition.y,
		self.object.worldPosition.z - ( 1.5*bge.logic.getTimeScale() )]
		ground_vec2 = [self.object.worldPosition.x, self.object.worldPosition.y,
		self.object.worldPosition.z + ( 4*bge.logic.getTimeScale() )]

		groundCheck = self.object.rayCast(ground_vec1, ground_vec2, xray=True,
		 mask=actorColMask-2**8)

		self.object.isOnGround = bool(groundCheck[0])

		ceiling_vec = [self.object.worldPosition.x, self.object.worldPosition.y,
		self.object.worldPosition.z + 6.5]

		ceilingCheck = self.object.rayCast(ceiling_vec, ground_vec2, xray=True,
		 mask=actorColMask-2**8)

		if ((self.object.accel.x != 0 or self.object.accel.y != 0
			or self.object.accel.z != 0)
			or not self.object.isOnGround):
			if not core.fMapGen: self.object.physicsUpdate()

		if self.object.isOnGround and self.object.isJumping < 1:
			if groundCheck[1]:
				self.object.worldPosition.z = groundCheck[1][2]

			if self.object.children["Armature"]["mode"] == "air":
				self.object.landing = True

		elif self.object.isOnGround and self.object.isJumping > 0:
			if self.object.accel.z < 0: self.object.isJumping = False

		elif ceilingCheck[0] and self.object.accel.z >= 0:
			f = max(0.5, (self.object.weight-self.object.jumpForce)*0.5 )
			self.object.accel.z = -f

		groundCheck = bool(groundCheck[0])

		if self.object.behaviour == "player":

			self.object.scene.objects["Sunguide"].worldPosition.xy =(
						 self.object.worldPosition.xy)

			fwd, back, up, down = (getEventStatus("fwd"), getEventStatus("back"),
									getEventStatus("up"), getEventStatus("down"))

			sright, sleft, sup, sdown = (getEventStatus("sright"),
			 getEventStatus("sleft"), getEventStatus("sup"), getEventStatus("sdown"))

			jump = (getEventStatus("jump") and groundCheck)
			fire, sheath, sneak = (getEventStatus("fire") and self.object.isWeaponOut,
			 getEventStatus("sheath"), getEventStatus("sneak")
				)

			toggleRun = getEventStatus("toggleRun")

			if core: joySens = core.cont["joySens"]
			else: joySens = [0,0,0,0]			

			if core.GUI.mouseLook:
				self.object.actorUpdate(fwd, back, up, down, sright, sleft, sup, sdown,
					jump, fire, sheath, sneak, toggleRun, joySens=joySens)

				if "OBJ:iTarget" in self.object:
					iTarget = self.object["OBJ:iTarget"]
					if iTarget:
						core.GUI.crosshair["mode"] = "interact"
						if getEventStatus("use"):
							if self.getInteractKey(iTarget):
								iTarget["active"] = not iTarget["active"]
								status = ".onOpen" if iTarget["active"] else ".onClose"
							else:
								status = ".onFail"

							if "iStrings" in iTarget:
								iStr = iTarget["iStrings"]
								if iStr+status in displayStrings:
									core.GUI.logEntry( strFromId(iStr+status, lang) )

							del self.object["OBJ:iTarget"]

					else:
						del self.object["OBJ:iTarget"]

			doReloc = [0,0]
			relocTresh = core.actFrustum
			if self.object.worldPosition.x > relocTresh[0][1]:
				doReloc[0] = 1
			elif self.object.worldPosition.x < relocTresh[0][0]:
				doReloc[0] = -1
			elif self.object.worldPosition.y > relocTresh[1][1]:
				doReloc[1] = 1
			elif self.object.worldPosition.y < relocTresh[1][0]:
				doReloc[1] = -1

			if (fire or self.object.isAttacking) and core.GUI.crosshair.state == 2:
				core.GUI.crosshair["mode"] = "fire"
				core.GUI.crosshair.actuators["fire"].frame = (
					self.object.children["Armature"].getAnimFrame("arms")/2
					)
			else:
				if core.GUI.crosshair.actuators["fire"].frame > 0:
					core.GUI.crosshair.actuators["fire"].frame -= 0.16
				else:
					core.GUI.crosshair.actuators["fire"].frame = 0.0

			if (doReloc[0] or doReloc[1]) and not core.queues["addObject_mainScene"]:
				core.cellReloc(doReloc)			
	
	def getInteractKey(self, ob):
		if "key" in ob:
			keyType, value  = ob["key"].split(": ")
			d = self.object.__dict__[keyType]
			if keyType == "runes":
				if value in d: return d[value] >= 100

			return value in d

		return True

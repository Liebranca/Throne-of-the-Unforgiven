#// 000. IMPORTS & NAMING
from bge.types import BL_ArmatureObject
from bge.logic import getSceneList
from bge.logic import getTimeScale
from dsm import _EquipMesh, apparel, ans, animRate
from dsm import armorKeys as bodySlots

core = None
animSlotLayers = {"legs":1, "arms":0}
hasBody = ["feet", "hands", "head"]
jumpPass = []

#// 001. CLASS DEFINITION
class Arma(BL_ArmatureObject):
	def __init__(self, old_owner, pos, rot, scale, d):
		self.worldPosition = pos
		self.name = "Armature"
		
		for slotKey, meshName in d["bodySlots"].items():
			child = self.children[slotKey]
			if slotKey in hasBody:
				origin = d["default"]+slotKey.capitalize()
			else: origin = False
			
			if slotKey == "head":
				self.__dict__[slotKey] = newSlot = _EquipMesh.new(child, "", origin)
				self.hat = hatSlot = _EquipMesh.new(self.children["hat"],
				 meshName, False)
				self.hair = hairSlot = _EquipMesh.new(self.children["hair"],
				 d["hair"], False)

				if meshName:
					self.head.toggleColors(apparel[meshName]["slotData"])
					self.hair.visible = 2 not in apparel[meshName]["slotData"]

				meshName = False

			else:
				self.__dict__[slotKey] = newSlot = _EquipMesh.new(child, meshName, origin)
			
			if slotKey != "body" and meshName:
				self.body.toggleColors(apparel[meshName]["slotData"])
				
				if slotKey == "feet":
					self.legs.toggleColors(apparel[meshName]["slotData"])
				if slotKey == "hands":
					self.chest.toggleColors(apparel[meshName]["slotData"])

		for key, value in d["animSettings"].items():
			self.__dict__[key] = value

	def onAnimChange(self, animSlot, act, reset=False, reverse=False):

		mod = self.__dict__["ansMod"+animSlot.capitalize()]
		if mod not in ans[self.ansFam]:
			mod = ".def"

		if act not in ans[self.ansFam][mod]:

			if "_walkWep" in act: token = "_walWep"
			else: token = act[0:4]

			if token in ans["reroute"]:
				act = ans["reroute"][token]

			else: mod = ".def"

		if act not in ans[self.ansFam][mod]:
			mod = ".def"

		self.__dict__["ans"+animSlot.capitalize()] = act

		newAnim = self.ansFam+act+mod		
		self.actuators[animSlot].action = newAnim
		for key, value in ans[self.ansFam][mod][act]["attr"].items():
			setattr(self.actuators[animSlot], key, value)
		
		if reverse:
			self.actuators[animSlot].frameStart, self.actuators[animSlot].frameEnd = (
				self.actuators[animSlot].frameEnd, self.actuators[animSlot].frameStart)

		if reset:
			self.setActionFrame(self.actuators[animSlot].frameStart,
			 animSlotLayers[animSlot])
			self[animSlot+"Frame"] = self.actuators[animSlot].frameStart

		self[animSlot+"End"] = False

	def animSync(self, animSlot1, animSlot2):
		self.setActionFrame(self.getActionFrame(animSlotLayers[animSlot2]),
		 animSlotLayers[animSlot1])

	def getAct(self, animSlot):
		return self.__dict__["ans"+animSlot.capitalize()]

	def onAnimEnd(self, animSlot):
		return self[animSlot+"End"]

	def getAnimFrame(self, animSlot):
		return self.getActionFrame(animSlotLayers[animSlot])

	def setAnimFrame(self, animSlot, frame):
		self.setActionFrame(frame, animSlotLayers[animSlot])

	def getIsActiveFrame(self, animSlot):
		mod = self.__dict__["ansMod"+animSlot.capitalize()]
		if mod not in ans[self.ansFam]:
			mod = ".def"

		act = self.__dict__["ans"+animSlot.capitalize()]
		if act not in ans[self.ansFam][mod]:
			mod = ".def"

		activeFrame = ans[self.ansFam][mod][act]["spec"]["frameActive"]
		dirn = (-1 if self.actuators[animSlot].frameStart
				 > self.actuators[animSlot].frameEnd else 1)

		if dirn > 0:
			isActive = activeFrame+(1*dirn) > self.getAnimFrame(animSlot) >= activeFrame
		else:
			isActive = activeFrame+(1*dirn) < self.getAnimFrame(animSlot) <= activeFrame

		return isActive

	def updateAnim(self, animSlot, speed=1):
		anim = self.actuators[animSlot]
		dirn = 1 if anim.frameStart < anim.frameEnd else -1
		step = 0.05*dirn

		mod = self.__dict__["ansMod"+animSlot.capitalize()]
		act = self.__dict__["ans"+animSlot.capitalize()]

		speed *= getTimeScale()

		try:
			hold = ans[self.ansFam][mod][act]["spec"]["hold"]
		except:
			hold = True
					 
		if ( (dirn > 0 and self[animSlot+"Frame"] < anim.frameEnd+step)
		or (dirn < 0 and self[animSlot+"Frame"] > anim.frameEnd+step ) ):
			self[animSlot+"Frame"] += (animRate*speed)*dirn
		elif not hold:
			self[animSlot+"End"] = True
			self[animSlot+"Frame"] = anim.frameStart
		else:
			self[animSlot+"End"] = True

		anim.frame = self[animSlot+"Frame"]

	def getInvSlots(self):
		items = [v for v in range(len(bodySlots))]
		for num, slotKey in enumerate(bodySlots):
			s = self.__dict__[slotKey] if slotKey != "head" else self.hat
			t = "%s: %s"%(slotKey, s.meshes[0].name)
			d = ["ui_button", { "kls":"def", "text":t, "align":True,
			"slot":s, "script":["invSlot", {}] }]

			items[num] = d

		return items

def run(cont):
	self = cont.owner
	speed = self.parent.moveSpeed if self.parent.isRunning else 1
	if "_draw" in self.ansArms or "_att" in self.ansArms:
		speed = self.parent.moveSpeed

	for tag in ["_jump", "_air"]:
		allowLegUpdate = tag not in self.ansLegs
		if not allowLegUpdate: break
		
	if (allowLegUpdate or ("_att" in self.ansArms or "_draw" in self.ansArms) ):
		cont.activate(self.actuators["arms"])
		self.updateAnim("arms", speed)
	else:
		cont.deactivate(self.actuators["arms"])
		if self.ansModArms not in jumpPass and self.ansArms != "_rsneak":
			self.onAnimChange("arms", "_rsneak")
			cont.activate(self.actuators["arms"])

		self.actuators["arms"].frame = 0

	speed = self.parent.moveSpeed if self.parent.isRunning else 1

	if "_jump" in self.ansLegs:
		speed = 2
	elif self.parent.isAttacking and self.parent.isRunning:
		speed = 1.15

	cont.activate(self.actuators["legs"])
	self.updateAnim("legs", speed)

	aim = self.actuators["spine"]

	cont.activate(aim)
	aim.frame = self["spineFrame"]
	

def new(old_owner, pos, rot, scale, d):
	setDefaults(d)
	return Arma(old_owner, pos, rot, scale, d)

def setDefaults(d):
	for key, value in armaDefaults.items():
		if key not in d: d[key] = value

armaDefaults = {"bodySlots":{"body":"maleBody", "legs":"pants_a0", "chest":"jacket_a0",
 				"feet":"boots_a0", "shoulders":False,
 				 "hands":False, "head":"helm_a0"}, "default":"male",
 				 "hair":"dudeHair_a0",

				"animSettings":{"ansFam":"mGent", "ansArms":"_idle", "ansLegs":"_idle",
				 "ansModArms":".def", "ansModLegs":".base"}
			}
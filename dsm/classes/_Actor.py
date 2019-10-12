#// 000. IMPORTS & NAMING
from dsm import _Obj
from mathutils import Vector
from math import radians, degrees
from dsm import lymath, physRate, physClamp, camTurn, armorKeys, damageFunc
from dsm import displayStrings, lang, strFromId
from random import randint
import numpy as np
core = None
Stat = None

actorStats = ["pain", "focus", "alma"]

actorBodyParts = ({"ds_torso":1, "ds_pelvis":1, "ds_head":1, "ds_neck":1, "ds_face":1,
				   "ds_upArm.L":1, "ds_upArm.R":1, "ds_foArm.L":1, "ds_foArm.R":1,
				   "ds_hand.L":1, "ds_hand.R":1, "ds_thigh.L":1, "ds_thigh.R":1,
				   "ds_calf.L":1, "ds_calf.R":1, "ds_foot.L":1, "ds_foot.R":1,
				})

#// 001. CLASS DEFINITION
class Actor(_Obj.Obj):

	def __init__(self, old_owner, pos, rot, scale, **kwargs):
		_Obj.Obj.__init__(self, old_owner, pos, rot, scale, **kwargs)
		for key in actorStats:
			value  = self[key]
			setattr(self, key, Stat(value, **{"max":value}))

			del self[key]

		self["lastAttack"] = ""
		self["actor"] = True

	def registerNewRune(self, runeword):
		self.runes[runeword] = Stat(0, **{"max":110})

	#// 001.0 BEHAVIOURS
	def bhWarden(self):
		pass


	#// 002.0 ACTOR UPDATE
	def actorUpdate(self, fwd, back, up, down, sright, sleft, sup, sdown,
		jump, fire, sheath, sneak, toggleRun, camTurn=camTurn, joySens=[0, 0, 0, 0]):

		m = 7.5; s = 2
		if not self.isRunning: m = 2
		isMoving = int(fwd + back + up + down)
		try: camrot = Vector(self.children["camguide"].localOrientation.to_euler())
		except: return False
		fpv = self.behaviour == "player" and core.firstPerson

		arma = self.children["Armature"]

		if not self.isOnGround:
			m *= 2

		if (jump and self.isOnGround) and arma["mode"] not in ["draw", "land", "air"]:
			self.isJumping = -1
			if arma["mode"] != "jump" and self.isOnGround:
				act = "_jumpMove" if isMoving else "_jump"
				act += "Right" if fwd else "Left" if back else ""
				arma.onAnimChange("legs", act, True)

			arma["mode"] = "jump"
			self.jumpForce += 0.1

			if arma["mode"] == "jump" and self.isOnGround:
				if arma.onAnimEnd("legs"):
					jump = False

		if not jump and arma["mode"] == "jump":
			self.isJumping = True
			self.accel.z = 25 + (self.jumpForce*3)
			arma["mode"] = "air"

		if not self.isOnGround and arma.getAct("legs") != "_air":
			arma["mode"] = "air"
			act = "_air"
			act += "Right" if fwd else "Left" if back else ""
			arma.onAnimChange("legs", act, True)

		if self.landing:
			if arma["mode"] == "air":
				if arma["mode"] != "land":
					act = "_jumpMove" if isMoving else "_jump"
					act += "Right" if fwd else "Left" if back else ""
					arma.onAnimChange("legs", act, True, True)
					arma["mode"] = "land"

					if self.isSneaking or jump: arma.actuators["legs"].frameEnd = 3

			if arma.onAnimEnd("legs"):
				self.landing = False
				self.jumpForce = 0.0

		if sneak and arma["mode"] != "draw":
			self.isSneaking = not self.isSneaking
			self.setDefaultAnims(arma, isMoving, fwd, back, down,
			 doLegs=True, doArms=True)

		if toggleRun and arma["mode"] != "draw":
			self.isRunning = not self.isRunning
			self.setDefaultAnims(arma, isMoving, fwd, back, down,
			 doLegs=True, doArms=True)

		if (self.isSneaking or self.isAttacking) and self.isOnGround:
			m = m/(1.75 if self.isRunning else 1.25)

		if sheath and arma.getAct("arms") != "_draw" and not self.isAttacking:
			act = "_draw"
			wep = arma.children[self.activeWeapon]
			try:
				wepMod = self.scene.objectsInactive[wep.meshes[0].name]["ansMod"]
			except:
				wepMod = ".def"
			
			arma.ansModArms = wepMod
			reverse = self.isWeaponOut
			self.isWeaponOut = not self.isWeaponOut

			arma.setAnimFrame("arms", 0)

			scb = arma.children[self.activeWeapon+".scb"]
			scb.actuators["Action"].action = "sw0a.scb"
			scb["active"] = self.isWeaponOut
			
			arma.onAnimChange("arms", act, True, reverse)
			self.setDefaultAnims(arma, isMoving, fwd, back, down,
			 doLegs=True, doArms=False)

			if arma["mode"] not in ["jump", "air", "land"]: arma["mode"] = "draw"

		if arma.getAct("arms") == "_draw":
			curr_frame = arma.getAnimFrame("arms")
			scb = arma.children[self.activeWeapon+".scb"]
			scb.actuators["Action"].frame = curr_frame

			if self.isWeaponOut and curr_frame >= 5:
				arma.children[self.activeWeapon].visible = True
			if not self.isWeaponOut and curr_frame < 5:
				arma.children[self.activeWeapon].visible = False

			if arma.onAnimEnd("arms"):
				wep = arma.children[self.activeWeapon]
				try:
					wepMod = self.scene.objectsInactive[wep.meshes[0].name]["ansMod"]
				except:
					wepMod = ".def"

				arma.ansModArms = (wepMod if self.isWeaponOut or wepMod == ".def"
					else wepMod+"_in")

				arma.ansArms = "_idle"
				self.setDefaultAnims(arma, isMoving, fwd, back, down, True)
				arma.children[self.activeWeapon].visible = self.isWeaponOut

				arma["mode"] = "move" if isMoving else "idle"
				if camrot.z != 0.0 and self.isWeaponOut: self.resetCamOffset(camrot)
				

		if fire and not self.isAttacking and arma.getAct("arms") != "_draw":
			self.isAttacking = True

			act = "_att" + ("Left" if (back or sleft)
			 else "Right" if (fwd or sright) else "Back" if (down or sdown) else "")

			if act == self["lastAttack"]:
				l = ["_att", "_attLeft", "_attRight", "_attBack"]
				l.remove(act)
				act = l[randint(0, len(l)-1)]

			self["lastAttack"] = act

			arma.onAnimChange("arms", act, True)
			if "FIRAH" in self:
				del self["FIRAH"]

		if self.isAttacking:
			fx = arma.childrenRecursive[self.activeWeapon+".fx"]
			fx.actuators["Action"].frame = arma.getAnimFrame("arms")

			if arma.getIsActiveFrame("arms") and "FIRAH" not in self:
				newPos = self.worldPosition.copy()
				newPos.z += self.cullingBox.max[2]/2

				newRot = Vector( self.worldOrientation.to_euler() )
				newRot.x = camrot.x
				fire_d =  {"obj":"melee_hitBox", "pos":newPos,
				"rot":newRot, "d":{"team":self.team},
				"kls":"fx", "life":10}

				newProj = self.scene.addObject(**fire_d)
				newProj.applyMovement([0,self.cullingBox.max[1]+0.025,0], True)
				self["FIRAH"] = "FEVERRRRR"

			if arma.onAnimEnd("arms"):
				self.isAttacking = False
				fx.visible = False
				self.setDefaultAnims(arma, isMoving, fwd, down, back)
				if "FIRAH" in self:
					del self["FIRAH"]

			else:
				fx["active"] = True
				fx.visible = True

		if isMoving:
			if camrot.z != 0.0: self.resetCamOffset(camrot)

			if isMoving > 1:
				m = m/1.25
			else:
				if not (fwd or back) and self.accel.x != 0:
					self.accel.x /= 1.2
				elif not (up or down) and self.accel.y != 0:
					self.accel.y /= 1.2

			if self.isRunning or (fwd or back):
				act = "_run" if not self.isSneaking else "_rsneak"
			else:
				act = "_walk" if not self.isSneaking else "_rsneak"
				if not self.isSneaking: act += "Wep" if self.isWeaponOut else ""

			act += "Right" if fwd else "Left" if back else ""
			checkAct = act

			if down: checkAct = "_walkWepBack" if not self.isSneaking else "_rsneakBack"
			if not self.isOnGround:
				checkAct = "_air"
				checkAct += "Right" if fwd else "Left" if back else ""
			elif self.isAttacking and act == "_run":
				checkAct = act = "_walkWep"

			if arma["mode"] == "idle" or arma.ansLegs != checkAct:
				if not (arma["mode"] in ["draw", "air", "jump", "land"]):
					arma["mode"] = "move"
				
				if (not self.isAttacking and arma["mode"] == "move"
					and not arma.getAct("arms") == "_draw"):
					arma.onAnimChange("arms", act, reverse=down)

				if down: act = "_walkWepBack" if not self.isSneaking else "_rsneakBack"
				if not (self.isJumping or self.landing):
					if not self.isOnGround:
						act = "_air"
						act += "Right" if fwd else "Left" if back else ""

					arma.onAnimChange("legs", act)

		else:
			self.accel.xy /= 2

			if arma["mode"] in ["move", "air"]:

				act = "_idle" + ("Wep" if self.isWeaponOut else "")
				if self.isSneaking: act = "_sneak"

				if not arma["mode"] in ["draw", "air", "jump", "land"]:
					arma["mode"] = "idle"
					if not self.isAttacking and not arma.getAct("arms") == "_draw":
						arma.onAnimChange("arms", act)

				if not (self.isJumping or self.landing):
					if not self.isOnGround:
						act = "_air"
						act += "Right" if fwd else "Left" if back else ""

					arma.onAnimChange("legs", act)

		if arma["mode"] in ["move", "idle"] and not self.isAttacking:
			arma.animSync("arms", "legs")

		if not self.landing and arma["mode"] == "land":

			if arma["mode"] != "draw":
				arma["mode"] = "move"
				self.setDefaultAnims(arma, isMoving, fwd, back, down,
				 doLegs=True, doArms=True)

		if sright or sleft:
			
			factor = camTurn * (1 if not self.isAttacking else 0.25)

			if not isMoving and not self.isWeaponOut and not fpv:
				self.children["camguide"].applyRotation([0,0,radians(factor*joySens[2])])
			else:
				self.applyRotation([0,0,radians(factor*joySens[2])])

		if fpv and camrot.z != 0.0: self.resetCamOffset(camrot)
		maxCamrot = radians(75)
		minCamrot = radians(-75)

		if sup:
			if lymath.floatApprox(camrot.x, maxCamrot, 0.05):
				self.children["camguide"].localOrientation = [maxCamrot, 0, camrot.z]

			else:
				r = radians(camTurn*joySens[3])
				self.children["camguide"].applyRotation([r,0,0], True)

		if sdown:
			if lymath.floatApprox(camrot.x, minCamrot, 0.05):
				self.children["camguide"].localOrientation = [minCamrot, 0, camrot.z]

			else:
				r = radians(camTurn*joySens[3])
				self.children["camguide"].applyRotation([r,0,0], True)

		if self.isWeaponOut and arma.getAct("arms") != "_draw":
			adjust_aimBone = degrees(camrot.x)/25
			oldv = arma["spineFrame"]; goal = adjust_aimBone
			arma["spineFrame"] = lymath.iLerp(oldv, goal, 6, abs(oldv)+abs(goal/6))

		else:
			oldv = arma["spineFrame"]; goal = 0
			arma["spineFrame"] = lymath.iLerp(oldv, goal, 6, abs(oldv)-abs(oldv/6))
		
		if fwd:
			self.accel.x = min( m, self.accel.x+(s*joySens[0]) )
		elif back:
			self.accel.x = max( -m, self.accel.x+(s*joySens[0]) )
		if up:
			self.accel.y = min( m, self.accel.y+(s*joySens[1]) )
		elif down:
			self.accel.y = max( -m, self.accel.y+(s*joySens[1]) )

	def setDefaultAnims(self, arma, isMoving, fwd, back,
	 down, doLegs=False, doArms=True):
		act = "_idle" + ("Wep" if self.isWeaponOut else "")
		if self.isSneaking: act = "_sneak"

		if isMoving:
			if self.isRunning: act = "_run" if not self.isSneaking else "_rsneak"
			else:
				act = "_walk" if not self.isSneaking else "_rsneak"
				if not self.isSneaking: act += "Wep" if self.isWeaponOut else ""

			act += "Right" if fwd else "Left" if back else ""
		
		doArms = not doArms if self.isAttacking else doArms
		if doArms and not arma.getAct("arms") == "_draw":
			arma.onAnimChange("arms", act, reverse=down)
			arma.animSync("arms", "legs")

		if doLegs and not (self.isJumping or self.landing):

			if down: act = "_walkWepBack" if not self.isSneaking else "_rsneakBack"

			if not self.isOnGround:
				act = "_air"
				act += "Right" if fwd else "Left" if back else ""
			
			arma.onAnimChange("legs", act)

	def resetCamOffset(self, camrot):
		selfrot = Vector(self.worldOrientation.to_euler())
		self.worldOrientation = [0,0,selfrot.z+camrot.z]
		self.children["camguide"].localOrientation = [camrot.x, 0, 0]


	#// 003.0 EQUIPMENT SLOTS
	def getInvSlots(self):
		items = [v for v in range(len(self.inventory))]
		for num, item in enumerate(self.inventory):
			slotKey = self.scene.objectsInactive[item]["slot"]
			t = "%s: %s"%(slotKey, item)
			
			if slotKey in armorKeys:
				s = (self.children["Armature"].__dict__[slotKey] if slotKey != "head"
					else self.children["Armature"].hat)

			d = ["ui_button", { "kls":"def", "align":False, "slot":s,
			"text":t, "script":["invItem", {}] }]

			items[num] = d

		return items

	def getSeenRunes(self):
		items = [i for i in range(len(self.runes))]

		for num, rune in enumerate(self.runes):
			learned = self.runes[rune] < 100
			t = rune+": "+ strFromId(rune, lang, learned)
			s = ["pickRune", {}] if learned else ["empty", {}]
			d = ["ui_button", { "kls":"def", "align":False,
			 "text":t, "script":s }]
			items[num] = d

		return items

	def equipSpell(self, ob, slot):
		spellname = ob.text.split(": ")[1]
		self.spells[slot] = spellname
		ico = ob.scene.objects["spellbar_%d"%slot]
		ico.endObject()


#// 003. MODULE HANDLE
def testCube(cont):
	own = cont.owner
	if "init" not in own:
		own["init"] = True

		own = new(own, own.worldPosition.copy(),
		 own.worldOrientation.copy(), own.worldScale.copy(),
		  {"behaviour":"cowFucker"})

		own["path"] = 0
		own["pathOld"] = []
		own["pathPoint"] = None
		own["moveTarget"] = own.scene.objects["navmeshTarget"].worldPosition
		own["currNav"] = None
		own["pathVs"] = []

	#own["moveTarget"] = core.player.worldPosition
	ground_vec1 = [own.worldPosition.x, own.worldPosition.y,
	own.worldPosition.z - ( 1.5 )]
	ground_vec2 = [own.worldPosition.x, own.worldPosition.y,
	own.worldPosition.z + ( 4 )]

	groundCheck = own.rayCast(ground_vec1, ground_vec2, prop="ground", xray=True)
	own.isOnGround = bool(groundCheck[0])

	if groundCheck[1] and own.isJumping < 1:
		own.worldPosition.z = groundCheck[1][2]

	hitObj = groundCheck[0]
	recalc = False; nav = None

	if "moveTarget" in own:
		target = own["moveTarget"]
		#own["pathPoint"] = target

		if hitObj:
			if own.parent != hitObj: own.setParent(hitObj)

			if hitObj.meshes[0].name+"navmesh" != own["currNav"]:
				own["path"] = 0
				own["pathPoint"] = None
				own["pathVs"] = []
				own["pathOld"] = []
				own["nav"] = Vector([0,0,0])
				if "bvh" in own:
					del own["bvh"]

			if own["path"] == 0:
				if hitObj.meshes[0].name+"navmesh" in own.scene.objects:
					nav = own.scene.objects[hitObj.meshes[0].name+"navmesh"]
					own["nav"] = nav.worldPosition
					if "bvh" not in own:
						own["bvh"] = nav.meshes[0].constructBvh( nav.worldTransform )
					
					own["currNav"] = nav.name
					own["path"] = [target-nav.worldPosition]
					start = own.worldPosition
					newVs = own["pathVs"]

					for i in range(256):
						newPoint, newVs = pathFind(own["bvh"], start,
						 nav, target, newVs, own["pathOld"])

						if newPoint:
							own["path"].append(newPoint)

							target = newPoint+nav.worldPosition
							own["pathVs"] = newVs
							toFinish = np.linalg.norm((start-nav.worldPosition)-newPoint)

							if toFinish < 48:
								break

						else:
							break

					own["path"] = own["path"][::-1]

				"""
				if own["path"]:
					own["path"] = ([ list(eval(vec)) for vec in
					 {str(tuple(p)):0 for p in own["path"]} ])
				"""
			
			
			elif own["path"] and not own["pathPoint"]:
				own["pathPoint"] = own["path"].pop(0)
				own.scene.objects["Suzanne"].worldPosition = own["pathPoint"]+own["nav"]

	if own["pathPoint"]:
		p = own.getVectTo(own["pathPoint"]+own["nav"])		
		if p[1] != Vector([0,0,0]):
			own.alignAxisToVect(p[1], 1, 0.25)			

		own.worldOrientation = [0,0,own.worldOrientation.to_euler().z]		

		if p[0] < 12:
			if own.getDistanceTo(target) < 12:
				own.accel.y = 0
				own["path"] = 0
				#del own["moveTarget"]

			elif not own["path"]:				
				own["path"] = 0				

			own["pathPoint"] = None

		else:
			own.accel.y = 20

	if "navCamguide" in own.scene.objects:
		own.scene.objects["navCamguide"].worldPosition = own.worldPosition

	own.physicsUpdate()

def pathFind(bvh, start, nav, target, lastVs, pathOld):
	
	first_co = None
	if not lastVs:
		nns = bvh.find_nearest(target, np.linalg.norm(start-target))

		if nns[0]:
			co, normal, index, dist = nns
			poly = nav.meshes[0].getPolygon(index)
			centroid = Vector([0,0,0])

			for v in range(3):
				sv = nav.meshes[0].getVertex(0, poly.getVertexIndex(v))
				v = sv.getXYZ()
				lastVs.append(v)

				centroid += v

			first_co = (centroid/3)
			return first_co, lastVs

	nns = bvh.find_nearest_range(target, 24.0)
	points = np.asarray([ 0 for v in range(len(nns)) ], dtype=object)
	i = 0

	for n in nns:
		co, normal, index, dist = n
		centroid = Vector([0,0,0])
		poly = nav.meshes[0].getPolygon(index)
		isNeighbor = 0
		polyVs = [vi for vi in range(3)]
		vi = 0

		for v in range(3):
			sv = nav.meshes[0].getVertex(0, poly.getVertexIndex(v))				
			v = sv.getXYZ()
			if v in lastVs or not lastVs:
				isNeighbor += 1

			polyVs[vi] = v
			vi += 1
			centroid += v

		co = (centroid/3)
		if isNeighbor and index not in pathOld:
			points[i] = [co, polyVs, index, isNeighbor]
			i += 1

	dist = 999999999 #np.linalg.norm(start-target)
	closest = None
	newVs = lastVs
	newIndex = None

	for poly in points[points != 0]:
		point, polyVs, index, nfac = poly
		newdist = np.linalg.norm((point+nav.worldPosition)
			-(start))/nfac

		if newdist < dist and index:
			closest = point
			newVs = polyVs
			dist = newdist
			newIndex = index

	if newIndex: pathOld.append(newIndex)
	return closest, newVs

def new(old_owner, pos, rot, scale, d):
	setDefaults(d)
	return Actor(old_owner, pos, rot, scale, **d)

def setDefaults(d):
	for key, value in actorDefaults.items():
		if key not in d: d[key] = value

actorDefaults = {
				"kls":"actors", "weight":4.0, "solid":False, "ripMesh":None,
				"behaviour":"player", "alignToSurface":False,
				"isAttacking":False, "isWeaponOut":False, "isSneaking":False,
				"isRunning":False, "moveSpeed":1.5, "landing":False,
				"activeWeapon":"weap_R", "cell":"TE000000001",
				"runes":{}, "runewords":{}, "drawRune":None,
				"spells":["Empty" for i in range(9)],
				"bodyParts":actorBodyParts, "inventory":[], "team":0
			}
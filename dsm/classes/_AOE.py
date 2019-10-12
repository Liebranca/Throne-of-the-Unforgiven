import numpy as np
from random import uniform
from math import radians
from mathutils import Vector
from bge.types import KX_GameObject
from dsm import lymath, physRate, physClamp, camTurn, armorKeys, damageFunc
core = None

class AOE(KX_GameObject):

	def __init__(self, old_owner, pos, rot, scale, **kwargs):

		for key, value in kwargs.items():
			self.__dict__[key] = value

		self.worldPosition = pos; self.worldOrientation = rot; self.localScale = scale

		if self.getPhysicsId():
			self.collisionCallbacks = [self.onCollision]
			self.alreadyHit = {}

	def onCollision(self, hitObject, point, normal, points):
		if hitObject.id not in self.alreadyHit:
			if getInRadius(hitObject, self.damage, self.team):
				scaling = [1.65, 2.25] if hitObject.pain <= 0 else [0.95, 1.5]

				if "hitFX" in hitObject:
					addHitFX(self, hitObject["hitFX"], point, scaling)

				if "hitFX" in self:
					addHitFX(self, self["hitFX"], point, scaling)

		self.alreadyHit[hitObject.id] = True
		self.endObject()

def addHitFX(ref, hitFX, point, sc=[0.95, 1.5]):
	d = {"obj":hitFX, "pos":point, "scale":Vector([1,1,1])*uniform(sc[0], sc[1]),
	"d":{"alignTo":ref.worldPosition.copy()},
	 "life":ref.scene.objectsInactive[hitFX]["dur"]}

	newFX = core.queues["addObject_mainScene"].append(d)

def getInRadius(hitObject, damageType, team):

	#non-projectile
	if hitObject.collisionGroup != 2**8:
		validTarget = hitObject.team != team
		if validTarget:
			dmg = damageFunc(hitObject["resist"], damageType)
			hitObject.pain -= dmg
			if "takeHit" in hitObject:
				hitObject["takeHit"] = True

		if hitObject.pain <= 0:
			hitObject.onDeath()			

		return validTarget

	return False

getInRadius_ufunc = np.frompyfunc(getInRadius, 3, 1)

def new(old_owner, pos, rot, scale, d):
	setDefaults(d)
	return AOE(old_owner, pos, rot, scale, **d)

def setDefaults(d):
	for key, value in objDefaults.items():
		if key not in d: d[key] = value

objDefaults = {
				"damage":"chaos", "canTouch":False, "team":0
			}
from dsm import showDebug
from mathutils import Vector
from math import radians

def resource(cont):
	own = cont.owner
	col = own.sensors["Collision"]

	if col.positive:
		index = col.hitObject.team
		core = own.scene.objects["Manager"]["core"]

		core.modRes(index, own["res"], round(own["value"]))

def multiSpawn(cont):
	own = cont.owner

	delay = cont.sensors["Delay"]
			
	if delay.positive and own["size"] > 0:
		own["size"] -= 0.25
		own.applyMovement([0.5,-0.05,0], True); own.applyRotation([0,0,radians(35)])
		
		newObj = own.scene.addObject(own["add"], life=1200)
		newObj.worldPosition = own.worldPosition
		newObj.worldOrientation = own.worldOrientation

		vecFrom = newObj.worldPosition.copy() + Vector([0,0,25])
		vecTo = newObj.worldPosition.copy() + Vector([0,0,-25])
		ray = newObj.rayCast(vecTo, vecFrom, xray=True)

		pos = ray[1] if ray[0] else own.worldPosition
		newObj.worldPosition = pos

		parent = own.parent
		if parent: newObj.setParent(parent)		

		for act in cont.actuators:
			cont.activate(act)

	else:
		own.endObject()

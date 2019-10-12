import bge
from math import radians, degrees
from mathutils import Vector

if not hasattr(bge, "__component__"):
	from dsm.gamekeys import getEvent, getJoyInput
	from dsm import physRate


class Static(bge.types.KX_PythonComponent):

	args = {}
	def start(self, args):
		pass

	def update(self):
		core = bge.logic.getCurrentScene().objects["Manager"]["core"]

		self.object.checkInFrustum()
		
		"""
		if "000000001" in self.object.id:
			cam = self.object.scene.active_camera.parent
			rot = Vector( cam.worldOrientation.to_euler() )
			ownRot = Vector( self.object.worldOrientation.to_euler() )
			
			facing = int( degrees(rot.z + ownRot.z) )
			for i in range( abs(divmod(facing,180)[0]) ):
				facing = facing - 180 if facing > 0 else facing + 180

			if facing < 45: s = "back"
			elif facing < 135: s = "side"
			else: s = "front"
			
			if "fizzel" not in core.cont:
				core.cont["fizzel"] = facing
				core.cont.addDebugProperty("fizzel")

			core.cont["fizzel"] = facing
		"""

		if self.object.solid:
			pass

		else:
			core = bge.logic.getCurrentScene().objects["Manager"]["core"]

			ground_vec1 = [self.object.worldPosition.x, self.object.worldPosition.y,
			self.object.worldPosition.z - 0.025]
			ground_vec2 = [self.object.worldPosition.x, self.object.worldPosition.y,
			self.object.worldPosition.z + 0.05]

			self.object.isOnGround, hitpoint = self.object.rayCast(ground_vec1, ground_vec2)[0:2]
			self.object.isOnGround = bool(self.object.isOnGround)

			if not self.object.isOnGround and not self.object.accel.z:
				self.object.accel.z = -self.object.weight
			elif self.object.isOnGround and self.object.worldPosition.z != hitpoint[2]:
				self.object.worldPosition.z = hitpoint[2]


			if self.object.accel.x or self.object.accel.y or self.object.accel.z:
				self.object.physicsUpdate()

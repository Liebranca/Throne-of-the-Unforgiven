#// 000. IMPORTS & NAMING
from mathutils import Vector
from bge.types import KX_Scene, KX_GameObject
from bge import logic

klsDict = {"statics": None, "actors": None, "fx": None,
 "armatures":None, "Terra": None, "widgets":None}

core = None

nonkls = ["PU", "HT", "FX", "Ico", "Text", "OCCLU", "navmesh"]


#// 001. CLASS DEFINITION
class Scene(KX_Scene):

	def __init__(self, old_scene):
		self.kls = "scenes"
		self.id = core.genID(self, "scenes")


	#// 001.0 STANDARD METHODS: OVERRIDE INHERITED
	def addObject(self, obj, pos=[0,0,0], rot=[0,0,0], scale=[1,1,1],
	 reference=None, life=0.0, d={}, kls="statics"):

		if kls=="Terra":
			wx = core.wOrigin[0]+d["cell"][0]
			wy = core.wOrigin[1]+d["cell"][1]
			ripMesh = "%s_%dx%d"%(core.worldName, wx, wy)
			if ripMesh in self.objectsInactive:
				obj = ripMesh

			else:
				obj = "TE000000001"

		elif kls=="widgets":
			return klsDict[kls].new( (KX_Scene.addObject(self, obj, reference, life)),
			 pos, d )

		else:
			for tag in nonkls:
				if tag in obj:
					newObj = KX_Scene.addObject(self, obj, reference, life)
					if d:
						newObj.worldPosition = pos; newObj.worldOrientation = rot
						newObj.worldScale = scale

						if "alignTo" in d:
							p = newObj.getVectTo(d["alignTo"])
							if p[1] != Vector([0,0,0]):
								newObj.alignAxisToVect(p[1], 0, 1)

					return newObj


		return klsDict[kls].new( ( KX_Scene.addObject(self, obj, reference, life) ),
		 pos, rot, scale, d )


#// 002. MODULE HANDLE
def new(old_scene):
	return Scene(old_scene)

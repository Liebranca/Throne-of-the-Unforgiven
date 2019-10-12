#// 000. IMPORTS & NAMING
from bge.types import KX_GameObject
from dsm import gamepath
import numpy as np


#// 001. CLASS DEFINITION
class EquipMesh(KX_GameObject):
	def __init__(self, old_owner, m, origin):
		self.origin = origin
		if m: self.onMeshChange(m)

	def onMeshChange(self, m):
		if m == "equipSlot" and self.origin:
			m = self.origin

		self.replaceMesh(m, 1, 1)
		m = self.meshes[0].copy()
		self.replaceMesh(m, 1, 1)

		self.visible = m.name != "equipSlot"

	def toggleColors(self, slots, invert=False):

		m = self.meshes[0]
		a = np.load( gamepath+"\\data\\chars\\meshData\\%s.npy"%(str(m)) )

		for slot, col in slots.items():
			if invert and not col: col = not col
			modVertCol_ufunc(a[slot], m, col)


def modVertCol(vi, m, col):
	v = m.getVertex(0, vi)
	v.color = vertColDict[col]

modVertCol_ufunc = np.frompyfunc(modVertCol, 3, 0)
vertColDict = {-1:[1,0,0,1], 0:[0,0,0,1], 1:[1,1,1,1]}


def new(old_owner, m, origin):
	return EquipMesh(old_owner, m, origin)

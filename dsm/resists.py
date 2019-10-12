import numpy as np

#"cutting":0,"cold":1,"blunt":2,"pierce":3,"fire":4


d = {
	"wood":[0.1, 0.25, 1.25, 1.5, 2.0],
	"rock":[0.1, 0.25, 2.25, 0.5, 0.20],
	"metal":[0.1, 2, 1.25, 0.25, 0.1]
}

d2 = {
	"chaos":[1, 1, 10, 1, 1],
	"axe":[10, 2, 1, 8, -1]
}

def damageFunc(resistType, damageType):
	return sum( applyDamage_ufunc(d[resistType], d2[damageType]).tolist() )

def applyDamage(resistMult, damageBase):
	return damageBase*resistMult

applyDamage_ufunc = np.frompyfunc(applyDamage, 2, 1)

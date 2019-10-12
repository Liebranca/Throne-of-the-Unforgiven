from dsm.ohjunn import d as ohjunn

def fromKey(cont):
	own = cont.owner
	own.text = ["displayName"] = ohjunn[ own["runeKey"] ]
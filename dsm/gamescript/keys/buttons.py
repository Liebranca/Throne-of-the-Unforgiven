from dsm.classes._Obj import spawners

def multiObject(cont):
	own = cont.owner
	gate = eval(own["gate"])
	targets = eval(own["targets"])

	if gate["active"] and own["active"]:
		for target in targets: target["active"] = True
	else:
		for target in targets: target["active"] = False

	if own["active"]:
		if "spawnDict" in own:
			newObj = spawners(cont)
			newObj.setParent(own)

	else:
		if "spawnDict" in own:
			if own.children: own.children[0].endObject()
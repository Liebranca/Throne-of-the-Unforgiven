from bge.types import KX_GameObject, KX_FontObject
from math import radians
from mathutils import Vector
from dsm import textRes, apparel, screens, armorKeys, displayStrings, lang, strFromId

nakedMesh = ["equipSlot", "maleHead", "maleFeet", "maleHands"]
equipCheck = {"feet":[False, "legs"], "legs":[True, "feet"],
			"chest":[True, "hands"], "hands":[False, "chest"]
		}
core = None

class Widget(KX_GameObject):
	def __init__(self, old_owner, pos, **kwargs):
		for key, value in kwargs.items():
			self.__dict__[key] = value

		resolution = core.GUI.windowRes

		x, y = pos; x, y = resolution[0]*x, resolution[1]*y
		self.worldPosition.xy = [x, y]
		self.pixelPos = pos

		self.getHasText()
		if self.meshes: self.replaceMesh( self.meshes[0].copy() )
		if self.hasText: self.onTextChange(self.text)

		self.clicked = False


	def getHasText(self):
		self.hasText = [child for child in self.childrenRecursive
		 if isinstance(child, KX_FontObject)]

	def onTextChange(self, s):
		ob = self.hasText[0]
		if ": " in s:
			pre, suf = s.split(": ")
			if suf in displayStrings:
				suf = strFromId(suf, lang)

			if self.script[0] == "invSlot":
				pre = strFromId(pre, lang)
				pre = pre.capitalize()+": "
			else: pre = ""

			s = pre+suf

		ootline = ob.children[0]
		ootline.text = ob.text = s
		self.adjustText(ob)

	def adjustText(self, ob):

		ootline = ob.children[0]

		if ob.resolution < textRes: ootline.resolution = ob.resolution = textRes
		x_fac = ( (len(ob.text)*0.075) )
		ob.size = ootline.size = 0.275

		ob.worldPosition.y = self.worldPosition.y - (self.cullingBox.max[1]/4)
		ob.worldPosition.x = self.worldPosition.x

		ob.removeParent()
		self.worldScale.x = x_fac/1.25
		ob.setParent(self)

	def onClick(self):
		if not self.script[0] == "empty":
			commandDict[self.script[0]](self, **self.script[1])

	def suspendPhysics(self):
		self.visible = False
		for child in self.childrenRecursive:
			child.suspendPhysics()
			child.visible = False

		KX_GameObject.suspendPhysics(self)

	def restorePhysics(self):
		self.visible = True
		for child in self.childrenRecursive:
			child.restorePhysics()
			child.visible = True

		KX_GameObject.restorePhysics(self)

class WList(Widget):

	def __init__(self, old_owner, pos, **kwargs):
		Widget.__init__(self, old_owner, pos, **kwargs)

		if "fetcher" in self.name: self.items = eval(self.items)

		scroll = self.getScroller()
		newItems = [ v for v in range(len(self.items)) ]
		x_fac = len(self.text)
		for num, item in enumerate(self.items):
			vx = 0.65 if item[1]["align"] else 0.0
			if not vx: defnum = num - ((len( eval(self.adjust)))) #/2)+0.25)
			else: defnum = num

			newPos = ( pos[0]+( (x_fac)*0.045 )+vx, pos[1]-(defnum*0.1) )
			newWid = self.scene.addObject(item[0],
			 pos=newPos, d=item[1], kls="widgets")

			newWid.applyMovement([0,0,0.025])
			newWid.suspendPhysics()

			newItems[num] = newWid
			if not vx: newWid.setParent(scroll)
			else: newWid.setParent(self)

		self.items = newItems
		self.itemsVisible = False

		if not core.GUI.listOpen:
			core.GUI.active_widget = self
			self.onClick()

	def appendItem(self, item):
		x_fac = len(self.text); num = len(self.items) - ((len( eval(self.adjust))/2)+0.25)
		scroll = self.getScroller()
		pos = self.pixelPos
		pos = ( pos[0], pos[1] + (scroll.localPosition.y/core.GUI.windowRes[1]) )

		newPos = ( pos[0]+(x_fac*0.045), pos[1]-(num*0.1) )
		newWid = self.scene.addObject(item[0],
		 pos=newPos, d=item[1], kls="widgets")

		newWid.applyMovement([0,0,0.025])
		newWid.setParent( scroll )

		self.items.append(newWid)
		newWid.restorePhysics()

	def getScroller(self):
		return self.children[self.name+".scroller"]

class PickWheel(Widget):

	def __init__(self, old_owner, pos, **kwargs):
		Widget.__init__(self, old_owner, pos, **kwargs)
		self.active_op = None

		for i in range(1, 9):
			op = "op"+str(i)
			if self.mode == "bind":
				tag = eval(self.__dict__[op])
			else:
				tag = self.__dict__[op]

			child = self.children[self.name+"."+op]
			if tag.lower() == "clothing": icoName = "armorIco"
			elif tag.lower() == "weapons": icoName = "weapIco"
			elif tag.lower() == "lytheknics": icoName = "bookIco"
			elif tag.lower() == "character": icoName = "charIco"
			else: icoName = "baseIco"

			newIco = child.scene.addObject(icoName)

			newIco.worldPosition = child.worldPosition
			newIco.localScale = [0.4,0.4,0.4]
			newIco.color[3] = 0.0
			newIco.setParent(child)

		self.itemPick = 0

	def onHover(self):
		deactivate = [False for i in range(1, 9)]
		for i in range(1, 9):
			deactivate[i-1] = self.checkOp("op"+str(i))
			if self.itemPick:
				self.itemPick = i
				if self.mode != "menu": break

		if self.itemPick and self.mode != "menu":
			pick = self.itemPick-1
			if self.mode == "bind":
				l = eval(self.bindTo)
				l[pick] = core.GUI.bindPick
				core.GUI.bindPick = "Empty"

		unactive = True in deactivate
		if False not in deactivate:
			self.active_op = None
			if core.GUI.pointer.text != "": core.GUI.onTextChange("")

		return unactive

	def checkOp(self, op):

		if self.mode == "bind":
			inUse = eval(self.__dict__[op])
		else:
			inUse = self.__dict__[op]

		if inUse:
			child = self.children[self.name+"."+op]
			self[op] = child["doMe"]

			if self[op]:
				self.actuators[op].frame = min(self.actuators[op].frame+0.25, 5)
				self.active_op = inUse

				if self.mode == "menu": newScreen = self.active_op.lower()
				else: newScreen = core.GUI.prevScreen 
				if core.GUI.mouse["frame"] and newScreen in screens:
					core.GUI.drawScreen(newScreen)
					if self.mode != "menu": core.GUI.onTextChange("", "prompter")
					self.itemPick = True
					return True

				elif core.GUI.pointer.text != self.active_op:
					core.GUI.onTextChange(self.active_op)

			else: self.actuators[op].frame = max(self.actuators[op].frame-0.25, 0)

			child.children[0].color[3] = self.actuators[op].frame/5

		return not self[op] and self.actuators[op].frame == 0

class icoRow(Widget):
	def __init__(self, old_owner, pos, **kwargs):
		Widget.__init__(self, old_owner, pos, **kwargs)
		for i in range(self.length+1):
			newIco = self.scene.addObject("baseIco")

			newIco.worldPosition = self.worldPosition
			newIco.applyMovement([0.4*i, 0, 0])
			newIco.localScale = [0.2,0.2,0.2]
			newIco.setParent(self)

			newIco["linkTo"] = self.linkTo
			newIco.name = self.idRoot+"_%d"%i

klsDict = {"def":Widget, "WList":WList, "PickWheel":PickWheel, "icoRow":icoRow}

def new(old_owner, pos, d):
	setDefaults(d)
	return klsDict[ d["kls"] ](old_owner, pos, **d)

def setDefaults(d):
	for key, value in objDefaults.items():
		if key not in d: d[key] = value

objDefaults = {
				"kls":"def", "text":"", "script":["empty", {}]
			}

def newGame(ob):
	core.playerLog = True
	core.GUI.mouseLook = True
	core.GUI.drawScreen("")
	core.GUI.resetMousePos()
	core.GUI.bkgn["active"] = True
	core.GUI.bkgn.state = 1

def invSlot(ob):
	slotKey, meshName = ob.text.split(": ")
	unequip = meshName not in nakedMesh
	
	if unequip:
		if slotKey != "body":
			ob.slot.onMeshChange("equipSlot")
			ob.slot.parent.body.toggleColors(
			apparel[meshName]["slotData"], invert=True)
			if slotKey in equipCheck:
				doSelf, childSlot = equipCheck[slotKey]
				childSlot = ob.slot.parent.__dict__[childSlot]
				childMesh = childSlot.meshes[0].name

				if childMesh not in nakedMesh:
					childSlot.toggleColors(
					apparel[meshName]["slotData"], invert=True)
					ob.slot.parent.body.toggleColors(
					apparel[childMesh]["slotData"])

			if slotKey == "head":
				ob.slot.parent.head.toggleColors(
					apparel[meshName]["slotData"], invert=True)

				ob.slot.parent.hair.visible = True

			ob.slot.parent.parent.inventory.append(meshName)
			d = ["ui_button", { "kls":"def", "slot":ob.slot,
			 "text":ob.text, "script":["invItem", {}] }]

			ob.parent.appendItem(d)

			ob.text = "%s: %s"%(slotKey, "equipSlot")
			ob.onTextChange(ob.text)

def invItem(ob):

	slotKey, meshName = ob.text.split(": ")

	if slotKey != "body" and slotKey in armorKeys:
		ob.slot.onMeshChange(meshName)
		ob.slot.parent.body.toggleColors(
		apparel[meshName]["slotData"])

		if slotKey in equipCheck:
			doSelf, childSlot = equipCheck[slotKey]
			childSlot = ob.slot.parent.__dict__[childSlot]
			doHide = childSlot.meshes[0].name not in nakedMesh
			if not doSelf:				
				if doHide:
					childSlot.toggleColors(apparel[meshName]["slotData"])
			elif doHide:
				childMesh = childSlot.meshes[0].name
				ob.slot.toggleColors(apparel[childMesh]["slotData"])

		if slotKey == "head":
			ob.slot.parent.head.toggleColors(
			apparel[meshName]["slotData"])
			ob.slot.parent.hair.visible = 2 not in apparel[meshName]["slotData"]

		inventory = ob.slot.parent.parent.inventory
		if meshName in inventory: inventory.remove(meshName)
		core.GUI.active_widget = None

		i = armorKeys.index(slotKey)
		other = ob.parent.parent.items[i]

		if other.text.split(": ")[1] != "equipSlot":
			d = ["ui_button", { "kls":"def", "slot":other.slot,
			 "text":other.text, "script":["invItem", {}] }]

			ob.parent.parent.appendItem(d)

		other.text = "%s: %s"%(slotKey, meshName)
		other.onTextChange(other.text)

		items = ob.parent.parent.items
		i = items.index(ob)
		if i < len(items):
			for item in items[i:]:
				item.applyMovement([0,0.1*core.GUI.windowRes[1],0])

		items.remove(ob)
		ob.endObject()

def listToggle(ob):
	if ob:
		if not ob.invalid:
			if ob.itemsVisible or core.GUI.active_widget != ob:
				for child in ob.items: child.suspendPhysics()
				ob.getScroller().worldPosition.y = ob.worldPosition.y
				ob.itemsVisible = False

			else:
				for child in ob.items: child.restorePhysics()
				core.GUI.active_widget = ob
				ob.itemsVisible = True

				if None != core.GUI.listOpen != ob:
					if not core.GUI.listOpen.invalid:
						obPos = Vector(ob.worldPosition)
						newPos = Vector(core.GUI.listOpen.worldPosition)

						core.GUI.listOpen.worldPosition, ob.worldPosition =(
							obPos, newPos)

						listToggle(core.GUI.listOpen)


				core.GUI.listOpen = ob

def screenChange(ob, newScreen):
	core.GUI.drawScreen(newScreen)
	core.GUI.onTextChange("")

def pickRune(ob):
	core.player.drawRune = ob.text.split(": ")[0]
	screenChange(ob, "spellpaint")

def equipSpell(ob):
	core.GUI.bindPick = ob.text.split(": ")[1]
	core.GUI.raisePrompt("Bind incantation to an item in the wheel", "spellwheel")

	"""
	fx = core.player.scene.addObject("flame_beam", kls="fx")
	fx.worldPosition = core.player.worldPosition
	fx.worldOrientation = core.player.worldOrientation
	camrot = Vector(core.player.children["camguide"].localOrientation.to_euler())
	
	fx.applyRotation([camrot.x, 0, 0], True)
	fx.applyMovement([0,fx.cullingBox.max[1],core.player.cullingBox.max[2]/1.5], True)
	"""


commandDict = {"newGame":newGame, "listToggle":listToggle, "invSlot":invSlot, "invItem":invItem,
			"screenChange":screenChange, "pickRune":pickRune, "equipSpell":equipSpell}

def scroller(cont):
	own = cont.owner
	adjust = eval(own.parent.adjust)
	if len(own.parent.items) > len(adjust):
		up = core.cont["up"] or core.cont["zoomout"]
		down = core.cont["down"] or core.cont["zoomin"]

		if up or down:
			v = 0
			if up:
				firstItem = own.parent.items[len(adjust)]
				longList = firstItem.worldPosition.y/core.GUI.windowRes[1] >= 0.90
				if longList: v = -0.05
				
			else:
				lastItem = own.parent.items[-1]
				longList = lastItem.worldPosition.y/core.GUI.windowRes[1] <= -0.90
				if longList: v = 0.05

			own.applyMovement([0,v,0])

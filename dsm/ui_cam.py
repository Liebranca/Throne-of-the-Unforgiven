from bge.logic import setTimeScale
from dsm.gamekeys import getEventStatus
from dsm.utils.lymath import boneTrack, floatApprox
from dsm import displayStrings, lang, strFromId
from mathutils import Vector
core = None

def update(cont):
	own = cont.owner
	if "lastHit" not in own: own["lastHit"] = None
	if getEventStatus("charmenu") and core.player:

		if core.GUI.currScreen == "":
			newScreen = "menus_char"
			setTimeScale(0.01)
			core.GUI.bkgn["active"] = True
			core.GUI.bkgn.state = 1
		else:
			newScreen = ""
			core.GUI.active_widget = None
			core.GUI.resetMousePos()
			core.cont["lookAngle"] = [0,0]
			setTimeScale(1.0)
			core.GUI.bkgn["active"] = False
			core.GUI.bkgn.state = 1
			core.GUI.onTextChange("", "prompter")

		core.GUI.drawScreen(newScreen)
		core.GUI.mouseLook = not core.GUI.mouseLook

	if not core.GUI.mouseLook:
		core.GUI.updateMouse()

		if core.GUI.mouseRay.positive:
			hitObj = core.GUI.mouseRay.hitObject
			if "op1" in hitObj:
				hitObj.onHover()
				core.GUI.active_widget = hitObj
			elif "doMe" in hitObj:
				hitObj.parent.onHover()
				core.GUI.active_widget = hitObj.parent

			else:
				actColor = ([1,1,0] if not core.GUI.mouse["frame"] else [1,0.25,0])
				isChild = own["lastHit"] in hitObj.childrenRecursive
				forget = own["lastHit"] != hitObj and not isChild
				check = own["lastHit"] == hitObj or isChild

				if (check and not forget) or (not own["lastHit"]):
					own["lastHit"] = hitObj if not hitObj.hasText else hitObj.hasText[0]
					if own["lastHit"].color[0:3] != actColor:
						own["lastHit"].color[0:3] = actColor

				elif forget and own["lastHit"]:
					if not own["lastHit"].invalid:
						own["lastHit"].color[0:3] = [1,1,1]

					own["lastHit"] = None

			if core.GUI.mouse["frame"]:
				if hasattr(hitObj, "clicked"):
					core.GUI.active_widget = hitObj
					core.GUI.active_widget.clicked = True

		elif own["lastHit"]:
			if not own["lastHit"].invalid:
				own["lastHit"].color[0:3] = [1,1,1]

			own["lastHit"] = None

		if core.GUI.active_widget:

			if not core.GUI.active_widget.invalid:
				if not core.GUI.mouse["frame"] and core.GUI.mouseRay.positive:
					if "op1" in core.GUI.active_widget:
						pass

					else:
						core.GUI.active_widget.onClick()
						core.GUI.active_widget = None
				
				elif core.GUI.mouseRay.hitObject != core.GUI.active_widget:
					if "op1" in core.GUI.active_widget:
						if not core.GUI.active_widget.onHover():
							core.GUI.active_widget = None

					else:
						core.GUI.active_widget = None

	core.GUI.mouse.visible = not core.GUI.mouseLook
	core.GUI.crosshair.visible = core.GUI.mouseLook

def mouseGate(cont):
	own = cont.owner

	if core.GUI.mouseLook:
		
		if own["mouseLook"]: core.cont["lookAngle"] = core.GUI.calcMouseLook()
		own["mouseLook"] = True
		if own.scene.active_camera.timeOffset > 1.0:
			own.scene.active_camera.timeOffset -= own.scene.active_camera.timeOffset/5

		else: own.scene.active_camera.timeOffset = 0.0

		if core.player:

			cam = own.childrenRecursive["gamecam"]
			arma = core.player.children["Armature"]
			camPoint = arma.children["camPoint"]
			own.worldPosition = camPoint.worldPosition
			
			if "origin" not in own:
				own["origin"] = cam.localPosition.y
				own["lastHit"] = cam.worldPosition
				own["y_offset"] = 0.0
				arma = core.player.children["Armature"]
				camPoint = arma.children["camPoint"]
				camPoint.localOrientation = [0,0,0]			
			
			if not core.firstPerson:
				backray_vec = Vector(cam.worldPosition)
				backray_vec += cam.worldOrientation.col[2]*own["y_offset"]

				camCol = own.rayCast(cam.worldPosition,
				 mask=own.collisionMask, xray=True)

				backRay = cam.parent.rayCast(backray_vec, mask=own.collisionMask)

				if camCol[0]:
					own["lastHit"] = camCol[1]
					if cam.localPosition.y < 0.0:
						own["y_offset"] += cam.getDistanceTo(camCol[1])

				elif not backRay[0] and cam.getDistanceTo(own["lastHit"]) > 5.0:
					clamp = floatApprox(cam.localPosition.y, own["origin"], 1.0)
					dirn = 1 if own["origin"]+own["y_offset"] > own["origin"] else -1
					step = cam.getDistanceTo(own["lastHit"])*dirn
					if not clamp and own["y_offset"] > 0:
						own["y_offset"] -= step*0.05

					else:
						cam.localPosition.y = own["origin"]
						own["lastHit"] = cam.worldPosition
						own["y_offset"] = 0.0

				cam.localPosition.y = min(0.0, own["origin"]+own["y_offset"])
				cam.parent.localPosition.x = max(0, 1.5-(own["y_offset"]*0.1875))

			depth = 0.3 if core.firstPerson else 1
			vecTo = cam.worldPosition.copy()
			vecTo -= cam.worldOrientation.col[2]*(32*depth)
			
			caster = cam if core.firstPerson else cam.parent
			crossSizeRay = caster.rayCast(vecTo, xray=True, mask=own.collisionMask)
			if crossSizeRay[0]:
				maxsize = 2
				dist = caster.getDistanceTo(crossSizeRay[1])
				if dist <= 1: dist = 1
				f = max(1, min(maxsize, maxsize/dist))

				core.GUI.crosshair.localScale.xy = [f,f]

			else: core.GUI.crosshair.localScale.xy = [1,1]


			enemyRay = cam.rayCast(vecTo, prop="resist",
			 xray=True, mask=own.collisionMask)[0]

			if enemyRay:
				if hasattr(enemyRay, "team"):
					if enemyRay.team != core.player.team:
						core.GUI.crosshair["mode"] = "enemy"
						core.GUI.crosshair.state = 2

			else:
				core.GUI.crosshair.state = 1

			depth = 0.3 if core.firstPerson else 1
			vecTo = cam.worldPosition.copy()
			vecTo -= cam.worldOrientation.col[2]*(12*depth)

			interactRay = cam.rayCast(vecTo, prop="interact",
			 xray=True, mask=own.collisionMask)[0]

			if interactRay:				
				if "iStrings" in interactRay:
					checkName = interactRay["iStrings"]

				else: checkName = interactRay.name

				if checkName in displayStrings:
					displayName = strFromId(checkName, lang, True)
					if interactRay["interact"]: core.player["iTarget"] = interactRay

				else:
					displayName = ""
					if "OBJ:iTarget" in core.player:
						del core.player["OBJ:iTarget"]

				if core.GUI.pointer.text != displayName:
					core.GUI.onTextChange(displayName)

					if interactRay.meshes:
						_id = interactRay.name

						if "rune" in interactRay:
							if _id not in core.player.runes:
								core.player.registerNewRune(_id)
								interactRay.state = 2

								core.GUI.logEntry("Sigil added to lytheknics")
								

			else:
				if core.GUI.pointer.text != "":
					core.GUI.onTextChange("")

				if "OBJ:iTarget" in core.player:
					del core.player["OBJ:iTarget"]

				if not core.player.isAttacking and not enemyRay:
					core.GUI.crosshair["mode"] = "idle"

	else:
		own["mouseLook"] = False
		core.cont["lookAngle"] = [0,0]
		own.scene.active_camera.timeOffset = 5000.0

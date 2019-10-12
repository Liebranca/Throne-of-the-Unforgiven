#// 000. IMPORTS & NAMING
from dsm import gamepath, gamekeys, lymath, GUI, timeMult, camFOV, camFOV_fp
from dsm.buildings import d as buildings
from dsm.sky import onSkyChange
from bge.logic import addScene, getSceneList, LibLoad, LibNew, LibFree
from bge.logic import LibList, getTimeScale
from bge.logic import joysticks
from dsm.utils.lymath import lyprint, coneRay, iLerp
from dsm.classes._Landmass import Tectonics_queued

from mathutils import Vector
from math import radians, degrees
import numpy as np
import os

getEvent = gamekeys.getEvent
core = None; _Scene = None

def sunit(cont):
	own = cont.owner
	if "Sunguide" in own.scene.objects:
		own.setParent(own.scene.objects["Sunguide"])

#// 001.0 INIT ROUTINES: GAME
def onGameStart(cont):
	lyprint("LOADING FILES")

	try:
		verts = gamepath+"\\dsm\\cache\\landmass\\verts.npy"
		print( "%s" %(verts) )
		core.grid["verts"] = np.load(verts)

	except:
		core.grid["verts"] = np.ndarray( (41, 41), dtype=object )
		core.genVerts = True
	
	LibLoad(gamepath+"\\data\\nature\\trees.blend", "Scene", load_actions=True)
	LibLoad(gamepath+"\\data\\chars\\dummy.blend", "Scene", load_actions=True)
	LibLoad(gamepath+"\\data\\runes.blend", "Scene", load_actions=True)
	LibLoad(gamepath+"\\data\\building\\fireShrine\\fireShrine_a0.blend",
	 "Scene", load_actions=True)
	LibLoad(gamepath+"\\data\\building\\houses\\houses.blend",
	 "Scene", load_actions=True)

	LibLoad(gamepath+"\\data\\mapping\\moonGate\\moonGate_a0.blend", "Scene")

	addScene("UI", 1)
	addScene("FX", 1)
	addScene("Skydome", 0)

	own = cont.owner
	core.cont = own
	own["core"] = core
	own["lookAngle"] = [0,0]

	new_scene = _Scene.new(own.scene)
	core.joyIndex = gamekeys.joystick_init(own)

	core.joyPlugged = joysticks[core.joyIndex] != None

	own["time"] = ""
	own["date"] = ""
	own.addDebugProperty("time")
	own.addDebugProperty("date")

	own["underwater"] = False
	own["ingame"] = False

	new_scene.active_camera.fov = camFOV_fp if core.firstPerson else camFOV


def spawnPlayer(own):

	initLandmass()
	core.queues["addObject_mainScene"].append( {"obj":"Actor", "pos":[10,0,999],
			 "d":{"weight":4.0, "behaviour":"player"}, "kls":"actors"} )

	core.queues["addObject_mainScene"].append( {"obj":"latHouse_a0.wWall",
	"pos":[10,10,42], "d":{"weight":4.0, "worldKey":tuple(core.wOrigin)},
	 "kls":"statics"} )
	
	
	#core.queues["addObject_mainScene"].append( {"obj":"navTester", "pos":[0,-20,999],
	#		 "d":{"weight":4.0, "behaviour":"cowFucker"}, "kls":"actors"} )


#// 001.1 INIT ROUTINES: UI
def onGUIStart(cont):
	own = cont.owner
	new_scene = _Scene.new(own.scene)
	core.GUI = GUI(new_scene.active_camera)
	core.GUI.drawScreen("menus_main")

	sc = getSceneList()["Main"]
	sc.objects["Manager"].state = 2

	for libName in LibList():

		file = libName.replace(".blend","Info.txt")
		if os.path.exists(file):
			data = [line.rstrip('\n') for line in open(file)]
			lib = LibNew(libName+"_GUICOPY", "Mesh", data)
			core.GUI.meshDict.update( dict( zip( data, lib)) )

	LibLoad(gamepath+"\\data\\livepaint.blend", "Scene", scene="UI")
	LibLoad(gamepath+"\\data\\ui_meshes.blend", "Scene", scene="UI")
	lyprint("GAME STARTED")

	own.state = 2


#// 002.0 MAIN GAME LOOP
def managerUpdate(cont):
	own = cont.owner

	if not own["ingame"] and core.playerLog:
		own["ingame"] = True
		sc = getSceneList()["Main"]
		spawnPlayer(sc.objects["Manager"])
		sc.objects["camguide"]["mouseLook"] = False
		sc.objects["camguide"].state = 1

	core.worldTime.update( getTimeScale() + timeMult)
	own["time"] = core.worldTime.convert_read()
	own["date"] = core.worldTime.convert_calendar()

	own["fwd"], own["back"], own["up"], own["down"] = (getEvent("fwd")[0],
	 getEvent("back")[0], getEvent("up")[0], getEvent("down")[0])

	own["sright"], own["sleft"], own["sup"], own["sdown"] = (getEvent("sright")[0],
	 getEvent("sleft")[0], getEvent("sup")[0], getEvent("sdown")[0])

	own["zoomin"], own["zoomout"] = getEvent("zoomin")[0], getEvent("zoomout")[0]
	own["fire"], own["sheath"], own["sneak"] = (getEvent("fire")[0],
	getEvent("sheath")[1], getEvent("sneak")[1] )

	own["toggleRun"], own["use"] = getEvent("toggleRun")[1], getEvent("use")[1]

	own["charmenu"] = getEvent("charmenu")[1]
	own["toggleView"] = getEvent("toggleView")[1]
	if own["charmenu"]:
		core.GUI.resetMousePos()
		own["lookAngle"] = [0,0]

	if own["toggleView"]:
		core.toggleView()

	#hel_i = 0 if not core.GUI.mouseLook else 1
	#own["jump"] = getEvent("jump", not hel_i)[hel_i]

	own["jump"] = getEvent("jump")[0]
	own["joySens"] = getJoySens(own["fwd"], own["back"], own["up"], own["down"],
		own["sright"], own["sleft"], own["sup"], own["sdown"])

	own["joySens"][2] -= (own["lookAngle"][0])
	own["joySens"][3] += (own["lookAngle"][1])

	if own["lookAngle"][0]:
		own["sright"] += own["lookAngle"][0] < 0
		own["sleft"] += own["lookAngle"][0] > 0

	if own["lookAngle"][1]:
		own["sup"] += own["lookAngle"][1] > 0
		own["sdown"] += own["lookAngle"][1] < 0

	if core.queues["endObject_mainScene"]:
		toKill = core.queues["endObject_mainScene"].pop(0)
		batchKill_ufunc(toKill)

	elif core.queues["addObject_mainScene"]:
		toAdd = core.queues["addObject_mainScene"].pop(0)
		batchSpawn_ufunc(toAdd, own)

	elif core.fMapGen == 1 and core.player:
		core.fMapGen = 0

		core.GUI.bkgn["active"] = False
		core.GUI.bkgn.state = 1
		core.player.groundCheck()

	if core.queues["tasks"]:
		pointer, task, completion = core.queues["tasks"][0]
		func, args = eval(task[0]), task[1:]
		args_new = [None for i in range(len(args))]
		for i, arg in enumerate(args):

			if isinstance(arg, str):
				if pointer[0] + "." + pointer[1] in arg: 
					arg.replace(pointer[0] + "." + pointer[1],
					str(eval(pointer[0] + "." + pointer[1])))
				
				arg = eval(arg)
			
			args_new[i] = arg

		setattr(eval(pointer[0]), pointer[1], func(*args_new))
		core.taskTimer += 0.1

		if eval(completion):
			core.queues["tasks"].pop(0)
			core.taskTimer = 0.0

	w = own.scene.world
	if not core.player: onSkyChange("", w)

	else:
		if ( core.player.getIsUnderwater() and not own["underwater"] ):
			own["underwater"] = True
			onSkyChange("underwater", w)

		elif (not core.player.getIsUnderwater() and own["underwater"]):
			own["underwater"] = False

		if not own["underwater"]: onSkyChange("", w)

		scList = getSceneList()
		if "FX" in scList:
			doReflector(own, scList["FX"])

		own.scene.objects["playerLight"].color = w.mistColor
		own.scene.objects["playerLight"].energy = (
			(1.0 - own.scene.objects["Sun"].energy)*3)

def doReflector(own, sc):
	sc.objects["Sunguide"].worldOrientation = (
		own.scene.objects["Sunguide"].worldOrientation)
	
	sc.objects["camguide"].worldOrientation = (
			own.scene.objects["camguide"].worldOrientation)
	
	if not core.firstPerson:
		sc.objects["camguide"].worldPosition = (
			own.scene.objects["camguide"].localPosition)
	
	elif "Armature" in core.player.children:
		arma = core.player.children["Armature"]
		camPoint = arma.children["camPoint"]
		sc.objects["camguide"].worldPosition = camPoint.localPosition

	sc.objects["Sun"].energy = (
		own.scene.objects["Sun"].energy)

	sc.objects["Contrasun"].energy = (
		own.scene.objects["Contrasun"].energy)

	sc.objects["Contrasun"].worldOrientation = (
		own.scene.objects["Contrasun"].worldOrientation)

	sc.objects["Contrasun"].worldPosition = (
		own.scene.objects["Contrasun"].worldPosition)

	light = "Sun"
	reflector = sc.objects["reflector"]

	if sc.objects[light].energy <= 0:
		light = "Contrasun"

	sunpos = sc.active_camera.getScreenPosition(sc.objects[light])

	reflector.localPosition.z = (0.5 - sunpos[1])
	reflector.localPosition.x = -(0.5 - sunpos[0])
	cone = sum(coneRay(own.scene.active_camera.parent,
	 own.scene.objects[light], 5, True, core.player.worldPosition.z))
	if cone:
		col = reflector.color[0]
		mx = 1 - (0.125*(cone))
		f = 0.01*cone

		if col > mx:
			f = col-f
			if f < mx: f = mx
			reflector.color[0:3] = [f for i in range(3)]

		elif col < mx:
			f = col+f
			if f > mx: f = mx
			reflector.color[0:3] = [f for i in range(3)]

	elif reflector.color[0] < 1:
		col = reflector.color[0]
		f = 0.01

		if col < 1:
			f = min(col+f, 1)
			reflector.color[0:3] = [f for i in range(3)]

def batchKill(toKill):
	try: toKill.endObject()
	except: pass

batchKill_ufunc = np.frompyfunc(batchKill, 1, 0)

def batchSpawn(toAdd, own):
	if isinstance(toAdd, str): toAdd = core.objSuspended[toAdd]
	newObj = own.scene.addObject(**toAdd)
			
	if newObj.name == "player":		
		camguide = own.scene.objects["camguide"]
		core.player = player = newObj
		camguide.worldPosition = player.worldPosition
		camguide.worldPosition.z += player.cullingBox.max[2]/1.15

		camguide.setParent(player)

	del toAdd

batchSpawn_ufunc = np.frompyfunc(batchSpawn, 2, 0)

def getJoySens(fwd, back, up, down, sright, sleft, sup, sdown):

	joySens = [0,0,0,0]
	if joysticks[core.joyIndex] != None:
		joySens = joysticks[core.joyIndex].axisValues[0:4]
		joySens[1] = -joySens[1]; joySens[2] = -joySens[2]; joySens[3] = -joySens[3]

	if joySens == [0,0,0,0]:
		solveJoySens(joySens, fwd, back, up,
		 down, sright, sleft, sup, sdown)

	return joySens

def solveJoySens(joySens, fwd, back, up, down, sright, sleft, sup, sdown):

	if fwd:
		joySens[0] = 1
	elif back:
		joySens[0] = -1

	if up:
		joySens[1] = 1
	elif down:
		joySens[1] = -1

	if sright:
		joySens[2] = -1
	elif sleft:
		joySens[2] = 1

	if sup:
		joySens[3] = 1
	elif sdown:
		joySens[3] = -1


def initLandmass():
	for x in range(-2, 3):
		for y in range(-2, 3):
			core.queues["addObject_mainScene"].append( {"obj":"",
			"pos":[200*x, 200*y, 0], "d":{"cell":(x, y)}, "kls":"Terra"} )

#// 000. IMPORTS & NAMING
from bge.render import getFullScreen, getWindowWidth, getWindowHeight, getDisplayDimensions, setWindowSize
from bge.render import setMousePosition
from dsm import screens, camTurn, textRes
from dsm.utils.lymath import lyprint

core = None


#// 001. CLASS DEFINITION
class GUI:

	def __init__(self, cam):
		self.cam = cam

		self.windowSize = [1366,768]
		self.windowRes = [4, 4/(max(self.windowSize[0],
		 self.windowSize[1])/min(self.windowSize[0], self.windowSize[1]))]

		self.mousePos = [0,0]

		self.mouse = cam.scene.objects["cursor"]
		self.mouseRay = self.mouse.sensors["Ray"]
		self.pointer = cam.scene.objects["pointerText"]
		self.prompter = cam.scene.objects["prompterText"]
		self.log = cam.scene.objects["logPoint"]
		self.bkgn = cam.scene.objects["ui_background"]
		self.resbar = cam.scene.objects["RESBAR"]
		self.crosshair = cam.scene.objects["crosshair"]

		self.onSetResolution()
		self.currScreen = ""
		self.prevScreen = ""
		self.bindPick = "Empty"
		self.listOpen = None

		self.currScreen_objects = []
		self.bkgn.localScale.xy = self.windowRes

		self.mouseLook = False
		self.active_widget = None

		self.meshDict = {}
		
		pos = (-0.95, 0.90)
		x, y = pos; x, y = self.windowRes[0]*x, self.windowRes[1]*y
		self.log.worldPosition.xy = [x, y]

		pos = (0.0, 0.95)
		x, y = pos; x, y = self.windowRes[0]*x, self.windowRes[1]*y
		self.resbar.worldPosition.xy = [x, y]

		for child in self.resbar.children:
			child.resolution = textRes
			res = child.name.replace("resbar.", "")
			res = res.replace("count", "")
			child.text = str(core.teams[0]["resources"][res])

	def toggleResbar(self, value=-1):
		if value == -1: value = not self.resbar.visible
		self.resbar.visible = value
		for child in self.resbar.children:
			child.visible = value

	def logEntry(self, s):
		newText = self.cam.scene.addObject("defText")
		newText.worldPosition = self.log.worldPosition
		for child in self.log.children:
			child["move"] += 1.2
			child["fademult"] += 0.0025

		ootline = newText.children[0]

		ootline.text = newText.text = s
		ootline.size = newText.size = 0.275
		ootline.resolution = newText.resolution = textRes

		newText.setParent(self.log)

	def updateMouse(self):
		res, size, pos = self.windowRes, self.windowSize, self.cam.sensors["Mouse"].position
		pos = [max(0, pos[0]), max(0, pos[1])]

		new_pos = [(pos[0]/size[0])*res[0]*2, (-pos[1]/size[1])*res[1]*2]
		new_pos = [(new_pos[0]-res[0]), (new_pos[1]+res[1])]

		pos[0] -= int(core.cont["joySens"][2]*10); pos[1] -= int(core.cont["joySens"][3]*10)

		self.mousePos = self.mouse.worldPosition.xy = new_pos
		setMousePosition(*pos)

		self.mouse["frame"] = self.mouse.sensors["LClick"].positive or core.cont["jump"]

	def calcMouseLook(self):
		oldPos = list(self.mousePos)
		self.updateMouse()

		disVec = [0,0]

		if oldPos != self.mousePos:
			disVec = self.mousePos
			disVec[0] *= camTurn; disVec[1] *= camTurn*2
			self.resetMousePos()

		return disVec

	def resetMousePos(self):
		setMousePosition(int(getWindowWidth()/2), int(getWindowHeight()/2))

	def drawScreen(self, newScreen):

		showResbar = newScreen in ["menus_char", "building"]
		if not showResbar and self.resbar.visible:
			self.toggleResbar(False)
		elif showResbar and not self.resbar.visible:
			self.toggleResbar(True)

		self.wipeScreen()
		toLoad = screens[newScreen]

		widget_list = []

		for pos, obj in toLoad.items():
			new_object = self.cam.scene.addObject(obj[0], pos=pos, d=obj[1], kls="widgets")
			widget_list.append(new_object)

		self.currScreen = newScreen
		self.currScreen_objects = widget_list

	def raisePrompt(self, s, prompt):
		self.prevScreen = str(self.currScreen)
		self.drawScreen(prompt)
		self.onTextChange(s, "prompter")

	def wipeScreen(self):
		for ob in self.currScreen_objects:
			ob.endObject()

		self.listOpen = None

	def onTextChange(self, s, obName="pointer"):
		ob = self.__dict__[obName]
		ootline = ob.children[0]
		
		try:
			ootline.text = ob.text = s

		except: None
		self.adjustText(ob, obName)

	def adjustText(self, ob, obName):

		if obName == "pointer": pos = (0.0, -0.9)
		else: pos = (0.0, 0.9)
		ootline = ob.children[0]
		if ob.resolution < textRes:
			ootline.resolution = ob.resolution = textRes

		x, y = pos; x, y = self.windowRes[0]*x, self.windowRes[1]*y
		ob.worldPosition.xy = [x, y]

		x_fac = (len(ob.text)*0.075)
		ootline.size = ob.size = 0.375

		ob.worldPosition.x -= x_fac


	def onSetResolution(self):
		
		window_x, window_y = getWindowWidth(), getWindowHeight()
		lyprint("SETTING VIEWPORT")

		res_mult = max(window_x, window_y)/min(window_x, window_y)
		old_aspect = False

		if 1.34 < res_mult < 1.78:
			self.cam.ortho_scale = 10.0
		else:
			self.cam.ortho_scale = 8.0
			old_aspect = True

		display = getDisplayDimensions()
		unit = 0.5 * self.cam.ortho_scale
		resolution = [unit, unit/res_mult]

		if max(window_x, window_y) == window_y:
			resolution = resolution[::-1]
            
		self.windowSize = [window_x, window_y]
		self.windowRes = resolution

		left_view = max(window_x, display[0])-min(window_x, display[0])
		bottom_view = max(window_y, display[1])-min(window_y, display[1])
        
		if old_aspect:
			self.cam.setViewport(0, 0, window_x, window_y)
		else:
			self.cam.setViewport(0, 0, display[0], display[1])


def logText(cont):
	own = cont.owner
	mult = own["fademult"]
	own["timer"] += mult
	if own["timer"] < 3.0:
		own.color[3] = min(1.0, own.color[3]+mult)
		own.children[0].color[3] = min(1.0, own.color[3]+mult)

	elif own["timer"] > 6.0:
		own.color[3] = max(0.0, own.color[3]-mult)
		own.children[0].color[3] = max(0.0, own.color[3]-mult)

	if not own.color[3]: own.endObject()

	if own["move"]:
		own.applyMovement([0,-0.05, 0.0])
		own["move"] = max(0, own["move"]-0.2)

def bkgnFade(cont):
	own = cont.owner

	if own["active"]:
		if "init" not in own:
			_max = 1.0
			step = 0.075
		else:
			_max = 0.5
			step = 0.025

		condition = own.color[3] < 1.0
		action = "min(own.color[3]+%f, %f)"%(step, _max)

	else:
		condition = own.color[3] > 0.0
		if "init" not in own:
			step = 0.005
		else:
			step = 0.025

		action = "max(own.color[3]-%f, 0.0)"%step

	if condition: own.color[3] = eval(action)
	else:
		own.state = 2
		if "init" not in own and core.fMapGen:
			own["init"] = True
			own.worldPosition.z = -0.2

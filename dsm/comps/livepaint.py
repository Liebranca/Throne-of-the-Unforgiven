import bge
import numpy as np
from math import sqrt
from mathutils import Vector
import itertools

if not hasattr(bge, "__component__"):
	from dsm.gamekeys import getEvent, getJoyInput
	from dsm.utils.lymath import calcDistance
	from dsm import physRate, gamepath, displayStrings, lang

	texture = bge.texture

class canvas(bge.types.KX_PythonComponent):

	args = {"texname":"livepaint_canvas",
			"width":512, "height":512}
	def start(self, args):
		own = self.object		

		size_x, size_y =args["width"], args["height"]

		size = int(size_x*size_y)

		mat_id = texture.materialID(own,"MA"+args["texname"])
		tex = texture.Texture(own,mat_id)
		tex.source = texture.ImageBuff()

		buff = bytearray(size*3)
		tex_matrix = np.ndarray((size_y, size_x, 3), dtype=object)
		tex_matrix[0:] = 0

		self.mat = tex_matrix
		self.buff = buff
		self.size = [size_y, size_x]
		self.tex = tex

		self.checkTex = None
		self.hasCheck = False
		self.compTotal = 0
		self.held = 0.0
		self.filled = {}

		self.wait = False
		self.doTexUpdate = False
		self.rune = ""

		update_tex(tex, buff)
		own.state = 2

	def update(self):
		mainScene = bge.logic.getSceneList()["Main"]
		core = mainScene.objects["Manager"]["core"]		
		
		clipboard = self.object.children[0]
		if "filled" not in clipboard:
			self.rune = str(core.GUI.meshDict[core.player.drawRune])
			clipboard["filled"] = True

		if clipboard["filled"] and not self.hasCheck:
			self.hasCheck = True

			mat_id = texture.materialID(clipboard,"MArune_canvas")
			tex = texture.Texture(clipboard, mat_id)

			path = (gamepath
			+"\\data\\textures\\runes\\%s.png"%(self.rune)
			)

			tex.source = im = texture.ImageFFmpeg(path)
			im_buff = np.asarray(im.image)

			self.checkTex = np.ndarray((512, 512, 4))
			im_buff.shape = self.checkTex.shape
			self.checkTex[:] = im_buff

			self.compTotal = len(self.checkTex[self.checkTex[:,:,3] != 0])/1.095
			self.compTotal = self.compTotal + (self.compTotal*0.070)
			
			tex.refresh(True)
			clipboard["tex"] = tex

		elif self.hasCheck:

			cam = self.object.scene.active_camera

			mouseCol = core.GUI.mouseRay
			mousePos = cam.getScreenPosition(core.GUI.mouse)
			ray_vec = Vector([core.GUI.mousePos[0], core.GUI.mousePos[1], -10])
			ray = cam.rayCast(ray_vec, xray=True, prop="canvas")

			brush_radius = 10

			if ray[0] == self.object:
				size_y, size_x = self.size
				vecTo = core.GUI.mouse.getVectTo(self.object)
				pos = vecTo[1].xy * -vecTo[0]
				pos.x /= self.object.localScale.x
				pos.y /= self.object.localScale.y

				x, y = world_to_tex(*pos, size_y, size_x)
				origin = (y, x)

				square_bounds = ([
				max(0, x-brush_radius), min(x+brush_radius, size_x),
				max(0, y-brush_radius), min(y+brush_radius, size_y-1),
				])
				
				if core.GUI.mouse["frame"]:
					for co in gen_squareRange(*square_bounds):
						dist = calcDistance(*origin[::-1], *co[::-1])
						f = (dist/brush_radius)*6

						if (dist < brush_radius) and self.mat[co][0] < int(255-f):
							col = min( 255, self.mat[co][0] + int( 255 - f ))

						else:
							col = self.mat[co][0]

						col = self.compToClipboard(co, col)
						if col: self.mat[co] = [col,col,col]

					
					col = self.compToClipboard(co, 255)
					if col: self.mat[origin] = [col,col,col]

					self.doTexUpdate = True
					percent = int( (min(len(self.filled), self.compTotal)/self.compTotal)*100)
					tt = ("%d/100"%(percent))

					core.GUI.onTextChange(tt)
					if col != 255: self.held += 0.1

				else: self.held = 0.0

		if self.doTexUpdate and not self.wait:
			self.doTexUpdate = False
			
			self.buff[0:] = np.ravel(self.mat).tolist()
			update_tex(self.tex, self.buff)
			mastery = core.player.runes[self.rune]

			if self.hasCheck:
				percent = int( (min(len(self.filled), self.compTotal)/self.compTotal)*100)
				tt = ("%d/100"%(percent))

				core.player.runes[self.rune] += max(0, percent-mastery)

			else:
				tt = "Complete"
				if 100 >= mastery:
					spellname = displayStrings[self.rune]
					spellname = spellname[lang if lang in spellname else "eng"]					
					core.GUI.logEntry( "Sigil deciphered -- %s"%(spellname) )

				core.player.runes[self.rune] += max(0, 100-mastery)

			core.GUI.onTextChange(tt)
			self.wait = True

		else:
			self.wait -= 0.5
			if self.wait <= 0.0: self.wait = False		

	def compToClipboard(self, co, col):
		
		if not self.checkTex[co][3] == 0.0:
			self.filled[co] = True
			if len(self.filled) >= self.compTotal:
				self.hasCheck = False
				self.object.children[0]["filled"] = False

			return col

		else:
			if self.held > 10 and len(self.filled) > 1:
				key = next(iter(self.filled))
				self.mat[key] = [0,0,0]
				del self.filled[key]

				self.held -= 0.25

			return 0

#// 000.1 MISC FUNCS
def gen_squareRange(start_x, end_x, start_y, end_y):
	return [(ry, rx) for rx in range(start_x, end_x) for ry in range(end_y, start_y, -1)]

def world_to_tex(x, y, size_y, size_x):
	x = round( (size_x/2) + (x*(size_x/2)) )
	y = round( (size_y/2) + (y*(size_x/2)) )

	return max(0, min(x, size_x-1)), max(0, min(y, size_y-1))

def update_tex(tex, buff, buff_size=False):
	if not buff_size: buff_size = int(sqrt(len(buff)/3 ) )
	tex.source.load(buff, buff_size, buff_size)
	tex.refresh(True)
	return tex

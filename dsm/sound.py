from random import randint, uniform
core = None

d = {
	"cutFX": ["cutFX_sound", "cutFX2_sound"],
	"swingFX":["swingFX_sound","swingFX1_sound", "swingFX2_sound"],
	"treeHT":["treeHT_sound", "treeHTalt_sound"],
	"rockHT":["rockHT_sound", "rockHTalt_sound"],
	"woodPU": ["woodPU_sound", "woodPUalt_sound"],
	"rockPU": ["rockPU_sound", "rockPUalt_sound"],
	"goldPU": ["goldPU_sound", "goldPUalt_sound"],
	}

def fx(cont):
	own = cont.owner
	duplis = len(own.scene.objects.filter(own.name))

	s = own.actuators["Sound"]
	s.volume *= core.settings["fx_volume"]

	if "pitchMod" in own:
		s.pitch = max( 1, min(3, duplis*own["pitchMod"]) )

	cont.activate(s)
	s.startSound()

	if "skip" in own:
		s.time += own["skip"]

def pick_random(cont):
	own = cont.owner

	if "soundAdd" not in own:
		own["soundAdd"] = True
		l = d[ own["soundPool"] ]
		sfx = l[randint(0, len(l)-1)]
		sd = {"obj":sfx, "pos": own.worldPosition.copy(),
		 "life":own.scene.objectsInactive[sfx]["dur"]}

		newSound = own.scene.addObject(**sd)

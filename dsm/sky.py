from dsm import skyColor, color_ops, GUI, lymath
from bge.logic import getSceneList, getTimeScale
from math import radians

core = None

def skyLerp(t1, t2, l, p, sk):
	sk[0] = [0,0,0]
	sk[0][0] = lymath.iLerp(skyColor[t1][0][0], skyColor[t2][0][0],
	 l, p)
	sk[0][1] = lymath.iLerp(skyColor[t1][0][1], skyColor[t2][0][1],
	 l, p)
	sk[0][2] = lymath.iLerp(skyColor[t1][0][2], skyColor[t2][0][2],
	 l, p)

	sk[1] = lymath.iLerp(skyColor[t1][1], skyColor[t2][1],
	 l, p)
	sk[2] = lymath.iLerp(skyColor[t1][2], skyColor[t2][2],
	 l, p)
	sk[3] = lymath.iLerp(skyColor[t1][3], skyColor[t2][3],
	 l, p)
	sk[4] = lymath.iLerp(skyColor[t1][4], skyColor[t2][4],
	 l, p)

def onSkyChange(n, w):
	if n == "":
		sk = [i for i in range(5)]
		
		timeco = ( core.worldTime.hour + (core.worldTime.min*0.0168) )

		if 17 > core.worldTime.hour >= 8:
			sk = skyColor["day"]

		elif 19 > core.worldTime.hour >= 17:
			p = timeco - 17
			l = 2
			skyLerp("day", "dusk", l, p, sk)

		elif 21 > core.worldTime.hour >= 19:
			p = timeco - 19
			l = 2
			skyLerp("dusk", "dawn", l, p, sk)

		elif 24 > core.worldTime.hour >= 21:
			p = timeco-21
			l = 3
			skyLerp("dawn", "night", l, p, sk)

		elif 3 > core.worldTime.hour >= 0:
			sk = skyColor["night"]

		elif 5 > core.worldTime.hour >= 3:
			p = timeco-3
			l = 2
			skyLerp("night", "dawn", l, p, sk)

		elif 6 > core.worldTime.hour >= 5:
			p = timeco-5
			l = 1
			skyLerp("dawn", "dusk", l, p, sk)

		elif 8 > core.worldTime.hour >= 6:
			p = timeco - 6
			l = 2
			skyLerp("dusk", "day", l, p, sk)

		

	else:
		sk = skyColor[n]

	w.horizonColor[0:3] = color_ops.lighten(*sk[0], 0.05)
	w.zenithColor[0:3] = sk[0]
	w.mistColor = w.horizonColor[0:3]
	w.mistStart, w.mistDistance, w.mistIntensity = sk[1:4]
	w.envLightEnergy = sk[4]

def skySync(w1, w2):
	w1.horizonColor = w2.horizonColor
	w1.zenithColor = w2.zenithColor
	w1.mistColor = w2.mistColor
	w1.mistStart, w1.mistDistance, w1.mistIntensity = (w2.mistStart,
		 w2.mistDistance, w2.mistIntensity)

	w1.envLightEnergy = w2.envLightEnergy

def skydomeCam(cont):

	sc = getSceneList()["Skydome"]
	dople = sc.objects["dome_camguide"]
	dople.worldOrientation = cont.owner.worldOrientation
	dople.worldPosition = cont.owner.localPosition
	w1, w2 = cont.owner.scene.world, sc.world

	sc.active_camera.timeOffset = cont.owner.scene.active_camera.timeOffset
	sc.active_camera.fov = cont.owner.scene.active_camera.fov

	skySync(w2, w1)
	dome = sc.objects["skydome"]
	stars = sc.objects["stardome"]
	sun = sc.objects["sun"]
	moon = sc.objects["moon"]
	contrasun = cont.owner.scene.objects["Contrasun"]

	white = [1,1,1,1]; grey = [0.15,0.15,0.15, 0.15]; black = [0,0,0,0]
	domewhite = [1,1,1,1]
	timeco = ( core.worldTime.hour + (core.worldTime.min*0.0168) )
	sunlight = cont.owner.scene.objects["Sun"]
	sunflex = sc.objects["sunflex"]

	if (8 > core.worldTime.hour >= 5):
		p = timeco - 5
		a, b = grey, white
		l = 3

		for i in range(3):
			dome.color[i] = lymath.iLerp(a[i], domewhite[i], l, p)

		for i in range(3):
			stars.color[i] = lymath.iLerp(grey[i], black[i], l, p)
			moon.color[i] = lymath.iLerp(grey[i], black[i], l, p)

	elif (18 > core.worldTime.hour >= 8):
		dome.color = domewhite
		moon.color = stars.color = black
		stars.visible = False
		moon.visible = False

	elif (20 > timeco >= 18):
		p = timeco - 18
		a, b = white, grey
		l = 2

		stars.visible = True
		moon.visible = True

		for i in range(3):
			dome.color[i] = lymath.iLerp(domewhite[i], b[i], l, p)

		for i in range(3):
			stars.color[i] = lymath.iLerp(black[i], grey[i], l, p)
			moon.color[i] = lymath.iLerp(black[i], grey[i], l, p)

	elif (5 > core.worldTime.hour >= 0) or (24 > core.worldTime.hour >= 20):
		dome.color = grey

		if 24 > core.worldTime.hour >= 20:
			p = timeco - 20
			a, b = grey, white
			l = 4
			for i in range(3):
				stars.color[i] = lymath.iLerp(a[i], b[i], l, p)
				moon.color[i] = lymath.iLerp(a[i], b[i], l, p)

		elif (5 > core.worldTime.hour >= 0):
			p = timeco
			a, b = white, grey
			l = 5
			for i in range(3):
				stars.color[i] = lymath.iLerp(a[i], b[i], l, p)
				moon.color[i] = lymath.iLerp(a[i], b[i], l, p)

	dome.applyRotation([0,0,( radians(0.0015*getTimeScale()) )])
	stars.visible = stars.color[0] > 0.25
	if stars.visible: stars.applyRotation([0,0,( radians(0.003*getTimeScale()) )])

	yellow = [1, 1, .365]; orange = [1, .1, 0]

	sunway = lymath.iLerp(180, -180, 24, timeco)
	sun.worldOrientation = [0, radians(sunway), 0]
	sunlight.color = sun.color[0:3]

	cont.owner.scene.objects["Sunguide"].worldOrientation = sun.worldOrientation

	if 20 > core.worldTime.hour >= 5:
		sun.visible = True
		p = timeco-5
		l = 15

		sunrise = 9 > core.worldTime.hour >= 5; sundown = 20 > core.worldTime.hour >= 16
		if abs(sunway) >= 80:
			sun["frame"] = (sunway+20) - 90 if sunway > 0 else abs(90 + (sunway-10))

		elif sun["frame"] > 0: sun["frame"] -= 0.1*getTimeScale()

		if sunrise or sundown:
			l = 4
			p = timeco-5 if sunrise else timeco-16
			a, b = yellow if sundown else orange, orange if sundown else yellow

			for i in range(3):
				sun.color[i] = lymath.iLerp(a[i], b[i], l, p)

			a, b = 0.0 if sunrise else 1, 1 if sunrise else 0.25
			sunlight.energy = lymath.iLerp(a, b, l, p)			

	else:
		if sun["frame"] > 0: sun["frame"] -= 0.1*getTimeScale()
		else: sun.visible = False
		
		if sunlight.energy > 0.0:
			sunlight.energy -= 0.01*getTimeScale()

	moonphase = core.worldTime.moonphase + (core.worldTime.hour*0.042)
	if not moon.visible: moon["frame"] = moonphase/7

	moonway = lymath.iLerp(0, 360, 64, moonphase)
	moon.worldOrientation = [0,0, radians(moonway)]
	
	contrasun.worldOrientation = [radians(-73.5), 0, radians(moonway)]
	contrasun.worldPosition = sc.objects["contrasunPos"].worldPosition
	contrasun.energy = moon.color[0]

from bge import logic, events
core = None

key_dict = {"fire":"LEFTMOUSE", "r_click":"RIGHTMOUSE",
			"zoomin":"WHEELUPMOUSE", "zoomout":"WHEELDOWNMOUSE",
			"toggleView":"FKEY",
			"fwd":"DKEY", "back":"AKEY", "up":"WKEY", "down":"SKEY",
			"jump":"SPACEKEY", "sneak":"LEFTCTRLKEY",
			"toggleRun":"LEFTSHIFTKEY", "use":"EKEY",
			"charmenu":"TABKEY", "sheath":"RKEY",
			"sright":"RIGHTARROWKEY","sleft":"LEFTARROWKEY",
			"sup":"UPARROWKEY","sdown":"DOWNARROWKEY"}

joy_dict = {"jump":0, "fire":9, "sheath":"L2", "sneak":8, "toggleRun":7,
			"charmenu":4, "use":1, "toggleView":4,
			"fwd":15, "back":16, "down":17, "up":18,
			"sleft":19, "sright":20, "sdown":21, "sup":22}

helKeys = ["fwd", "back", "down", "up",
			"sleft", "sright", "sdown", "sup",
			"zoomin", "zoomout"]

devices = {"k":logic.keyboard, "m":logic.mouse}

def getEvent(key_index, force_hel=False):

	device_index="k"
	if "MOUSE" in key_dict[key_index]:
		device_index = "m"

	device = devices[device_index]
	key = device.inputs[events.__dict__[key_dict[key_index]]]

	if key_index in helKeys or force_hel:
		joyHel = getJoyInput(key_index) if core.joyPlugged else False
		if not key.inactive: return key.active or joyHel, key.activated, key.released
		return key.active or joyHel, key.activated, key.released

	else:
		joyTap = getJoyButton(joy_dict[key_index], True) if core.joyPlugged else False
		if not key.inactive: return (key.active, key.activated or joyTap, key.released)
		return key.active, key.activated or joyTap, key.released

def getEventStatus(key_index):
	return core.cont[key_index]

def getEvent_fromKeycode(keycode, device_index="k"):
	if "MOUSE" in keycode:
		device_index = "m"

	device = devices[device_index]
	key = device.inputs[events.__dict__[keycode]]

	if not key.inactive: return key.active, key.activated, key.released
	return False, key.activated, key.released

def key_remap(index, new_key):
	key_dict[index] = new_key

def getJoyInput(key_index, getSens=False):
	key = joy_dict[key_index] if key_index in joy_dict else -1
	if isinstance(key, str):
		return core.cont.sensors[ joy_dict[key_index] ].positive
	elif key >= 0:
		if key >= 15: return getJoyAxis(key, getSens)
		else: return getJoyButton(key)

	return False

def getJoyButton(key, tap=False):
	joy = logic.joysticks[core.joyIndex]
	events = joy.activeButtons

	if key in events:
		if key not in core.joyLastFrame:
			core.joyLastFrame.append(key)
			return True

		else:
			return not tap

	else:
		if key in core.joyLastFrame:
			core.joyLastFrame.remove(key)
			return not tap

		else:
			return False


def getJoyAxis(key, getSens):
	joy = logic.joysticks[core.joyIndex]
	axis = joy.axisValues[0:4]

	if key < 17: index = 0
	elif key < 19: index = 1
	elif key < 21: index = 2
	else: index = 3

	if axis[index]:
		
		if getSens: return axis[index]

		if key%2:
			return axis[index] > 0

		return axis[index] < 0

	return False

def joystick_init(own):

	L2 = own.sensors["L2"]
	R2 = own.sensors["R2"]
	BUTT = own.sensors["BUTT"]

	for index in range(0, 7):
		L2.index = index

		if L2.connected and logic.joysticks[index]:
			R2.index = index
			BUTT.index = index

	if L2.index != R2.index: L2.index = R2.index
	return R2.index

	"""
	if joy:
		events = joy.activeButtons
		axis = joy.axisValues[0:4]
		mx, my = axis[0:2]

		if 9 in events: print("L1")
        if L2.positive: print("L2")
        if 7 in events: print("L3")
        
        if 10 in events: print("R1")
        if R2.positive: print("R2")
        if 8 in events: print("R3")
        
        if 0 in events: print("X")
        if 1 in events: print("O")
        if 2 in events: print("N")
        if 3 in events: print("A")
        
        if 11 in events: print("UP")
        if 12 in events: print("DOWN")
        if 13 in events: print("LEFT")
        if 14 in events: print("RIGHT")
        
        if 4 in events: print("SELECT")
        if 6 in events: print("START")
	"""

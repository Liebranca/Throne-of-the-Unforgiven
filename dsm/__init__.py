#// 000. IMPORTS & NAMING
from dsm.utils import lymath, color_ops
lymath.lyprint( "DSM")
from math import radians, sqrt
from mathutils import Vector, kdtree
import numpy as np

#// 000.1 DEFINE GAMEPATH
import sys
import os

gamepath = os.path.dirname(os.path.abspath(__file__)).replace("\\dsm", "")
if gamepath+"\\comps\\" not in sys.path: sys.path.append(gamepath+"\\comps\\")

#// 000.2 CONSTANTS
from dsm import lang as displayStrings
strFromId = displayStrings.strFromId
displayStrings = displayStrings.d

lang = "eng"

timeMult = 0.15
physRate = 20
physClamp = 0.45
camTurn = 2.5
camFOV = 82.5
camFOV_fp = 112.5
animRate = 0.10

waterLevel = -4

textRes = 2.0
showDebug = True

actorColMask = sum([2**g for g in (0,1,2,8)])

skyColor = { "day":[Vector([0.6, 0.748, 1.0]), 350, 45, 0.005, 0.25 ],
			"dusk":[Vector([0.6, 0.2, 0.2]), 350, 45, 0.0075, 0.4 ],
			 "night":[Vector([0.0, 0.2, 0.6]), 350, 45, 0.01, 1 ],			 
			 "dawn":[Vector([0.2, 0.3, 0.7]), 350, 45, 0.0075, 0.4 ],

			 "underwater":[Vector([0.420, 0.763, 1.0]), 0, 50, 0.25, 1 ] }

armorKeys = ["body", "legs", "chest", "feet", "shoulders", "hands", "head"]

from dsm.resists import damageFunc


#// 000.3 NAMESPACE
from dsm import screens
screens = screens.d

from dsm.classes import _Time, _GUI
Time = _Time.Time
GUI = _GUI.GUI

from dsm.classes import _Manager
core = _Manager.Manager()

from dsm import apparel, ans
apparel = apparel.d; ans = ans.d

from dsm.classes import _Obj, _Scene, _Landmass, _EquipMesh, _AOE
_Scene.core = _Obj.core = _Landmass.core = core; _AOE.core = core

from dsm import gamekeys, fkk
gamekeys.core = core; fkk.core = core

fkk._Scene = _Scene

from dsm.classes import _ActorValue
from dsm.classes import _Actor, _Armature, _Widgets
_Actor.core = core; _Widgets.core = core; _GUI.core = core
_Armature.core = core

_Obj.Stat = _ActorValue.Stat; _Actor.Stat = _ActorValue.Stat

_Scene.klsDict["statics"] = _Obj; _Scene.klsDict["actors"] = _Actor
_Scene.klsDict["Terra"] = _Landmass; _Scene.klsDict["armatures"] = _Armature
_Scene.klsDict["widgets"] = _Widgets; _Scene.klsDict["fx"] = _AOE

from dsm import sky, ui_cam, sound
sky.core = core; ui_cam.core = core; sound.core = core

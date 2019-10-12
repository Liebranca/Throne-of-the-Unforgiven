import sys, bpy

cwd = bpy.path.abspath("//")

if cwd not in sys.path:
	sys.path.append(cwd)

gamepath = cwd.replace("\\data","")
if gamepath not in sys.path:
	sys.path.append(gamepath)

_evil = gamepath+"\\_evil\\"
if _evil not in sys.path:
	sys.path.append(_evil)
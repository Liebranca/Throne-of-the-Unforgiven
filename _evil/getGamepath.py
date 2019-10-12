import sys
from pathlib import Path
from bpy.path import abspath

gameKey = "Throne of the Unforgiven"
libKey = "dsm"

curr = abspath('//')
s = curr.split('\\')

if s:
	if not s[-1]: s.pop(-1)
	if s and s != gameKey: s.pop(-1)

s = s[::-1]
dir = None
for i, parent in enumerate(Path(curr).parents):
	if s[i] == gameKey:
		dir = str(parent)
		break

if dir:
	dsmpath = dir+"\\"+libKey
	if dsmpath not in sys.path:
		sys.path.append(dsmpath)
		
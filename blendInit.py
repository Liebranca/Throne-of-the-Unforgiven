import sys
from os import path as os_path

gamepath = os_path.dirname(os_path.abspath(__file__)).replace("\\THRONE.blend", "")

if gamepath not in sys.path:
    sys.path.append(gamepath)

if gamepath+"\\dsm\\comps\\" not in sys.path:
    sys.path.append(gamepath+"\\dsm\\comps\\")


import bpy, os

cwd = bpy.path.abspath("//")

def writeMeshNames(cont):
	path = cwd
	filename = bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend","Info.txt")
	file = path+filename

	open(file, "w+")
	meshList = open(file,"a")

	for ob in bpy.context.scene.objects:
		if ob.type == "MESH" and "ui" in ob.game.properties:
			meshName = ob.data.name			
			meshList.write(meshName+"\n")

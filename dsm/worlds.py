from dsm.buildings import d as buildings

#cruelty size -- x:224, y:124
#startY, startX, level, lenY, lenX, falloff, vertY, vertX, m, worldY, worldX, terraKey

cruelty = {
	
	"cellDict":{
		#(155,55):{ "heightMap":[], "seed":0,
		#"objects":buildings["fireShrine"],
		#"init":False }
	},

	"terraform":{},

	#	"moonGate":[
	#		["[7, 7, 40, 720, 720, 2, 22, 22, 0, 55, 155, 'mountCircle']",
	#		"[14, 1, -40, 720*2, 10, 2, 22, 22, m, 55, 155,'river_aY']"],
	#		[ (x,y) for x in range(155-6, 155+6) for y in range(55-12, 55+12) ]
	#		],

	#	"moonBay":[
	#		["[7, 7, -40, 720, 720, 2, 22, 22, 0, 65, 155, 'bayCircle']"],
	#		[ (x,y) for x in range(155-6, 155+6) for y in range(65-6, 65+6) ]
	#		]

	"cellGen":{}

}

"""
for key, value in cruelty["terraform"].items():
	for pos in value[1]:
		if pos not in cruelty["cellGen"]:
			cruelty["cellGen"][pos] = []

		cruelty["cellGen"][pos].append(key)
"""

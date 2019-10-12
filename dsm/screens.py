d = {
	
	"":{},

	"menus_main":{
		(-0.75, 0.4):["ui_button", {"kls":"def", "text":"Play", "script":["newGame", {}] }],
	},

	"menus_char":{
		(0.0,0.0):["ui_wheel", {"kls":"PickWheel", "op1":"Clothing", "op2":"Weapons",
		"op3":"Lytheknics", "op4":"Character", "op5":"Building", "op6":"",
		"op7":"", "op8":"", "mode":"menu"}]
	},

	"building":{
		(-0.98, 0.8):["ui_backArrow", {"kls":"def",
		"script":["screenChange",{"newScreen":"menus_char"}] }]
	},

	"clothing":{
		(-0.95, 0.90):["ui_fetcher", {"kls":"WList", "text":"Inventory",
		"items":"core.player.children['Armature'].getInvSlots() + core.player.getInvSlots()",
		"adjust":"armorKeys", "script":["listToggle", {} ]}],
		
		(-0.98, 0.8):["ui_backArrow", {"kls":"def",
		"script":["screenChange",{"newScreen":"menus_char"}] }]
	},

	"lytheknics":{
		(-0.95, 0.90):["ui_fetcher", {"kls":"WList", "text":"Sigils",
		"items":"core.player.getSeenRunes()",
		"adjust":"[]",
		"script":["listToggle", {} ]}],

		(-0.95, 0.80):["ui_fetcher", {"kls":"WList", "text":"Cantrips",
		"items":"[]",
		"adjust":"[]",
		"script":["listToggle", {} ]}],

		(-0.95, 0.70):["ui_fetcher", {"kls":"WList", "text":"Prayers",
		"items":"[]",
		"adjust":"[]",
		"script":["listToggle", {} ]}],

		#(-0.4, -0.90):["ui_icoRow", {"kls":"icoRow", "length":8,
		#"linkTo":"core.player.spells", "idRoot":"spellbar"}],
		
		(-0.98, 0.6):["ui_backArrow", {"kls":"def",
		"script":["screenChange",{"newScreen":"menus_char"}] }]
	},

	"spellwheel":{
		(0.0,0.0):["ui_wheel", {"kls":"PickWheel", "op1":"core.player.spells[0]",
		"op2":"core.player.spells[1]", "op3":"core.player.spells[2]",
		"op4":"core.player.spells[3]", "op5":"core.player.spells[4]",
		"op6":"core.player.spells[5]", "op7":"core.player.spells[6]",
		"op8":"core.player.spells[7]", "mode":"bind", "bindTo":"core.player.spells"}]
	},

	"spellpaint":{
		(0,0):["livepaint_canvas", {"kls":"def"}],

		(-0.98, 0.9):["ui_backArrow", {"kls":"def",
		"script":["screenChange",{"newScreen":"lytheknics"}] }]
	}
}

d = {
	"equipSlot":{"eng":"--"},
	"maleHead":{"eng":"--"},
	"maleHands":{"eng":"--"},
	"maleFeet":{"eng":"--"},

	"body":{"eng":"Body"},
	"legs":{"eng":"Legs"},
	"hands":{"eng":"Hands"},
	"head":{"eng":"Head"},
	"chest":{"eng":"Chest"},
	"feet":{"eng":"Feet"},
	"shoulders":{"eng":"Shldr"},
	"maleBody":{"eng":"Underpants"},

	"pants_a0":{"eng":"Pants"},
	"jacket_a0":{"eng":"Jacket"},
	"boots_a0":{"eng":"Boots"},
	"shold_a0":{"eng":"Pauldrons"},
	"gloves_a0":{"eng":"Gloves"},
	"helm_a0":{"eng":"Helmet"},

	"fwenn":{"ohj":"ý", "eng":"Fire"},

	"magic_brazier":{"eng":"Stone Brazier"},
	"magic_brazier.onFail":{"eng":"You must draw a specific sigil to light this brazier"},

	"slide_curtain":{"eng":"Slide curtain"}
	
	}

def strFromId(_id, lang, doOhj=False):
	return d[_id]["ohj" if "ohj" in d[_id] and doOhj else lang if lang in d[_id] else "eng"]

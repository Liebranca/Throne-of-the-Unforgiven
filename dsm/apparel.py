actorBodyParts = ({"ds_torso":0, "ds_pelvis":1, "ds_head":2, "ds_neck":3, "ds_face":4,
				   "ds_upArm.L":5, "ds_upArm.R":6, "ds_foArm.L":7, "ds_foArm.R":8,
				   "ds_hand.L":9, "ds_hand.R":10, "ds_thigh.L":11, "ds_thigh.R":12,
				   "ds_calf.L":13, "ds_calf.R":14, "ds_foot.L":15, "ds_foot.R":16,
				})

hideLegs = {1:0, 11:0, 12:0, 13:0, 14:0}
hideTopFullArms = {0:0, 5:0, 6:0, 7:0, 8:0}
hideCalvesFeet = {13:0, 14:0, 15:0, 16:0}
hideFoArmsHands = {7:0, 8:0, 9:0, 10:0}
hideHands = {9:0, 10:0}
hideHead = {2:0}
hideFaceHead = {2:0, 4:0}
fpv = {0:0, 2:0, 3:0, 4:0}

d = {
	"fpv":fpv,

	"pants_a0":{"slotData":hideLegs},
	"jacket_a0":{"slotData":hideTopFullArms},
	"boots_a0":{"slotData":hideCalvesFeet},
	"shold_a0":{"slotData": {} },
	"gloves_a0":{"slotData": hideHands},
	"helm_a0":{"slotData": hideFaceHead},

	}
defLoop = { "attr":{"frameStart":0, "frameEnd":6, "blendIn":1},
		 "spec":{"frameActive":0, "hold":False}
		 }

defTrans = { "attr":{"frameStart":0, "frameEnd":6, "blendIn":3},
		 "spec":{"frameActive":0, "hold":False}
		 }

defTransHold = { "attr":{"frameStart":0, "frameEnd":6, "blendIn":3},
 		"spec":{"frameActive":0, "hold":True}
 		 }

longTransHold = { "attr":{"frameStart":0, "frameEnd":8, "blendIn":3},
 		"spec":{"frameActive":0, "hold":True}
 		 }

defRepHold = { "attr":{"frameStart":0, "frameEnd":6, "blendIn":1},
 		"spec":{"frameActive":0, "hold":True}
 		 }

defChop = { "attr":{"frameStart":0, "frameEnd":4, "blendIn":1},
	 	"spec":{"frameActive":3, "hold":True}
	 	 }

defShoot = { "attr":{"frameStart":0, "frameEnd":5, "blendIn":1},
	 	"spec":{"frameActive":3, "hold":True}
	 	 }

d = {
	"reroute":{"_run":"_run", "_rsn":"_rsneak",
	 "_wal":"_walk", "_walWep":"_walkWep",
	 "_jum":"_jump", "_att":"_att"},

	"mGent":
		{

			".def":{
				"_idle":defTrans,
				"_idleWep":defTrans,
				"_walk":defTrans,
				"_walkWep":defTrans,
				"_run":defTrans,
				"_runLeft":defTrans,
				"_runRight":defTrans,

				"_sneak":defTrans,
				"_rsneak":defTrans,

				"_att":defChop,
				"_draw":defTransHold,

			},

			".sw0a_in":{
				"_idle":defTrans,
				"_walk":defTrans,
				"_run":defTrans,
				"_runLeft":defTrans,
				"_runRight":defTrans,

				"_sneak":defTrans,
				"_rsneak":defTrans,
				"_rsneakLeft":defTrans,
				"_rsneakRight":defTrans,
			},

			".ps0a":{
				"_run":defTrans,
				"_att":defShoot,	

				"_idleWep":defTrans,
				"_walkWep":defTrans,

				"_draw":longTransHold,			
			},

			".sw0a":{
				"_idleWep":defTrans,

				"_walkWep":defTrans,
				"_run":defTrans,
				"_runRight":defTrans,
				"_runLeft":defTrans,

				"_sneak":defTrans,
				"_rsneak":defTrans,
				"_rsneakLeft":defTrans,
				"_rsneakRight":defTrans,

				"_att":defChop,
				"_attLeft":defChop,
				"_attRight":defChop,
				"_attBack":defChop,

				"_draw":defTransHold

			},

			".base":{
				"_idle":defLoop,
				"_idleWep":defLoop,

				"_walk":defLoop,

				"_walkWep":defLoop,
				"_walkWepBack":defLoop,

				"_run":defLoop,
				"_runRight":defLoop,
				"_runLeft":defLoop,

				"_jump":defRepHold,
				"_jumpMove":defRepHold,
				"_jumpMoveRight":defRepHold,
				"_jumpMoveLeft":defRepHold,

				"_air":defLoop,
				"_airRight":defLoop,
				"_airLeft":defLoop,

				"_sneak":defLoop,
				"_rsneak":defLoop,
				"_rsneakRight":defLoop,
				"_rsneakLeft":defLoop,
				"_rsneakBack":defLoop

			}

		}
	}
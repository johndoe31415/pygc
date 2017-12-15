#!/usr/bin/python3
#
#

import geo
import cwrap
import gcwidget
from GCGTKApplication import GCGTKApplication
from GlutApplication import GlutApplication

res = 720
config = {
	"screen_dimension":	geo.Vector2d(res * 16 // 9, res),
}

instrument_data = {
	"pos": {
		"heading_deg":		128,
		"altitude_ft":		12345,
		"pitch_angle_deg":	10,
		"roll_angle_deg":	10,
		"tas":				123,
		"ias":				0,
	},
	"ap": {
		"hdgbug_deg":		90,
	},
	"vor1": {
		"obs":				72,
		"deviation_deg":	0.5,
	},
	"freq": {
		"com1": {
			"active":	118.8,
			"stby":		118.6,
		},
		"com2": {
			"active":	121.5,
			"stby":		122.8,
		},
		"nav1": {
			"active":	109.9,
			"stby":		110.9,
		},
		"nav2": {
			"active":	113.25,
			"stby":		112.95,
		},
	},
	"xpdr": {
		"squawk":			7003,
	},
	"ias_bars": {
		"white":			[0, 100],		# flaps permitted until V_FE
		"red":				[0, 60],		# stall speed V_S
		"green":			[60, 150],		# design maneuvering speed
		"yellow":			[150, 220],		# maximum structural crusining speed V_NO to never exceed
		"redwhite":			[220, 9999],	# never exceed V_NE
	},
}

def modify_data():
	instrument_data["pos"]["heading_deg"] = (instrument_data["pos"]["heading_deg"] + 0.5) % 360
	instrument_data["pos"]["roll_angle_deg"] = (instrument_data["pos"]["roll_angle_deg"] + 0.5) % 360
	instrument_data["pos"]["ias"] += 0.13
	instrument_data["vor1"]["obs"] = (instrument_data["vor1"]["obs"] + 1.13) % 360
	instrument_data["ap"]["hdgbug_deg"] = (instrument_data["ap"]["hdgbug_deg"] - 0.75) % 360

#glasscockpit = gcwidget.GlassCockpit(config, context_class = cwrap.CairoContext)
#glasscockpit.feed_data(instrument_data)
#GCGTKApplication.run(glasscockpit, 0, data_callback = modify_data)

glasscockpit = gcwidget.GlassCockpit(config, context_class = cwrap.OpenGLContext, img_prefix = "tex_")
glasscockpit.feed_data(instrument_data)
GlutApplication.run(glasscockpit, frametime_millis = 50, data_callback = modify_data)

#screen = cwrap.CairoContext.create(geo.Vector2d(res * 16 // 9, res))
#glasscockpit.render(screen)
#screen.write_to_png("out.png")

#!/usr/bin/python3
#
#

import geo
import cwrap
import gcwidget
from GCGTKApplication import GCGTKApplication

res = 720
screen = cwrap.CairoContext.create(geo.Vector2d(res * 16 // 9, res))

glasscockpit = gcwidget.GlassCockpit(screen)
instrument_data = {
	"pos": {
		"heading_deg":		128,
		"altitude_ft":		12345,
		"pitch_angle_deg":	10,
		"roll_angle_deg":	10,
	},
	"vor1": {
		"obs":				72,
		"deviation_deg":	0.5,
	},
	"xpdr": {
		"squawk":			7003,
	},
}
glasscockpit.feed_data(instrument_data)

def modify_data():
	instrument_data["pos"]["heading_deg"] += 0.5
	instrument_data["pos"]["roll_angle_deg"] += 0.5

GCGTKApplication.run(glasscockpit, screen, 10, data_callback = modify_data)
#glasscockpit.render(screen)
#screen.write_to_png("out.png")

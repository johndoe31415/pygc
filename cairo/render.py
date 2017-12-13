#!/usr/bin/python3
#
#

import cairo
import gcwidget
import time
from gi.repository import Gtk, GObject

class Example(Gtk.Window):
	def __init__(self, gc, cctx):
		Gtk.Window.__init__(self)
		self._gc = gc
		self._cctx = cctx
		self._data = {
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

		self.connect("delete-event", Gtk.main_quit)

		self._darea = Gtk.DrawingArea()
		self._darea.connect("draw", self.on_draw)
		self.add(self._darea)

		self.set_title("PyGC")
		self.resize(self._cctx.width + 20, self._cctx.height + 20)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.show_all()
		GObject.timeout_add(100, self.on_frame)

	def on_frame(self, *args):
		#self._data["pos"]["roll_angle_deg"] = (self._data["pos"]["roll_angle_deg"] + 1) % 360
		#self._data["pos"]["pitch_angle_deg"] = (self._data["pos"]["pitch_angle_deg"] + 1) % 360
		self._data["pos"]["heading_deg"] = (self._data["pos"]["heading_deg"] + 1) % 360
#		print(self._data)
		gc.update(self._data)

		GObject.timeout_add(100, self.on_frame)
		t0 = time.time()
		self._gc.render(self._cctx)
		t1 = time.time()
		tdiff = t1 - t0
		self._darea.queue_draw()
		print("%.1f ms / %.1f fps" % (tdiff * 1000, 1 / tdiff))


	def on_draw(self, wid, cr):
		cr.set_source_surface(self._cctx.surface, 10, 10)
		cr.paint()


#cctx = gcwidget.CairoContext.create(1920, 1080)
cctx = gcwidget.CairoContext.create(1280, 720)

gc = gcwidget.GlassCockpit({ })
gc.update({
	"pos": {
		"heading_deg":		128,
		"altitude_ft":		12345,
		"pitch_angle_deg":	10,
		"roll_angle_deg":	5,
	},
	"vor1": {
		"obs":				72,
		"deviation_deg":	0.5,
	},
	"xpdr": {
		"squawk":			7003,
	},
}
)

app = Example(gc, cctx)
Gtk.main()


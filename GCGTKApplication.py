#!/usr/bin/python3
import time
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject

class GCGTKApplication(Gtk.Window):
	def __init__(self, glasscockpit, screen, frametime_millis, data_callback = None):
		Gtk.Window.__init__(self)
		self._glasscockpit = glasscockpit
		self._screen = screen
		self._frametime_millis = frametime_millis
		self._data_callback = data_callback
		self.connect("delete-event", Gtk.main_quit)

		self._darea = Gtk.DrawingArea()
		self._darea.connect("draw", self.on_draw)
		self.add(self._darea)

		self.set_title("PyGC")
		self.resize(self._screen.dimensions.x + 20, self._screen.dimensions.y + 20)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.show_all()
		self._t0 = 0
		self.on_frame()

	def on_frame(self, *args):
		if self._data_callback is not None:
			self._data_callback()
		self._t0 = time.time()
		self._glasscockpit.render(self._screen)
		self._darea.queue_draw()

	def on_draw(self, wid, cr):
		cr.set_source_surface(self._screen.surface, 10, 10)
		cr.paint()
		t1 = time.time()
		tdiff = t1 - self._t0
		print("%.1f ms / %.1f fps" % (tdiff * 1000, 1 / tdiff))
		GObject.timeout_add(self._frametime_millis, self.on_frame)

	@classmethod
	def run(cls, glasscockpit, screen, frametime_millis, data_callback = None):
		app = cls(glasscockpit, screen, frametime_millis, data_callback = data_callback)
		Gtk.main()

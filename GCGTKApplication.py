#!/usr/bin/python3
import time
import geo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, GLib

class GCGTKApplication(Gtk.Window):
	def __init__(self, glasscockpit, frametime_millis, data_callback = None, quit_callback = None):
		Gtk.Window.__init__(self)
		self._glasscockpit = glasscockpit
		self._frametime_millis = frametime_millis
		self._data_callback = data_callback
		self._quit_callback = quit_callback

		self.connect("delete-event", self._quit_callback)
		self.connect("key_press_event", self.on_keypress)

		self._darea = Gtk.DrawingArea()
		self._darea.connect("draw", self.on_draw)
		self.add(self._darea)

		self.set_title("PyGC")
		window_size = self._glasscockpit.screen_dimension + geo.Vector2d(20, 20)
		self.resize(window_size.x, window_size.y)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.show_all()
		self._t0 = 0
		self.on_frame()

	def on_keypress(self, wid, key):
		if key.get_keycode().keycode == 9:
			# ESC
			self._quit_callback()

	def _quit(self):
		#Gtk.main_quit()
		GLib.MainLoop().quit()

	def on_frame(self, *args):
		if self._data_callback is not None:
			self._data_callback()
#		self._glasscockpit.render(self._screen)
		self._darea.queue_draw()

	def on_draw(self, wid, cr):
#		cr.set_source_surface(self._screen.surface, 10, 10)
#		cr.paint()
		self._t0 = time.time()
		self._glasscockpit.render_cairo(cr)
		t1 = time.time()
		tdiff = t1 - self._t0
		print("%.1f ms / %.1f fps" % (tdiff * 1000, 1 / tdiff))
		GObject.timeout_add(self._frametime_millis, self.on_frame)

	@classmethod
	def run(cls, glasscockpit, frametime_millis, data_callback = None):
		mainloop = GLib.MainLoop()
		app = cls(glasscockpit, frametime_millis, data_callback = data_callback, quit_callback = lambda: mainloop.quit())
		mainloop.run()

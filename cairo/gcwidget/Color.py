class Color(object):
	def __init__(self, r, g, b, a):
		self._r = r
		self._g = g
		self._b = b
		self._a = a

	@property
	def r(self):
		return self._r

	@property
	def g(self):
		return self._g

	@property
	def b(self):
		return self._b

	@property
	def a(self):
		return self._a

	@classmethod
	def from_rgb_int(cls, rgb):
		r = (rgb >> 16) & 0xff
		g = (rgb >> 8) & 0xff
		b = (rgb >> 0) & 0xff
		return cls(r / 255, g / 255, b / 255, 1)

	@classmethod
	def from_rgba_int(cls, rgba):
		r = (rgba >> 24) & 0xff
		g = (rgba >> 16) & 0xff
		b = (rgba >> 8) & 0xff
		a = (rgba >> 0) & 0xff
		return cls(r / 255, g / 255, b / 255, a / 255)

	def cairo_set_source(self, cctx):
		cctx.set_source_rgba(self._r, self._g, self._b, self._a)

	def __repr__(self):
		return "Color<%.2f %.2f %.2f %.2f>" % (self.r, self.g, self.b, self.a)

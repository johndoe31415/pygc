class Box2d(object):
	def __init__(self, base, dimensions):
		self._base = base
		self._dimensions = dimensions

	@property
	def base(self):
		return self._base

	@property
	def dimensions(self):
		return self._dimensions

	@property
	def v0(self):
		return self._base

	@property
	def v1(self):
		return self._base + self._dimensions

	@property
	def center(self):
		return self.v0 + (self._dimensions / 2)

	def __repr__(self):
		return "Box<%s, %s>" % (self.v0, self.v1)

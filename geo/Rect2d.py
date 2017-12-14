from .Vector2d import Vector2d

class Rect2d(object):
	def __init__(self, v1, v2, v3, v4):
		self._v1 = v1
		self._v2 = v2
		self._v3 = v3
		self._v4 = v4

	@classmethod
	def basic(cls, base, width, height):
		return cls(base, base + Vector2d(width, 0), base + Vector2d(width, height), base + Vector2d(0, height))

	@property
	def v1(self):
		return self._v1

	@property
	def v2(self):
		return self._v2

	@property
	def v3(self):
		return self._v3

	@property
	def v4(self):
		return self._v4

	@property
	def center(self):
		return (self.v1 + self.v3) / 2

	def __getitem__(self, index):
		if index == 0:
			return self.v1
		elif index == 1:
			return self.v2
		if index == 2:
			return self.v3
		elif index == 3:
			return self.v4
		else:
			raise KeyError("Unsupported point index")

	def transform(self, matrix):
		return Rect2d(matrix.transform(self.v1), matrix.transform(self.v2), matrix.transform(self.v3), matrix.transform(self.v4))

	def __iter__(self):
		yield self.v1
		yield self.v2
		yield self.v3
		yield self.v4

	def __repr__(self):
		return "Rect<%s, %s, %s, %s>" % (self.v1, self.v2, self.v3, self.v4)

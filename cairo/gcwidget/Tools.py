import math

class AngleTools(object):
	@classmethod
	def hdg2deg(cls, heading_degrees):
		return (-heading_degrees + 90) % 360

	@classmethod
	def hdg2rad(cls, heading_degrees):
		return cls.hdg2deg(heading_degrees) * math.pi / 180

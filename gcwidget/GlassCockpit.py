import json
import collections
import cwrap
import math
from geo import Vector2d, Box2d
from .Tools import AngleTools

_GCElement = collections.namedtuple("GCElement", [ "name", "offset", "dimensions", "clip", "center_of_rotation", "cctx" ])

class GlassCockpit(object):
	def __init__(self, config):
		self._config = config
		self._data = { }
		self._elements = [ ]
		self._load_elements("imgs/render/")

	def _load_elements(self, basedir):
		with open(basedir + "layers.json") as f:
			data = json.loads(f.read())
		for element in data:
			name = element["name"]
			offset = Vector2d(*element["offset"])
			dimensions = Vector2d(*element["dimensions"])
			if "clip" in element:
				clipoffset = Vector2d(*element["clip"]["offset"])
				clipdimensions = Vector2d(*element["clip"]["dimensions"])
				clip = Box2d(base = clipoffset, dimensions = clipdimensions)
			else:
				clip = None
			if "cor" in element:
				center_of_rotation = Vector2d(*element["cor"])
			else:
				center_of_rotation = offset + (dimensions / 2)
			cctx = cwrap.CairoContext.load_from_png(basedir + name + ".png")
			gcelement = _GCElement(name = name, offset = offset, dimensions = dimensions, clip = clip, center_of_rotation = center_of_rotation, cctx = cctx)
			self._elements.append(gcelement)

	def _determine_renderopts(self, name):
		translation = None
		rotation_rad = None

		if name in [ "ahoriz-skygnd", "ahoriz-degs" ]:
			pixel_per_deg_pitch = 124 / 30
			translation = Vector2d(0, pixel_per_deg_pitch * self._data["pos"]["pitch_angle_deg"])
			rotation_rad = self._data["pos"]["roll_angle_deg"] / 180 * math.pi
		elif name == "compass-rot":
			rotation_rad = -self._data["pos"]["heading_deg"] / 180 * math.pi
		elif name in [ "compass-obs", "compass-obs-center" ]:
			rotation_rad = (self._data["vor1"]["obs"] - self._data["pos"]["heading_deg"]) / 180 * math.pi
			if name == "compass-obs-center":
				pixel_per_deg_deviation = 47 / 4
				deviation_deg = self._data["vor1"]["deviation_deg"]
				if deviation_deg < -4:
					deviation_deg = -4
				elif deviation_deg > 4:
					deviation_deg = 4
				translation = Vector2d(deviation_deg * pixel_per_deg_deviation, 0)
		return (translation, rotation_rad)

	def feed_data(self, data):
		self._data = data

	def render(self, screen):
		for element in self._elements:
			(translation, rotation_rad) = self._determine_renderopts(element.name)
			offset = element.offset
			if translation is not None:
				offset += translation
			screen.blit(element.cctx, offset = offset, clip = element.clip, rotation_rad = rotation_rad, center_of_rotation = element.center_of_rotation)

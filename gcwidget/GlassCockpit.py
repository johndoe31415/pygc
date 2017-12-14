import json
import collections
import cwrap
import math
import datetime
from geo import Vector2d, Box2d
from .Tools import AngleTools
from .Color import Color

_GCElement = collections.namedtuple("GCElement", [ "name", "offset", "dimensions", "clip", "center_of_rotation", "cctx" ])

class GlassCockpit(object):
	_COLORS = {
		"horizon_line":		Color.from_rgb_int(0xffffff),
		"menu_bg":			Color.from_rgb_int(0x2c3e50),
		"sep_lines":		Color.from_rgb_int(0xecf0f1),
		"alpha_bg":			Color.from_rgba_int(0x00000030),
		"vor_arrow":		Color.from_rgb_int(0xd407d5),
		"heading_arrow":	Color.from_rgb_int(0xf1c40f),

		"ias_text":				Color.from_rgb_int(0xffffff),
		"active_freq_text":		Color.from_rgb_int(0x2ecc71),
		"standby_freq_text":	Color.from_rgb_int(0xecf0f1),
	}

	def __init__(self, config):
		self._config = config
		self._autoconfig = { }
		self._data = { }
		self._elements = [ ]
		self._load_elements("imgs/render/")

	def _load_elements(self, basedir):
		with open(basedir + "layers.json") as f:
			data = json.loads(f.read())
		for element in data["layers"]:
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

		self._pois = { name: Vector2d(*poi) for (name, poi) in data["pois"].items() }
		self._autoconfig["pixel_per_deg_pitch"] = abs((self._pois["pitch-40deg"] - self._pois["pitch-0deg"]).y / 40)
		self._autoconfig["pixel_per_deg_deviation"] = abs((self._pois["leftmost-cdi-dot"] - self._pois["rightmost-cdi-dot"]).x / 8)

	def _determine_renderopts(self, name):
		translation = None
		rotation_rad = None

		if name in [ "ahoriz-skygnd", "ahoriz-degs" ]:
			translation = Vector2d(0, self._autoconfig["pixel_per_deg_pitch"] * self._data["pos"]["pitch_angle_deg"])
			rotation_rad = self._data["pos"]["roll_angle_deg"] / 180 * math.pi
		elif name == "compass-rot":
			rotation_rad = -self._data["pos"]["heading_deg"] / 180 * math.pi
		elif name in [ "compass-obs", "compass-obs-center" ]:
			rotation_rad = (self._data["vor1"]["obs"] - self._data["pos"]["heading_deg"]) / 180 * math.pi
			if name == "compass-obs-center":
				deviation_deg = self._data["vor1"]["deviation_deg"]
				if deviation_deg < -4:
					deviation_deg = -4
				elif deviation_deg > 4:
					deviation_deg = 4
				translation = Vector2d(deviation_deg * self._autoconfig["pixel_per_deg_deviation"], 0)
		elif name == "hdgbug":
			rotation_rad = (self._data["ap"]["hdgbug_deg"] - self._data["pos"]["heading_deg"]) / 180 * math.pi
		return (translation, rotation_rad)

	def feed_data(self, data):
		self._data = data

	def _render_textelements(self, screen):
		screen.font_select("Nimbus Sans L", 22, fontcolor = self._COLORS["ias_text"])
		screen.text(self._pois["ias"], "%.0f" % ((self._data["pos"]["ias"])), anchor = "cr")

		screen.font_select("Nimbus Sans L", 20, fontcolor = self._COLORS["active_freq_text"])
		screen.text(self._pois["com1-act-freq"], "%.3f" % ((self._data["freq"]["com1"]["active"])), anchor = "bl")
		screen.text(self._pois["com2-act-freq"], "%.3f" % ((self._data["freq"]["com2"]["active"])), anchor = "bl")
		screen.text(self._pois["nav1-act-freq"], "%.2f" % ((self._data["freq"]["nav1"]["active"])), anchor = "bl")
		screen.text(self._pois["nav2-act-freq"], "%.2f" % ((self._data["freq"]["nav2"]["active"])), anchor = "bl")

		screen.font_select("Nimbus Sans L", 20, fontcolor =  self._COLORS["standby_freq_text"])
		screen.text(self._pois["com1-stby-freq"], "%.3f" % ((self._data["freq"]["com1"]["stby"])), anchor = "bl")
		screen.text(self._pois["com2-stby-freq"], "%.3f" % ((self._data["freq"]["com2"]["stby"])), anchor = "bl")
		screen.text(self._pois["nav1-stby-freq"], "%.2f" % ((self._data["freq"]["nav1"]["stby"])), anchor = "bl")
		screen.text(self._pois["nav2-stby-freq"], "%.2f" % ((self._data["freq"]["nav2"]["stby"])), anchor = "bl")

		screen.text(self._pois["xpdr-squawk"], "%04d" % (self._data["xpdr"]["squawk"]), anchor = "bl")
		screen.text(self._pois["time-utc"], datetime.datetime.utcnow().strftime("%H:%M:%S"), anchor = "bl")

	def render(self, screen):
		for element in self._elements:
			(translation, rotation_rad) = self._determine_renderopts(element.name)
			offset = element.offset
			if translation is not None:
				offset += translation
			screen.blit(element.cctx, offset = offset, clip = element.clip, rotation_rad = rotation_rad, center_of_rotation = element.center_of_rotation)

		self._render_textelements(screen)

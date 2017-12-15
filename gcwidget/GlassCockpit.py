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

		"hdgbug-text":			Color.from_rgb_int(0x05d5cb),
		"crs-text":				Color.from_rgb_int(0xd405d4),
	}

	def __init__(self, config, context_class, img_prefix = ""):
		self._config = config
		self._context_class = context_class
		self._autoconfig = { }
		self._data = { }
		self._elements = [ ]
		self._img_prefix = img_prefix
		self._load_elements("imgs/render/")

	@property
	def screen_dimension(self):
		return self._config["screen_dimension"]

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
			cctx = self._context_class.load_from_png(basedir + self._img_prefix + name + ".png", dimensions)
			gcelement = _GCElement(name = name, offset = offset, dimensions = dimensions, clip = clip, center_of_rotation = center_of_rotation, cctx = cctx)
			self._elements.append(gcelement)

		self._pois = { name: Vector2d(*poi) for (name, poi) in data["pois"].items() }
		self._autoconfig["pixel_per_deg_pitch"] = abs((self._pois["pitch-40deg"] - self._pois["pitch-0deg"]).y / 40)
		self._autoconfig["pixel_per_deg_deviation"] = abs((self._pois["leftmost-cdi-dot"] - self._pois["rightmost-cdi-dot"]).x / 8)
		self._autoconfig["speedindicator_pixel_per_kt"] = abs((self._pois["speedindicator-top"] - self._pois["speedindicator-bottom"]).y / 50)


	def _speedindicator_tics_text(self, element, at_offset):
		element.font_select("Nimbus Sans L", 14, fontcolor = self._COLORS["ias_text"])
		center_speed = int(self._data["pos"]["ias"] // 10) * 10
		speed_offset = center_speed - 30
		for i in range(8):
			speed = speed_offset + (10 * i)
			if speed < 0:
				continue
			translation = Vector2d(0, (self._data["pos"]["ias"] % 10) * self._autoconfig["speedindicator_pixel_per_kt"])
			element.text((self._pois["speedindicator-top"] - at_offset) + (Vector2d(0, self._autoconfig["speedindicator_pixel_per_kt"]) * (10 * (6 - i))) + translation, str(speed), anchor = "cr")

	def _determine_clipping_ias_bar(self, element, color):
		min_shown_speed = self._data["pos"]["ias"] - 30
		max_shown_speed = min_shown_speed + 60
		(bar_show_min, bar_show_max) = self._data["ias_bars"][color]

		if (bar_show_min > max_shown_speed) or (bar_show_max < min_shown_speed):
			# Don't render at all
			return None
		else:
			overlap_speed = (max(bar_show_min, min_shown_speed), min(bar_show_max, max_shown_speed))
			clip_speed_bottom = overlap_speed[0] - min_shown_speed
			clip_speed_top = max_shown_speed - overlap_speed[1]
#			print("%10s: SPD [%3d %3d], RNG [%3d %3d], OVL [%3d %3d], CLIP TOP %3d, BTM %3d" % (color, min_shown_speed, max_shown_speed, bar_show_min, bar_show_max, overlap_speed[0], overlap_speed[1], clip_speed_top, clip_speed_bottom))
			clip_px_top = clip_speed_top * self._autoconfig["speedindicator_pixel_per_kt"]
			clip_px_bottom = clip_speed_bottom * self._autoconfig["speedindicator_pixel_per_kt"]
			clip = Box2d(element.clip.base + Vector2d(0, clip_px_top), element.clip.dimensions - Vector2d(0, clip_px_top + clip_px_bottom))
			return clip

	def _determine_renderopts(self, element):
		clip = element.clip
		translation = None
		rotation_rad = None
		clipped_callback = None
		do_draw = True

		if element.name in [ "ahoriz-skygnd", "ahoriz-degs" ]:
			translation = Vector2d(0, self._autoconfig["pixel_per_deg_pitch"] * self._data["pos"]["pitch_angle_deg"])
			rotation_rad = self._data["pos"]["roll_angle_deg"] / 180 * math.pi
		elif element.name == "compass-rot":
			rotation_rad = -self._data["pos"]["heading_deg"] / 180 * math.pi
		elif element.name in [ "compass-obs", "compass-obs-center" ]:
			rotation_rad = (self._data["vor1"]["obs"] - self._data["pos"]["heading_deg"]) / 180 * math.pi
			if element.name == "compass-obs-center":
				deviation_deg = self._data["vor1"]["deviation_deg"]
				if deviation_deg < -4:
					deviation_deg = -4
				elif deviation_deg > 4:
					deviation_deg = 4
				translation = Vector2d(deviation_deg * self._autoconfig["pixel_per_deg_deviation"], 0)
		elif element.name == "hdgbug":
			rotation_rad = (self._data["ap"]["hdgbug_deg"] - self._data["pos"]["heading_deg"]) / 180 * math.pi
		elif element.name == "speedindicator":
			clipped_callback = self._speedindicator_tics_text
		elif element.name == "speedindicator-tics":
			translation = Vector2d(0, (self._data["pos"]["ias"] % 10) * self._autoconfig["speedindicator_pixel_per_kt"])
		elif element.name.startswith("speedindicator-bar-"):
			color = element.name[19:]
			clip = self._determine_clipping_ias_bar(element, color)
			if clip is None:
				do_draw = False
		return (clip, translation, rotation_rad, clipped_callback, do_draw)

	def feed_data(self, data):
		self._data = data

	def _render_textelements(self, screen):
		screen.font_select("Nimbus Sans L", 22, fontcolor = self._COLORS["ias_text"])
		screen.text(self._pois["ias-text"], "%.0f" % ((self._data["pos"]["ias"])), anchor = "cr")

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

		screen.font_select("Nimbus Sans L", 22, fontcolor = self._COLORS["ias_text"])
		screen.text(self._pois["hdg-text"], "%.0f°" % ((self._data["pos"]["heading_deg"])), anchor = "cc")

		screen.font_select("Nimbus Sans L", 14, fontcolor = self._COLORS["hdgbug-text"])
		screen.text(self._pois["hdgbug-text"], "%.0f°" % ((self._data["ap"]["hdgbug_deg"])), anchor = "bl")

		screen.font_select("Nimbus Sans L", 14, fontcolor = self._COLORS["crs-text"])
		screen.text(self._pois["crs-text"], "%.0f°" % ((self._data["vor1"]["obs"])), anchor = "bl")

	def render(self, screen):
		for element in self._elements:
			(clip, translation, rotation_rad, clipped_callback, do_draw) = self._determine_renderopts(element)
			if do_draw:
				offset = element.offset
				if translation is not None:
					offset += translation
				screen.blit(element.cctx, offset = offset, clip = clip, rotation_rad = rotation_rad, center_of_rotation = element.center_of_rotation, clipped_callback = clipped_callback)

		self._render_textelements(screen)

	def render_cairo(self, cairo_context):
		return self.render(cwrap.CairoContext.wrap(self._config["screen_dimension"], cairo_context))

	def render_opengl(self, opengl_context):
		return self.render(cwrap.OpenGLContext())

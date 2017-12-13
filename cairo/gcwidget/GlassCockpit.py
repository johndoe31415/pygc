import datetime
from geo import Vector2d
from .Widget import Widget
from .Color import Color
from .Tools import AngleTools

class GlassCockpit(Widget):
	_colors = {
		"sky":				Color.from_rgb_int(0x3875de),
		"ground":			Color.from_rgb_int(0x64432a),
		"horizon_line":		Color.from_rgb_int(0xffffff),
		"menu_bg":			Color.from_rgb_int(0x2c3e50),
		"sep_lines":		Color.from_rgb_int(0xecf0f1),
		"alpha_bg":			Color.from_rgba_int(0x00000030),
		"vor_arrow":		Color.from_rgb_int(0xd407d5),
		"heading_arrow":	Color.from_rgb_int(0xf1c40f),
	}

	def __init__(self, config_data):
		Widget.__init__(self, config_data)
		self._data = None

	def update(self, instrument_data):
		self._data = instrument_data

	def _em(self, value):
		return value

	def _draw_top_menu(self, cctx):
		cctx.flood(self._colors["menu_bg"])
		cctx.line_bottom(1, color = self._colors["sep_lines"])

	def _draw_right_menu(self, cctx):
		cctx.flood(self._colors["menu_bg"])
		cctx.line_left(1, color = self._colors["sep_lines"])

		lines = [
			("XPDR", "%04d" % (self._data["xpdr"]["squawk"])),
			("UTC", datetime.datetime.utcnow().strftime("%H:%M:%S")),
		]
		yoffset = cctx.height - 100
		for (key, value) in lines:
			cctx.text(Vector2d(10, yoffset), key, fontsize = 20, color = self._colors["sep_lines"])
			yoffset += 23
			cctx.text(Vector2d(20, yoffset), value, fontsize = 20, color = self._colors["sep_lines"])
			yoffset += 30

	def _draw_menu_background(self, cctx):
		self._colors["menu_bg"].cairo_set_source(cctx)
		cctx.rectangle(0, 0, self._config["width"], self._top_height)
		cctx.fill()

		cctx.rectangle(self._config["width"] - self._right_width, 0, self._config["width"], self._config["height"])
		cctx.fill()

		self._colors["sep_lines"].cairo_set_source(cctx)
		cctx.set_line_width(self._em(1))
		cctx.move_to(0, self._top_height)
		cctx.line_to(self._config["width"], self._top_height)

		cctx.move_to(self._config["width"] - self._right_width, self._top_height)
		cctx.line_to(self._config["width"] - self._right_width, self._config["height"])
		cctx.stroke()

	def _draw_artificial_horizon(self, cctx):
		#horizon_zero = cctx.height * 2 / 5

		horizon_zero = cctx.height / 2
		pixels_per_deg = 5

		with cctx:
			cctx._cairoctx.translate(0, 200)

			cctx._cairoctx.translate(cctx.width / 2, cctx.height / 2)
			cctx._cairoctx.rotate(0.1)
			cctx._cairoctx.translate(-cctx.width / 2, -cctx.height / 2)


			cctx.path([
				Vector2d(-cctx.width, -cctx.height),
				Vector2d(cctx.width * 2, -cctx.height),
				Vector2d(cctx.width * 2, cctx.height / 2),
				Vector2d(-cctx.width, cctx.height / 2)
			], fill_color = self._colors["sky"], close = True)

			cctx.path([
				Vector2d(-cctx.width, cctx.height / 2),
				Vector2d(cctx.width * 2, cctx.height / 2),
				Vector2d(cctx.width * 2, cctx.height * 2),
				Vector2d(-cctx.width, cctx.height * 2),
			], fill_color = self._colors["ground"], close = True)

			cctx.line(Vector2d(-cctx.width, cctx.height / 2), Vector2d(cctx.width * 2, cctx.height / 2), color = self._colors["horizon_line"], width = 2)

			for pitch_angle_deg in range(-40, 40 + 1, 5):
				if pitch_angle_deg == 0:
					continue
				if (pitch_angle_deg % 10) == 0:
					length = 30
					width = 1
					text = str(abs(pitch_angle_deg))
				else:
					length = 15
					width = 0.5
					text = None
				y_offset = horizon_zero + (pitch_angle_deg * -pixels_per_deg)
				if 30 < y_offset < (3 / 5 * cctx.height):
					cctx.line(Vector2d(cctx.width / 2 - length, y_offset), Vector2d((cctx.width / 2) + length, y_offset), color = self._colors["horizon_line"], width = width)
					if text is not None:
						cctx.text(Vector2d((cctx.width / 2) + length + 10, y_offset + 4), text, 12, color = self._colors["horizon_line"])


		cctx.path([
			Vector2d((cctx.width / 2) - 100, horizon_zero + 40),
			Vector2d((cctx.width / 2), horizon_zero),
			Vector2d((cctx.width / 2) + 100, horizon_zero + 40),
		], stroke_width = 3, stroke_color = self._colors["heading_arrow"])

		vor_dimensions = 225
		with cctx.subctx(offset = Vector2d((cctx.width - vor_dimensions) / 2, (cctx.height - vor_dimensions) - 25), width = vor_dimensions, height = vor_dimensions) as vor_gauge:
			self._draw_vor_gauge(vor_gauge)

	def _draw_vor_gauge(self, cctx):
		circle = cctx.circle(center = cctx.center, radius = cctx.width / 2, fill_color = self._colors["alpha_bg"])
		heading_deg = self._data["pos"]["heading_deg"]
		for hdg_deg in range(0, 360, 5):
			if (hdg_deg % 10) == 0:
				width = 2
				length = -8
			else:
				width = 1
				length = -5
			circle.tick(angle = AngleTools.hdg2rad(hdg_deg - heading_deg), length = length, width = width, color = self._colors["horizon_line"])
			if (hdg_deg % 30) == 0:
				text = {
					0:		"N",
					90:		"E",
					180:	"S",
					270:	"W",
				}.get(hdg_deg, str(hdg_deg // 10))
				if text.isdigit():
					fontsize = 17
				else:
					fontsize = 22
				circle.text(angle = AngleTools.hdg2rad(hdg_deg - heading_deg), text = text, distance = -28, fontsize = fontsize, color = self._colors["horizon_line"])

		cctx.circle(center = cctx.center, radius = cctx.width / 4, stroke_width = 0.5, stroke_color = self._colors["horizon_line"])

		vor_vector = Vector2d.angle(AngleTools.hdg2rad(self._data["vor1"]["obs"] - heading_deg), y_flip = True)

		vor_deviation = -vor_vector.perpendicular(y_flip = True).norm() * 20
		for i in [ -2, -1, 1, 2 ]:
			cctx.circle(center = cctx.center + (i * vor_deviation), radius = 4, stroke_width = 0.5, stroke_color = self._colors["horizon_line"])

		# Every dot equals 2°, clamp at +-4°
		current_deviation = self._data["vor1"]["deviation_deg"] / 2.0
		if current_deviation < -2:
			current_deviation = -2
		elif current_deviation > 2:
			current_deviation = 2

		inner_length = 30
		spacing = 5
		outer_length = 95
		cctx.line(cctx.center + (vor_vector * (inner_length + spacing)), cctx.center + (vor_vector * outer_length), color = self._colors["vor_arrow"], width = 3, arrow_end = True)
		cctx.line(cctx.center + (vor_vector * inner_length) + (vor_deviation * current_deviation), cctx.center + (vor_vector * -inner_length) + (vor_deviation * current_deviation), color = self._colors["vor_arrow"], width = 3)
		cctx.line(cctx.center + (vor_vector * -(inner_length + spacing)), cctx.center + (vor_vector * -outer_length), color = self._colors["vor_arrow"], width = 3)
		print(vor_vector)

	def render(self, cctx):
		top_height = 100
		right_width = 200

		with cctx.subctx(offset = Vector2d(0, 0), width = cctx.width, height = top_height) as top_menu:
			self._draw_top_menu(top_menu)

		with cctx.subctx(offset = Vector2d(cctx.width - right_width, top_height), width = right_width, height = cctx.height - top_height) as right_menu:
			self._draw_right_menu(right_menu)

		with cctx.subctx(offset = Vector2d(0, top_height + cctx.relval(0.5)), width = cctx.width - right_width - cctx.relval(0.5), height = cctx.height - top_height) as ahorizon:
			self._draw_artificial_horizon(ahorizon)


import math
import cairo
from geo import Vector2d

class CairoCircle(object):
	def __init__(self, cctx, center, radius):
		self._cairoctx = cctx
		self._c = center
		self._r = radius

	def tick(self, angle, length, width, color):
		v_angle = Vector2d.angle(angle, y_flip = True)
		p1 = (self._r * v_angle) + self._c
		p2 = ((self._r + length) * v_angle) + self._c
		self._cairoctx.line(p1, p2, width = width, color = color)

	def text(self, angle, distance, text, fontsize, color):
		v_angle = Vector2d.angle(angle, y_flip = True)
		perpendicular = v_angle.perpendicular().norm()
		pos = ((self._r + distance) * v_angle) + self._c

		(x_off, y_off, text_width, text_height, x_adv, y_adv) = self._cairoctx.text_extents(text, fontsize)
		self._cairoctx.text(pos, text, fontsize, color, angle = angle, translate = Vector2d(-x_adv / 2, 0))

class CairoContext(object):
	def __init__(self, offset, width, height, parent = None, surface = None, cairoctx = None):
		self._offset = offset
		self._width = width
		self._height = height
		self._parent = parent
		self._surface = surface
		self._cairoctx = cairoctx

	@classmethod
	def create(cls, width, height):
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
		cairoctx = cairo.Context(surface)
		return cls(offset = Vector2d(0, 0), width = width, height = height, parent = None, surface = surface, cairoctx = cairoctx)

	@property
	def surface(self):
		return self._surface

	@property
	def width(self):
		return self._width

	@property
	def height(self):
		return self._height

	@property
	def center(self):
		return Vector2d(self.width / 2, self.height / 2)

	def relval(self, value):
		return value

	def _offset_interpret(self, offsetx, offsety, width, height):
		if isinstance(offsetx, str):
			if offsetx == "center":
				offsetx = (self.width - width) / 2
			else:
				raise Exception(NotImplemented)
		if isinstance(offsety, str):
			if offsety == "bottom":
				offsety = (self.height - height)
			elif offsety == "center":
				offsety = (self.height - height) / 2
			else:
				raise Exception(NotImplemented)
		return (offsetx, offsety)

	def subctx(self, offset, width, height):
		return CairoContext(offset = self._offset + offset, width = width, height = height, parent = self, surface = self._surface, cairoctx = self._cairoctx)

	def __enter__(self):
		self._cairoctx.save()
		self._cairoctx.rectangle(self._offset.x, self._offset.y, self._width, self._height)
		self._cairoctx.clip()
		return self

	def __exit__(self, *args):
		self._cairoctx.restore()

	def _set_source(self, color):
		self._cairoctx.set_source_rgba(color.r, color.g, color.b, color.a)

	def circle(self, center, radius, stroke_width = None, stroke_color = None, fill_color = None):
		abs_center = self._offset + center
		if fill_color is not None:
			self._cairoctx.arc(abs_center.x, abs_center.y, radius, 0, 2 * math.pi)
			self._set_source(fill_color)
			self._cairoctx.fill()
		if (stroke_color is not None) and (stroke_width is not None):
			self._cairoctx.set_line_width(self.relval(stroke_width))
			self._cairoctx.arc(abs_center.x, abs_center.y, radius, 0, 2 * math.pi)
			self._set_source(stroke_color)
			self._cairoctx.stroke()
		return CairoCircle(cctx = self, center = center, radius = radius)

	def flood(self, color):
		self._set_source(color)
		self._cairoctx.rectangle(self._offset.x, self._offset.y, self._width, self._height)
		self._cairoctx.fill()

	def _move_to(self, pos):
		pos += self._offset
		self._cairoctx.move_to(pos.x, pos.y)

	def _line_to(self, pos):
		pos += self._offset
		self._cairoctx.line_to(pos.x, pos.y)

	def line(self, pos1, pos2, width = None, color = None, arrow_end = None):
		if width is not None:
			self._cairoctx.set_line_width(self.relval(width))
		if color is not None:
			self._set_source(color)

		if arrow_end is not None:
			arrow = (pos2 - pos1).norm()
			perp = arrow.perpendicular(y_flip = True)
			self._line_to(pos2 + 10 * (perp - arrow))
			self._line_to(pos2 + 10 * (-perp - arrow))
			self._line_to(pos2)
			self._cairoctx.fill()
			self._move_to(pos2 - (5 * arrow))
			self._line_to(pos1)
			self._cairoctx.stroke()
		else:
			self._move_to(pos1)
			self._line_to(pos2)
			self._cairoctx.stroke()

	def _fill(self, fill_color):
		self._set_source(fill_color)
		self._cairoctx.fill()

	def _stroke(self, stroke_width, stroke_color):
		self._set_source(stroke_color)
		self._cairoctx.set_line_width(self.relval(stroke_width))
		self._cairoctx.stroke()

	def _stroke_fill(self, draw_func, stroke_width, stroke_color, fill_color):
		if fill_color is not None:
			draw_func()
			self._fill(fill_color)

		if (stroke_width is not None) and (stroke_color is not None):
			draw_func()
			self._stroke(stroke_width, stroke_color)

	def path(self, points, stroke_width = None, stroke_color = None, fill_color = None, close = False):
		def draw():
			self._move_to(points[0])
			for point in points[1:]:
				self._line_to(point)
			if close:
				self._line_to(points[0])
		self._stroke_fill(draw, stroke_width, stroke_color, fill_color)

	def text_extents(self, text, fontsize):
		self._cairoctx.select_font_face("Modern")
		self._cairoctx.set_font_size(self.relval(fontsize))
		return self._cairoctx.text_extents(text)

	def text(self, pos, text, fontsize, color, angle = None, translate = None):
		self._cairoctx.select_font_face("Modern")
		self._cairoctx.set_font_size(self.relval(fontsize))
		self._cairoctx.save()
		pos = pos + self._offset
		self._cairoctx.translate(pos.x, pos.y)
		if angle is not None:
			self._cairoctx.rotate(-angle + (math.pi / 2))
		if translate is not None:
			self._cairoctx.translate(translate.x, translate.y)
		self._cairoctx.move_to(0, 0)
		self._set_source(color)
		self._cairoctx.show_text(text)
		self._cairoctx.restore()

	def line_left(self, width, color):
		self.line(Vector2d(0, 0), Vector2d(0, self.height), width = width, color = color)

	def line_bottom(self, width, color):
		self.line(Vector2d(0, self.height), Vector2d(self.width, self.height), width = width, color = color)

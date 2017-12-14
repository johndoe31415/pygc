import cairo
import collections
from geo import Vector2d

_FontExtents = collections.namedtuple("FontExtents", [ "ascent", "descent", "height", "max_x_advance", "max_y_advance" ])
_TextExtents = collections.namedtuple("TextExtents", [ "x_bearing", "y_bearing", "width", "height", "x_advance", "y_advance" ])

class CairoContext(object):
	def __init__(self, dimensions, surface, cairoctx):
		self._dimensions = dimensions
		self._surface = surface
		self._cairoctx = cairoctx
		self._font_extents = None

	@property
	def dimensions(self):
		return self._dimensions

	@property
	def surface(self):
		return self._surface

	@classmethod
	def create(cls, dimensions):
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, dimensions.x, dimensions.y)
		cairoctx = cairo.Context(surface)
		return cls(dimensions = dimensions, surface = surface, cairoctx = cairoctx)

	@classmethod
	def load_from_png(cls, png_filename):
		surface = cairo.ImageSurface.create_from_png(png_filename)
		cairoctx = cairo.Context(surface)
		dimensions = Vector2d(surface.get_width(), surface.get_height())
		return cls(dimensions = dimensions, surface = surface, cairoctx = cairoctx)

	def write_to_png(self, filename):
		self._surface.write_to_png(filename)

	def blit(self, source, offset = None, clip = None, rotation_rad = None, center_of_rotation = None, clipped_callback = None):
		if offset is None:
			offset = Vector2d(0, 0)
		self._cairoctx.save()
		if clip is not None:
			self._cairoctx.rectangle(clip.base.x, clip.base.y, clip.dimensions.x, clip.dimensions.y)
			self._cairoctx.clip()

		if rotation_rad is not None:
			assert(center_of_rotation is not None)
			self._cairoctx.translate(center_of_rotation.x, center_of_rotation.y)
			self._cairoctx.rotate(rotation_rad)
			self._cairoctx.translate(-center_of_rotation.x, -center_of_rotation.y)

		self._cairoctx.translate(offset.x, offset.y)
		self._cairoctx.set_source_surface(source.surface)
		self._cairoctx.rectangle(0, 0, source.dimensions.x, source.dimensions.y)
		self._cairoctx.fill()
		if clipped_callback is not None:
			clipped_callback(self, offset)
		self._cairoctx.restore()

	def font_select(self, fontname, fontsize, fontcolor = None):
		if fontcolor is not None:
			fontcolor.cairo_set_source(self._cairoctx)
		else:
			# Black by default
			self._cairoctx.set_source_rgb(0, 0, 0)
		self._cairoctx.select_font_face(fontname, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		self._cairoctx.set_font_size(fontsize)
		self._font_extents = _FontExtents(*self._cairoctx.font_extents())

	def text(self, pos, text, anchor = "tl"):
		# Anchor is one of top/center/bottom - left/center/right combinations
		assert(len(anchor) == 2)
		(valign, halign) = anchor
		assert(valign in "tcb")
		assert(halign in "lcr")

		text_extents = _TextExtents(*self._cairoctx.text_extents(text))
		if valign == "b":
			# Baseline, Cairo default
			pass
		elif valign == "t":
			# Top left
			pos -= Vector2d(0, text_extents.y_bearing)
		elif valign == "c":
			# Center left
			pos -= Vector2d(0, text_extents.y_bearing / 2)
		else:
			raise Exception(NotImplemented)
		if halign == "l":
			# Left-aligned, Cairo default
			pass
		elif halign == "r":
			# Right-alighed
			pos -= Vector2d(text_extents.x_advance, 0)
		elif valign == "c":
			# Center alignment
			pos -= Vector2d(text_extents.x_advance / 2, 0)
		else:
			raise Exception(NotImplemented)
		self._cairoctx.move_to(pos.x, pos.y)
		self._cairoctx.show_text(text)

	def __str__(self):
		return "CairoContext<%s>" % (self._dimensions)

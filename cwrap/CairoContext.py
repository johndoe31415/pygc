import cairo
from geo import Vector2d

class CairoContext(object):
	def __init__(self, dimensions, surface, cairoctx):
		self._dimensions = dimensions
		self._surface = surface
		self._cairoctx = cairoctx

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

	def blit(self, source, offset = None, clip = None, rotation_rad = None, center_of_rotation = None):
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
		self._cairoctx.restore()

	def font_select(self, fontname, fontsize, fontcolor = None):
		if fontcolor is not None:
			self._cairoctx.set_source_rgb(*fontcolor)
		else:
			# Black by default
			self._cairoctx.set_source_rgb(0, 0, 0)
		self._cairoctx.set_font_size(fontsize)
#		self._cairoctx.set_font_face(fontname, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
#		self._cairoctx.set_font_face(fontname)

	def text(self, pos, text):
		self._cairoctx.move_to(pos.x, pos.y)
		self._cairoctx.show_text(text)

	def __str__(self):
		return "CairoContext<%s>" % (self._dimensions)

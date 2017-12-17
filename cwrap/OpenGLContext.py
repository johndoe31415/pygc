import time
import sys
import math
import cairo
import collections
from geo import Vector2d, Box2d
from . import TextExtents
from OpenGL.GL import *

OpenGLTexture = collections.namedtuple("OpenGLTexture", [ "texid", "dimension", "surface_dimension", "filename", "maxx", "maxy", "text_extents" ])
OpenGLTexturePromise = collections.namedtuple("OpenGLTexturePromise", [ "dimension", "filename", "texture" ])
SelectedFont = collections.namedtuple("SelectedFont", [ "name", "size", "color" ])
RenderedText = collections.namedtuple("RenderedText", [ "font", "text", "textureid" ])

class ObjectLRUCache(object):
	def __init__(self, create_callback, purge_callback, purge_timeout = 5):
		self._create_callback = create_callback
		self._purge_callback = purge_callback
		self._purge_timeout = purge_timeout
		self._autopurge_interval = 1
		self._last_purge = time.time()
		self._cache = { }

	def purge(self):
		now = time.time()
		self._last_purge = now
		delete_keys = [ ]
		delete_items = [ ]
		for (key, (lastuse_time, item)) in self._cache.items():
			if (now - lastuse_time) > self._purge_timeout:
				delete_items.append(item)
				delete_keys.append(key)
		if len(delete_items) > 0:
			self._purge_callback(delete_items)
			for key in delete_keys:
				del self._cache[key]

	def _auto_purge(self):
		time_since_last_purge = time.time() - self._last_purge
		if time_since_last_purge > self._autopurge_interval:
			self.purge()

	def __getitem__(self, key):
		try:
			item = self._cache.get(key)
			if item is not None:
				# Item is cached. Reset timestamp and return object.
				item[0] = time.time()
				return item[1]

			# Item not in cache. Create
			new_item = self._create_callback(*key)

			# Insert into cache and return object
			self._cache[key] = [ time.time(), new_item ]
			return new_item
		finally:
			self._auto_purge()

	def __str__(self):
		return "Cache<%d>" % (len(self._cache))

class OpenGLContext(object):
	_depth = 1

	def __init__(self):
		self._selected_font = None
		self._text_cache = ObjectLRUCache(self.render_text_to_texture, self._delete_text_textures)

	def _delete_text_textures(self, textures):
		texids = [ texture.texid for texture in textures ]
		glDeleteTextures(texids)

	@classmethod
	def load_from_png(cls, png_filename, dimension):
		return OpenGLTexturePromise(dimension = dimension, filename = png_filename, texture = [ ])

	def _finish_texture(self, promise):
		if len(promise.texture) != 0:
			return
		surface = cairo.ImageSurface.create_from_png(promise.filename)
		surface_dimension = Vector2d(surface.get_width(), surface.get_height())
		rgba_data = bytes(surface.get_data())
		assert(len(rgba_data) == 4 * surface_dimension.x * surface_dimension.y)

		texture_id = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, texture_id)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surface_dimension.x, surface_dimension.y, 0, GL_RGBA, GL_UNSIGNED_BYTE, rgba_data)
		texture = OpenGLTexture(texid = texture_id, dimension = promise.dimension, surface_dimension = surface_dimension, filename = promise.filename, maxx = 1, maxy = 1, text_extents = None)
		promise.texture.append(texture)
		return texture

	def blit(self, source, offset = None, clip = None, rotation_rad = None, center_of_rotation = None, clipped_callback = None):
		if isinstance(source, OpenGLTexturePromise):
			if len(source.texture) == 0:
				self._finish_texture(source)
			source = source.texture[0]

		depth = 0

		glBindTexture(GL_TEXTURE_2D, source.texid)

		glPushMatrix()

		if clip is True:
			# Keep clipping but do not modify any settings.
			pass
		elif (clip is None) or (clip is False):
			# Disable clipping
			glDisable(GL_STENCIL_TEST)
		else:
			# Activate stencil buffer
			glEnable(GL_STENCIL_TEST)

			# Don't paint any framebuffer components
			glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)

			# Set whole stencil buffer to zero
			glClear(GL_STENCIL_BUFFER_BIT)

			# But where we paint next, replace stencil buffer by 1
			glStencilFunc(GL_NEVER, 1, 0)
			glStencilOp(GL_REPLACE, GL_KEEP, GL_KEEP)

			# Draw the clipping plane (i.e., set stencil to one therein)
			glBegin(GL_QUADS)
			for vertex in clip:
				glVertex3f(vertex.x, vertex.y, 1)
			glEnd()

			# Re-enable drawing
			glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

			# But only where stencil == 1
			glStencilFunc(GL_EQUAL, 1, 0xff)

		if rotation_rad is not None:
			glTranslate(center_of_rotation.x, center_of_rotation.y, 0)
			glRotate(180 / math.pi * rotation_rad, 0, 0, 1)
			glTranslate(-center_of_rotation.x, -center_of_rotation.y, 0)

		if offset is None:
			offset = Vector2d(0, 0)

		if source.text_extents is not None:
			offset += Vector2d(0, source.text_extents.y_bearing)
		glTranslate(offset.x, offset.y, 0)

		glBegin(GL_QUADS)
		glTexCoord2f(0, 0)
		glVertex3f(0, 0, depth)

		glTexCoord2f(source.maxx, 0)
		glVertex3f(source.dimension.x, 0, depth)

		glTexCoord2f(source.maxx, source.maxy)
		glVertex3f(source.dimension.x, source.dimension.y, depth)

		glTexCoord2f(0, source.maxy)
		glVertex3f(0, source.dimension.y, depth)
		glEnd()

		if clipped_callback is not None:
			clipped_callback(self, offset)

		glPopMatrix()

	@staticmethod
	def _next_pwr2(value):
		for i in range(16):
			if (2 ** i) >= value:
				return 2 ** i

	def _cctx_set_font(self, cctx, font_params):
		cctx.select_font_face(font_params.name, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		cctx.set_font_size(font_params.size)
		font_params.color.cairo_set_source(cctx)

	def render_text_to_texture(self, selected_font, text):
		# Determine size first by creating a dummy surface
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
		cctx = cairo.Context(surface)

		# Then set font parameters on that context to determine text extents
		self._cctx_set_font(cctx, selected_font)
		text_extents = TextExtents(*cctx.text_extents(text))

		# Create an appropriately-sized surface now.
		(width, height) = (text_extents.width + 2, text_extents.height)
		(gl_width, gl_height) = (self._next_pwr2(width), self._next_pwr2(height))

		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, gl_width, gl_height)
		cctx = cairo.Context(surface)
		self._cctx_set_font(cctx, selected_font)

		# And draw text on it
		cctx.move_to(0, -text_extents.y_bearing)
		cctx.show_text(text)

		# Now create texture from it
		rgba_data = bytes(surface.get_data())
		texture_id = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, texture_id)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, gl_width, gl_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, rgba_data)
		texture = OpenGLTexture(texid = texture_id, dimension = Vector2d(width, height), surface_dimension = Vector2d(width, height), filename = None, maxx = width / gl_width, maxy = height / gl_height, text_extents = text_extents)
		return texture

	def font_select(self, fontname, fontsize, fontcolor = None):
		self._selected_font = SelectedFont(name = fontname, size = fontsize, color = fontcolor)

	def text(self, pos, text, anchor = "tl"):
		# Anchor is one of top/center/bottom - left/center/right combinations
		assert(len(anchor) == 2)
		(valign, halign) = anchor
		assert(valign in "tcb")
		assert(halign in "lcr")

		key = (self._selected_font, text)
		texture = self._text_cache[key]
		if valign == "b":
			# Baseline, Cairo default
			pass
		elif valign == "t":
			# Top left
			pos -= Vector2d(0, texture.text_extents.y_bearing)
		elif valign == "c":
			# Center left
			pos -= Vector2d(0, texture.text_extents.y_bearing / 2)
		else:
			raise Exception(NotImplemented)

		if halign == "l":
			# Left-aligned, Cairo default
			pass
		elif halign == "r":
			# Right-alighed
			pos -= Vector2d(texture.text_extents.x_advance, 0)
		elif valign == "c":
			# Center alignment
			pos -= Vector2d(texture.text_extents.x_advance / 2, 0)
		else:
			raise Exception(NotImplemented)

		self.blit(texture, offset = pos, clip = True)

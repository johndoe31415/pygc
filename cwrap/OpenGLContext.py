import time
import sys
import math
import cairo
import collections
from geo import Vector2d, Box2d
from . import TextExtents
from OpenGL.GL import *

OpenGLTexture = collections.namedtuple("OpenGLTexture", [ "texid", "dimension", "surface_dimension", "filename" ])
OpenGLTexturePromise = collections.namedtuple("OpenGLTexturePromise", [ "dimension", "filename", "texture" ])
SelectedFont = collections.namedtuple("SelectedFont", [ "name", "size", "color" ])
RenderedText = collections.namedtuple("RenderedText", [ "renderts", "font", "text", "textureid" ])

class OpenGLContext(object):
	_depth = 1

	def __init__(self):
		self._selected_font = None
#		self._text

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
		texture = OpenGLTexture(texid = texture_id, dimension = promise.dimension, surface_dimension = surface_dimension, filename = promise.filename)
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

		if clip is not None:
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
		else:
			glDisable(GL_STENCIL_TEST)


		if rotation_rad is not None:
			glTranslate(center_of_rotation.x, center_of_rotation.y, 0)
			glRotate(180 / math.pi * rotation_rad, 0, 0, 1)
			glTranslate(-center_of_rotation.x, -center_of_rotation.y, 0)
		if offset is not None:
			glTranslate(offset.x, offset.y, 0)

		glBegin(GL_QUADS)
		glTexCoord2f(0, 0)
		glVertex3f(0, 0, depth)

		glTexCoord2f(1, 0)
		glVertex3f(source.dimension.x, 0, depth)

		glTexCoord2f(1, 1)
		glVertex3f(source.dimension.x, source.dimension.y, depth)

		glTexCoord2f(0, 1)
		glVertex3f(0, source.dimension.y, depth)
		glEnd()

		glPopMatrix()

	def draw_image(self, img, vertices):
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, source.texid)
		glBegin(GL_QUADS)

		glTexCoord2f(0, 1)
		glVertex2f(vertices[0][0], vertices[0][1])

		glTexCoord2f(1, 1)
		glVertex2f(vertices[1][0], vertices[1][1])

		glTexCoord2f(1, 0)
		glVertex2f(vertices[2][0], vertices[2][1])

		glTexCoord2f(0, 0)
		glVertex2f(vertices[3][0], vertices[3][1])

		glEnd()
		glDisable(GL_TEXTURE_2D)

	@staticmethod
	def _next_pwr2(value):
		for i in range(16):
			if (2 ** i) >= value:
				return 2 ** i

	def _cctx_set_font(self, cctx, font_params):
		cctx.select_font_face(font_params.name, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		cctx.set_font_size(font_params.size)
		font_params.color.cairo_set_source(cctx)

	def render_text_to_texture(self, text):
		# Determine size first by creating a dummy surface
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
		cctx = cairo.Context(surface)

		# Then set font parameters on that context to determine text extents
		self._cctx_set_font(cctx, self._selected_font)
		text_extents = TextExtents(*cctx.text_extents(text))

		# Create an appropriately-sized surface now.
		(width, height) = (text_extents.width + 2, text_extents.height)
		(gl_width, gl_height) = (self._next_pwr2(width), self._next_pwr2(height))

		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, gl_width, gl_height)
		cctx = cairo.Context(surface)
		self._cctx_set_font(cctx, self._selected_font)

		# Upscale for OpenGL
		cctx.scale(gl_width / width, gl_height / height)

		# And draw text on it
		print(text_extents)
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
		texture = OpenGLTexture(texid = texture_id, dimension = Vector2d(width, height), surface_dimension = Vector2d(width, height), filename = None)
		return texture


	def font_select(self, fontname, fontsize, fontcolor = None):
		self._selected_font = SelectedFont(name = fontname, size = fontsize, color = fontcolor)

	def text(self, pos, text, anchor = "tl"):
		texture = self.render_text_to_texture(text)
		self.blit(texture, offset = pos)

import cairo
import collections
from geo import Vector2d, Box2d
from OpenGL.GL import *

OpenGLTexture = collections.namedtuple("OpenGLTexture", [ "texid", "dimension", "surface_dimension", "filename" ])
OpenGLTexturePromise = collections.namedtuple("OpenGLTexturePromise", [ "dimension", "filename", "texture" ])


class OpenGLContext(object):
	_depth = 1

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
		print(source)


#		if source.texid != 1:
#			return


		depth = 0

		glBindTexture(GL_TEXTURE_2D, source.texid)

#		glRotate(10, 0, 0, 1)

		glPushMatrix()
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


	def font_select(self, *args, **kwargs):
		pass

	def text(self, *args, **kwargs):
		pass

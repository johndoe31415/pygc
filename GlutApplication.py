#!/usr/bin/python3
import sys
import enum
import time
import cwrap
from geo import Vector2d, Box2d
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class MouseButton(enum.IntEnum):
	LeftButton = 0
	MiddleButton = 1
	RightButton = 2
	WheelUp = 3
	WheelDown = 4

class MouseButtonAction(enum.IntEnum):
	ButtonDown = 0
	ButtonUp = 1

class GlutApplication(object):
	def __init__(self, glasscockpit, data_callback = None):
		self._data_callback = data_callback
		self._screen_ctx = cwrap.OpenGLContext()
		self._glasscockpit = glasscockpit
		self._initialize_opengl()

	def _initialize_opengl(self):
		glutInit(1, "None")
		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_STENCIL | GLUT_MULTISAMPLE)
		glutInitWindowSize(self._glasscockpit.screen_dimension.x, self._glasscockpit.screen_dimension.y)
		glutInitWindowPosition(200, 200)

		self._window = glutCreateWindow(b"Glass Cockpit")

		glutDisplayFunc(self._gl_display)
		glutIdleFunc(self._gl_idle)
		glutKeyboardFunc(self._gl_keyboard)
		glutReshapeFunc(self._gl_reshape)

		glViewport(0, 0, self._glasscockpit.screen_dimension.x, self._glasscockpit.screen_dimension.y)
		glClearColor(0.5, 0.5, 0.5, 0)
		glClear(GL_COLOR_BUFFER_BIT)

		glEnable(GL_TEXTURE_2D)
		glEnable(GL_ALPHA_TEST)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, 1, 0, 1, -1, 1)
		glScale(1 / self._glasscockpit.screen_dimension.x, -1 / self._glasscockpit.screen_dimension.y, 1)
		glTranslate(0, -self._glasscockpit.screen_dimension.y, 0)

		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	def _gl_reshape(self, width, height):
		aspect = self._glasscockpit.screen_dimension.ratio

		height_at_fullwidth = width / aspect
		actual_height = min(height_at_fullwidth, height)
		scale = actual_height / self._glasscockpit.screen_dimension.y
#		width = height * aspect
#		print(height, width)
		print(height)


		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, 1, 0, 1, -1, 1)
		glScale(scale / self._glasscockpit.screen_dimension.x, -scale / self._glasscockpit.screen_dimension.y, 1)
		glTranslate(0, -720, 0)

	def _gl_idle(self):
		self._gl_display()

	def _draw_test_square(self, box, zvalue = 0):
		vertices = list(box)
		print("Red %s, Green, %s, Blue %s and %s" % (vertices[0], vertices[1], vertices[2], vertices[3]))
		glBegin(GL_QUADS)
		glColor3f(1, 0, 0)
		glVertex3f(vertices[0][0], vertices[0][1], zvalue)
		glColor3f(0, 1, 0)
		glVertex3f(vertices[1][0], vertices[1][1], zvalue)
		glColor3f(0, 0, 1)
		glVertex3f(vertices[2][0], vertices[2][1], zvalue)
		glVertex3f(vertices[3][0], vertices[3][1], zvalue)
		glEnd()

	def _gl_display(self):
		self._data_callback()
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		self._glasscockpit.render_opengl(self._screen_ctx)
#		self._draw_test_square(Box2d(Vector2d(0, 0), Vector2d(100, 100)), 0)

		glutSwapBuffers(1)

	def _gl_keyboard(self, key, pos_x, pos_y):
		if key == b"\x1b":
			sys.exit(0)

	@classmethod
	def run(cls, glasscockpit, frametime_millis, data_callback = None):
		app = cls(glasscockpit, data_callback = data_callback)
		glutMainLoop()

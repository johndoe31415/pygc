#!/usr/bin/python3
import sys
import enum
import time
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
	def __init__(self, glasscockpit):
		self._glasscockpit = glasscockpit
		self._initialize_opengl()

	def _initialize_opengl(self):
		glutInit(1, "None")
		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_MULTISAMPLE)
		glEnable(GL_MULTISAMPLE)
		glutInitWindowSize(self._glasscockpit.screen_dimension.x, self._glasscockpit.screen_dimension.y)
		glutInitWindowPosition(200, 200)

		self._window = glutCreateWindow(b"Glass Cockpit")

		glutDisplayFunc(self._draw_gl_scene)
		glutIdleFunc(self._gl_idle)
		glutKeyboardFunc(self._gl_keyboard)

		glClearColor(1.0, 1.0, 1.0, 0.0)
		glClearDepth(1.0)
		glDepthFunc(GL_LESS)
		glEnable(GL_DEPTH_TEST)
		glShadeModel(GL_SMOOTH)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(45.0, self._glasscockpit.screen_dimension.x / self._glasscockpit.screen_dimension.y, 0.1, 100.0)
		glMatrixMode(GL_MODELVIEW)


		# Re-init....
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

		glViewport(0, 0, self._glasscockpit.screen_dimension.x, self._glasscockpit.screen_dimension.y)
		glClearDepth(1)
		glClearColor(0, 0, 0, 0)
		glClear(GL_COLOR_BUFFER_BIT)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self._glasscockpit.screen_dimension.x / self._glasscockpit.screen_dimension.y, 0, 1, -1, 1)
		glScale(0.1, 0.1, 1)


	def _draw_test_square(self, box):
		vertices = list(box)
		print("Red %s, Green, %s, Blue %s and %s" % (vertices[0], vertices[1], vertices[2], vertices[3]))
		glBegin(GL_QUADS)
		glColor3f(1, 0, 0)
		glVertex3f(vertices[0][0], vertices[0][1], 0)
		glColor3f(0, 1, 0)
		glVertex3f(vertices[1][0], vertices[1][1], 0)
		glColor3f(0, 0, 1)
		glVertex3f(vertices[2][0], vertices[2][1], 0)
		glVertex3f(vertices[3][0], vertices[3][1], 0)
		glEnd()

	def _draw_gl_scene(self):
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		self._draw_test_square(Box2d(Vector2d(0, 0), Vector2d(1, 1)))

		glutSwapBuffers(1)

	def _gl_idle(self):
		pass

	def _gl_keyboard(self, key, pos_x, pos_y):
		if key == b"\x1b":
			sys.exit(0)

	@classmethod
	def run(cls, glasscockpit, frametime_millis, data_callback = None):
		app = cls(glasscockpit)
		glutMainLoop()

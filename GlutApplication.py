#!/usr/bin/python3
import sys
import enum
import time
import cwrap
from geo import Vector2d, Box2d
from StopWatch import StopWatch
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
	def __init__(self, glasscockpit, data_callback = None, fullscreen = False):
		self._data_callback = data_callback
		self._screen_ctx = cwrap.OpenGLContext()
		self._glasscockpit = glasscockpit
		self._initialize_opengl(fullscreen = fullscreen)
		self._fps_timesum = 0
		self._fps_timecnt = 0

	def _initialize_opengl(self, fullscreen = False):
		glutInit(1, "None")
		glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_MULTISAMPLE)
		glutInitWindowSize(self._glasscockpit.screen_dimension.x, self._glasscockpit.screen_dimension.y)
		glutInitWindowPosition(200, 200)

		self._window = glutCreateWindow(b"Glass Cockpit")
		if fullscreen:
			glutFullScreen()

		glutDisplayFunc(self._gl_display)
		glutIdleFunc(self._gl_idle)
		glutKeyboardFunc(self._gl_keyboard)
		glutReshapeFunc(self._gl_reshape)

		glViewport(0, 0, self._glasscockpit.screen_dimension.x, self._glasscockpit.screen_dimension.y)
		glClearColor(0.5, 0.5, 0.5, 0)
		glClear(GL_COLOR_BUFFER_BIT)

		glEnable(GL_TEXTURE_2D)
		glEnable(GL_ALPHA_TEST)

		glEnable(GL_BLEND)
		glBlendEquation(GL_FUNC_ADD)
		glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)

		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glOrtho(0, self._glasscockpit.screen_dimension.x, self._glasscockpit.screen_dimension.y, 0, -1, 1)

	def _gl_reshape(self, width, height):
		aspect = self._glasscockpit.screen_dimension.ratio
		max_width = height * aspect
		window_width = int(min(width, max_width))
		window_height = round(window_width / aspect)

		glViewport((width - window_width) // 2, (height - window_height) // 2, window_width, window_height)
		glClear(GL_COLOR_BUFFER_BIT)

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
		try:
			t0 = time.time()
			self._gl_display_gc()
			t1 = time.time()
			self._fps_timesum += (t1 - t0)
			self._fps_timecnt += 1
			if self._fps_timecnt == 10:
				t = self._fps_timesum / self._fps_timecnt
				print("Average %.1f ms = %.1f fps (over %d frames)" % (t * 1000, 1 / t, self._fps_timecnt))
				self._fps_timecnt = 0
				self._fps_timesum = 0
		except GLError as e:
			print("OpenGL error")
			sys.exit(1)
		except KeyboardInterrupt:
			sys.exit(0)

	def _gl_display_gc(self):
		self._data_callback()
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity()

		glClear(GL_COLOR_BUFFER_BIT)
		self._glasscockpit.render_opengl(self._screen_ctx)
#		self._draw_test_square(Box2d(Vector2d(0, 0), Vector2d(100, 100)), 0)

		glutSwapBuffers(1)

	def _gl_keyboard(self, key, pos_x, pos_y):
		if key == b"\x1b":
			sys.exit(0)

	@classmethod
	def run(cls, glasscockpit, frametime_millis, data_callback = None, fullscreen = False):
		app = cls(glasscockpit, data_callback = data_callback, fullscreen = fullscreen)
		glutMainLoop()

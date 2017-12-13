#       pygpufractal - Fractal computation on GPU using GLSL.
#       Copyright (C) 2017-2017 Johannes Bauer
#
#       This file is part of pygpufractal.
#
#       pygpufractal is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; this program is ONLY licensed under
#       version 3 of the License, later versions are explicitly excluded.
#
#       pygpufractal is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with pygpufractal; if not, write to the Free Software
#       Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#       Johannes Bauer <JohannesBauer@gmx.de>

import unittest
import random
from .. import Viewport2d, Vector2d

class Viewport2dTests(unittest.TestCase):
	def test_set(self):
		v = Viewport2d(device_width = 640, device_height = 480)
		self.assertAlmostEqual(v.device_size.x, 640)
		self.assertAlmostEqual(v.device_size.y, 480)

	def test_logical_lower(self):
		v = Viewport2d(device_width = 640, device_height = 480, logical_center_x = 3, logical_center_y = 5, logical_width = 1, logical_height = 10)
		c = v.logical_lower
		self.assertAlmostEqual(c.x, 2.5)
		self.assertAlmostEqual(c.y, 0)

	def test_logical_upper(self):
		v = Viewport2d(device_width = 640, device_height = 480, logical_center_x = 3, logical_center_y = 5, logical_width = 1, logical_height = 10)
		c = v.logical_upper
		self.assertAlmostEqual(c.x, 3.5)
		self.assertAlmostEqual(c.y, 10)

	def test_device_to_logical(self):
		v = Viewport2d(device_width = 640, device_height = 480, logical_center_x = 0, logical_center_y = 0, logical_width = 1, logical_height = 10)
		c = v.device_to_logical(0, 0)
		self.assertAlmostEqual(c.x, -0.5)
		self.assertAlmostEqual(c.y, -5)

		c = v.device_to_logical(640, 0)
		self.assertAlmostEqual(c.x, 0.5)
		self.assertAlmostEqual(c.y, -5)

		c = v.device_to_logical(100, 100)
		self.assertAlmostEqual(c.x, -0.34375)
		self.assertAlmostEqual(c.y, -2.916666667)

		v = Viewport2d(device_width = 640, device_height = 480, logical_center_x = 3, logical_center_y = 5, logical_width = 1, logical_height = 10)
		c = v.device_to_logical(0, 0)
		self.assertAlmostEqual(c.x, 2.5)
		self.assertAlmostEqual(c.y, 0)

		c = v.device_to_logical(640, 480)
		self.assertAlmostEqual(c.x, 3.5)
		self.assertAlmostEqual(c.y, 10)

		c = v.device_to_logical(v.device_size.x / 2, v.device_size.y / 2)
		self.assertAlmostEqual(c.x, 3)
		self.assertAlmostEqual(c.y, 5)

	def test_zoom(self):
		v = Viewport2d(device_width = 640, device_height = 480, logical_center_x = 3, logical_center_y = 5, logical_width = 7, logical_height = 11)
		old_logical_center = v.logical_center
		old_logical_size = v.logical_size
		v.zoom_in(2)

		# Center hasn't moved, but size has changed
		self.assertEqual(v.logical_center, old_logical_center)
		self.assertNotEqual(v.logical_size, old_logical_size)

		# Assert mid-of-screen still maps to logical center point
		c = v.device_to_logical(v.device_size.x / 2, v.device_size.y / 2)
		self.assertAlmostEqual(c.x, 3)
		self.assertAlmostEqual(c.y, 5)

		# But low point now maps differently
		c = v.device_to_logical(0, 0)
		self.assertAlmostEqual(c.x, 1.25)
		self.assertAlmostEqual(c.y, 2.25)

		# Now zoom back out
		v.zoom_out(2)
		self.assertEqual(v.logical_center, old_logical_center)
		self.assertEqual(v.logical_size, old_logical_size)

	def test_logical_to_device(self):
		v = Viewport2d(device_width = 640, device_height = 480, logical_center_x = 3, logical_center_y = 5, logical_width = 7, logical_height = 11)
		c = v.logical_to_device(3, 5)
		self.assertAlmostEqual(c.x, 640 / 2)
		self.assertAlmostEqual(c.y, 480 / 2)

		c = v.logical_to_device(3 - (7 / 2), 5 - (11 / 2))
		self.assertAlmostEqual(c.x, 0)
		self.assertAlmostEqual(c.y, 0)

		c = v.logical_to_device(3 + (7 / 2), 5 + (11 / 2))
		self.assertAlmostEqual(c.x, 640)
		self.assertAlmostEqual(c.y, 480)

		c = v.logical_to_device(3 + (7 / 2), 5 - (11 / 2))
		self.assertAlmostEqual(c.x, 640)
		self.assertAlmostEqual(c.y, 0)

	def test_logical_device_logical(self):
		v = Viewport2d(device_width = random.randint(10, 10000), device_height = random.randint(10, 10000),
				logical_center_x = (random.random() * 100) - 50, logical_center_y = (random.random() * 100) - 50,
				logical_width = (random.random() * 100) + 0.1, logical_height = (random.random() * 100) + 0.1)
		for i in range(30):
			dx = random.randint(0, v.device_size.x)
			dy = random.randint(0, v.device_size.y)
			logical = v.device_to_logical(dx, dy)
			device = v.logical_to_device(logical.x, logical.y)
			self.assertAlmostEqual(device.x, dx)
			self.assertAlmostEqual(device.y, dy)
			logical2 = v.device_to_logical(device.x, device.y)
			self.assertAlmostEqual(logical2.x, logical.x)
			self.assertAlmostEqual(logical2.y, logical.y)

	def test_move_logical_to_device(self):
		v = Viewport2d(device_width = 640, device_height = 480, logical_center_x = 3, logical_center_y = 5, logical_width = 7, logical_height = 11)
		v.move_device_point_to_logical(123, 456, 1.23, 4.56)
		self.assertEqual(v.logical_to_device(1.23, 4.56), Vector2d(123, 456))
		self.assertEqual(v.device_to_logical(123, 456), Vector2d(1.23, 4.56))

	def test_zoom_in_around_logical(self):
		v = Viewport2d(device_width = 640, device_height = 480, logical_center_x = 3, logical_center_y = 5, logical_width = 7, logical_height = 11)
		zoom_center = Vector2d(3.456, 2.345)
		zoom_ctr_device_before = v.logical_to_device(zoom_center.x, zoom_center.y)
		v.zoom_in_around_logical(1.2345, zoom_center.x, zoom_center.y)
		zoom_ctr_device_after = v.logical_to_device(zoom_center.x, zoom_center.y)
		self.assertEqual(zoom_ctr_device_before, zoom_ctr_device_after)

	def test_zoom_in_around_device(self):
		v = Viewport2d(device_width = 640, device_height = 480, logical_center_x = 3, logical_center_y = 5, logical_width = 7, logical_height = 11)
		zoom_center = Vector2d(123, 456)
		zoom_ctr_logical_before = v.device_to_logical(zoom_center.x, zoom_center.y)
		v.zoom_in_around_device(1.2345, zoom_center.x, zoom_center.y)
		zoom_ctr_logical_after = v.device_to_logical(zoom_center.x, zoom_center.y)
		self.assertEqual(zoom_ctr_logical_before, zoom_ctr_logical_after)



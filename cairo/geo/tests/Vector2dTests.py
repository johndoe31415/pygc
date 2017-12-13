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
from .. import Vector2d

class Vector2dTests(unittest.TestCase):
	def test_set(self):
		v = Vector2d(-1, 5)
		self.assertAlmostEqual(v.x, -1)
		self.assertAlmostEqual(v.y, 5)

	def test_add(self):
		v = Vector2d(-1, 5) + Vector2d(9, 8)
		self.assertAlmostEqual(v.x, -1 + 9)
		self.assertAlmostEqual(v.y, 5 + 8)

	def test_sub(self):
		v = Vector2d(-1, 5) - Vector2d(9, 8)
		self.assertAlmostEqual(v.x, -1 - 9)
		self.assertAlmostEqual(v.y, 5 - 8)

	def test_mul(self):
		v = Vector2d(-1, 5) * 2.5
		self.assertAlmostEqual(v.x, -2.5)
		self.assertAlmostEqual(v.y, 12.5)

		v = 2.5 * Vector2d(-1, 5)
		self.assertAlmostEqual(v.x, -2.5)
		self.assertAlmostEqual(v.y, 12.5)

	def test_div(self):
		v = Vector2d(-1, 5) / 2.5
		self.assertAlmostEqual(v.x, -0.4)
		self.assertAlmostEqual(v.y, 2)

	def test_length(self):
		self.assertAlmostEqual(Vector2d(1, 0).length(), 1)
		self.assertAlmostEqual(Vector2d(0, 1).length(), 1)
		self.assertAlmostEqual(Vector2d(1, 1).length(), 1.4142135623730951)
		self.assertAlmostEqual(Vector2d(1, 10).length(), 10.04987562112089)

	def test_comp_div(self):
		v = Vector2d(-1, 5).comp_div(Vector2d(9, 12))
		self.assertAlmostEqual(v.x, -1 / 9)
		self.assertAlmostEqual(v.y, 5 / 12)

	def test_comp_mul(self):
		v = Vector2d(-1, 5).comp_mul(Vector2d(9, 12))
		self.assertAlmostEqual(v.x, -1 * 9)
		self.assertAlmostEqual(v.y, 5 * 12)

	def test_eq_neq(self):
		self.assertEqual(Vector2d(99, 3), Vector2d(99, 3))
		self.assertNotEqual(Vector2d(99, 3), Vector2d(99, 3.1))
		self.assertNotEqual(Vector2d(99, 3), Vector2d(99.1, 3))


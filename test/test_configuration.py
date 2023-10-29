"""
dralithus/test/test_configuration.py: Unit and integration test for the top-level dralithus script.
"""
# Copyright 2023. Sumanth Vepa. svepa@milestone42.com
#
# This file is part of dralithus-core.
#
# dralithus-core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dralithus-core is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dralithus-core. If not, see <https://www.gnu.org/licenses/>.
import os.path
import unittest

from dralithus import configuration


class TestConfiguration(unittest.TestCase):
  """ Unit tests for the top-level dralithus script. """
  def test_read_minimal(self):
    """
      Test that reading a minimal configuration  file works.
      TODO: Implement this.
    """
    filename = os.path.join(
      os.path.dirname(os.path.realpath(__file__)), 'sample0.yaml')
    config: dict[str, dict] = configuration.read(filename)
    self.assertTrue(isinstance(config, dict))
    self.assertTrue('meta' in config.keys())
    metadata: dict[str, str] = config.get('meta')
    self.assertTrue(isinstance(metadata, dict))
    self.assertTrue('description' in metadata.keys())
    self.assertEqual(
      metadata.get('description'),
      'sample0: A single line description')

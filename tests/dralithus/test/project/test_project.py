"""
  test_project.py: Unit tests for project facade classes.
"""
# -------------------------------------------------------------------
# test_project.py: Unit tests for project facade classes.
#
# Copyright (C) 2026 Sumanth Vepa.
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License a
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <https://www.gnu.org/licenses/>.
# -------------------------------------------------------------------
from pathlib import Path
import unittest

from dralithus.project.project import PythonProject


class TestPythonProject(unittest.TestCase):
  """
    Unit tests for the PythonProject class.
  """
  _PROJECT_CLASS = PythonProject
  _PYTHON = Path('/usr/bin/python3')

  def test_create_delegates_to_create_step_with_dry_run_false(
      self
  ) -> None:
    """
      Verify that create delegates with dry_run set to False.

      :return: None
    """
    self.fail(
      'TODO checkpoint 2: add red assertion for '
      'PythonProject.create(dry_run=False) facade delegation')

  def test_create_delegates_to_create_step_with_dry_run_true(
      self
  ) -> None:
    """
      Verify that create delegates with dry_run set to True.

      :return: None
    """
    self.fail(
      'TODO checkpoint 2: add red assertion for '
      'PythonProject.create(dry_run=True) facade delegation')

  def test_update_raises_not_implemented_error(self) -> None:
    """
      Verify that update raises NotImplementedError.

      :return: None
    """
    self.fail(
      'TODO checkpoint 2: add red assertion for '
      'PythonProject.update() placeholder behavior')

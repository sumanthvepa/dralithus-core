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
from unittest import mock

from dralithus.test.project import project_context
from dralithus.project.project import Project, PythonProject


_MODULE = 'dralithus.project.project'


class TestPythonProject(unittest.TestCase):
  """
    Unit tests for the PythonProject class.
  """
  _PROJECT_CLASS = PythonProject
  _PYTHON = Path('/usr/bin/python3')

  def test_project_is_abstract(self) -> None:
    """
      Verify that Project cannot be instantiated directly.

      :return: None
    """
    with project_context() as (_project_root, context):
      with self.assertRaises(TypeError):
        # noinspection PyAbstractClass
        Project(context)  # type: ignore[abstract]  # pylint: disable=abstract-class-instantiated

  def test_create_delegates_to_create_step_with_dry_run_false(
      self
  ) -> None:
    """
      Verify that create delegates with dry_run set to False.

      :return: None
    """
    with project_context() as (_project_root, context):
      with mock.patch(f'{_MODULE}.CreatePythonProjectStep') as step_class:
        project = self._PROJECT_CLASS(context, self._PYTHON)
        project.create(dry_run=False)
      step_class.assert_called_once_with(context, self._PYTHON)
      step_class.return_value.run.assert_called_once_with(False)

  def test_create_delegates_to_create_step_with_dry_run_true(
      self
  ) -> None:
    """
      Verify that create delegates with dry_run set to True.

      :return: None
    """
    with project_context() as (_project_root, context):
      with mock.patch(f'{_MODULE}.CreatePythonProjectStep') as step_class:
        project = self._PROJECT_CLASS(context, self._PYTHON)
        project.create(dry_run=True)
      step_class.assert_called_once_with(context, self._PYTHON)
      step_class.return_value.run.assert_called_once_with(True)

  def test_update_raises_not_implemented_error(self) -> None:
    """
      Verify that update raises NotImplementedError.

      :return: None
    """
    with project_context() as (_project_root, context):
      with mock.patch(f'{_MODULE}.CreatePythonProjectStep') as step_class:
        project = self._PROJECT_CLASS(context, self._PYTHON)
        with self.assertRaisesRegex(
            NotImplementedError,
            r'PythonProject\.update\(\) is not implemented yet'
        ):
          project.update()
      step_class.return_value.run.assert_not_called()

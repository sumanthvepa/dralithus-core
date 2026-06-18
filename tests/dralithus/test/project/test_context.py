"""
  test_context.py: Unit tests for ProjectContext.
"""
# -------------------------------------------------------------------
# test_context.py: Unit tests for ProjectContext.
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
from tempfile import TemporaryDirectory
import unittest

from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError


class TestProjectContext(unittest.TestCase):
  """
    Unit tests for the ProjectContext class.
  """
  def test_default_venv_name_is_venv(self) -> None:
    """
      Verify that the default venv name is venv.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)

      self.assertEqual('venv', context.venv_name)

  def test_default_venv_path_uses_venv_name(self) -> None:
    """
      Verify that the default venv path uses the default venv name.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)

      self.assertEqual(project_root / 'venv', context.venv_path)

  def test_default_venv_python_uses_venv_path(self) -> None:
    """
      Verify that the default venv Python path uses the venv path.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)

      self.assertEqual(project_root / 'venv' / 'bin' / 'python',
                       context.venv_python)

  def test_custom_venv_name_updates_derived_paths(self) -> None:
    """
      Verify that a custom venv name updates derived paths.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root, venv_name='env')

      self.assertEqual('env', context.venv_name)
      self.assertEqual(project_root / 'env', context.venv_path)
      self.assertEqual(project_root / 'env' / 'bin' / 'python',
                       context.venv_python)

  def test_rejects_empty_venv_name(self) -> None:
    """
      Verify that empty venv names are rejected.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Venv name must not be empty'
      ):
        ProjectContext(project_root=project_root, venv_name='')

  def test_rejects_current_directory_venv_name(self) -> None:
    """
      Verify that current-directory venv names are rejected.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Venv name must not contain path components'
      ):
        ProjectContext(project_root=project_root, venv_name='.')

  def test_rejects_parent_directory_venv_name(self) -> None:
    """
      Verify that parent-directory venv names are rejected.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Venv name must not contain path components'
      ):
        ProjectContext(project_root=project_root, venv_name='..')

  def test_rejects_absolute_venv_path(self) -> None:
    """
      Verify that absolute venv paths are rejected.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Venv name must not contain path components'
      ):
        ProjectContext(
          project_root=project_root,
          venv_name=str(project_root / 'venv'))

  def test_rejects_nested_venv_name(self) -> None:
    """
      Verify that nested venv names are rejected.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Venv name must not contain path components'
      ):
        ProjectContext(project_root=project_root, venv_name='env/venv')

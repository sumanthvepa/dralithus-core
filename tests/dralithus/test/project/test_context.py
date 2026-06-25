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

  def test_default_package_name_is_dralithus(self) -> None:
    """
      Verify that the default package name is dralithus.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)

      self.assertEqual('dralithus', context.package_name)

  def test_custom_package_name_is_stored(self) -> None:
    """
      Verify that a custom package name is stored.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='mypkg')

      self.assertEqual('mypkg', context.package_name)

  def test_default_copyright_holder_is_sumanth_vepa(self) -> None:
    """
      Verify that the default copyright holder is Sumanth Vepa.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)

      self.assertEqual('Sumanth Vepa', context.copyright_holder)

  def test_default_copyright_year_is_none(self) -> None:
    """
      Verify that the default copyright year is unspecified.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)

      self.assertIsNone(context.copyright_year)

  def test_custom_copyright_settings_are_stored(self) -> None:
    """
      Verify that custom copyright settings are stored.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        copyright_holder='Milestone 42',
        copyright_year=2030)

      self.assertEqual('Milestone 42', context.copyright_holder)
      self.assertEqual(2030, context.copyright_year)

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

  def test_rejects_empty_package_name(self) -> None:
    """
      Verify that empty package names are rejected.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Package name must not be empty'
      ):
        ProjectContext(project_root=project_root, package_name='')

  def test_rejects_non_identifier_package_name(self) -> None:
    """
      Verify that non-identifier package names are rejected.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Package name is not a valid identifier'
      ):
        ProjectContext(project_root=project_root, package_name='my-pkg')

  def test_rejects_keyword_package_name(self) -> None:
    """
      Verify that Python keywords are rejected as package names.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Package name must not be a Python keyword'
      ):
        ProjectContext(project_root=project_root, package_name='class')

  def test_rejects_uppercase_package_name(self) -> None:
    """
      Verify that uppercase package names are rejected.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Package name must be lowercase'
      ):
        ProjectContext(project_root=project_root, package_name='MyPkg')

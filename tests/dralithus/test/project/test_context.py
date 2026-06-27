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
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from dralithus.project.context import ProjectContext, ProjectContextDict
from dralithus.project.copyright_header import CopyrightHeader
from dralithus.project.error import DralithusProjectError


class TestProjectContext(unittest.TestCase):
  """
    Unit tests for the ProjectContext class.
  """
  @staticmethod
  def _copyright_header(
    copyright_holder: str = 'Sumanth Vepa',
    copyright_year: int = 2026
  ) -> CopyrightHeader:
    """
      Return a copyright header renderer for context tests.

      :param copyright_holder: The copyright holder name
      :param copyright_year: The copyright year
      :return: The copyright header renderer
    """
    return CopyrightHeader(
      '{{ description }}\n'
      'Copyright (C) {{ copyright_year }} {{ copyright_holder }}.\n',
      copyright_holder,
      copyright_year)

  def test_default_venv_name_is_venv(self) -> None:
    """
      Verify that the default venv name is venv.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_header=self._copyright_header())

      self.assertEqual('venv', context.venv_name)

  def test_custom_package_name_is_stored(self) -> None:
    """
      Verify that a custom package name is stored.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='mypkg',
        copyright_header=self._copyright_header())

      self.assertEqual('mypkg', context.package_name)

  def test_copyright_header_is_stored(self) -> None:
    """
      Verify that the supplied copyright header is stored.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      copyright_header = self._copyright_header('Milestone 42', 2020)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_header=copyright_header)

      self.assertIs(copyright_header, context.copyright_header)

  def test_default_venv_path_uses_venv_name(self) -> None:
    """
      Verify that the default venv path uses the default venv name.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_header=self._copyright_header())

      self.assertEqual(project_root / 'venv', context.venv_path)

  def test_default_venv_python_uses_venv_path(self) -> None:
    """
      Verify that the default venv Python path uses the venv path.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_header=self._copyright_header())

      self.assertEqual(project_root / 'venv' / 'bin' / 'python',
                       context.venv_python)

  def test_custom_venv_name_updates_derived_paths(self) -> None:
    """
      Verify that a custom venv name updates derived paths.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_header=self._copyright_header(),
        venv_name='env')

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
        ProjectContext(
          project_root=project_root,
          package_name='sample',
          copyright_header=self._copyright_header(),
          venv_name='')

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
        ProjectContext(
          project_root=project_root,
          package_name='sample',
          copyright_header=self._copyright_header(),
          venv_name='.')

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
        ProjectContext(
          project_root=project_root,
          package_name='sample',
          copyright_header=self._copyright_header(),
          venv_name='..')

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
          package_name='sample',
          copyright_header=self._copyright_header(),
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
        ProjectContext(
          project_root=project_root,
          package_name='sample',
          copyright_header=self._copyright_header(),
          venv_name='env/venv')

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
        ProjectContext(
          project_root=project_root,
          package_name='',
          copyright_header=self._copyright_header())

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
        ProjectContext(
          project_root=project_root,
          package_name='my-pkg',
          copyright_header=self._copyright_header())

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
        ProjectContext(
          project_root=project_root,
          package_name='class',
          copyright_header=self._copyright_header())

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
        ProjectContext(
          project_root=project_root,
          package_name='MyPkg',
          copyright_header=self._copyright_header())

  def test_as_dict_contains_all_fields(self) -> None:
    """
      Verify as_dict returns all fields with correct values.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      copyright_header = self._copyright_header()
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_header=copyright_header)

      result = context.as_dict()

      expected: ProjectContextDict = {
        'project_root': project_root,
        'package_name': 'sample',
        'copyright_header': copyright_header,
        'venv_name': 'venv',
        'venv_path': project_root / 'venv',
        'venv_python': project_root / 'venv' / 'bin' / 'python',
      }
      self.assertEqual(expected, result)

  def test_as_dict_reflects_custom_venv_name(self) -> None:
    """
      Verify as_dict derived paths update when venv_name is custom.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_header=self._copyright_header(),
        venv_name='env')

      result = context.as_dict()

      self.assertEqual('env', result['venv_name'])
      self.assertEqual(project_root / 'env', result['venv_path'])
      self.assertEqual(
        project_root / 'env' / 'bin' / 'python',
        result['venv_python'])

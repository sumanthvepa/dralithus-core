"""
  test_packages3.py: Unit tests for packages3.
"""
# -------------------------------------------------------------------
# test_packages3.py: Unit tests for packages3.
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

from dralithus.project.error import DralithusProjectError
from dralithus.project.packages3 import Packages3


class TestPackages3(unittest.TestCase):
  """
    Unit tests for the Packages3 class.
  """

  @staticmethod
  def _write_packages_txt(project_root: Path, text: str) -> None:
    """
      Write packages.txt in the test project root.

      :param project_root: The test project root directory
      :param text: The file text
      :return: None
    """
    (project_root / 'packages.txt').write_text(
      text, encoding='utf-8')

  @staticmethod
  def _write_local_packages_txt(project_root: Path, text: str) -> None:
    """
      Write local-packages.txt in the test project root.

      :param project_root: The test project root directory
      :param text: The file text
      :return: None
    """
    (project_root / 'local-packages.txt').write_text(
      text, encoding='utf-8')

  def test_empty_project_root_raises_error(self) -> None:
    """
      Verify from_project_root raises if packages.txt is missing.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      with self.assertRaises(DralithusProjectError) as context:
        Packages3.from_project_root(project_root)

      self.assertEqual(
        str(context.exception),
        'No packages.txt file found in project root')

  def test_project_root_returns_packages3(self) -> None:
    """
      Verify from_project_root reads the packages3 artifacts.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._write_packages_txt(
        project_root,
        'requests\n'
        'rich\n')
      self._write_local_packages_txt(
        project_root,
        '../common-lib\n'
        '../tools-lib\n')

      packages = Packages3.from_project_root(project_root)

      self.assertEqual(
        packages.production_dependencies,
        ['requests', 'rich'])
      self.assertEqual(
        packages.dev_dependencies,
        ['mypy', 'pylint', 'parameterized'])
      self.assertEqual(
        packages.local_dependencies,
        ['../common-lib', '../tools-lib'])

  def test_production_dependencies_reads_packages_txt(self) -> None:
    """
      Verify production_dependencies reads packages.txt.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._write_packages_txt(
        project_root,
        '# third-party packages\n'
        '\n'
        'requests\n'
        'rich\n')

      packages = Packages3.from_project_root(project_root)

      self.assertEqual(
        packages.production_dependencies,
        ['requests', 'rich'])

  def test_production_dependencies_ignores_comments(self) -> None:
    """
      Verify production_dependencies ignores blank and comment text.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._write_packages_txt(
        project_root,
        '# third-party packages\n'
        '\n'
        'requests  # HTTP client\n'
        '  rich  \n'
        '  # display library\n')

      packages = Packages3.from_project_root(project_root)

      self.assertEqual(
        packages.production_dependencies,
        ['requests', 'rich'])

  def test_local_dependencies_reads_local_packages_txt(self) -> None:
    """
      Verify local_dependencies reads local-packages.txt.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._write_packages_txt(project_root, '')
      self._write_local_packages_txt(
        project_root,
        '../common-lib\n'
        '../tools-lib\n')

      packages = Packages3.from_project_root(project_root)

      self.assertEqual(
        packages.local_dependencies,
        ['../common-lib', '../tools-lib'])

  def test_local_dependencies_ignores_comments(self) -> None:
    """
      Verify local_dependencies ignores blank and comment text.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._write_packages_txt(project_root, '')
      self._write_local_packages_txt(
        project_root,
        '# local packages\n'
        '\n'
        '../common-lib  # shared library\n'
        '  ../tools-lib  \n')

      packages = Packages3.from_project_root(project_root)

      self.assertEqual(
        packages.local_dependencies,
        ['../common-lib', '../tools-lib'])

  def test_local_dependencies_missing_file_is_empty(self) -> None:
    """
      Verify missing local-packages.txt means no local dependencies.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._write_packages_txt(project_root, '')

      packages = Packages3.from_project_root(project_root)

      self.assertEqual(packages.local_dependencies, [])

  def test_empty_packages_txt_and_no_local_packages_txt(self) -> None:
    """
      Verify an empty packages.txt and no local-packages.txt.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._write_packages_txt(project_root, '')

      packages = Packages3.from_project_root(project_root)

      self.assertEqual(packages.production_dependencies, [])
      self.assertEqual(
        packages.dev_dependencies,
        ['mypy', 'pylint', 'parameterized'])
      self.assertEqual(packages.local_dependencies, [])

  def test_packages_txt_dev_marker_adds_dev_dependencies(self) -> None:
    """
      Verify packages.txt dependencies marked [dev] are dev deps.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._write_packages_txt(
        project_root,
        'requests\n'
        'pytest [dev]\n'
        'rich\n')

      packages = Packages3.from_project_root(project_root)

      self.assertEqual(
        packages.production_dependencies,
        ['requests', 'rich'])
      self.assertEqual(
        packages.dev_dependencies,
        ['mypy', 'pylint', 'parameterized', 'pytest'])

  def test_local_packages_txt_dev_marker_adds_dev_dependencies(
    self
  ) -> None:
    """
      Verify local-packages.txt dependencies marked [dev] are dev deps.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._write_packages_txt(project_root, '')
      self._write_local_packages_txt(
        project_root,
        '../common-lib\n'
        '../test-lib [dev]\n'
        '../tools-lib\n')

      packages = Packages3.from_project_root(project_root)

      self.assertEqual(
        packages.local_dependencies,
        ['../common-lib', '../tools-lib'])
      self.assertEqual(
        packages.dev_dependencies,
        ['mypy', 'pylint', 'parameterized', '../test-lib'])

  def test_dev_dependencies_returns_implicit_dependencies(self) -> None:
    """
      Verify dev_dependencies returns the packages3 implicit baseline.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._write_packages_txt(project_root, '')

      packages = Packages3.from_project_root(project_root)

      self.assertEqual(
        packages.dev_dependencies,
        ['mypy', 'pylint', 'parameterized'])

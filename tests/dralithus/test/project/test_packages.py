"""
  test_packages.py: Unit tests for the Packages model.
"""
# -------------------------------------------------------------------
# test_packages.py: Unit tests for the Packages model.
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
from typing import NamedTuple
import unittest

from parameterized import parameterized

from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages
from dralithus.test import CaseData, CaseExecutor


class PackagesCaseArgs(NamedTuple):
  """
    Hold Packages System artifact contents for a test case.
  """
  packages_txt: str | None
  local_packages_txt: str | None


class PackagesExpected(NamedTuple):
  """
    Hold the expected Packages dependency lists.
  """
  production_dependencies: list[str]
  dev_dependencies: list[str]
  local_dependencies: list[str]


def basic_cases() -> list[tuple[str, CaseData]]:
  """
    Return basic Packages System artifact cases.

    :return: The basic Packages System cases
  """
  return [
    (
      'empty_packages_no_local_packages',
      CaseData(
        args=PackagesCaseArgs(
          packages_txt='',
          local_packages_txt=None),
        expected=PackagesExpected(
          production_dependencies=[],
          dev_dependencies=['mypy', 'pylint', 'parameterized'],
          local_dependencies=[]))),
    (
      'production_and_local_dependencies',
      CaseData(
        args=PackagesCaseArgs(
          packages_txt='requests\nrich\n',
          local_packages_txt='../common-lib\n../tools-lib\n'),
        expected=PackagesExpected(
          production_dependencies=['requests', 'rich'],
          dev_dependencies=['mypy', 'pylint', 'parameterized'],
          local_dependencies=['../common-lib', '../tools-lib']))),
  ]


def comment_and_whitespace_cases() -> list[tuple[str, CaseData]]:
  """
    Return Packages System comment and whitespace cases.

    :return: The comment and whitespace cases
  """
  return [
    (
      'packages_txt_comments_and_whitespace',
      CaseData(
        args=PackagesCaseArgs(
          packages_txt='# third-party packages\n'
          '\n'
          'requests  # HTTP client\n'
          '  rich  \n'
          '  # display library\n',
          local_packages_txt=None),
        expected=PackagesExpected(
          production_dependencies=['requests', 'rich'],
          dev_dependencies=['mypy', 'pylint', 'parameterized'],
          local_dependencies=[]))),
    (
      'local_packages_txt_comments_and_whitespace',
      CaseData(
        args=PackagesCaseArgs(
          packages_txt='',
          local_packages_txt='# local packages\n'
          '\n'
          '../common-lib  # shared library\n'
          '  ../tools-lib  \n'),
        expected=PackagesExpected(
          production_dependencies=[],
          dev_dependencies=['mypy', 'pylint', 'parameterized'],
          local_dependencies=['../common-lib', '../tools-lib']))),
  ]


def dev_marker_cases() -> list[tuple[str, CaseData]]:
  """
    Return Packages System development marker cases.

    :return: The development marker cases
  """
  return [
    (
      'packages_txt_dev_marker',
      CaseData(
        args=PackagesCaseArgs(
          packages_txt='requests\npytest [dev]\nrich\n',
          local_packages_txt=None),
        expected=PackagesExpected(
          production_dependencies=['requests', 'rich'],
          dev_dependencies=[
            'mypy', 'pylint', 'parameterized', 'pytest'],
          local_dependencies=[]))),
    (
      'local_packages_txt_dev_marker',
      CaseData(
        args=PackagesCaseArgs(
          packages_txt='',
          local_packages_txt=(
            '../common-lib\n../test-lib [dev]\n../tools-lib\n')),
        expected=PackagesExpected(
          production_dependencies=[],
          dev_dependencies=[
            'mypy', 'pylint', 'parameterized', '../test-lib'],
          local_dependencies=['../common-lib', '../tools-lib']))),
  ]


def execute_packages_case(args: PackagesCaseArgs) -> PackagesExpected:
  """
    Execute a Packages System artifact case.

    :param args: The Packages System artifact contents
    :return: The dependency lists read from the artifacts
  """
  with TemporaryDirectory() as temp_directory:
    project_root = Path(temp_directory)
    if args.packages_txt is not None:
      (project_root / Packages.PACKAGES_FILENAME).write_text(
        args.packages_txt, encoding='utf-8')
    if args.local_packages_txt is not None:
      (project_root / Packages.LOCAL_PACKAGES_FILENAME).write_text(
        args.local_packages_txt, encoding='utf-8')
    packages = Packages(project_root)
    result = PackagesExpected(
      packages.production_dependencies,
      packages.dev_dependencies,
      packages.local_dependencies)
  return result


class TestPackages(unittest.TestCase, CaseExecutor):
  """
    Unit tests for the Packages class.
  """

  def test_missing_packages_txt_raises(self) -> None:
    """
      Verify constructing over a missing packages.txt raises
      DralithusProjectError identifying the unreadable dependency file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      with self.assertRaises(DralithusProjectError) as context:
        Packages(project_root)
      self.assertEqual(
        f'Could not read dependency file: {packages_txt}',
        str(context.exception))

  def test_dangling_local_packages_symlink_raises(self) -> None:
    """
      Verify constructing over a dangling local-packages.txt symlink
      raises DralithusProjectError instead of silently treating the
      optional file as absent.

      Path.exists follows symlinks and reports False for a dangling
      symlink, so the constructor must detect the entry without
      following the link and then attempt to read it, failing loudly.
      The symlink is left in place; it simply cannot be read.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      (project_root / Packages.PACKAGES_FILENAME).write_text(
        '', encoding='utf-8')
      local_packages_txt = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME)
      local_packages_txt.symlink_to(project_root / 'does-not-exist')
      with self.assertRaises(DralithusProjectError) as context:
        Packages(project_root)
      self.assertEqual(
        f'Could not read dependency file: {local_packages_txt}',
        str(context.exception))
      self.assertTrue(local_packages_txt.is_symlink())

  @parameterized.expand(basic_cases())
  def test_basic_cases(self, _name: str, case: CaseData) -> None:
    """
      Verify basic Packages System artifact behavior.

      :param _name: The test case name
      :param case: The test case
      :return: None
    """
    self.execute(execute_packages_case, case)

  @parameterized.expand(comment_and_whitespace_cases())
  def test_comment_and_whitespace_cases(
    self,
    _name: str,
    case: CaseData
  ) -> None:
    """
      Verify comments and whitespace are ignored.

      :param _name: The test case name
      :param case: The test case
      :return: None
    """
    self.execute(execute_packages_case, case)

  @parameterized.expand(dev_marker_cases())
  def test_dev_marker_cases(self, _name: str, case: CaseData) -> None:
    """
      Verify dependencies marked [dev] become dev dependencies.

      :param _name: The test case name
      :param case: The test case
      :return: None
    """
    self.execute(execute_packages_case, case)

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
from unittest import mock

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

  def test_create_writes_packages_files(self) -> None:
    """
      Verify create writes packages.txt and local-packages.txt into an
      uninitialized project root and returns the dev baseline only.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      packages = Packages.create(project_root)

      self.assertTrue((project_root / Packages.PACKAGES_FILENAME).is_file())
      self.assertTrue((project_root / Packages.LOCAL_PACKAGES_FILENAME).is_file())
      self.assertEqual([], packages.production_dependencies)
      self.assertEqual(
        ['mypy', 'pylint', 'parameterized'], packages.dev_dependencies)
      self.assertEqual([], packages.local_dependencies)

  def test_create_seeds_header_comments(self) -> None:
    """
      Verify create seeds each dependency file with a header comment
      and no actual dependencies.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)

      Packages.create(project_root)

      packages_text = (project_root / Packages.PACKAGES_FILENAME).read_text(
        encoding='utf-8')
      local_text = (project_root / Packages.LOCAL_PACKAGES_FILENAME).read_text(
        encoding='utf-8')
      self.assertTrue(packages_text.startswith('#'))
      self.assertTrue(local_text.startswith('#'))

  def test_create_keeps_existing_packages_txt(self) -> None:
    """
      Verify create leaves an existing packages.txt untouched and
      creates only the missing local-packages.txt.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      packages_txt.write_text('requests\n', encoding='utf-8')

      packages = Packages.create(project_root)

      self.assertEqual(
        'requests\n', packages_txt.read_text(encoding='utf-8'))
      self.assertTrue(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).is_file())
      self.assertEqual(['requests'], packages.production_dependencies)

  def test_create_keeps_existing_local_packages_txt(self) -> None:
    """
      Verify create leaves an existing local-packages.txt untouched
      and creates only the missing packages.txt.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      local_packages_txt = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME)
      local_packages_txt.write_text('../common-lib\n', encoding='utf-8')

      packages = Packages.create(project_root)

      self.assertEqual(
        '../common-lib\n',
        local_packages_txt.read_text(encoding='utf-8'))
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      self.assertTrue(packages_txt.is_file())
      self.assertTrue(
        packages_txt.read_text(encoding='utf-8').startswith('#'))
      self.assertEqual(['../common-lib'], packages.local_dependencies)

  def test_create_keeps_both_existing_files(self) -> None:
    """
      Verify create leaves both existing dependency files untouched
      and reads dependencies from them.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      local_packages_txt = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME)
      packages_txt.write_text('requests\n', encoding='utf-8')
      local_packages_txt.write_text('../common-lib\n', encoding='utf-8')

      packages = Packages.create(project_root)

      self.assertEqual(
        'requests\n', packages_txt.read_text(encoding='utf-8'))
      self.assertEqual(
        '../common-lib\n',
        local_packages_txt.read_text(encoding='utf-8'))
      self.assertEqual(['requests'], packages.production_dependencies)
      self.assertEqual(['../common-lib'], packages.local_dependencies)

  def test_seed_creates_missing_files_and_returns_them(self) -> None:
    """
      Verify seed creates both dependency files in an empty project
      root and returns exactly the paths it created.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      local_packages_txt = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME)

      created = Packages.seed(project_root)

      self.assertEqual([packages_txt, local_packages_txt], created)
      self.assertTrue(packages_txt.is_file())
      self.assertTrue(local_packages_txt.is_file())

  def test_seed_returns_only_created_files(self) -> None:
    """
      Verify seed reports only the files it created, leaving an
      existing dependency file untouched and unreported.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      local_packages_txt = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME)
      packages_txt.write_text('requests\n', encoding='utf-8')

      created = Packages.seed(project_root)

      self.assertEqual([local_packages_txt], created)
      self.assertEqual(
        'requests\n', packages_txt.read_text(encoding='utf-8'))

  def test_seed_returns_empty_when_nothing_missing(self) -> None:
    """
      Verify seed creates and reports nothing when both dependency
      files already exist.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      (project_root / Packages.PACKAGES_FILENAME).write_text(
        'requests\n', encoding='utf-8')
      (project_root / Packages.LOCAL_PACKAGES_FILENAME).write_text(
        '../common-lib\n', encoding='utf-8')

      created = Packages.seed(project_root)

      self.assertEqual([], created)

  def test_seed_does_not_claim_dangling_symlink(self) -> None:
    """
      Verify seed neither replaces nor reports a dangling symlink.

      A dangling symlink fails Path.exists but is still a user-owned
      path entry; exclusive creation refuses it, and seed must not
      claim it as created.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      local_packages_txt = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME)
      local_packages_txt.symlink_to(project_root / 'does-not-exist')

      created = Packages.seed(project_root)

      self.assertEqual([packages_txt], created)
      self.assertTrue(local_packages_txt.is_symlink())

  def test_seed_cleans_up_partial_failure(self) -> None:
    """
      Verify a failed seed removes the files it created before
      raising.

      The first dependency file is written for real; the write of
      the second is forced to fail. The failed seed must remove the
      first file so nothing is left behind.

      :return: None
    """
    real_seed_file = Packages._seed_file  # pylint: disable=protected-access

    def fail_local(path: Path, content: str) -> bool:
      if path.name == Packages.LOCAL_PACKAGES_FILENAME:
        raise OSError('simulated write failure')
      return real_seed_file(path, content)

    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      packages_txt = project_root / Packages.PACKAGES_FILENAME

      with mock.patch.object(
        Packages, '_seed_file', side_effect=fail_local
      ):
        with self.assertRaises(DralithusProjectError) as context:
          Packages.seed(project_root)

      self.assertEqual(
        f'Could not write dependency file: {project_root}',
        str(context.exception))
      self.assertFalse(packages_txt.exists())

  def test_create_never_overwrites_despite_stale_existence_check(
    self
  ) -> None:
    """
      Verify create does not overwrite a file that an existence
      check failed to see.

      Simulates the time-of-check to time-of-use race: the file is
      on disk, but Path.exists reports it missing - as it would for
      a file created concurrently after the check. Creation must be
      exclusive, so the existing content survives.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      packages_txt.write_text('requests\n', encoding='utf-8')

      with mock.patch.object(Path, 'exists', return_value=False):
        Packages.create(project_root)

      self.assertEqual(
        'requests\n', packages_txt.read_text(encoding='utf-8'))

  def test_create_raises_when_packages_txt_unreadable(self) -> None:
    """
      Verify create raises when an existing packages.txt cannot be
      read.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      packages_txt.mkdir()

      with self.assertRaises(DralithusProjectError) as context:
        Packages.create(project_root)
      self.assertEqual(
        f'Could not read dependency file: {packages_txt}',
        str(context.exception))

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

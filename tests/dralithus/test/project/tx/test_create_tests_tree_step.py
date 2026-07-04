"""
  test_create_tests_tree_step.py: Unit tests for
  dralithus.project.tx.create_tests_tree_step.
"""
# -------------------------------------------------------------------
# test_create_tests_tree_step.py: Unit tests for
# dralithus.project.tx.create_tests_tree_step.
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

from dralithus.test.project import (
  FailingWriteFile,
  copyright_header,
  project_context)
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.create_tests_tree_step import (
  CreateTestsTreeStep)
from dralithus.project.tx.execution_step import execute
from dralithus.project.tx.project_state import ProjectState


class TestCreateTestsTreeStep(unittest.TestCase):
  """
    Unit tests for the CreateTestsTreeStep class.

    CreateTestsTreeStep composes a MkdirStep, three
    CreateGitIgnoreFileStep children and a CreatePythonInitFileStep
    with no phase logic of its own, so these tests cover the wiring
    and the created tree through the execute() driver: a full real
    run, a deep dry run with no guarded skipping, a mid-commit
    failure cleaned up by the global abort, and prepare-time
    rejection of unusable targets. The children's exhaustive
    file-type handling is covered by their own suites.
  """
  _PACKAGE_NAME = 'sample'
  _DESCRIPTION = 'sample/test/__init__.py: Unit tests for sample.'

  @classmethod
  def _tests(cls, project_root: Path) -> Path:
    """
      Return the tests directory path.

      :param project_root: The project root directory
      :return: The tests directory path
    """
    return project_root / 'tests'

  @classmethod
  def _package(cls, project_root: Path) -> Path:
    """
      Return the tests/<package_name> directory path.

      :param project_root: The project root directory
      :return: The tests package directory path
    """
    return cls._tests(project_root) / cls._PACKAGE_NAME

  @classmethod
  def _test_package(cls, project_root: Path) -> Path:
    """
      Return the tests/<package_name>/test directory path.

      :param project_root: The project root directory
      :return: The test package directory path
    """
    return cls._package(project_root) / 'test'

  @classmethod
  def _init_py(cls, project_root: Path) -> Path:
    """
      Return the generated test package __init__.py path.

      :param project_root: The project root directory
      :return: The test package __init__.py path
    """
    return cls._test_package(project_root) / '__init__.py'

  # execute: real run

  def test_execute_creates_full_tests_tree(self) -> None:
    """
      Verify execute creates tests/, tests/<package_name>/,
      tests/<package_name>/test/, a .gitignore in each of those
      three directories, and the test package __init__.py.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateTestsTreeStep(context)

      execute(step, context)

      self.assertTrue(self._tests(project_root).is_dir())
      self.assertTrue(self._package(project_root).is_dir())
      self.assertTrue(self._test_package(project_root).is_dir())
      self.assertTrue(
        (self._tests(project_root) / '.gitignore').is_file())
      self.assertTrue(
        (self._package(project_root) / '.gitignore').is_file())
      self.assertTrue(
        (self._test_package(project_root) / '.gitignore').is_file())
      self.assertTrue(self._init_py(project_root).is_file())

  def test_execute_creates_init_py_with_docstring_and_header(
    self
  ) -> None:
    """
      Verify the generated __init__.py holds the module docstring
      and the rendered copyright header.

      :return: None
    """
    with project_context() as (project_root, context):
      header = copyright_header()
      step = CreateTestsTreeStep(context)

      execute(step, context)

      # The rendered-content assertion repeats across step suites; a
      # future refactoring could extract a shared helper.
      # pylint: disable=duplicate-code
      self.assertEqual(
        '"""\n'
        f'  {self._DESCRIPTION}\n'
        '"""\n'
        f'# {self._DESCRIPTION}\n'
        f'# Copyright (C) {header.copyright_year} '
        f'{header.copyright_holder}.\n',
        self._init_py(project_root).read_text(encoding='utf-8'))

  def test_execute_creates_empty_gitignore_files(self) -> None:
    """
      Verify the .gitignore files execute creates are empty.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateTestsTreeStep(context)

      execute(step, context)

      for directory in (
        self._tests(project_root),
        self._package(project_root),
        self._test_package(project_root)
      ):
        self.assertEqual(
          '',
          (directory / '.gitignore').read_text(encoding='utf-8'))

  def test_execute_preserves_preexisting_init_py(self) -> None:
    """
      Verify execute preserves a pre-existing __init__.py in an
      existing tests tree (convergence).

      :return: None
    """
    with project_context() as (project_root, context):
      self._test_package(project_root).mkdir(parents=True)
      init_py = self._init_py(project_root)
      init_py.write_text('# existing\n', encoding='utf-8')
      step = CreateTestsTreeStep(context)

      execute(step, context)

      self.assertEqual(
        '# existing\n', init_py.read_text(encoding='utf-8'))

  def test_execute_aborts_all_owned_work_on_mid_commit_failure(
    self
  ) -> None:
    """
      Verify a child commit failure makes execute abort the whole
      tree: every artifact earlier commits created is removed.

      :return: None
    """
    real_open = Path.open

    with project_context() as (project_root, context):
      failing_path = self._init_py(project_root)

      # The write-failure closure repeats across step suites; a
      # future refactoring could extract a shared helper.
      # pylint: disable=duplicate-code
      def failing_open(
        path: Path,
        mode: str = 'r',
        encoding: str | None = None
      ) -> object:
        # The wrapper (or the caller) is responsible for closing.
        # noinspection PyTypeChecker
        # pylint: disable-next=consider-using-with
        file = real_open(path, mode, encoding=encoding)
        if mode == 'x' and path == failing_path:
          return FailingWriteFile(file)
        return file

      step = CreateTestsTreeStep(context)

      with mock.patch.object(Path, 'open', failing_open):
        with self.assertRaises(DralithusProjectError):
          execute(step, context)

      self.assertFalse(self._tests(project_root).exists())

  def test_execute_prepare_failure_leaves_disk_untouched(self) -> None:
    """
      Verify a prepare failure in a real run propagates before any
      commit, leaving the file system untouched.

      :return: None
    """
    with project_context() as (project_root, context):
      tests_gitignore = self._tests(project_root) / '.gitignore'
      tests_gitignore.mkdir(parents=True)
      step = CreateTestsTreeStep(context)

      with self.assertRaises(DralithusProjectError):
        execute(step, context)

      self.assertTrue(self._tests(project_root).is_dir())
      self.assertTrue(tests_gitignore.is_dir())
      self.assertFalse(self._package(project_root).exists())

  # execute: dry run

  def test_execute_dry_run_validates_deeply_and_creates_nothing(
    self
  ) -> None:
    """
      Verify a dry run against an empty project root validates
      every child through its claims, skips nothing, and creates
      nothing.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateTestsTreeStep(context)

      execute(step, context, dry_run=True)

      self.assertFalse(self._tests(project_root).exists())

  def test_execute_dry_run_rejects_unusable_existing_target(
    self
  ) -> None:
    """
      Verify a dry run rejects an existing but unusable .gitignore
      target.

      :return: None
    """
    with project_context() as (project_root, context):
      (self._tests(project_root) / '.gitignore').mkdir(parents=True)
      step = CreateTestsTreeStep(context)

      with self.assertRaises(DralithusProjectError):
        execute(step, context, dry_run=True)

  # abort

  def test_abort_removes_created_artifacts(self) -> None:
    """
      Verify abort removes the directories and files commit
      created.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateTestsTreeStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse(self._tests(project_root).exists())

  def test_abort_preserves_preexisting_init_py(self) -> None:
    """
      Verify abort preserves a pre-existing __init__.py and its
      tests tree.

      :return: None
    """
    with project_context() as (project_root, context):
      self._test_package(project_root).mkdir(parents=True)
      init_py = self._init_py(project_root)
      init_py.write_text('# existing\n', encoding='utf-8')
      step = CreateTestsTreeStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertEqual(
        '# existing\n', init_py.read_text(encoding='utf-8'))
      self.assertTrue(self._test_package(project_root).is_dir())

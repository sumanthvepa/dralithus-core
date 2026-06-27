"""
  test_create_tests_tree_step.py: Unit tests for
  create_tests_tree_step.
"""
# -------------------------------------------------------------------
# test_create_tests_tree_step.py: Unit tests for
# create_tests_tree_step.
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

from dralithus.test import project_context
from dralithus.project.copyright_header import CopyrightHeader
from dralithus.project.create_tests_tree_step import CreateTestsTreeStep
from dralithus.project.error import DralithusProjectError


class TestCreateTestsTreeStep(unittest.TestCase):
  """
    Unit tests for the CreateTestsTreeStep class.

    CreateTestsTreeStep composes a MkdirStep, three
    CreateGitIgnoreFileStep children, and a CreatePythonInitFileStep
    child, so these tests cover the step's own wiring and behaviour
    (the created tests tree, the generated __init__.py, convergence,
    rollback, and guarded dry-run) rather than re-testing the child
    steps' exhaustive file-type and directory handling, which is
    covered by their own suites.
  """
  _PACKAGE_NAME = 'sample'
  _DESCRIPTION = 'sample/test/__init__.py: Unit tests for sample.'
  _TEMPLATE = (
    '{{ description }}\n'
    'Copyright (C) {{ copyright_year }} {{ copyright_holder }}.\n')

  @classmethod
  def _copyright_header(cls) -> CopyrightHeader:
    """
      Return the copyright header renderer for the tests.

      :return: The copyright header renderer
    """
    return CopyrightHeader(cls._TEMPLATE, 'Sumanth Vepa', 2026)

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
  def _tests_gitignore(cls, project_root: Path) -> Path:
    """
      Return the tests/.gitignore path.

      :param project_root: The project root directory
      :return: The tests .gitignore path
    """
    return cls._tests(project_root) / '.gitignore'

  @classmethod
  def _package_gitignore(cls, project_root: Path) -> Path:
    """
      Return the tests/<package_name>/.gitignore path.

      :param project_root: The project root directory
      :return: The tests package .gitignore path
    """
    return cls._package(project_root) / '.gitignore'

  @classmethod
  def _test_gitignore(cls, project_root: Path) -> Path:
    """
      Return the tests/<package_name>/test/.gitignore path.

      :param project_root: The project root directory
      :return: The test package .gitignore path
    """
    return cls._test_package(project_root) / '.gitignore'

  @classmethod
  def _init_py(cls, project_root: Path) -> Path:
    """
      Return the tests/<package_name>/test/__init__.py path.

      :param project_root: The project root directory
      :return: The test package __init__.py path
    """
    return cls._test_package(project_root) / '__init__.py'

  # run

  def test_run_creates_full_tests_tree(self) -> None:
    """
      Verify run creates tests/, tests/<package_name>/ and
      tests/<package_name>/test/, a .gitignore in each, and the test
      package __init__.py.
    """
    with project_context() as (project_root, context):
      step = CreateTestsTreeStep(context, self._copyright_header())

      step.run()

      self.assertTrue(self._tests(project_root).is_dir())
      self.assertTrue(self._package(project_root).is_dir())
      self.assertTrue(self._test_package(project_root).is_dir())
      self.assertTrue(self._tests_gitignore(project_root).is_file())
      self.assertTrue(self._package_gitignore(project_root).is_file())
      self.assertTrue(self._test_gitignore(project_root).is_file())
      self.assertTrue(self._init_py(project_root).is_file())

  def test_run_creates_init_py_with_docstring_and_header(self) -> None:
    """
      Verify run creates the test package __init__.py with a module
      docstring holding the description, followed by the copyright
      header.
    """
    with project_context() as (project_root, context):
      step = CreateTestsTreeStep(context, self._copyright_header())

      step.run()

      self.assertEqual(
        '"""\n'
        f'  {self._DESCRIPTION}\n'
        '"""\n'
        f'# {self._DESCRIPTION}\n'
        '# Copyright (C) 2026 Sumanth Vepa.\n',
        self._init_py(project_root).read_text(encoding='utf-8'))

  def test_run_creates_empty_gitignore_files(self) -> None:
    """
      Verify the .gitignore files run creates are empty.
    """
    with project_context() as (project_root, context):
      step = CreateTestsTreeStep(context, self._copyright_header())

      step.run()

      self.assertEqual(
        '',
        self._tests_gitignore(project_root).read_text(encoding='utf-8'))
      self.assertEqual(
        '',
        self._package_gitignore(project_root).read_text(encoding='utf-8'))
      self.assertEqual(
        '',
        self._test_gitignore(project_root).read_text(encoding='utf-8'))

  def test_run_preserves_representative_preexisting_artifacts(
    self
  ) -> None:
    """
      Verify run leaves a pre-existing tests/ directory and a
      pre-existing __init__.py untouched (convergent).
    """
    with project_context() as (project_root, context):
      self._test_package(project_root).mkdir(parents=True)
      self._init_py(project_root).write_text(
        '# user init\n', encoding='utf-8')
      step = CreateTestsTreeStep(context, self._copyright_header())

      step.run()

      self.assertEqual(
        '# user init\n',
        self._init_py(project_root).read_text(encoding='utf-8'))
      self.assertTrue(self._tests_gitignore(project_root).is_file())

  def test_run_cleans_up_owned_partial_work_on_failure(self) -> None:
    """
      Verify run rolls back the children it already completed when a
      later child fails, so no partial tests tree is left behind.
    """
    with project_context() as (project_root, context):
      # A directory at tests/<pkg>/.gitignore makes the package
      # .gitignore child fail after mkdir created tests/<pkg>/test.
      self._package_gitignore(project_root).mkdir(parents=True)
      step = CreateTestsTreeStep(context, self._copyright_header())

      with self.assertRaises(DralithusProjectError):
        step.run()

      self.assertFalse(self._test_package(project_root).exists())
      self.assertFalse(self._tests_gitignore(project_root).exists())
      self.assertTrue(self._package(project_root).is_dir())
      self.assertTrue(self._package_gitignore(project_root).is_dir())

  # dry run

  def test_run_dry_run_creates_nothing(self) -> None:
    """
      Verify dry run creates no directories or files, and does not
      fail when the target directories are absent (guarded dry-run
      skips validating a child whose parent does not exist).
    """
    with project_context() as (project_root, context):
      step = CreateTestsTreeStep(context, self._copyright_header())

      step.run(dry_run=True)

      self.assertFalse(self._tests(project_root).exists())

  def test_run_dry_run_rejects_unusable_existing_target(self) -> None:
    """
      Verify dry run rejects an existing but unusable target whose
      parent directory already exists.
    """
    with project_context() as (project_root, context):
      self._tests_gitignore(project_root).mkdir(parents=True)
      step = CreateTestsTreeStep(context, self._copyright_header())

      with self.assertRaises(DralithusProjectError):
        step.run(dry_run=True)

  # rollback

  def test_rollback_removes_created_artifacts(self) -> None:
    """
      Verify rollback removes the directories and files run created.
    """
    with project_context() as (project_root, context):
      step = CreateTestsTreeStep(context, self._copyright_header())

      step.run()
      step.rollback()

      self.assertFalse(self._tests(project_root).exists())

  def test_rollback_preserves_preexisting_artifacts(self) -> None:
    """
      Verify rollback leaves pre-existing directories and files in
      place.
    """
    with project_context() as (project_root, context):
      self._test_package(project_root).mkdir(parents=True)
      self._init_py(project_root).write_text(
        '# user init\n', encoding='utf-8')
      step = CreateTestsTreeStep(context, self._copyright_header())

      step.run()
      step.rollback()

      self.assertTrue(self._test_package(project_root).is_dir())
      self.assertEqual(
        '# user init\n',
        self._init_py(project_root).read_text(encoding='utf-8'))
      self.assertFalse(self._tests_gitignore(project_root).exists())

  def test_rollback_dry_run_keeps_everything(self) -> None:
    """
      Verify a dry-run rollback changes nothing.
    """
    with project_context() as (project_root, context):
      step = CreateTestsTreeStep(context, self._copyright_header())

      step.run()
      step.rollback(dry_run=True)

      self.assertTrue(self._tests(project_root).is_dir())
      self.assertTrue(self._test_package(project_root).is_dir())
      self.assertTrue(self._init_py(project_root).is_file())
      self.assertTrue(self._tests_gitignore(project_root).is_file())


if __name__ == '__main__':
  unittest.main()

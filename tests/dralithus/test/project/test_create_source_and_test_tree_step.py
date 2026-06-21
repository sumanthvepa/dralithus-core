"""
  test_create_source_and_test_tree_step.py: Unit tests for
  create_source_and_test_tree_step.
"""
# -------------------------------------------------------------------
# test_create_source_and_test_tree_step.py: Unit tests for
# create_source_and_test_tree_step.
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

from dralithus.test import project_context
from dralithus.project.create_source_and_test_tree_step import (
  CreateSourceAndTestTreeStep)
from dralithus.project.error import DralithusProjectError


# pylint: disable-next=too-many-public-methods
class TestCreateSourceAndTestTreeStep(unittest.TestCase):
  """
    Unit tests for the CreateSourceAndTestTreeStep class.
  """
  _PACKAGE_NAME = 'mypkg'

  def _src_package(self, project_root: Path) -> Path:
    """
      Return the source package directory for the test package.

      :param project_root: The project root directory
      :return: The src/<package_name> directory path
    """
    return project_root / 'src' / self._PACKAGE_NAME

  def _test_package(self, project_root: Path) -> Path:
    """
      Return the test package directory for the test package.

      :param project_root: The project root directory
      :return: The tests/<package_name>/test directory path
    """
    return project_root / 'tests' / self._PACKAGE_NAME / 'test'

  # Constructor validation

  def test_init_rejects_empty_package_name(self) -> None:
    """
      Verify that the constructor rejects an empty package name.

      :return: None
    """
    with self.assertRaises(DralithusProjectError):
      CreateSourceAndTestTreeStep('')

  def test_init_rejects_non_identifier_package_name(self) -> None:
    """
      Verify that the constructor rejects a package name that is not
      a valid Python identifier.

      :return: None
    """
    with self.assertRaises(DralithusProjectError):
      CreateSourceAndTestTreeStep('my-pkg')
    with self.assertRaises(DralithusProjectError):
      CreateSourceAndTestTreeStep('my.pkg')

  def test_init_rejects_keyword_package_name(self) -> None:
    """
      Verify that the constructor rejects a Python keyword as a
      package name.

      :return: None
    """
    with self.assertRaises(DralithusProjectError):
      CreateSourceAndTestTreeStep('class')

  def test_init_rejects_uppercase_package_name(self) -> None:
    """
      Verify that the constructor rejects a package name that
      contains uppercase letters.

      :return: None
    """
    with self.assertRaises(DralithusProjectError):
      CreateSourceAndTestTreeStep('MyPkg')

  # run

  def test_run_creates_trees_and_files(self) -> None:
    """
      Verify that run creates both package trees and the
      files in an empty project root.

      The source package is a namespace package (no __init__.py); the
      test package has a generated __init__.py with a docstring and the
      copyleft header; both directories get an empty .gitignore.

      :return: None
    """
    with project_context() as (project_root, context):
      src_package = self._src_package(project_root)
      test_package = self._test_package(project_root)
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)

      self.assertTrue(src_package.is_dir())
      self.assertTrue(test_package.is_dir())
      self.assertFalse((src_package / '__init__.py').exists())
      init_text = (
        test_package / '__init__.py').read_text(encoding='utf-8')
      self.assertTrue(init_text.startswith('"""'))
      self.assertIn(self._PACKAGE_NAME, init_text)
      self.assertIn('GNU General Public License', init_text)
      src_gitignore = src_package / '.gitignore'
      test_gitignore = test_package / '.gitignore'
      self.assertTrue(src_gitignore.is_file())
      self.assertTrue(test_gitignore.is_file())
      self.assertEqual('', src_gitignore.read_text(encoding='utf-8'))
      self.assertEqual('', test_gitignore.read_text(encoding='utf-8'))

  def test_run_creates_gitignore_in_every_created_directory(self) -> None:
    """
      Verify that run creates an empty .gitignore in every directory
      it is responsible for, not only the two leaf package directories.

      The tracked-directory principle requires every durable directory
      created for a tracked project - including the parent src, tests,
      and tests/<package_name> directories - to carry a .gitignore.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)

      directories = [
        project_root / 'src',
        project_root / 'src' / self._PACKAGE_NAME,
        project_root / 'tests',
        project_root / 'tests' / self._PACKAGE_NAME,
        project_root / 'tests' / self._PACKAGE_NAME / 'test',
      ]
      for directory in directories:
        gitignore = directory / '.gitignore'
        self.assertTrue(
          gitignore.is_file(), f'missing .gitignore in {directory}')
        self.assertEqual('', gitignore.read_text(encoding='utf-8'))

  def test_run_keeps_existing_parent_gitignore(self) -> None:
    """
      Verify that run leaves a pre-existing parent .gitignore
      untouched (convergent).

      :return: None
    """
    with project_context() as (project_root, context):
      tests_dir = project_root / 'tests'
      tests_dir.mkdir()
      gitignore = tests_dir / '.gitignore'
      gitignore.write_text('*.log\n', encoding='utf-8')
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)

      self.assertEqual('*.log\n', gitignore.read_text(encoding='utf-8'))

  def test_run_accepts_preexisting_directories(self) -> None:
    """
      Verify that run accepts pre-existing package directories
      without error (convergent).

      :return: None
    """
    with project_context() as (project_root, context):
      src_package = self._src_package(project_root)
      test_package = self._test_package(project_root)
      src_package.mkdir(parents=True)
      test_package.mkdir(parents=True)
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)

      self.assertTrue(src_package.is_dir())
      self.assertTrue(test_package.is_dir())
      self.assertTrue((test_package / '__init__.py').is_file())

  def test_run_keeps_existing_init_py(self) -> None:
    """
      Verify that run leaves a pre-existing __init__.py untouched.

      :return: None
    """
    with project_context() as (project_root, context):
      test_package = self._test_package(project_root)
      test_package.mkdir(parents=True)
      init_py = test_package / '__init__.py'
      init_py.write_text('# existing\n', encoding='utf-8')
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)

      self.assertEqual(
        '# existing\n', init_py.read_text(encoding='utf-8'))

  def test_run_keeps_existing_gitignore(self) -> None:
    """
      Verify that run leaves a pre-existing .gitignore untouched.

      :return: None
    """
    with project_context() as (project_root, context):
      src_package = self._src_package(project_root)
      src_package.mkdir(parents=True)
      gitignore = src_package / '.gitignore'
      gitignore.write_text('*.pyc\n', encoding='utf-8')
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)

      self.assertEqual(
        '*.pyc\n', gitignore.read_text(encoding='utf-8'))

  def test_run_raises_when_path_component_not_a_directory(self) -> None:
    """
      Verify that run raises when a tree path component exists but is
      not a directory.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / 'src').mkdir()
      (project_root / 'src' / self._PACKAGE_NAME).write_text(
        'not a directory\n', encoding='utf-8')
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_dry_run_creates_nothing(self) -> None:
    """
      Verify that dry-run mode does not create any directories or
      files.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context, dry_run=True)

      self.assertFalse((project_root / 'src').exists())
      self.assertFalse((project_root / 'tests').exists())

  # rollback

  def test_rollback_removes_everything_run_created(self) -> None:
    """
      Verify that rollback removes everything run created in an empty
      project root.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)
      step.rollback(context)

      self.assertFalse((project_root / 'src').exists())
      self.assertFalse((project_root / 'tests').exists())

  def test_rollback_keeps_preexisting_directories_and_files(self) -> None:
    """
      Verify that rollback leaves pre-existing directories and files
      in place, removing only what the step created.

      :return: None
    """
    with project_context() as (project_root, context):
      test_package = self._test_package(project_root)
      test_package.mkdir(parents=True)
      init_py = test_package / '__init__.py'
      init_py.write_text('# existing\n', encoding='utf-8')
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)
      step.rollback(context)

      self.assertTrue(test_package.is_dir())
      self.assertEqual(
        '# existing\n', init_py.read_text(encoding='utf-8'))
      self.assertFalse((project_root / 'src').exists())

  def test_rollback_dry_run_keeps_everything(self) -> None:
    """
      Verify that rollback dry-run mode leaves everything in place.

      :return: None
    """
    with project_context() as (project_root, context):
      src_package = self._src_package(project_root)
      test_package = self._test_package(project_root)
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)
      step.rollback(context, dry_run=True)

      self.assertTrue(src_package.is_dir())
      self.assertTrue(test_package.is_dir())
      self.assertTrue((test_package / '__init__.py').is_file())

  def test_rollback_accepts_externally_removed_file(self) -> None:
    """
      Verify that rollback succeeds when a file has already
      been removed externally (convergent).

      :return: None
    """
    with project_context() as (project_root, context):
      test_package = self._test_package(project_root)
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)
      (test_package / '__init__.py').unlink()
      step.rollback(context)

      self.assertFalse((project_root / 'src').exists())
      self.assertFalse((project_root / 'tests').exists())

  def test_rollback_preserves_preexisting_init_py_symlink(self) -> None:
    """
      Verify that rollback preserves a pre-existing valid symlink at
      the __init__.py path, removing only what the step created.

      The step never claimed the symlink, so rollback must leave it
      (and its target) in place while removing the source tree it did
      create.

      :return: None
    """
    with project_context() as (project_root, context):
      test_package = self._test_package(project_root)
      test_package.mkdir(parents=True)
      target = project_root / 'target.txt'
      target.write_text('linked content\n', encoding='utf-8')
      init_link = test_package / '__init__.py'
      init_link.symlink_to(target)
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)
      step.rollback(context)

      self.assertTrue(init_link.is_symlink())
      self.assertEqual(
        'linked content\n', init_link.read_text(encoding='utf-8'))
      self.assertFalse((project_root / 'src').exists())

  def test_rollback_removes_trees_after_multiple_runs(self) -> None:
    """
      Verify that rollback removes the created trees after multiple
      run calls.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)
      step.run(context)
      step.rollback(context)

      self.assertFalse((project_root / 'src').exists())
      self.assertFalse((project_root / 'tests').exists())

  # run: strict typing of pre-existing paths

  def test_run_raises_when_init_py_path_is_a_directory(self) -> None:
    """
      Verify that run fails loudly when the __init__.py path already
      exists as a directory rather than a regular file.

      A directory where the regular file belongs is not state
      the step could have produced, so it must fail loudly (the
      convergent-step rule) and clean up the source tree it created.

      :return: None
    """
    with project_context() as (project_root, context):
      test_package = self._test_package(project_root)
      test_package.mkdir(parents=True)
      init_dir = test_package / '__init__.py'
      init_dir.mkdir()
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      with self.assertRaises(DralithusProjectError):
        step.run(context)

      self.assertTrue(init_dir.is_dir())
      self.assertFalse((project_root / 'src').exists())

  def test_run_raises_on_dangling_init_py_symlink(self) -> None:
    """
      Verify that run fails loudly when the __init__.py path is a
      dangling symlink rather than a regular file.

      :return: None
    """
    with project_context() as (project_root, context):
      test_package = self._test_package(project_root)
      test_package.mkdir(parents=True)
      init_link = test_package / '__init__.py'
      init_link.symlink_to(project_root / 'does-not-exist')
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      with self.assertRaises(DralithusProjectError):
        step.run(context)

      self.assertTrue(init_link.is_symlink())
      self.assertFalse((project_root / 'src').exists())

  def test_run_accepts_init_py_symlink_to_regular_file(self) -> None:
    """
      Verify that run accepts a valid symlink to a regular file at the
      __init__.py path and leaves it untouched (convergent).

      A symlink resolving to a regular file is a usable artifact, so
      the step must accept it without claiming or replacing it, the
      same valid-symlink policy MkdirStep and CreateFileStep follow.

      :return: None
    """
    with project_context() as (project_root, context):
      test_package = self._test_package(project_root)
      test_package.mkdir(parents=True)
      target = project_root / 'target.txt'
      target.write_text('linked content\n', encoding='utf-8')
      init_link = test_package / '__init__.py'
      init_link.symlink_to(target)
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      step.run(context)

      self.assertTrue(init_link.is_symlink())
      self.assertEqual(
        'linked content\n', init_link.read_text(encoding='utf-8'))
      self.assertTrue(self._src_package(project_root).is_dir())

  def test_run_raises_on_init_py_symlink_to_directory(self) -> None:
    """
      Verify that run fails loudly when the __init__.py path is a
      symlink resolving to a directory rather than a regular file.

      A symlink to the wrong type is not a usable file, so the
      step must fail loudly and clean up the source tree it created.

      :return: None
    """
    with project_context() as (project_root, context):
      test_package = self._test_package(project_root)
      test_package.mkdir(parents=True)
      target_dir = project_root / 'target-dir'
      target_dir.mkdir()
      init_link = test_package / '__init__.py'
      init_link.symlink_to(target_dir)
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      with self.assertRaises(DralithusProjectError):
        step.run(context)

      self.assertTrue(init_link.is_symlink())
      self.assertFalse((project_root / 'src').exists())

  # run: transactional cleanup on failure

  def test_run_cleans_up_when_test_tree_creation_fails(self) -> None:
    """
      Verify that a run whose test-tree creation fails after the
      source tree was created removes the source tree before raising.

      A file placed at the tests path makes the test-tree MkdirStep
      fail after the source tree has already been created. The failed
      run must not leave the source tree behind, because the
      orchestrator never rolls back a step whose own run raised.

      :return: None
    """
    with project_context() as (project_root, context):
      tests_path = project_root / 'tests'
      tests_path.write_text('not a directory\n', encoding='utf-8')
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      with self.assertRaises(DralithusProjectError):
        step.run(context)

      self.assertFalse((project_root / 'src').exists())
      self.assertTrue(tests_path.is_file())

  def test_run_cleans_up_when_file_write_fails(self) -> None:
    """
      Verify that a run whose file write fails removes the trees and
      files it created and raises DralithusProjectError.

      The first file (__init__.py) is written for real; the
      write of the source .gitignore is forced to fail. The failed
      run must wrap the raw OSError as DralithusProjectError (so the
      orchestrator can roll back earlier steps) and leave nothing
      behind.

      :return: None
    """
    real_create_file = (
      CreateSourceAndTestTreeStep._create_file)  # pylint: disable=protected-access

    with project_context() as (project_root, context):
      step = CreateSourceAndTestTreeStep(self._PACKAGE_NAME)

      def fail_src_gitignore(path: Path, content: str) -> None:
        if (path.name == '.gitignore'
            and path.parent.name == self._PACKAGE_NAME):
          raise OSError('simulated write failure')
        real_create_file(step, path, content)

      with mock.patch.object(
        CreateSourceAndTestTreeStep, '_create_file',
        side_effect=fail_src_gitignore
      ):
        with self.assertRaises(DralithusProjectError):
          step.run(context)

      self.assertFalse((project_root / 'src').exists())
      self.assertFalse((project_root / 'tests').exists())


if __name__ == '__main__':
  unittest.main()

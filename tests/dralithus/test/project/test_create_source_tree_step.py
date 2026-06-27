"""
  test_create_source_tree_step.py: Unit tests for
  create_source_tree_step.
"""
# -------------------------------------------------------------------
# test_create_source_tree_step.py: Unit tests for
# create_source_tree_step.
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

from dralithus.test.project import project_context
from dralithus.project.create_source_tree_step import CreateSourceTreeStep
from dralithus.project.error import DralithusProjectError


class TestCreateSourceTreeStep(unittest.TestCase):
  """
    Unit tests for the CreateSourceTreeStep class.

    CreateSourceTreeStep composes a MkdirStep and two
    CreateGitIgnoreFileStep children, so these tests cover the step's
    own wiring and behaviour (the created source tree, convergence,
    rollback, and guarded dry-run) rather than re-testing the child
    steps' exhaustive file-type and directory handling, which is
    covered by their own suites.
  """
  _PACKAGE_NAME = 'sample'

  @classmethod
  def _src(cls, project_root: Path) -> Path:
    """
      Return the src directory path.

      :param project_root: The project root directory
      :return: The src directory path
    """
    return project_root / 'src'

  @classmethod
  def _src_package(cls, project_root: Path) -> Path:
    """
      Return the src/<package_name> directory path.

      :param project_root: The project root directory
      :return: The src package directory path
    """
    return cls._src(project_root) / cls._PACKAGE_NAME

  @classmethod
  def _src_gitignore(cls, project_root: Path) -> Path:
    """
      Return the src/.gitignore path.

      :param project_root: The project root directory
      :return: The src .gitignore path
    """
    return cls._src(project_root) / '.gitignore'

  @classmethod
  def _src_package_gitignore(cls, project_root: Path) -> Path:
    """
      Return the src/<package_name>/.gitignore path.

      :param project_root: The project root directory
      :return: The src package .gitignore path
    """
    return cls._src_package(project_root) / '.gitignore'

  @classmethod
  def _src_package_init(cls, project_root: Path) -> Path:
    """
      Return the src/<package_name>/__init__.py path.

      :param project_root: The project root directory
      :return: The src package __init__.py path
    """
    return cls._src_package(project_root) / '__init__.py'

  # run

  def test_run_creates_full_source_tree(self) -> None:
    """
      Verify run creates src/, src/<package_name>/ and a .gitignore
      in each of those two directories.
    """
    with project_context() as (project_root, context):
      step = CreateSourceTreeStep(context)

      step.run()

      self.assertTrue(self._src(project_root).is_dir())
      self.assertTrue(self._src_package(project_root).is_dir())
      self.assertTrue(self._src_gitignore(project_root).is_file())
      self.assertTrue(self._src_package_gitignore(project_root).is_file())

  def test_run_creates_namespace_package_without_init_py(self) -> None:
    """
      Verify run does not create an __init__.py in
      src/<package_name>; the source package is a namespace package.
    """
    with project_context() as (project_root, context):
      step = CreateSourceTreeStep(context)

      step.run()

      self.assertTrue(self._src_package(project_root).is_dir())
      self.assertFalse(self._src_package_init(project_root).exists())

  def test_run_creates_empty_gitignore_files(self) -> None:
    """
      Verify the .gitignore files run creates are empty.
    """
    with project_context() as (project_root, context):
      step = CreateSourceTreeStep(context)

      step.run()

      self.assertEqual(
        '',
        self._src_gitignore(project_root).read_text(encoding='utf-8'))
      self.assertEqual(
        '',
        self._src_package_gitignore(project_root).read_text(
          encoding='utf-8'))

  def test_run_preserves_representative_preexisting_artifacts(
    self
  ) -> None:
    """
      Verify run leaves a pre-existing src/ directory and a
      pre-existing src/.gitignore untouched (convergent).
    """
    with project_context() as (project_root, context):
      self._src(project_root).mkdir()
      self._src_gitignore(project_root).write_text(
        'user ignore\n', encoding='utf-8')
      step = CreateSourceTreeStep(context)

      step.run()

      self.assertEqual(
        'user ignore\n',
        self._src_gitignore(project_root).read_text(encoding='utf-8'))
      self.assertTrue(self._src_package(project_root).is_dir())
      self.assertTrue(self._src_package_gitignore(project_root).is_file())

  def test_run_cleans_up_owned_partial_work_on_failure(self) -> None:
    """
      Verify run rolls back the children it already completed when a
      later child fails, so no partial source tree is left behind.
    """
    with project_context() as (project_root, context):
      # A directory at src/.gitignore makes the src .gitignore child
      # fail after the directory child has already created src/sample.
      self._src_gitignore(project_root).mkdir(parents=True)
      step = CreateSourceTreeStep(context)

      with self.assertRaises(DralithusProjectError):
        step.run()

      self.assertFalse(self._src_package(project_root).exists())
      self.assertTrue(self._src(project_root).is_dir())
      self.assertTrue(self._src_gitignore(project_root).is_dir())

  # dry run

  def test_run_dry_run_creates_nothing(self) -> None:
    """
      Verify dry run creates no directories or files, and does not
      fail when the target directories are absent (guarded dry-run
      skips validating a .gitignore whose parent does not exist).
    """
    with project_context() as (project_root, context):
      step = CreateSourceTreeStep(context)

      step.run(dry_run=True)

      self.assertFalse(self._src(project_root).exists())

  def test_run_dry_run_rejects_unusable_existing_target(self) -> None:
    """
      Verify dry run rejects an existing but unusable .gitignore
      target whose parent directory already exists.
    """
    with project_context() as (project_root, context):
      self._src_gitignore(project_root).mkdir(parents=True)
      step = CreateSourceTreeStep(context)

      with self.assertRaises(DralithusProjectError):
        step.run(dry_run=True)

  # rollback

  def test_rollback_removes_created_artifacts(self) -> None:
    """
      Verify rollback removes the directories and files run created.
    """
    with project_context() as (project_root, context):
      step = CreateSourceTreeStep(context)

      step.run()
      step.rollback()

      self.assertFalse(self._src(project_root).exists())
      self.assertFalse(self._src_package(project_root).exists())

  def test_rollback_preserves_preexisting_artifacts(self) -> None:
    """
      Verify rollback leaves pre-existing directories and files in
      place.
    """
    with project_context() as (project_root, context):
      self._src(project_root).mkdir()
      self._src_gitignore(project_root).write_text(
        'user ignore\n', encoding='utf-8')
      step = CreateSourceTreeStep(context)

      step.run()
      step.rollback()

      self.assertTrue(self._src(project_root).is_dir())
      self.assertEqual(
        'user ignore\n',
        self._src_gitignore(project_root).read_text(encoding='utf-8'))
      self.assertFalse(self._src_package(project_root).exists())

  def test_rollback_dry_run_keeps_everything(self) -> None:
    """
      Verify a dry-run rollback changes nothing.
    """
    with project_context() as (project_root, context):
      step = CreateSourceTreeStep(context)

      step.run()
      step.rollback(dry_run=True)

      self.assertTrue(self._src(project_root).is_dir())
      self.assertTrue(self._src_package(project_root).is_dir())
      self.assertTrue(self._src_gitignore(project_root).is_file())
      self.assertTrue(self._src_package_gitignore(project_root).is_file())


if __name__ == '__main__':
  unittest.main()

"""
  test_create_source_tree_step.py: Unit tests for
  dralithus.project.tx.create_source_tree_step.
"""
# -------------------------------------------------------------------
# test_create_source_tree_step.py: Unit tests for
# dralithus.project.tx.create_source_tree_step.
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

from dralithus.test.project import FailingWriteFile, project_context
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.create_source_tree_step import (
  CreateSourceTreeStep)
from dralithus.project.tx.execution_step import execute
from dralithus.project.tx.project_state import ProjectState


class TestCreateSourceTreeStep(unittest.TestCase):
  """
    Unit tests for the CreateSourceTreeStep class.

    CreateSourceTreeStep composes a MkdirStep and two
    CreateGitIgnoreFileStep children with no phase logic of its own,
    so these tests cover the wiring and serve as the Phase 1
    end-to-end integration for the execute() driver: a full real
    run, a deep dry run with no guarded skipping, and a mid-commit
    failure cleaned up by the single global abort. The children's
    exhaustive file-type handling is covered by their own suites.
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

  # execute: real run

  def test_execute_creates_full_source_tree(self) -> None:
    """
      Verify execute creates src/, src/<package_name>/ and a
      .gitignore in each of those two directories.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateSourceTreeStep(context)

      execute(step, context)

      self.assertTrue(self._src(project_root).is_dir())
      self.assertTrue(self._src_package(project_root).is_dir())
      self.assertTrue(self._src_gitignore(project_root).is_file())
      self.assertTrue(
        self._src_package_gitignore(project_root).is_file())

  def test_execute_creates_namespace_package_without_init_py(
    self
  ) -> None:
    """
      Verify execute does not create an __init__.py in
      src/<package_name>; the source package is a namespace
      package.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateSourceTreeStep(context)

      execute(step, context)

      self.assertTrue(self._src_package(project_root).is_dir())
      self.assertFalse(self._src_package_init(project_root).exists())

  def test_execute_creates_empty_gitignore_files(self) -> None:
    """
      Verify the .gitignore files execute creates are empty.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateSourceTreeStep(context)

      execute(step, context)

      self.assertEqual(
        '',
        self._src_gitignore(project_root).read_text(encoding='utf-8'))
      self.assertEqual(
        '',
        self._src_package_gitignore(project_root).read_text(
          encoding='utf-8'))

  def test_execute_preserves_preexisting_src_and_gitignore(
    self
  ) -> None:
    """
      Verify execute leaves a pre-existing src/ directory and a
      pre-existing src/.gitignore untouched (convergence).

      :return: None
    """
    with project_context() as (project_root, context):
      self._src(project_root).mkdir()
      self._src_gitignore(project_root).write_text(
        'user ignore\n', encoding='utf-8')
      step = CreateSourceTreeStep(context)

      execute(step, context)

      self.assertEqual(
        'user ignore\n',
        self._src_gitignore(project_root).read_text(encoding='utf-8'))
      self.assertTrue(self._src_package(project_root).is_dir())
      self.assertTrue(
        self._src_package_gitignore(project_root).is_file())

  def test_execute_aborts_all_owned_work_on_mid_commit_failure(
    self
  ) -> None:
    """
      Verify a child commit failure makes execute abort the whole
      tree: every artifact earlier commits created is removed and
      pre-existing artifacts are preserved.

      :return: None
    """
    real_open = Path.open

    with project_context() as (project_root, context):
      failing_path = self._src_package_gitignore(project_root)

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

      step = CreateSourceTreeStep(context)

      with mock.patch.object(Path, 'open', failing_open):
        with self.assertRaises(DralithusProjectError):
          execute(step, context)

      self.assertFalse(self._src(project_root).exists())

  def test_execute_prepare_failure_leaves_disk_untouched(self) -> None:
    """
      Verify a prepare failure in a real run propagates before any
      commit, leaving the file system untouched.

      :return: None
    """
    with project_context() as (project_root, context):
      # A directory at src/.gitignore is caught by prepare, before
      # any commit runs; under the old hierarchy this same scenario
      # failed midway through the run and needed rollback.
      self._src_gitignore(project_root).mkdir(parents=True)
      step = CreateSourceTreeStep(context)

      with self.assertRaises(DralithusProjectError):
        execute(step, context)

      self.assertTrue(self._src(project_root).is_dir())
      self.assertTrue(self._src_gitignore(project_root).is_dir())
      self.assertFalse(self._src_package(project_root).exists())

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
      step = CreateSourceTreeStep(context)

      execute(step, context, dry_run=True)

      self.assertFalse(self._src(project_root).exists())

  def test_execute_dry_run_rejects_unusable_existing_target(
    self
  ) -> None:
    """
      Verify a dry run rejects an existing but unusable .gitignore
      target.

      :return: None
    """
    with project_context() as (project_root, context):
      self._src_gitignore(project_root).mkdir(parents=True)
      step = CreateSourceTreeStep(context)

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
      step = CreateSourceTreeStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse(self._src(project_root).exists())
      self.assertFalse(self._src_package(project_root).exists())

  def test_abort_preserves_preexisting_artifacts(self) -> None:
    """
      Verify abort leaves pre-existing directories and files in
      place.

      :return: None
    """
    with project_context() as (project_root, context):
      self._src(project_root).mkdir()
      self._src_gitignore(project_root).write_text(
        'user ignore\n', encoding='utf-8')
      step = CreateSourceTreeStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertTrue(self._src(project_root).is_dir())
      self.assertEqual(
        'user ignore\n',
        self._src_gitignore(project_root).read_text(encoding='utf-8'))
      self.assertFalse(self._src_package(project_root).exists())

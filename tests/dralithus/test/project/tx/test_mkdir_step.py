"""
  test_mkdir_step.py: Unit tests for
  dralithus.project.tx.mkdir_step.
"""
# -------------------------------------------------------------------
# test_mkdir_step.py: Unit tests for
# dralithus.project.tx.mkdir_step.
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
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.mkdir_step import MkdirStep
from dralithus.project.tx.project_state import ProjectState


class TestMkdirStep(unittest.TestCase):
  """
    Unit tests for the MkdirStep class.

    These tests port the behavioral contract of the run/rollback
    MkdirStep to prepare/commit/abort: prepare validates and claims
    the directory and its missing parents without touching the file
    system, commit creates the missing directories and records
    ownership, and abort removes only the directories this step
    created, in reverse order.
  """
  # constructor

  def test_init_rejects_absolute_directory(self) -> None:
    """
      Verify the constructor rejects an absolute directory path.

      :return: None
    """
    with project_context() as (project_root, context):
      with self.assertRaises(DralithusProjectError):
        MkdirStep(context, project_root / 'src')

  # prepare

  def test_prepare_claims_directory(self) -> None:
    """
      Verify prepare claims the target directory so a later step
      sees it as a projected directory.

      :return: None
    """
    with project_context() as (project_root, context):
      step = MkdirStep(context, Path('src'))
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertTrue(state.is_dir(project_root / 'src'))

  def test_prepare_claims_missing_parent_directories(self) -> None:
    """
      Verify prepare claims every missing parent directory the step
      would create.

      :return: None
    """
    with project_context() as (project_root, context):
      target = Path('src') / 'dralithus' / 'project'
      step = MkdirStep(context, target)
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertTrue(state.is_dir(project_root / target))
      self.assertTrue(
        state.is_dir(project_root / 'src' / 'dralithus'))
      self.assertTrue(state.is_dir(project_root / 'src'))

  def test_prepare_accepts_preexisting_directory(self) -> None:
    """
      Verify prepare accepts a directory that already exists on the
      real file system and claims it (convergence).

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / 'src').mkdir()
      step = MkdirStep(context, Path('src'))
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertTrue(state.is_dir(project_root / 'src'))

  def test_prepare_rejects_real_file_occupant(self) -> None:
    """
      Verify prepare rejects a real regular file occupying the
      directory path.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / 'src').write_text(
        'not a directory\n', encoding='utf-8')
      step = MkdirStep(context, Path('src'))

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_rejects_claimed_file_occupant(self) -> None:
    """
      Verify prepare rejects a path an earlier step claimed as a
      regular file (projected conflict).

      :return: None
    """
    with project_context() as (project_root, context):
      state = ProjectState(project_root)
      state.claim_file(project_root / 'src')
      step = MkdirStep(context, Path('src'))

      with self.assertRaises(DralithusProjectError):
        step.prepare(state)

  def test_prepare_creates_nothing_on_disk(self) -> None:
    """
      Verify prepare performs no file system mutation.

      :return: None
    """
    with project_context() as (project_root, context):
      target = Path('src') / 'dralithus' / 'project'
      step = MkdirStep(context, target)

      step.prepare(ProjectState(project_root))

      self.assertFalse((project_root / 'src').exists())

  # commit

  def test_commit_creates_relative_directory(self) -> None:
    """
      Verify commit creates a project-relative directory.

      :return: None
    """
    with project_context() as (project_root, context):
      step = MkdirStep(context, Path('src'))

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertTrue((project_root / 'src').is_dir())

  def test_commit_creates_parent_directories(self) -> None:
    """
      Verify commit creates missing parent directories as needed.

      :return: None
    """
    with project_context() as (project_root, context):
      target = Path('src') / 'dralithus' / 'project'
      step = MkdirStep(context, target)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertTrue((project_root / target).is_dir())

  def test_repeated_commits_are_convergent(self) -> None:
    """
      Verify committing twice leaves one directory and abort still
      removes it.

      :return: None
    """
    with project_context() as (project_root, context):
      step = MkdirStep(context, Path('src'))

      step.prepare(ProjectState(project_root))
      step.commit()
      step.commit()
      step.abort()

      self.assertFalse((project_root / 'src').exists())

  # abort

  def test_abort_removes_directory_created_by_commit(self) -> None:
    """
      Verify abort removes a directory created by commit.

      :return: None
    """
    with project_context() as (project_root, context):
      step = MkdirStep(context, Path('src'))

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse((project_root / 'src').exists())

  def test_abort_removes_parent_directories_created_by_commit(
    self
  ) -> None:
    """
      Verify abort removes the parent directories commit created,
      in reverse order.

      :return: None
    """
    with project_context() as (project_root, context):
      target = Path('src') / 'dralithus' / 'project'
      step = MkdirStep(context, target)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse((project_root / target).exists())
      self.assertFalse((project_root / 'src' / 'dralithus').exists())
      self.assertFalse((project_root / 'src').exists())

  def test_abort_preserves_preexisting_parent_directories(
    self
  ) -> None:
    """
      Verify abort preserves parent directories that existed before
      commit.

      :return: None
    """
    with project_context() as (project_root, context):
      preexisting_parent = project_root / 'src'
      preexisting_parent.mkdir()
      target = Path('src') / 'dralithus' / 'project'
      step = MkdirStep(context, target)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse((project_root / target).exists())
      self.assertFalse((project_root / 'src' / 'dralithus').exists())
      self.assertTrue(preexisting_parent.is_dir())

  def test_abort_preserves_preexisting_directory(self) -> None:
    """
      Verify abort leaves a pre-existing target directory alone.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / 'src').mkdir()
      step = MkdirStep(context, Path('src'))

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertTrue((project_root / 'src').is_dir())

  def test_abort_is_idempotent(self) -> None:
    """
      Verify abort can be called again after removing the created
      directories.

      :return: None
    """
    with project_context() as (project_root, context):
      step = MkdirStep(context, Path('src'))

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()
      step.abort()

      self.assertFalse((project_root / 'src').exists())

  def test_abort_without_commit_changes_nothing(self) -> None:
    """
      Verify abort after prepare alone is a no-op.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / 'existing').mkdir()
      step = MkdirStep(context, Path('src'))

      step.prepare(ProjectState(project_root))
      step.abort()

      self.assertFalse((project_root / 'src').exists())
      self.assertTrue((project_root / 'existing').is_dir())

  def test_abort_raises_error_for_non_empty_directory(self) -> None:
    """
      Verify abort raises an error rather than removing a created
      directory that has since gained content.

      :return: None
    """
    with project_context() as (project_root, context):
      target = project_root / 'src'
      step = MkdirStep(context, Path('src'))

      step.prepare(ProjectState(project_root))
      step.commit()
      (target / 'module.py').touch()

      with self.assertRaises(DralithusProjectError):
        step.abort()

      self.assertTrue(target.is_dir())
      self.assertTrue((target / 'module.py').is_file())

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
import unittest


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
    raise NotImplementedError('test not implemented yet')

  # prepare

  def test_prepare_claims_directory(self) -> None:
    """
      Verify prepare claims the target directory so a later step
      sees it as a projected directory.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_prepare_claims_missing_parent_directories(self) -> None:
    """
      Verify prepare claims every missing parent directory the step
      would create.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_prepare_accepts_preexisting_directory(self) -> None:
    """
      Verify prepare accepts a directory that already exists on the
      real file system and claims it (convergence).

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_prepare_rejects_real_file_occupant(self) -> None:
    """
      Verify prepare rejects a real regular file occupying the
      directory path.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_prepare_rejects_claimed_file_occupant(self) -> None:
    """
      Verify prepare rejects a path an earlier step claimed as a
      regular file (projected conflict).

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_prepare_creates_nothing_on_disk(self) -> None:
    """
      Verify prepare performs no file system mutation.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  # commit

  def test_commit_creates_relative_directory(self) -> None:
    """
      Verify commit creates a project-relative directory.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_commit_creates_parent_directories(self) -> None:
    """
      Verify commit creates missing parent directories as needed.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_repeated_commits_are_convergent(self) -> None:
    """
      Verify committing twice leaves one directory and abort still
      removes it.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  # abort

  def test_abort_removes_directory_created_by_commit(self) -> None:
    """
      Verify abort removes a directory created by commit.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_abort_removes_parent_directories_created_by_commit(
    self
  ) -> None:
    """
      Verify abort removes the parent directories commit created,
      in reverse order.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_abort_preserves_preexisting_parent_directories(
    self
  ) -> None:
    """
      Verify abort preserves parent directories that existed before
      commit.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_abort_preserves_preexisting_directory(self) -> None:
    """
      Verify abort leaves a pre-existing target directory alone.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_abort_is_idempotent(self) -> None:
    """
      Verify abort can be called again after removing the created
      directories.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_abort_without_commit_changes_nothing(self) -> None:
    """
      Verify abort after prepare alone is a no-op.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_abort_raises_error_for_non_empty_directory(self) -> None:
    """
      Verify abort raises an error rather than removing a created
      directory that has since gained content.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

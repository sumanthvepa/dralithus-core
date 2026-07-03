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
import unittest


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
  # execute: real run

  def test_execute_creates_full_source_tree(self) -> None:
    """
      Verify execute creates src/, src/<package_name>/ and a
      .gitignore in each of those two directories.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_execute_creates_namespace_package_without_init_py(
    self
  ) -> None:
    """
      Verify execute does not create an __init__.py in
      src/<package_name>; the source package is a namespace
      package.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_execute_creates_empty_gitignore_files(self) -> None:
    """
      Verify the .gitignore files execute creates are empty.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_execute_preserves_preexisting_src_and_gitignore(
    self
  ) -> None:
    """
      Verify execute leaves a pre-existing src/ directory and a
      pre-existing src/.gitignore untouched (convergence).

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_execute_aborts_all_owned_work_on_mid_commit_failure(
    self
  ) -> None:
    """
      Verify a child commit failure makes execute abort the whole
      tree: every artifact earlier commits created is removed and
      pre-existing artifacts are preserved.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_execute_prepare_failure_leaves_disk_untouched(self) -> None:
    """
      Verify a prepare failure in a real run propagates before any
      commit, leaving the file system untouched.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

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
    raise NotImplementedError('test not implemented yet')

  def test_execute_dry_run_rejects_unusable_existing_target(
    self
  ) -> None:
    """
      Verify a dry run rejects an existing but unusable .gitignore
      target.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  # abort

  def test_abort_removes_created_artifacts(self) -> None:
    """
      Verify abort removes the directories and files commit
      created.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_abort_preserves_preexisting_artifacts(self) -> None:
    """
      Verify abort leaves pre-existing directories and files in
      place.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

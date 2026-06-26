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
import unittest


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

  # run

  def test_run_creates_full_tests_tree(self) -> None:
    """
      Verify run creates tests/, tests/<package_name>/ and
      tests/<package_name>/test/, a .gitignore in each, and the test
      package __init__.py.
    """

  def test_run_creates_init_py_with_docstring_and_header(self) -> None:
    """
      Verify run creates the test package __init__.py with a module
      docstring holding the description, followed by the copyright
      header.
    """

  def test_run_creates_empty_gitignore_files(self) -> None:
    """
      Verify the .gitignore files run creates are empty.
    """

  def test_run_preserves_representative_preexisting_artifacts(
    self
  ) -> None:
    """
      Verify run leaves a pre-existing tests/ directory and a
      pre-existing __init__.py untouched (convergent).
    """

  def test_run_cleans_up_owned_partial_work_on_failure(self) -> None:
    """
      Verify run rolls back the children it already completed when a
      later child fails, so no partial tests tree is left behind.
    """

  # dry run

  def test_run_dry_run_creates_nothing(self) -> None:
    """
      Verify dry run creates no directories or files, and does not
      fail when the target directories are absent (guarded dry-run
      skips validating a child whose parent does not exist).
    """

  def test_run_dry_run_rejects_unusable_existing_target(self) -> None:
    """
      Verify dry run rejects an existing but unusable target whose
      parent directory already exists.
    """

  # rollback

  def test_rollback_removes_created_artifacts(self) -> None:
    """
      Verify rollback removes the directories and files run created.
    """

  def test_rollback_preserves_preexisting_artifacts(self) -> None:
    """
      Verify rollback leaves pre-existing directories and files in
      place.
    """

  def test_rollback_dry_run_keeps_everything(self) -> None:
    """
      Verify a dry-run rollback changes nothing.
    """


if __name__ == '__main__':
  unittest.main()

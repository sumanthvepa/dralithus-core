"""
  test_create_python_project_step.py: Unit tests for
  dralithus.project.tx.create_python_project_step.
"""
# -------------------------------------------------------------------
# test_create_python_project_step.py: Unit tests for
# dralithus.project.tx.create_python_project_step.
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


class TestCreatePythonProjectStep(unittest.TestCase):
  """
    Unit tests for the CreatePythonProjectStep class.

    CreatePythonProjectStep wires the leaf and composite project
    creation steps in dependency order and delegates all phase logic
    to CompositeExecutionStep. These tests cover the wiring,
    argument passing, and the driver-level behavior with recording
    fakes, plus two integration tests with real file-system children
    and faked expensive venv and dependency steps. The headline
    change from the old hierarchy is pinned here: a dry run against
    an empty project root prepares every child, including pyproject
    and dependencies, because claims replace prerequisite guards.
  """
  # constructor

  def test_constructor_wires_children_in_dependency_order(self) -> None:
    """
      Verify the constructor creates the child steps in dependency
      order, so prepare and commit drive them in that order.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_constructor_passes_expected_arguments_to_children(
    self
  ) -> None:
    """
      Verify each child step receives the constructor arguments it
      needs, including python_executable and the project metadata.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  # execute: dry run

  def test_execute_dry_run_prepares_all_children_and_creates_nothing(
    self
  ) -> None:
    """
      Verify a dry run against an empty project root prepares every
      child, including pyproject and dependencies, commits nothing,
      aborts nothing, and creates nothing on disk.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_execute_prepare_failure_propagates_without_abort(
    self
  ) -> None:
    """
      Verify a child prepare failure propagates without committing
      or aborting, and later children are not prepared.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  # execute: commit failure

  def test_execute_aborts_all_children_and_reraises_on_commit_failure(
    self
  ) -> None:
    """
      Verify a late child commit failure makes execute abort every
      child in reverse order and re-raise the error.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  # abort

  def test_abort_aborts_children_in_reverse_order(self) -> None:
    """
      Verify an explicit abort delegates to the children in reverse
      dependency order.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  # integration

  def test_execute_with_real_files_and_fake_expensive_steps_creates_shape(
    self
  ) -> None:
    """
      Verify the top-level composition produces a coherent project
      shape using real file-system children and faked venv and
      dependency steps.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

  def test_failed_late_commit_aborts_real_owned_artifacts(self) -> None:
    """
      Verify that when a late child commit fails, the real
      artifacts created by earlier children are removed by the
      global abort.

      :return: None
    """
    raise NotImplementedError('test not implemented yet')

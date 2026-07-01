"""
  test_create_python_project_step.py: Unit tests for
  create_python_project_step.
"""
# -------------------------------------------------------------------
# test_create_python_project_step.py: Unit tests for
# create_python_project_step.
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
    creation steps in dependency order and delegates orchestration,
    rollback, and dry-run to CompositeExecutionStep. These tests cover
    the step's own wiring, argument passing, and guarded dry-run
    behaviour rather than re-testing the exhaustive behaviour of the
    child steps, which is covered by their own suites.
  """
  # constructor

  def test_constructor_wires_children_in_dependency_order(self) -> None:
    """
      Verify the constructor creates the child steps and runs them in
      the expected dependency order.
    """
    raise NotImplementedError('test not implemented yet')

  def test_constructor_passes_expected_arguments_to_children(
    self
  ) -> None:
    """
      Verify each child step receives the constructor arguments it
      needs, including python_executable and the project metadata.
    """
    raise NotImplementedError('test not implemented yet')

  # run

  def test_run_rolls_back_children_and_reraises_on_failure(
    self
  ) -> None:
    """
      Verify that a child failure during run rolls back the children
      in reverse order and re-raises the error.
    """
    raise NotImplementedError('test not implemented yet')

  # dry run

  def test_run_dry_run_validates_independent_children_only_when_empty(
    self
  ) -> None:
    """
      Verify a dry run against an empty project root validates the
      independent children, skips the dependent children whose
      prerequisites are absent, and creates nothing.
    """
    raise NotImplementedError('test not implemented yet')

  def test_run_dry_run_validates_pyproject_when_prerequisites_exist(
    self
  ) -> None:
    """
      Verify the dry run validates pyproject.toml when its
      prerequisites (packages.txt and venv metadata) already exist.
    """
    raise NotImplementedError('test not implemented yet')

  def test_run_dry_run_validates_dependencies_when_prerequisites_exist(
    self
  ) -> None:
    """
      Verify the dry run reaches dependency validation when a venv
      Python and a package file already exist.
    """
    raise NotImplementedError('test not implemented yet')

  def test_run_dry_run_reraises_child_validation_error(self) -> None:
    """
      Verify a dry-run validation error from a child is not swallowed
      and does not trigger rollback.
    """
    raise NotImplementedError('test not implemented yet')

  # rollback

  def test_rollback_rolls_back_children_in_reverse_order(self) -> None:
    """
      Verify an explicit rollback delegates to the children in reverse
      dependency order.
    """
    raise NotImplementedError('test not implemented yet')

  def test_rollback_dry_run_forwards_dry_run_to_children(self) -> None:
    """
      Verify rollback(dry_run=True) forwards the dry-run flag to every
      child rollback.
    """
    raise NotImplementedError('test not implemented yet')

  # integration

  def test_run_with_real_files_and_fake_expensive_steps_creates_shape(
    self
  ) -> None:
    """
      Verify the top-level composition produces a coherent project
      shape using real file-system children and faked venv and
      dependency steps.
    """
    raise NotImplementedError('test not implemented yet')

  def test_failed_late_step_rolls_back_real_owned_artifacts(
    self
  ) -> None:
    """
      Verify that when a late child fails, the real artifacts created
      by earlier children are removed by rollback.
    """
    raise NotImplementedError('test not implemented yet')


if __name__ == '__main__':
  unittest.main()

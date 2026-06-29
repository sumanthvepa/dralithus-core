"""
  test_composite_execution_step.py: Unit tests for
  composite_execution_step.
"""
# -------------------------------------------------------------------
# test_composite_execution_step.py: Unit tests for
# composite_execution_step.
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

from dralithus.test.project import copyright_header
from dralithus.project.composite_execution_step import (
  CompositeExecutionStep)
from dralithus.project.context import ProjectContext


class TestCompositeExecutionStep(unittest.TestCase):
  """
    Unit tests for the CompositeExecutionStep base class.

    These tests cover the shared orchestration the base provides:
    running the child steps in order, rolling back on failure,
    rolling back in reverse order, and delegating dry-run validation
    to the subclass _run_dry_run(). Child steps are replaced by
    lightweight recording fakes so the tests exercise the base's
    orchestration rather than any real file system behavior.
  """
  @staticmethod
  def _context() -> ProjectContext:
    """
      Return a project context for orchestration tests.

      The base's run() and rollback() do not touch the file system,
      so the project root need not exist.

      :return: A project context with a valid package name
    """
    return ProjectContext(
      Path('/nonexistent/project'), 'sample', copyright_header())

  # construction

  def test_cannot_instantiate_abstract_base(self) -> None:
    """
      Verify the base class cannot be instantiated directly because
      _run_dry_run() is abstract.
    """
    with self.assertRaises(TypeError):
      # noinspection PyAbstractClass
      # pylint: disable-next=abstract-class-instantiated
      CompositeExecutionStep(self._context(), [])  # type: ignore[abstract]

  # run

  def test_run_executes_children_in_order(self) -> None:
    """
      Verify run() runs every child step once, in the order the
      children were given.
    """
    self.skipTest('Implemented in the red-test phase.')

  def test_run_rolls_back_and_reraises_on_failure(self) -> None:
    """
      Verify that when a child step raises DralithusProjectError,
      run() rolls back the step's children and re-raises the error.
    """
    self.skipTest('Implemented in the red-test phase.')

  def test_run_dry_run_delegates_to_run_dry_run(self) -> None:
    """
      Verify run(dry_run=True) calls the subclass _run_dry_run() and
      does not run the children directly.
    """
    self.skipTest('Implemented in the red-test phase.')

  # rollback

  def test_rollback_rolls_back_children_in_reverse(self) -> None:
    """
      Verify rollback() rolls back every child step once, in reverse
      of the order the children were given.
    """
    self.skipTest('Implemented in the red-test phase.')

  def test_rollback_forwards_dry_run_to_children(self) -> None:
    """
      Verify rollback(dry_run=True) rolls back each child with
      dry_run set to True.
    """
    self.skipTest('Implemented in the red-test phase.')


if __name__ == '__main__':
  unittest.main()

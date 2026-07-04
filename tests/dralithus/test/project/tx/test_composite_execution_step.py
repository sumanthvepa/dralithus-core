"""
  test_composite_execution_step.py: Unit tests for
  dralithus.project.tx.composite_execution_step.
"""
# -------------------------------------------------------------------
# test_composite_execution_step.py: Unit tests for
# dralithus.project.tx.composite_execution_step.
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

from dralithus.test.project import project_context
from dralithus.test.project.tx import RecordingStep
from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.composite_execution_step import (
  CompositeExecutionStep)
from dralithus.project.tx.project_state import ProjectState


class TestCompositeExecutionStep(unittest.TestCase):
  """
    Unit tests for the CompositeExecutionStep class.

    The composite is concrete and adds no phase logic beyond
    fan-out: prepare and commit drive the children in order and
    abort drives them in reverse order. Child steps are replaced by
    lightweight recording fakes so the tests exercise the fan-out
    rather than any real file system behavior. The composite does no
    failure handling of its own; the execute() driver owns the one
    global abort path.
  """
  @staticmethod
  def _children(
      context: ProjectContext,
      log: list[str],
      failing_phase: str | None = None,
      failing_name: str | None = None
  ) -> list[RecordingStep]:
    """
      Build three recording child steps named a, b and c.

      :param context: The shared project creation context
      :param log: The shared list that records phase calls
      :param failing_phase: The phase in which the failing child
        should fail, or None if no child should fail
      :param failing_name: The name of the child that should fail,
        or None if no child should fail
      :return: The recording child steps
    """
    return [
      RecordingStep(
        context,
        name,
        log,
        fails_in=failing_phase if name == failing_name else None)
      for name in ('a', 'b', 'c')]

  def test_prepare_prepares_children_in_order_with_shared_state(
    self
  ) -> None:
    """
      Verify prepare prepares every child once, in order, passing
      each child the same ProjectState instance.

      :return: None
    """
    log: list[str] = []
    with project_context() as (project_root, context):
      children = self._children(context, log)
      composite = CompositeExecutionStep(context, children)
      state = ProjectState(project_root)

      composite.prepare(state)

      self.assertEqual(['prepare a', 'prepare b', 'prepare c'], log)
      for child in children:
        self.assertIs(state, child.prepared_states[0])

  def test_prepare_propagates_child_failure_and_stops(self) -> None:
    """
      Verify a child prepare failure propagates immediately: later
      children are not prepared and nothing is aborted.

      :return: None
    """
    log: list[str] = []
    with project_context() as (project_root, context):
      children = self._children(
        context, log, failing_phase='prepare', failing_name='b')
      composite = CompositeExecutionStep(context, children)

      with self.assertRaisesRegex(
        DralithusProjectError, 'b prepare failed'
      ):
        composite.prepare(ProjectState(project_root))

    self.assertEqual(['prepare a', 'prepare b'], log)

  def test_commit_commits_children_in_order(self) -> None:
    """
      Verify commit commits every child once, in the order the
      children were given.

      :return: None
    """
    log: list[str] = []
    with project_context() as (_project_root, context):
      children = self._children(context, log)
      composite = CompositeExecutionStep(context, children)

      composite.commit()

    self.assertEqual(['commit a', 'commit b', 'commit c'], log)

  def test_commit_propagates_child_failure_without_aborting(
    self
  ) -> None:
    """
      Verify a child commit failure propagates immediately without
      the composite aborting anything; the execute() driver owns the
      global abort.

      :return: None
    """
    log: list[str] = []
    with project_context() as (_project_root, context):
      children = self._children(
        context, log, failing_phase='commit', failing_name='b')
      composite = CompositeExecutionStep(context, children)

      with self.assertRaisesRegex(
        DralithusProjectError, 'b commit failed'
      ):
        composite.commit()

    self.assertEqual(['commit a', 'commit b'], log)

  def test_abort_aborts_children_in_reverse_order(self) -> None:
    """
      Verify abort aborts every child once, in reverse of the order
      the children were given.

      :return: None
    """
    log: list[str] = []
    with project_context() as (_project_root, context):
      children = self._children(context, log)
      composite = CompositeExecutionStep(context, children)

      composite.abort()

    self.assertEqual(['abort c', 'abort b', 'abort a'], log)

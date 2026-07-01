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
from collections.abc import Sequence
import unittest
from typing import override

from dralithus.test.project import project_context
from dralithus.project.composite_execution_step import (
  CompositeExecutionStep)
from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.execution_step import ExecutionStep


class _RecordingStep(ExecutionStep):
  """
    A fake execution step that records its run and rollback calls.

    Each call appends a line to a shared log so tests can check the
    order in which CompositeExecutionStep drives its children and how
    it forwards the dry_run flag. A step may be configured to fail,
    raising DralithusProjectError from run().
  """
  def __init__(
      self,
      context: ProjectContext,
      name: str,
      log: list[str],
      fails: bool = False
  ) -> None:
    """
      Initialize the recording step.

      :param context: The shared project creation context
      :param name: The name used to identify this step in the log
      :param log: The shared list that records run and rollback calls
      :param fails: True if run() should raise DralithusProjectError
      :return: None
    """
    super().__init__(context)
    self._name = name
    self._log = log
    self._fails = fails

  @override
  def run(self, dry_run: bool = False) -> None:
    """
      Record the run call and optionally fail.

      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
      :raises DralithusProjectError: When the step is configured to
        fail
    """
    self._log.append(f'run {self._name} dry_run={dry_run}')
    if self._fails:
      raise DralithusProjectError(f'{self._name} failed')

  @override
  def rollback(self, dry_run: bool = False) -> None:
    """
      Record the rollback call.

      :param dry_run: True if the step should change nothing
      :return: None
    """
    self._log.append(f'rollback {self._name} dry_run={dry_run}')


class _RecordingComposite(CompositeExecutionStep):
  """
    A concrete CompositeExecutionStep that records dry-run delegation.

    Its _run_dry_run() records that it was called instead of doing any
    real validation, so tests can confirm run(dry_run=True) delegates
    to it rather than running the children.
  """
  @override
  def _run_dry_run(self) -> None:
    """
      Record that dry-run validation was delegated to the subclass.

      :return: None
    """
    self._log.append('dry_run')

  def __init__(
      self,
      context: ProjectContext,
      steps: Sequence[ExecutionStep],
      log: list[str]
  ) -> None:
    """
      Initialize the recording composite.

      :param context: The shared project creation context
      :param steps: The child steps, in dependency order
      :param log: The shared list that records calls
      :return: None
    """
    super().__init__(context, steps)
    self._log = log


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
  def _composite(
      context: ProjectContext,
      names: list[str],
      log: list[str],
      failing: str | None = None
  ) -> _RecordingComposite:
    """
      Build a recording composite over child steps named by names.

      :param context: The shared project creation context
      :param names: The child step names, in order
      :param log: The shared list that records calls
      :param failing: The name of the child whose run() should fail,
        or None if no child should fail
      :return: A recording composite over the named child steps
    """
    steps = [
      _RecordingStep(context, name, log, fails=name == failing)
      for name in names]
    return _RecordingComposite(context, steps, log)

  # construction

  def test_cannot_instantiate_abstract_base(self) -> None:
    """
      Verify the base class cannot be instantiated directly because
      _run_dry_run() is abstract.
    """
    with self.assertRaises(TypeError):
      with project_context() as (_, context):
        # noinspection PyAbstractClass
        # pylint: disable-next=abstract-class-instantiated
        CompositeExecutionStep(context, [])  # type: ignore[abstract]

  # run

  def test_run_executes_children_in_order(self) -> None:
    """
      Verify run() runs every child step once, in the order the
      children were given.
    """
    log: list[str] = []
    with project_context() as (_, context):
      composite = TestCompositeExecutionStep._composite(context, ['a', 'b', 'c'], log)

      composite.run()

    self.assertEqual(
      ['run a dry_run=False',
       'run b dry_run=False',
       'run c dry_run=False'],
      log)

  def test_run_rolls_back_and_reraises_on_failure(self) -> None:
    """
      Verify that when a child step raises DralithusProjectError,
      run() rolls back the step's children and re-raises the error.
    """
    log: list[str] = []
    with project_context() as (_, context):
      composite = TestCompositeExecutionStep._composite(
        context, ['a', 'b', 'c'], log, failing='b')

      with self.assertRaises(DralithusProjectError):
        composite.run()

    self.assertEqual(
      ['run a dry_run=False',
       'run b dry_run=False',
       'rollback c dry_run=False',
       'rollback b dry_run=False',
       'rollback a dry_run=False'],
      log)

  def test_run_dry_run_delegates_to_run_dry_run(self) -> None:
    """
      Verify run(dry_run=True) calls the subclass _run_dry_run() and
      does not run the children directly.
    """
    log: list[str] = []
    with project_context() as (_, context):
      composite = TestCompositeExecutionStep._composite(context, ['a', 'b'], log)

      composite.run(dry_run=True)

    self.assertEqual(['dry_run'], log)

  # rollback

  def test_rollback_rolls_back_children_in_reverse(self) -> None:
    """
      Verify rollback() rolls back every child step once, in reverse
      of the order the children were given.
    """
    log: list[str] = []
    with project_context() as (_, context):
      composite = TestCompositeExecutionStep._composite(context, ['a', 'b', 'c'], log)

      composite.rollback()

    self.assertEqual(
      ['rollback c dry_run=False',
       'rollback b dry_run=False',
       'rollback a dry_run=False'],
      log)

  def test_rollback_forwards_dry_run_to_children(self) -> None:
    """
      Verify rollback(dry_run=True) rolls back each child with
      dry_run set to True.
    """
    log: list[str] = []
    with project_context() as (_, context):
      composite = TestCompositeExecutionStep._composite(context, ['a', 'b', 'c'], log)

      composite.rollback(dry_run=True)

    self.assertEqual(
      ['rollback c dry_run=True',
       'rollback b dry_run=True',
       'rollback a dry_run=True'],
      log)


if __name__ == '__main__':
  unittest.main()

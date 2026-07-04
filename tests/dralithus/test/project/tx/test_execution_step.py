"""
  test_execution_step.py: Unit tests for
  dralithus.project.tx.execution_step.
"""
# -------------------------------------------------------------------
# test_execution_step.py: Unit tests for
# dralithus.project.tx.execution_step.
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
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.execution_step import execute
from dralithus.project.tx.project_state import ProjectState


class TestExecute(unittest.TestCase):
  """
    Unit tests for the execute() driver.

    execute() owns the single global abort path: it prepares a step
    against a fresh ProjectState, commits it unless the run is a dry
    run, and aborts the whole step tree when commit fails. Child
    steps are replaced by lightweight recording fakes so the tests
    exercise the driver's phase sequencing rather than any real file
    system behavior.
  """
  def test_execute_prepares_then_commits_step(self) -> None:
    """
      Verify a real run prepares the step and then commits it.

      :return: None
    """
    log: list[str] = []
    with project_context() as (_project_root, context):
      step = RecordingStep(context, 'a', log)

      execute(step, context)

    self.assertEqual(['prepare a', 'commit a'], log)

  def test_execute_dry_run_prepares_only(self) -> None:
    """
      Verify a dry run prepares the step and never commits or
      aborts it.

      :return: None
    """
    log: list[str] = []
    with project_context() as (_project_root, context):
      step = RecordingStep(context, 'a', log)

      execute(step, context, dry_run=True)

    self.assertEqual(['prepare a'], log)

  def test_execute_passes_state_rooted_at_project_root(self) -> None:
    """
      Verify prepare receives a fresh ProjectState rooted at the
      context project root.

      :return: None
    """
    log: list[str] = []
    with project_context() as (project_root, context):
      step = RecordingStep(context, 'a', log)

      execute(step, context)

      state = step.prepared_states[0]
      self.assertIsInstance(state, ProjectState)
      state.claim_file(project_root / 'marker.txt')
      self.assertTrue(state.is_file(project_root / 'marker.txt'))
      with self.assertRaises(DralithusProjectError):
        state.claim_file(project_root.parent / 'marker.txt')

  def test_execute_aborts_step_and_reraises_on_commit_failure(
    self
  ) -> None:
    """
      Verify a commit failure aborts the step and re-raises the
      original error.

      :return: None
    """
    log: list[str] = []
    with project_context() as (_project_root, context):
      step = RecordingStep(context, 'a', log, fails_in='commit')

      with self.assertRaisesRegex(
        DralithusProjectError, 'a commit failed'
      ):
        execute(step, context)

    self.assertEqual(['prepare a', 'commit a', 'abort a'], log)

  def test_execute_does_not_abort_on_prepare_failure(self) -> None:
    """
      Verify a prepare failure propagates without committing or
      aborting, because prepare writes nothing that needs undoing.

      :return: None
    """
    log: list[str] = []
    with project_context() as (_project_root, context):
      step = RecordingStep(context, 'a', log, fails_in='prepare')

      with self.assertRaisesRegex(
        DralithusProjectError, 'a prepare failed'
      ):
        execute(step, context)

    self.assertEqual(['prepare a'], log)

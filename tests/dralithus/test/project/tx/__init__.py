"""
  tx/__init__.py: Unit tests for transactional project creation
  classes.
"""
# -------------------------------------------------------------------
# tx/__init__.py: Unit tests for transactional project creation
# classes.
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
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.execution_step import ExecutionStep
from dralithus.project.tx.project_state import ProjectState


class RecordingStep(ExecutionStep):
  """
    A fake execution step that records its phase calls.

    Each call appends 'prepare <name>', 'commit <name>' or
    'abort <name>' to a shared log so tests can check the order in
    which the execute() driver and CompositeExecutionStep drive
    steps. Every ProjectState passed to prepare is recorded in
    prepared_states. A step may be configured to fail in prepare or
    in commit, raising DralithusProjectError from that phase.
  """
  def __init__(
      self,
      context: ProjectContext,
      name: str,
      log: list[str],
      fails_in: str | None = None
  ) -> None:
    """
      Initialize the recording step.

      :param context: The shared project creation context
      :param name: The name used to identify this step in the log
      :param log: The shared list that records phase calls
      :param fails_in: The phase ('prepare' or 'commit') that should
        raise DralithusProjectError, or None if no phase should fail
      :return: None
    """
    super().__init__(context)
    self._name = name
    self._log = log
    self._fails_in = fails_in
    self.prepared_states: list[ProjectState] = []

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Record the prepare call and optionally fail.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When the step is configured to
        fail in prepare
    """
    self._log.append(f'prepare {self._name}')
    self.prepared_states.append(state)
    if self._fails_in == 'prepare':
      raise DralithusProjectError(f'{self._name} prepare failed')

  @override
  def commit(self) -> None:
    """
      Record the commit call and optionally fail.

      :return: None
      :raises DralithusProjectError: When the step is configured to
        fail in commit
    """
    self._log.append(f'commit {self._name}')
    if self._fails_in == 'commit':
      raise DralithusProjectError(f'{self._name} commit failed')

  @override
  def abort(self) -> None:
    """
      Record the abort call.

      :return: None
    """
    self._log.append(f'abort {self._name}')

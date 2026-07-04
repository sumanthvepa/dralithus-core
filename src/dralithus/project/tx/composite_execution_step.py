"""
  composite_execution_step.py: Define the CompositeExecutionStep
  class.
"""
# -------------------------------------------------------------------
# composite_execution_step.py: Define the CompositeExecutionStep
# class.
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
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.tx.execution_step import ExecutionStep
from dralithus.project.tx.project_state import ProjectState


class CompositeExecutionStep(ExecutionStep):
  """
    Represent an execution step composed of ordered child steps.

    Subclasses build their child steps and pass them, in dependency
    order, to this base; they add no phase logic of their own. The
    base prepares and commits the children in order and aborts them
    in reverse order. The step sequence is the single source of
    child order; subclasses hold no named child attributes.

    commit() deliberately does no failure handling: the execute()
    driver owns the one global abort path.
  """
  def __init__(
      self,
      context: ProjectContext,
      steps: Sequence[ExecutionStep]
  ) -> None:
    """
      Initialize the composite execution step.

      :param context: The shared project creation context
      :param steps: The child steps, in dependency order
      :return: None
    """
    super().__init__(context)
    self._steps = steps

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Prepare the child steps in order.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When a child step cannot be
        satisfied given the current-or-projected state
    """
    for step in self._steps:
      step.prepare(state)

  @override
  def commit(self) -> None:
    """
      Commit the child steps in order.

      :return: None
      :raises DralithusProjectError: When a child step cannot
        complete its work
    """
    for step in self._steps:
      step.commit()

  @override
  def abort(self) -> None:
    """
      Abort the child steps in reverse order.

      :return: None
      :raises DralithusProjectError: When a child step cleanup fails
    """
    for step in reversed(self._steps):
      step.abort()

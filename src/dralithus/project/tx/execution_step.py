"""
  execution_step.py: Define the ExecutionStep abstract base class
  and the execute() driver.
"""
# -------------------------------------------------------------------
# execution_step.py: Define the ExecutionStep abstract base class
# and the execute() driver.
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
from abc import ABC, abstractmethod

from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.project_state import ProjectState


class ExecutionStep(ABC):
  """
    Represent one transactional project-creation step.

    A step is executed as prepare -> commit, with abort undoing a
    committed step. A dry run executes prepare alone. Ownership of
    created artifacts is established at commit time by exclusive
    creation, so abort removes only what this step created.
  """
  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the execution step.

      :param context: The shared project creation context
      :return: None
    """
    self._context = context

  @abstractmethod
  def prepare(self, state: ProjectState) -> None:
    """
      Validate feasibility and declare post-conditions.

      Validate this step against the current-or-projected state, and
      declare the artifacts this step will create as claims on
      state. Must not perform destructive or externally visible
      mutation.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When this step cannot be
        satisfied given the current-or-projected state
    """
    raise NotImplementedError(
      'prepare() must be implemented in derived class')

  @abstractmethod
  def commit(self) -> None:
    """
      Perform the real work, recording ownership of what is created.

      :return: None
      :raises DralithusProjectError: When the work cannot be
        completed
    """
    raise NotImplementedError(
      'commit() must be implemented in derived class')

  @abstractmethod
  def abort(self) -> None:
    """
      Undo what this step's commit created; a no-op otherwise.

      Removes only artifacts this step created. Pre-existing
      artifacts are left in place. Must be idempotent.

      :return: None
      :raises DralithusProjectError: When cleanup fails
    """
    raise NotImplementedError(
      'abort() must be implemented in derived class')


def execute(
    step: ExecutionStep,
    context: ProjectContext,
    dry_run: bool = False
) -> None:
  """
    Prepare a step, then commit it unless this is a dry run.

    A dry run executes prepare alone: nothing is written, so nothing
    needs undoing. A real run executes prepare then commit; when
    commit fails, the whole step tree is aborted before the error is
    re-raised.

    :param step: The step to execute
    :param context: The shared project creation context
    :param dry_run: True if the step should validate without
      changing the file system
    :return: None
    :raises DralithusProjectError: When prepare or commit fails; on
      a commit failure the whole tree is aborted before re-raising
  """
  state = ProjectState(context.project_root)
  step.prepare(state)
  if not dry_run:
    try:
      step.commit()
    except DralithusProjectError:
      step.abort()
      raise

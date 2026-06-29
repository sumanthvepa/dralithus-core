"""
  composite_execution_step.py: Define the CompositeExecutionStep class.
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
from abc import abstractmethod
from collections.abc import Sequence
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.execution_step import ExecutionStep


class CompositeExecutionStep(ExecutionStep):
  """
    Represent an execution step composed of ordered child steps.

    Subclasses build their child steps and pass them, in dependency
    order, to this base. The base runs the children forward and, on
    failure, rolls back its own completed children before re-raising;
    rollback runs the children in reverse order. Dry-run validation is
    step-specific and is delegated to the subclass via _run_dry_run().
  """
  @abstractmethod
  def _run_dry_run(self) -> None:
    """
      Validate existing state without changing the file system.

      Subclasses implement the step-specific dry-run validation,
      because a child file step can be validated only once its parent
      directory exists, and MkdirStep does not create directories
      during a dry run.

      :return: None
      :raises DralithusProjectError: When existing state cannot be
        accepted
    """
    raise NotImplementedError(
      '_run_dry_run() must be implemented in derived class')

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
  def run(self, dry_run: bool = False) -> None:
    """
      Run the composite execution step.

      In a dry run, delegate to the subclass _run_dry_run(). Otherwise,
      run the children in order and, on any failure, roll back the
      step's own completed children before re-raising.

      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
      :raises DralithusProjectError: When the composite step fails
    """
    if dry_run:
      self._run_dry_run()
    else:
      try:
        for step in self._steps:
          step.run()
      except DralithusProjectError:
        self.rollback()
        raise

  @override
  def rollback(self, dry_run: bool = False) -> None:
    """
      Roll back the composite execution step.

      Roll back the children in reverse order. Each child removes only
      what its own run created; pre-existing artifacts are left alone.

      :param dry_run: True if the step should change nothing
      :return: None
      :raises DralithusProjectError: When rollback fails
    """
    for step in reversed(self._steps):
      step.rollback(dry_run)

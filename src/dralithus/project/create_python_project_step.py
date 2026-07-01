"""
  create_python_project_step.py: Define the CreatePythonProjectStep
  class.
"""
# -------------------------------------------------------------------
# create_python_project_step.py: Define the CreatePythonProjectStep
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
from pathlib import Path
from typing import override

from dralithus.project.composite_execution_step import (
  CompositeExecutionStep)
from dralithus.project.context import ProjectContext


class CreatePythonProjectStep(CompositeExecutionStep):
  """
    Create a complete Milestone 42 Python project.

    Wire the leaf and composite project creation steps in dependency
    order and delegate orchestration, rollback, and dry-run validation
    to CompositeExecutionStep.
  """
  @override
  def _run_dry_run(self) -> None:
    """
      Validate existing project state without changing the file
      system.

      :return: None
      :raises DralithusProjectError: When existing project state
        cannot be accepted
    """
    raise NotImplementedError(
      '_run_dry_run() is not implemented yet')

  # pylint: disable-next=super-init-not-called,unused-argument
  def __init__(
    self,
    context: ProjectContext,
    python_executable: Path
  ) -> None:
    """
      Initialize the Python project creation step.

      :param context: The shared project creation context
      :param python_executable: The Python executable used to create
        the project virtual environment
      :return: None
      :raises DralithusProjectError: When a child step constructor
        rejects its inputs
    """
    raise NotImplementedError(
      'CreatePythonProjectStep.__init__() is not implemented yet')

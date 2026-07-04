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

from dralithus.project.context import ProjectContext
from dralithus.project.tx.composite_execution_step import (
  CompositeExecutionStep)


class CreatePythonProjectStep(CompositeExecutionStep):
  """
    Create a complete Python project.

    Wire the leaf and composite project creation steps in dependency
    order and delegate all phase logic to CompositeExecutionStep.
    Because every child declares its post-conditions as claims
    during prepare, a dry run validates every child deeply, with no
    prerequisite guards: the pyproject and dependency children
    validate against the venv and dependency files that earlier
    children will create at commit time.
  """
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

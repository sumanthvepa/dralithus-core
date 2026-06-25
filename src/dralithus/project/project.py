"""
  project.py: Define the Project base class.
"""
# -------------------------------------------------------------------
# project.py: Define the Project base class.
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
from dralithus.project.execution_step import ExecutionStep
from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError


class Project:  # pylint: disable=too-few-public-methods
  """
    Represent a project that can be created.
  """
  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the project.

      :param context: The shared project creation context
      :return: None
    """
    self._context = context
    self._creation_steps: list[ExecutionStep] = []

  def create(self, dry_run: bool = False) -> None:
    """
      Create the project by running its creation steps.

      :param dry_run: True if creation should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: If project creation fails.
    """
    completed_steps: list[ExecutionStep] = []
    try:
      for step in self._creation_steps:
        step.run(dry_run)
        completed_steps.append(step)
    except DralithusProjectError:
      for step in reversed(completed_steps):
        step.rollback(dry_run)
      raise

"""
  create_mypy_configuration_step.py: Define the
  CreateMypyConfigurationStep class.
"""
# -------------------------------------------------------------------
# create_mypy_configuration_step.py: Define the
# CreateMypyConfigurationStep class.
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
from dralithus.project.execution_step import ExecutionStep


class CreateMypyConfigurationStep(ExecutionStep):
  """
    Represent a project creation step that creates mypy configuration
    for a new Milestone 42 Python project.
  """
  def __init__(self) -> None:
    """
      Initialize the mypy configuration creation step.

      :return: None
    """

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the mypy configuration creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
      :raises NotImplementedError: Until behavior is implemented
    """
    raise NotImplementedError(
      'CreateMypyConfigurationStep.run() is not implemented')

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the mypy configuration creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should change nothing
      :return: None
      :raises NotImplementedError: Until behavior is implemented
    """
    raise NotImplementedError(
      'CreateMypyConfigurationStep.rollback() is not implemented')

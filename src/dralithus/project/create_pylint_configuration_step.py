"""
  create_pylint_configuration_step.py: Define the
  CreatePylintConfigurationStep class.
"""
# -------------------------------------------------------------------
# create_pylint_configuration_step.py: Define the
# CreatePylintConfigurationStep class.
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


class CreatePylintConfigurationStep(ExecutionStep):
  """
    Represent a project creation step that creates Pylint
    configuration for a new Milestone 42 Python project.

    The packaged pylintrc resource is the canonical default generated
    for new projects.
  """
  def __init__(self) -> None:
    """
      Initialize the Pylint configuration creation step.

      :return: None
    """

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the Pylint configuration creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
    """
    raise NotImplementedError(
      'CreatePylintConfigurationStep.run() is not implemented yet')

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the Pylint configuration creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should change nothing
      :return: None
    """
    raise NotImplementedError(
      'CreatePylintConfigurationStep.rollback() is not implemented yet')

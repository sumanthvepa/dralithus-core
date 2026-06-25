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
from pathlib import Path
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.create_file_step import CreateFileStep
from dralithus.project.execution_step import ExecutionStep


class CreatePylintConfigurationStep(ExecutionStep):
  """
    Represent a project creation step that creates Pylint
    configuration for a new Milestone 42 Python project.

    The packaged pylintrc resource is the canonical default generated
    for new projects.
  """
  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the Pylint configuration creation step.

      :param context: The shared project creation context
      :return: None
    """
    super().__init__(context)
    self._pylintrc_step = CreateFileStep.from_resource(
      context,
      Path('pylintrc'),
      'dralithus.project.templates',
      'pylintrc')

  @override
  def run(self, dry_run: bool = False) -> None:
    """
      Run the Pylint configuration creation step.

      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
      :raises DralithusProjectError: When pylintrc cannot be created
        or accepted
    """
    self._pylintrc_step.run(dry_run)

  @override
  def rollback(self, dry_run: bool = False) -> None:
    """
      Roll back the Pylint configuration creation step.

      :param dry_run: True if the step should change nothing
      :return: None
      :raises DralithusProjectError: When an owned pylintrc cannot be
        removed
    """
    self._pylintrc_step.rollback(dry_run)

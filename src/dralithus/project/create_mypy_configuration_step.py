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
from pathlib import Path
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.create_file_step import CreateFileStep
from dralithus.project.error import DralithusProjectError
from dralithus.project.execution_step import ExecutionStep
from dralithus.project.mkdir_step import MkdirStep


class CreateMypyConfigurationStep(ExecutionStep):
  """
    Represent a project creation step that creates mypy configuration
    for a new Milestone 42 Python project.
  """
  def _run_dry_run(self, context: ProjectContext) -> None:
    """
      Validate existing mypy configuration state without changing it.

      :param context: The shared project creation context
      :return: None
      :raises DralithusProjectError: When existing mypy configuration
        state cannot be accepted
    """
    self._steps[0].run(context, dry_run=True)
    self._steps[1].run(context, dry_run=True)
    if (context.project_root / 'stubs').is_dir():
      self._steps[2].run(context, dry_run=True)
    if (context.project_root / 'stubs' / 'parameterized').is_dir():
      self._steps[3].run(context, dry_run=True)
      self._steps[4].run(context, dry_run=True)

  def __init__(self) -> None:
    """
      Initialize the mypy configuration creation step.

    :return: None
    """
    self._steps: list[ExecutionStep] = [
      CreateFileStep.from_resource(
        Path('mypy.ini'),
        'dralithus.project.templates',
        'mypy.ini'),
      MkdirStep(Path('stubs') / 'parameterized'),
      CreateFileStep(Path('stubs') / '.gitignore', ''),
      CreateFileStep(
        Path('stubs') / 'parameterized' / '.gitignore',
        ''),
      CreateFileStep.from_resource(
        Path('stubs') / 'parameterized' / '__init__.pyi',
        'dralithus.project.templates.parameterized',
        '__init__.pyi')
    ]

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the mypy configuration creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
      :raises DralithusProjectError: When mypy configuration cannot
        be created or accepted
    """
    if dry_run:
      self._run_dry_run(context)
    else:
      try:
        for step in self._steps:
          step.run(context)
      except DralithusProjectError:
        self.rollback(context)
        raise

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the mypy configuration creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should change nothing
      :return: None
      :raises DralithusProjectError: When an owned mypy artifact
        cannot be removed
    """
    for step in reversed(self._steps):
      step.rollback(context, dry_run)

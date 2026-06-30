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

from dralithus.project.composite_execution_step import (
  CompositeExecutionStep)
from dralithus.project.context import ProjectContext
from dralithus.project.create_file_step import CreateFileStep
from dralithus.project.mkdir_step import MkdirStep


class CreateMypyConfigurationStep(CompositeExecutionStep):
  """
    Represent a project creation step that creates mypy configuration
    for a new Milestone 42 Python project.
  """
  @override
  def _run_dry_run(self) -> None:
    """
      Validate existing mypy configuration state without changing it.

      :return: None
      :raises DralithusProjectError: When existing mypy configuration
        state cannot be accepted
    """
    # Normal step iteration cannot be used here because dry-run
    # directory steps validate without creating directories. Running
    # child file steps when their parent directories are absent would
    # fail validation for paths this composite step normally creates.
    self._mypy_ini.run(dry_run=True)
    self._mkdir.run(dry_run=True)
    if (self._context.project_root / 'stubs').is_dir():
      self._stubs_gitignore.run(dry_run=True)
    if (self._context.project_root / 'stubs' / 'parameterized').is_dir():
      self._parameterized_gitignore.run(dry_run=True)
      self._parameterized_stub.run(dry_run=True)

  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the mypy configuration creation step.

      :param context: The shared project creation context
      :return: None
    """
    self._mypy_ini = CreateFileStep.from_resource(
      context,
      Path('mypy.ini'),
      'dralithus.project.templates',
      'mypy.ini')
    self._mkdir = MkdirStep(context, Path('stubs') / 'parameterized')
    self._stubs_gitignore = CreateFileStep(
      context, Path('stubs') / '.gitignore', '')
    self._parameterized_gitignore = CreateFileStep(
      context,
      Path('stubs') / 'parameterized' / '.gitignore',
      '')
    self._parameterized_stub = CreateFileStep.from_resource(
      context,
      Path('stubs') / 'parameterized' / '__init__.pyi',
      'dralithus.project.templates.parameterized',
      '__init__.pyi')
    super().__init__(
      context,
      (self._mypy_ini,
       self._mkdir,
       self._stubs_gitignore,
       self._parameterized_gitignore,
       self._parameterized_stub))

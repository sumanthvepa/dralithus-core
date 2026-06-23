"""
  create_gitignore_file_step.py: Define the
  CreateGitIgnoreFileStep class.
"""
# -------------------------------------------------------------------
# create_gitignore_file_step.py: Define the
# CreateGitIgnoreFileStep class.
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


class CreateGitIgnoreFileStep(ExecutionStep):
  """
    Represent a project creation step that creates a .gitignore file
    for one project-relative directory.
  """
  _GITIGNORE_FILENAME = '.gitignore'

  def __init__(self, directory: Path) -> None:
    """
      Initialize the .gitignore creation step.

      :param directory: The project-relative directory that should
        contain the .gitignore file
      :return: None
    """
    self._create_file_step = CreateFileStep(
      directory / self._GITIGNORE_FILENAME,
      '')

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the .gitignore creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
    """
    self._create_file_step.run(context, dry_run)

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the .gitignore creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should change nothing
      :return: None
    """
    self._create_file_step.rollback(context, dry_run)

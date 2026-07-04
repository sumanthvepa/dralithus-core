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
from dralithus.project.tx.create_file_step import CreateFileStep
from dralithus.project.tx.execution_step import ExecutionStep
from dralithus.project.tx.project_state import ProjectState


class CreateGitIgnoreFileStep(ExecutionStep):
  """
    Represent a project creation step that creates a .gitignore file
    for one project-relative directory.

    Delegates every phase to an inner CreateFileStep that creates an
    empty .gitignore in the given directory.
  """
  _GITIGNORE_FILENAME = '.gitignore'

  def __init__(self, context: ProjectContext, directory: Path) -> None:
    """
      Initialize the .gitignore creation step.

      :param context: The shared project creation context
      :param directory: The project-relative directory that should
        contain the .gitignore file
      :return: None
      :raises DralithusProjectError: When directory is absolute
    """
    super().__init__(context)
    self._create_file_step = CreateFileStep(
      context,
      directory / self._GITIGNORE_FILENAME,
      '')

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Prepare the inner file creation step.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When the .gitignore target
        cannot be accepted
    """
    self._create_file_step.prepare(state)

  @override
  def commit(self) -> None:
    """
      Commit the inner file creation step.

      :return: None
      :raises DralithusProjectError: When the .gitignore file cannot
        be created or written
    """
    self._create_file_step.commit()

  @override
  def abort(self) -> None:
    """
      Abort the inner file creation step.

      :return: None
      :raises DralithusProjectError: When the owned .gitignore file
        cannot be removed
    """
    self._create_file_step.abort()

"""
  mkdir_step.py: Define the MkdirStep class.
"""
# -------------------------------------------------------------------
# mkdir_step.py: Define the MkdirStep class.
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
from dralithus.project.tx.execution_step import ExecutionStep
from dralithus.project.tx.project_state import ProjectState


class MkdirStep(ExecutionStep):
  """
    Represent a project creation step that creates a directory.

    prepare() claims the directory and every missing parent it would
    create, and rejects a non-directory occupant. commit() creates
    the missing directories, recording which it made. abort()
    removes the recorded directories in reverse order; pre-existing
    directories are left in place.
  """
  # pylint: disable-next=super-init-not-called,unused-argument
  def __init__(self, context: ProjectContext, directory: Path) -> None:
    """
      Initialize the directory creation step.

      :param context: The shared project creation context
      :param directory: The project-relative directory to create
      :return: None
      :raises DralithusProjectError: When directory is not relative
    """
    raise NotImplementedError(
      'MkdirStep.__init__() is not implemented yet')

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Validate the directory path and claim it.

      Claims the directory and every missing parent this step would
      create. Rejects a current-or-projected non-directory occupant
      of the path.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When the path is occupied by a
        non-directory
    """
    raise NotImplementedError(
      'prepare() is not implemented yet')

  @override
  def commit(self) -> None:
    """
      Create the missing directories, recording which were made.

      :return: None
      :raises DralithusProjectError: When directory creation fails
    """
    raise NotImplementedError(
      'commit() is not implemented yet')

  @override
  def abort(self) -> None:
    """
      Remove the directories this step created, in reverse order.

      Pre-existing directories are left in place.

      :return: None
      :raises DralithusProjectError: When directory removal fails
    """
    raise NotImplementedError(
      'abort() is not implemented yet')

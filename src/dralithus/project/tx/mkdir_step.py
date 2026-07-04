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
import os
from pathlib import Path
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
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
  def _missing_directories(self, root: Path) -> list[Path]:
    """
      Find the directories that need to be created.

      :param root: The project root path
      :return: Project-relative directories that need to be created
      :raises DralithusProjectError: When a path exists but is not a
        directory
    """
    missing: list[Path] = []
    current = self._directory
    while current != Path('.') and self._directory_does_not_exist(
        root / current):
      missing.append(current)
      current = current.parent
    return missing

  def _create_directory(self, root: Path) -> None:
    """
      Create the directory for this step.

      :param root: The project root path
      :return: None
      :raises DralithusProjectError: When directory creation fails
    """
    try:
      target = root / self._directory
      target.mkdir(parents=True, exist_ok=True)
    except OSError as error:
      raise DralithusProjectError(
        f'Could not create directory: {self._directory}') from error

  @staticmethod
  def _directory_does_not_exist(path: Path) -> bool:
    """
      Check if a directory path does not exist.

      :param path: The path to check
      :return: True if path does not exist, False if path is a
        directory
      :raises DralithusProjectError: When path exists but is not a
        directory
    """
    if path.is_dir():
      return False
    if path.exists():
      raise DralithusProjectError(f'Path is not a directory: {path}')
    return True

  @staticmethod
  def _remove_directory(base: Path, path: Path) -> None:
    """
      Remove a directory.

      :param base: The base directory for path
      :param path: The path of the directory to remove
      :return: None
      :raises DralithusProjectError: When directory removal fails
    """
    try:
      (base / path).rmdir()
    except OSError as error:
      raise DralithusProjectError(
        f'Could not remove directory: {path}') from error

  def __init__(self, context: ProjectContext, directory: Path) -> None:
    """
      Initialize the directory creation step.

      :param context: The shared project creation context
      :param directory: The project-relative directory to create
      :return: None
      :raises DralithusProjectError: When directory is not relative
    """
    super().__init__(context)
    if directory.is_absolute():
      raise DralithusProjectError(
        f'Directory must be relative: {directory}')
    self._directory = directory
    self._created_directories: list[Path] = []

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Validate the directory path and claim it.

      Claims the directory and every missing parent this step would
      create, walking up until a current-or-projected directory is
      found. Rejects a current-or-projected non-directory occupant
      of any path on the way.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When a path is occupied by a
        non-directory
    """
    root = self._context.project_root
    current = self._directory
    while current != Path('.') and not state.is_dir(root / current):
      path = root / current
      if state.is_file(path) or os.path.lexists(path):
        raise DralithusProjectError(
          f'Path is not a directory: {path}')
      state.claim_directory(path)
      current = current.parent

  @override
  def commit(self) -> None:
    """
      Create the missing directories, recording which were made.

      :return: None
      :raises DralithusProjectError: When directory creation fails
    """
    missing = self._missing_directories(self._context.project_root)
    self._create_directory(self._context.project_root)
    self._created_directories.extend(reversed(missing))

  @override
  def abort(self) -> None:
    """
      Remove the directories this step created, in reverse order.

      Pre-existing directories are left in place.

      :return: None
      :raises DralithusProjectError: When directory removal fails
    """
    while self._created_directories:
      self._remove_directory(
        self._context.project_root,
        self._created_directories[-1])
      self._created_directories.pop()

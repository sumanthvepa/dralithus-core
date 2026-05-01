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

from dralithus.project.context import ProjectContext
from dralithus.project.creation_step import CreationStep
from dralithus.project.error import DralithusProjectError


class MkdirStep(CreationStep):
  """
    Represent a project creation step that creates a directory.
  """
  def __init__(self, directory: Path) -> None:
    """
      Initialize the directory creation step.

      :param directory: The project-relative directory to create
      :return: None
      :raises DralithusProjectError: When directory is not relative
    """
    if directory.is_absolute():
      raise DralithusProjectError(
        f'Directory must be relative: {directory}')
    self._directory = directory
    self._created_directories: list[Path] = []

  @staticmethod
  def _directory_does_not_exist(path: Path) -> bool:
    """
      Check if a directory path does not exist.

      :param path: The path to check
      :return: True if path does not exist, False if path is a directory
      :raises DralithusProjectError: When path exists but is not a
        directory
    """
    if path.is_dir():
      return False
    if path.exists():
      raise DralithusProjectError(f'Path is not a directory: {path}')
    return True

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
    while current != Path('.') and self._directory_does_not_exist(root / current):
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

  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the directory creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When directory creation fails
    """
    missing = self._missing_directories(context.project_root)
    if not dry_run:
      self._create_directory(context.project_root)
      self._created_directories.extend(reversed(missing))

  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the directory creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When directory removal fails
    """
    if not dry_run:
      while self._created_directories:
        self._remove_directory(
          context.project_root,
          self._created_directories[-1])
        self._created_directories.pop()

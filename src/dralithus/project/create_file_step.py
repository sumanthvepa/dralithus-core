"""
  create_file_step.py: Define the CreateFileStep class.
"""
# -------------------------------------------------------------------
# create_file_step.py: Define the CreateFileStep class.
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
from importlib import resources
import os
from pathlib import Path
from typing import Self, override

from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.execution_step import ExecutionStep


class CreateFileStep(ExecutionStep):
  """
    Represent a project creation step that creates one file.
  """
  _file_created: bool

  def _remove_created_file(self, path: Path) -> None:
    """
      Remove the file owned by this step.

      Files already removed externally are accepted silently.

      :param path: The target file path
      :return: None
      :raises DralithusProjectError: When the file cannot be removed
    """
    try:
      path.unlink(missing_ok=True)
    except OSError as error:
      raise DralithusProjectError(
        f'Could not remove file: {path}') from error
    self._file_created = False

  def _create_file(self, path: Path) -> None:
    """
      Create the target file exclusively.

      :param path: The target file path
      :return: None
      :raises DralithusProjectError: When the file cannot be created
        or written
    """
    try:
      # The with statement starts only after ownership is recorded.
      # pylint: disable-next=consider-using-with
      file = path.open('x', encoding='utf-8')
    except FileExistsError:
      self._verify_existing_file(path)
    except OSError as error:
      raise DralithusProjectError(
        f'Could not create file: {path}') from error
    else:
      self._file_created = True
      try:
        with file:
          file.write(self._content)
      except OSError as error:
        self._remove_created_file(path)
        raise DralithusProjectError(
          f'Could not write file: {path}') from error

  @staticmethod
  def _verify_parent(path: Path) -> None:
    """
      Verify that the target parent is a usable directory.

      :param path: The target file path
      :return: None
      :raises DralithusProjectError: When the parent is not a usable
        directory
    """
    try:
      parent_is_directory = path.parent.is_dir()
    except OSError as error:
      raise DralithusProjectError(
        f'Could not inspect parent directory: {path.parent}') from error
    if not parent_is_directory:
      if os.path.lexists(path.parent):
        raise DralithusProjectError(
          f'Parent path is not a directory: {path.parent}')
      raise DralithusProjectError(
        f'Parent directory does not exist: {path.parent}')

  @staticmethod
  def _verify_existing_file(path: Path) -> None:
    """
      Verify that an existing target is a readable regular file.

      Valid symlinks to readable regular files are accepted.

      :param path: The target file path
      :return: None
      :raises DralithusProjectError: When the target is not a
        readable regular file
    """
    try:
      regular_file = path.is_file()
    except OSError as error:
      raise DralithusProjectError(
        f'Could not inspect file: {path}') from error
    if not regular_file:
      raise DralithusProjectError(
        f'Path is not a regular file: {path}')
    try:
      with path.open('r', encoding='utf-8'):
        pass
    except OSError as error:
      raise DralithusProjectError(
        f'Could not read file: {path}') from error

  def __init__(self, filename: Path, content: str) -> None:
    """
      Initialize the file creation step.

      :param filename: The project-relative file to create
      :param content: The literal UTF-8 text to write
      :return: None
      :raises DralithusProjectError: When filename is absolute
    """
    if filename.is_absolute():
      raise DralithusProjectError(
        f'Filename must be relative: {filename}')
    self._filename = filename
    self._content = content
    self._file_created = False

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the file creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
      :raises DralithusProjectError: When the target cannot be
        created or accepted
    """
    path = context.project_root / self._filename
    self._verify_parent(path)
    if dry_run:
      if os.path.lexists(path):
        self._verify_existing_file(path)
    else:
      self._create_file(path)

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the file creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should change nothing
      :return: None
      :raises DralithusProjectError: When the owned file cannot be
        removed
    """
    if not dry_run and self._file_created:
      self._remove_created_file(context.project_root / self._filename)

  @classmethod
  def from_file(cls, filename: Path, source_filename: Path) -> Self:
    """
      Create a step whose content is read from a file.

      :param filename: The project-relative file to create
      :param source_filename: The source file to read
      :return: The configured file creation step
      :raises DralithusProjectError: When the source cannot be read
    """
    try:
      content = source_filename.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
      raise DralithusProjectError(
        f'Could not read source file: {source_filename}') from error
    return cls(filename, content)

  @classmethod
  def from_resource(
    cls,
    filename: Path,
    package: str,
    resource: str
  ) -> Self:
    """
      Create a step whose content is read from a package resource.

      :param filename: The project-relative file to create
      :param package: The package containing the resource
      :param resource: The package-relative resource name
      :return: The configured file creation step
      :raises DralithusProjectError: When the resource cannot be read
    """
    try:
      content = resources.files(package).joinpath(resource).read_text(
        encoding='utf-8')
    except (ImportError, OSError, TypeError, UnicodeError) as error:
      raise DralithusProjectError(
        f'Could not read package resource: {package}/{resource}') from error
    return cls(filename, content)

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

from jinja2 import Environment, TemplateError

from dralithus.project.context import ProjectContext, ProjectContextDict
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.execution_step import ExecutionStep
from dralithus.project.tx.project_state import ProjectState


class CreateFileStep(ExecutionStep):
  """
    Represent a project creation step that creates one file.

    prepare() requires the parent directory to be a current or
    projected directory, validates an acceptable existing file or an
    absent path, and claims the file. commit() creates the file by
    exclusive creation, recording ownership the instant creation
    succeeds, and then writes the content. abort() removes the file
    only when this step created it.
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

      Ownership is recorded the instant exclusive creation succeeds,
      before the content write, so a failed write can still be
      cleaned up. A pre-existing target is re-verified rather than
      overwritten, because it may have appeared after prepare.

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
  def _verify_parent(path: Path, state: ProjectState) -> None:
    """
      Verify that the target parent is a usable directory.

      The parent is acceptable when it is a directory on the real
      file system or is claimed as a directory by an earlier step.

      :param path: The target file path
      :param state: The projected project state to read
      :return: None
      :raises DralithusProjectError: When the parent is not a
        current-or-projected directory
    """
    if not state.is_dir(path.parent):
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

  @staticmethod
  def _template_context(context: ProjectContext) -> ProjectContextDict:
    """
      Convert a project context into a Jinja2 template context.

      :param context: The shared project creation context
      :return: The template context dictionary
    """
    return context.as_dict()

  def __init__(
    self,
    context: ProjectContext,
    filename: Path,
    content: str
  ) -> None:
    """
      Initialize the file creation step.

      :param context: The shared project creation context
      :param filename: The project-relative file to create
      :param content: The literal UTF-8 text to write
      :return: None
      :raises DralithusProjectError: When filename is absolute
    """
    super().__init__(context)
    if filename.is_absolute():
      raise DralithusProjectError(
        f'Filename must be relative: {filename}')
    self._filename = filename
    self._content = content
    self._file_created = False

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Validate the target file and claim it.

      Requires the parent directory to be a current or projected
      directory. An existing target must be a readable regular file;
      an absent target is claimed as to-be-created.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When the parent is not a
        current-or-projected directory or the target cannot be
        accepted
    """
    path = self._context.project_root / self._filename
    self._verify_parent(path, state)
    if os.path.lexists(path):
      self._verify_existing_file(path)
    state.claim_file(path)

  @override
  def commit(self) -> None:
    """
      Create the target file exclusively and write its content.

      Ownership is recorded the instant exclusive creation succeeds,
      before the content write. An acceptable pre-existing file is
      left in place and not owned.

      :return: None
      :raises DralithusProjectError: When the file cannot be created
        or written
    """
    self._create_file(self._context.project_root / self._filename)

  @override
  def abort(self) -> None:
    """
      Remove the target file when this step created it.

      Pre-existing files are left in place. Files already removed
      externally are accepted silently.

      :return: None
      :raises DralithusProjectError: When the owned file cannot be
        removed
    """
    if self._file_created:
      self._remove_created_file(
        self._context.project_root / self._filename)

  @classmethod
  def from_file(
    cls,
    context: ProjectContext,
    filename: Path,
    source_filename: Path
  ) -> Self:
    """
      Create a step whose content is read from a file.

      :param context: The shared project creation context
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
    return cls(context, filename, content)

  @classmethod
  def from_resource(
    cls,
    context: ProjectContext,
    filename: Path,
    package: str,
    resource: str
  ) -> Self:
    """
      Create a step whose content is read from a package resource.

      :param context: The shared project creation context
      :param filename: The project-relative file to create
      :param package: The package containing the resource
      :param resource: The package-relative resource name
      :return: The configured file creation step
      :raises DralithusProjectError: When the resource cannot be
        read
    """
    try:
      content = resources.files(package).joinpath(resource).read_text(
        encoding='utf-8')
    except (ImportError, OSError, TypeError, UnicodeError) as error:
      raise DralithusProjectError(
        f'Could not read package resource: '
        f'{package}/{resource}') from error
    return cls(context, filename, content)

  @classmethod
  def from_template_resource(
    cls,
    context: ProjectContext,
    filename: Path,
    package: str,
    resource: str
  ) -> Self:
    """
      Create a step whose content is rendered from a package
      template.

      :param context: The shared project creation context
      :param filename: The project-relative file to create
      :param package: The package containing the resource
      :param resource: The package-relative resource name
      :return: The configured file creation step
      :raises DralithusProjectError: When the resource cannot be
        read or rendered
    """
    try:
      template_text = resources.files(package).joinpath(
        resource).read_text(encoding='utf-8')
      content = Environment(keep_trailing_newline=True).from_string(
        template_text).render(
        cls._template_context(context))
    except (
      ImportError,
      OSError,
      TemplateError,
      TypeError,
      UnicodeError
    ) as error:
      raise DralithusProjectError(
        f'Could not render package resource: '
        f'{package}/{resource}') from error
    return cls(context, filename, content)

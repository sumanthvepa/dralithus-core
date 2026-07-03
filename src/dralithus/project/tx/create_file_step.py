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
from pathlib import Path
from typing import Self, override

from dralithus.project.context import ProjectContext
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
  # pylint: disable-next=super-init-not-called,unused-argument
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
    raise NotImplementedError(
      'CreateFileStep.__init__() is not implemented yet')

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
    raise NotImplementedError(
      'prepare() is not implemented yet')

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
    raise NotImplementedError(
      'commit() is not implemented yet')

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
    raise NotImplementedError(
      'abort() is not implemented yet')

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
    raise NotImplementedError(
      'from_file() is not implemented yet')

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
    raise NotImplementedError(
      'from_resource() is not implemented yet')

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
    raise NotImplementedError(
      'from_template_resource() is not implemented yet')

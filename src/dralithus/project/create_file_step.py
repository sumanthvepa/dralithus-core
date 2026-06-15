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
from dralithus.project.execution_step import ExecutionStep


class CreateFileStep(ExecutionStep):
  """
    Represent a project creation step that creates one file.
  """
  def __init__(self, filename: Path, content: str) -> None:
    """
      Initialize the file creation step.

      :param filename: The project-relative file to create
      :param content: The literal UTF-8 text to write
      :return: None
    """
    self._filename = filename
    self._content = content

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the file creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
    """
    raise NotImplementedError('CreateFileStep.run() is not implemented')

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the file creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should change nothing
      :return: None
    """
    raise NotImplementedError(
      'CreateFileStep.rollback() is not implemented')

  @classmethod
  def from_file(cls, filename: Path, source_filename: Path) -> Self:
    """
      Create a step whose content is read from a file.

      :param filename: The project-relative file to create
      :param source_filename: The source file to read
      :return: The configured file creation step
    """
    raise NotImplementedError(
      'CreateFileStep.from_file() is not implemented')

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
    """
    raise NotImplementedError(
      'CreateFileStep.from_resource() is not implemented')

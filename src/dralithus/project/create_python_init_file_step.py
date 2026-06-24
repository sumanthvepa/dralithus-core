"""
  create_python_init_file_step.py: Define the
  CreatePythonInitFileStep class.
"""
# -------------------------------------------------------------------
# create_python_init_file_step.py: Define the
# CreatePythonInitFileStep class.
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
from dralithus.project.copyright_header import CopyrightHeader
from dralithus.project.create_file_step import CreateFileStep
from dralithus.project.execution_step import ExecutionStep


class CreatePythonInitFileStep(ExecutionStep):
  """
    Represent a project creation step that creates an __init__.py file
    with a copyright notice in one project-relative directory.
  """
  def _content(self, context: ProjectContext) -> str:
    """
      Return the generated __init__.py file content.

      :param context: The shared project creation context
      :return: The UTF-8 text to write
    """
    return self._copyright_header.text('python', context)

  def __init__(
    self,
    directory: Path,
    copyright_header: CopyrightHeader
  ) -> None:
    """
      Initialize the Python __init__.py creation step.

      :param directory: The project-relative directory that should
        contain the __init__.py file
      :param copyright_header: The copyright header renderer for the
        generated __init__.py file
      :return: None
    """
    self._copyright_header = copyright_header
    self._create_file_step = CreateFileStep(
      directory / self.init_filename,
      self._content)

  @property
  def init_filename(self) -> str:
    """
      Return the Python package initializer filename.

      :return: The initializer filename
    """
    return '__init__.py'

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the Python __init__.py creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
    """
    self._create_file_step.run(context, dry_run)

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the Python __init__.py creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should change nothing
      :return: None
    """
    self._create_file_step.rollback(context, dry_run)

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
  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def __init__(
    self,
    context: ProjectContext,
    directory: Path,
    copyright_header: CopyrightHeader,
    description: str
  ) -> None:
    """
      Initialize the Python __init__.py creation step.

      The generated __init__.py begins with a module docstring holding
      the description, followed by the copyright header that repeats
      the same description. Both are rendered here, because the project
      context is known at construction time.

      :param context: The shared project creation context
      :param directory: The project-relative directory that should
        contain the __init__.py file
      :param copyright_header: The copyright header renderer for the
        generated __init__.py file
      :param description: The file description for the docstring and
        the copyright header
      :return: None
    """
    super().__init__(context)
    header = copyright_header.text('python', context, description)
    content = f'"""\n  {description}\n"""\n{header}'
    self._create_file_step = CreateFileStep(
      context,
      directory / self.init_filename,
      content)

  @property
  def init_filename(self) -> str:
    """
      Return the Python package initializer filename.

      :return: The initializer filename
    """
    return '__init__.py'

  @override
  def run(self, dry_run: bool = False) -> None:
    """
      Run the Python __init__.py creation step.

      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
    """
    self._create_file_step.run(dry_run)

  @override
  def rollback(self, dry_run: bool = False) -> None:
    """
      Roll back the Python __init__.py creation step.

      :param dry_run: True if the step should change nothing
      :return: None
    """
    self._create_file_step.rollback(dry_run)

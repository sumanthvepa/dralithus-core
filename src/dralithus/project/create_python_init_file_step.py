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
from dralithus.project.execution_step import ExecutionStep


class CreatePythonInitFileStep(ExecutionStep):
  """
    Represent a project creation step that creates an __init__.py file
    with a copyright notice in one project-relative directory.
  """
  def __init__(self, directory: Path) -> None:
    """
      Initialize the Python __init__.py creation step.

      :param directory: The project-relative directory that should
        contain the __init__.py file
      :return: None
    """
    raise NotImplementedError()

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the Python __init__.py creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
    """
    raise NotImplementedError()

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the Python __init__.py creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should change nothing
      :return: None
    """
    raise NotImplementedError()

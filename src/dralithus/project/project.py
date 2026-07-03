"""
  project.py: Define project facade classes.
"""
# -------------------------------------------------------------------
# project.py: Define project facade classes.
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
from abc import ABC, abstractmethod
from pathlib import Path
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.create_python_project_step import (
  CreatePythonProjectStep)


class Project(ABC):  # pylint: disable=too-few-public-methods
  """
    Represent the abstract project lifecycle API.
  """
  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the project.

      :param context: The shared project creation context
      :return: None
    """
    self._context = context

  @abstractmethod
  def create(self, dry_run: bool = False) -> None:
    """
      Create the project.

      :param dry_run: True if creation should report what it would
        do without changing the file system
      :return: None
      :raises NotImplementedError: Always, in abstract implementations
    """
    raise NotImplementedError

  @abstractmethod
  def update(self, dry_run: bool = False) -> None:
    """
      Update the project.

      :param dry_run: True if update should report what it would do
        without changing the file system
      :return: None
      :raises NotImplementedError: Always, in abstract implementations
    """
    raise NotImplementedError


class PythonProject(Project):
  """
    Represent a Python project facade.
  """
  def __init__(
      self,
      context: ProjectContext,
      python_executable: Path
  ) -> None:
    """
      Initialize the Python project facade.

      :param context: The shared project creation context
      :param python_executable: The Python executable used to create
        the project virtual environment
      :return: None
    """
    super().__init__(context)
    self._create_step = CreatePythonProjectStep(
      context,
      python_executable)

  @override
  def create(self, dry_run: bool = False) -> None:
    """
      Create the Python project.

      :param dry_run: True if creation should report what it would
        do without changing the file system
      :return: None
    """
    self._create_step.run(dry_run)

  @override
  def update(self, dry_run: bool = False) -> None:
    """
      Update the Python project.

      :param dry_run: True if update should report what it would do
        without changing the file system
      :return: None
      :raises NotImplementedError: Always for this release
    """
    raise NotImplementedError(
      'PythonProject.update() is not implemented yet')

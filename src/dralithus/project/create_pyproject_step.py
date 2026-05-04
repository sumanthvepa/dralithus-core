"""
  create_pyproject_step.py: Define the CreatePyProjectStep class.
"""
# -------------------------------------------------------------------
# create_pyproject_step.py: Define the CreatePyProjectStep class.
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
from typing_extensions import override

from dralithus.project.context import ProjectContext
from dralithus.project.execution_step import ExecutionStep


class CreatePyProjectStep(ExecutionStep):
  """
    Represent a project creation step that creates pyproject.toml.
  """
  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def __init__(
    self,
    project_name: str,
    project_description: str,
    package_name: str,
    project_version: str = '0.1.0'
  ) -> None:
    """
      Initialize the pyproject.toml creation step.

      :param project_name: The project distribution name
      :param project_description: The project description
      :param package_name: The Python package name
      :param project_version: The project version
      :return: None
    """
    raise NotImplementedError()

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the pyproject.toml creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
    """
    raise NotImplementedError()

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the pyproject.toml creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
    """
    raise NotImplementedError()

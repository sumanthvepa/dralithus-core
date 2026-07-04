"""
  project_config.py: Define the ProjectConfig class.
"""
# -------------------------------------------------------------------
# project_config.py: Define the ProjectConfig class.
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
from typing import Self

from dralithus.project.context import ProjectContext
from dralithus.project.project import Project, PythonProject


class ProjectConfig:
  """
    Hold validated project-creation configuration.

    This command-facing model is distinct from ProjectContext. It
    stores the validated context and the resolved Python executable
    needed to build the concrete project facade.
  """
  def __init__(
      self,
      context: ProjectContext,
      python_executable: Path
  ) -> None:
    """
      Initialize the project configuration.

      :param context: The validated project creation context
      :param python_executable: The resolved Python executable
      :return: None
    """
    self._context = context
    self._python_executable = python_executable

  @property
  def context(self) -> ProjectContext:
    """
      Return the validated project context.

      :return: The validated project context
    """
    return self._context

  @property
  def python_executable(self) -> Path:
    """
      Return the resolved Python executable.

      :return: The resolved Python executable
    """
    return self._python_executable

  def project(self) -> Project:
    """
      Build the concrete project facade for this configuration.

      :return: The project facade for this configuration
    """
    return PythonProject(self.context, self.python_executable)

  @classmethod
  def from_toml_file(cls, config_path: Path) -> Self:
    """
      Create a ProjectConfig from a TOML configuration file.

      TOML parsing and validation are intentionally deferred to a
      later checkpoint.

      :param config_path: The TOML configuration file path
      :return: The validated project configuration
      :raises NotImplementedError: Always in this skeleton
    """
    del cls
    del config_path
    raise NotImplementedError(
      'ProjectConfig.from_toml_file() is not implemented yet')

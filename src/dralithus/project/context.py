"""
  context.py: Define the ProjectContext class.
"""
# -------------------------------------------------------------------
# context.py: Define the ProjectContext class.
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
import keyword
from pathlib import Path
from typing import TypedDict

from dralithus.project.copyright_header import CopyrightHeader
from dralithus.project.error import DralithusProjectError


class ProjectContextDict(TypedDict):
  """
    Typed dictionary representation of a ProjectContext.
  """
  project_name: str
  project_description: str
  project_version: str
  project_copyright: CopyrightHeader
  project_root: Path
  package_name: str
  venv_name: str
  venv_path: Path
  venv_python: Path


class ProjectContext:
  """
    Hold shared state for project creation steps.
  """
  @staticmethod
  def _validate_project_root(project_root: Path) -> Path:
    """
      Validate the project root.

      :param project_root: The project root to validate
      :return: The validated project root
      :raises DralithusProjectError: When project_root does not exist
        or is not a directory
    """
    if not project_root.exists():
      raise DralithusProjectError(
        f'Project root does not exist: {project_root}')
    if not project_root.is_dir():
      raise DralithusProjectError(
        f'Project root is not a directory: {project_root}')
    return project_root

  @staticmethod
  def _validate_venv_name(venv_name: str) -> str:
    """
      Validate that venv_name is a single directory name.

      :param venv_name: The venv name to validate
      :return: The validated venv name
      :raises DralithusProjectError: When venv_name is empty or has
        path components
    """
    if venv_name == '':
      raise DralithusProjectError('Venv name must not be empty')
    parts = Path(venv_name).parts
    if len(parts) != 1 or parts[0] == '..':
      raise DralithusProjectError(
        f'Venv name must not contain path components: {venv_name}')
    return venv_name

  @staticmethod
  def _validate_project_name(project_name: str) -> str:
    """
      Validate the project name.

      :param project_name: The project name to validate
      :return: The validated project name
      :raises DralithusProjectError: When project_name is empty or
        has leading or trailing whitespace
    """
    if project_name == '':
      raise DralithusProjectError('Project name must not be empty')
    if project_name.strip() != project_name:
      raise DralithusProjectError(
        f'Project name must not contain leading or trailing '
        f'whitespace: {project_name}')
    return project_name

  @staticmethod
  def _validate_project_description(project_description: str) -> str:
    """
      Validate the project description.

      :param project_description: The project description to validate
      :return: The validated project description
      :raises DralithusProjectError: When project_description has
        leading or trailing whitespace
    """
    if project_description != '':
      if project_description.strip() != project_description:
        raise DralithusProjectError(
          'Project description must not contain leading or trailing '
          'whitespace')
    return project_description

  @staticmethod
  def _validate_project_version(project_version: str) -> str:
    """
      Validate the project version.

      :param project_version: The project version to validate
      :return: The validated project version
      :raises DralithusProjectError: When project_version is empty or
        has leading or trailing whitespace
    """
    if project_version == '':
      raise DralithusProjectError('Project version must not be empty')
    if project_version.strip() != project_version:
      raise DralithusProjectError(
        f'Project version must not contain leading or trailing '
        f'whitespace: {project_version}')
    return project_version

  @staticmethod
  def validate_package_name(package_name: str) -> str:
    """
      Validate that package_name is a valid Python package name.

      :param package_name: The package name to validate
      :return: The validated package name
      :raises DralithusProjectError: When package_name is empty, not
        a valid identifier, a Python keyword, or not lowercase
    """
    if package_name == '':
      raise DralithusProjectError('Package name must not be empty')
    if not package_name.isidentifier():
      raise DralithusProjectError(
        f'Package name is not a valid identifier: {package_name}')
    if keyword.iskeyword(package_name):
      raise DralithusProjectError(
        f'Package name must not be a Python keyword: {package_name}')
    if package_name != package_name.lower():
      raise DralithusProjectError(
        f'Package name must be lowercase: {package_name}')
    return package_name

  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def __init__(
      self,
      project_name: str,
      project_description: str,
      project_version: str,
      project_copyright: CopyrightHeader,
      project_root: Path,
      package_name: str,
      venv_name: str = 'venv'
  ) -> None:
    """
      Initialize the project context.

      :param project_name: The distribution/project name
      :param project_description: The project description
      :param project_version: The project version
      :param project_copyright: The shared copyright header renderer
      :param project_root: The root directory of the project
      :param package_name: The Python package name
      :param venv_name: The name of the virtual environment directory
      :return: None
      :raises DralithusProjectError: When a supplied value is invalid
    """
    self.project_name = self._validate_project_name(project_name)
    self.project_description = self._validate_project_description(
      project_description)
    self.project_version = self._validate_project_version(project_version)
    self.copyright_header = project_copyright
    self.project_root = self._validate_project_root(project_root)
    self.package_name = self.validate_package_name(package_name)
    self.venv_name = self._validate_venv_name(venv_name)

  @property
  def venv_path(self) -> Path:
    """
      Return the virtual environment path.

      :return: The path to the project virtual environment
    """
    return self.project_root / self.venv_name

  @property
  def venv_python(self) -> Path:
    """
      Return the virtual environment Python executable path.

      :return: The path to the project virtual environment's Python
        executable
    """
    # POSIX-only for now; Windows venv layout support is deferred.
    return self.venv_path / 'bin' / 'python'

  def as_dict(self) -> ProjectContextDict:
    """
      Return a typed dictionary of all context fields.

      :return: A ProjectContextDict containing every field and
        derived property of this context
    """
    return ProjectContextDict(
      project_name=self.project_name,
      project_description=self.project_description,
      project_version=self.project_version,
      project_copyright=self.copyright_header,
      project_root=self.project_root,
      package_name=self.package_name,
      venv_name=self.venv_name,
      venv_path=self.venv_path,
      venv_python=self.venv_python)

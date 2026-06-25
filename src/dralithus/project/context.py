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

from dralithus.project.error import DralithusProjectError


class ProjectContext:
  """
    Hold shared state for project creation steps.
  """
  @staticmethod
  def _validate_venv_name(venv_name: str) -> None:
    """
      Validate that venv_name is a single directory name.

      :param venv_name: The venv name to validate
      :return: None
      :raises DralithusProjectError: When venv_name is empty or has
        path components
    """
    if venv_name == '':
      raise DralithusProjectError('Venv name must not be empty')
    parts = Path(venv_name).parts
    if len(parts) != 1 or parts[0] == '..':
      raise DralithusProjectError(
        f'Venv name must not contain path components: {venv_name}')

  @staticmethod
  def validate_package_name(package_name: str) -> None:
    """
      Validate that package_name is a valid Python package name.

      :param package_name: The package name to validate
      :return: None
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

  # pylint: disable-next=too-many-arguments, too-many-positional-arguments
  def __init__(
      self,
      project_root: Path,
      package_name: str,
      copyright_holder: str,
      copyright_year: int | None,
      venv_name: str = 'venv'
  ) -> None:
    """
      Initialize the project context.

      :param project_root: The root directory of the project
      :param package_name: The Python package name
      :param copyright_holder: The copyright holder name
      :param copyright_year: The copyright year, or None for the
        current year
      :param venv_name: The name of the virtual environment directory
      :return: None
      :raises DralithusProjectError: When venv_name or package_name
        is invalid
    """
    self._validate_venv_name(venv_name)
    self.validate_package_name(package_name)
    self.project_root = project_root
    self.venv_name = venv_name
    self.copyright_holder = copyright_holder
    self.copyright_year = copyright_year
    self.package_name = package_name

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

"""
  packages3.py: Define the Packages3 class.
"""
# -------------------------------------------------------------------
# packages3.py: Define the Packages3 class.
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
from __future__ import annotations
from pathlib import Path

from dralithus.project.error import DralithusProjectError


class Packages3:
  """
    Represent the Milestone 42 packages3 dependency convention.

    This is a read-only proxy for the artifacts used by
    packages system: packages.txt, local-packages.txt, and the implicit
    Milestone 42 development dependencies installed by packages3.sh.
  """
  _implicit_dev_dependencies = ('mypy', 'pylint', 'parameterized')

  @staticmethod
  def _read_dependencies(path: Path) -> tuple[list[str], list[str]]:
    """
      Read production and development dependencies from a file.

      :param path: The dependency file to read
      :return: The production and development dependency lists
      :raises DralithusProjectError: When the file cannot be read or
        decoded. The original exception is preserved as the cause.
    """
    production: list[str] = []
    development: list[str] = []
    try:
      lines = path.read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeDecodeError) as error:
      raise DralithusProjectError(
        f'Could not read dependency file: {path}') from error
    for line in lines:
      dependency = line.split('#', maxsplit=1)[0].strip()
      if dependency.endswith(' [dev]'):
        development.append(dependency.removesuffix(' [dev]').strip())
      elif dependency:
        production.append(dependency)
    return production, development

  def __init__(self, project_root: Path) -> None:
    """
      Initialize the packages3 proxy.

      :param project_root: The root directory of the Python project
      :return: None
      :raises DralithusProjectError: When a dependency file cannot be
        read or decoded
    """
    packages_txt = project_root / 'packages.txt'
    local_packages_txt = project_root / 'local-packages.txt'
    production, production_dev = self._read_dependencies(packages_txt)
    local: list[str] = []
    local_dev: list[str] = []
    if local_packages_txt.exists():
      local, local_dev = self._read_dependencies(local_packages_txt)
    self._production_dependencies = production
    self._dev_dependencies = [
      *self._implicit_dev_dependencies,
      *production_dev,
      *local_dev]
    self._local_dependencies = local

  @property
  def production_dependencies(self) -> list[str]:
    """
      Return the production dependencies from packages.txt.

      :return: The production dependency list
    """
    return list(self._production_dependencies)

  @property
  def dev_dependencies(self) -> list[str]:
    """
      Return the implicit development dependencies.

      :return: The implicit development dependency list
    """
    return list(self._dev_dependencies)

  @property
  def local_dependencies(self) -> list[str]:
    """
      Return the editable local dependencies from local-packages.txt.

      :return: The local dependency list
    """
    return list(self._local_dependencies)

  @classmethod
  def from_project_root(cls, project_root: Path) -> Packages3:
    """
      Create an empty packages configuration in the specified project root.

      This will create an empty packages.txt file as well as
      local-packages.txt.

      :param project_root: The root directory of the Python project
      :return: The packages3 proxy
      :raises DralithusProjectError: When packages.txt is missing, or
        a dependency file cannot be read or decoded
    """
    return cls(project_root)

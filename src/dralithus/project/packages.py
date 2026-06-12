"""
  packages.py: Define the Packages class.
"""
# -------------------------------------------------------------------
# packages.py: Define the Packages class.
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


class Packages:
  """
    Represent the Milestone 42 Packages System dependency convention.

    This models the Packages System artifacts: packages.txt,
    local-packages.txt, and the implicit Milestone 42 development
    dependencies (mypy, pylint, parameterized). The Packages System
    is dralithus's successor to the legacy packages3.sh shell script.
  """
  PACKAGES_FILENAME = 'packages.txt'
  LOCAL_PACKAGES_FILENAME = 'local-packages.txt'

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
      Initialize the Packages model.

      :param project_root: The root directory of the Python project
      :return: None
      :raises DralithusProjectError: When a dependency file cannot be
        read or decoded
    """
    packages_txt = project_root / self.PACKAGES_FILENAME
    local_packages_txt = project_root / self.LOCAL_PACKAGES_FILENAME
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
  def create(cls, project_root: Path) -> Packages:
    """
      Create a new packages configuration in the project root.

      Writes a fresh packages.txt and local-packages.txt, each seeded
      with a header comment, then returns a Packages over them. Use
      the constructor instead to read an already-initialized project.

      :param project_root: The root directory of the Python project
      :return: The newly created Packages model
      :raises DralithusProjectError: When the project is already
        initialized, or a dependency file cannot be written
    """
    packages_header = (
      '# Third-party packages, one per line.\n'
      '# Append " [dev]" to mark a development-only dependency.\n')
    local_packages_header = (
      '# Local editable packages, one path per line.\n'
      '# Append " [dev]" to mark a development-only dependency.\n')
    packages_txt = project_root / cls.PACKAGES_FILENAME
    local_packages_txt = project_root / cls.LOCAL_PACKAGES_FILENAME
    if packages_txt.exists():
      raise DralithusProjectError(
        f'Packages already initialized: {packages_txt}')
    try:
      packages_txt.write_text(packages_header, encoding='utf-8')
      local_packages_txt.write_text(
        local_packages_header, encoding='utf-8')
    except OSError as error:
      raise DralithusProjectError(
        f'Could not write dependency file: {project_root}') from error
    return cls(project_root)

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
    is Dralithus's successor to the legacy packages3.sh shell script.
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

  @staticmethod
  def _seed_file(path: Path, content: str) -> bool:
    """
      Write content to path unless the path already exists.

      Creation is exclusive, so a file that appears between any
      earlier existence check and the write is never overwritten,
      and the return value reports true ownership: True only when
      this call created the file.

      :param path: The dependency file to seed
      :param content: The seed content to write
      :return: True if this call created the file, False if the
        path already existed (including as a dangling symlink)
      :raises OSError: When the file cannot be written
    """
    created = False
    try:
      with path.open('x', encoding='utf-8') as file:
        file.write(content)
      created = True
    except FileExistsError:
      pass
    return created

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
  def seed(cls, project_root: Path) -> list[Path]:
    """
      Seed any missing dependency files in the project root.

      Writes whichever of packages.txt and local-packages.txt does
      not already exist, seeded with a header comment, and returns
      exactly the paths this call created. Existing dependency files
      are left untouched. On a write failure the files this call
      created are removed before raising, so seed either returns an
      accurate list or leaves nothing behind.

      :param project_root: The root directory of the Python project
      :return: The dependency file paths this call created
      :raises DralithusProjectError: When a missing dependency file
        cannot be written
    """
    packages_header = (
      '# Third-party packages, one per line.\n'
      '# Append " [dev]" to mark a development-only dependency.\n')
    local_packages_header = (
      '# Local editable packages, one path per line.\n'
      '# Append " [dev]" to mark a development-only dependency.\n')
    targets = (
      (project_root / cls.PACKAGES_FILENAME, packages_header),
      (project_root / cls.LOCAL_PACKAGES_FILENAME,
       local_packages_header))
    created: list[Path] = []
    try:
      for path, content in targets:
        if cls._seed_file(path, content):
          created.append(path)
    except OSError as error:
      for path in created:
        path.unlink(missing_ok=True)
      raise DralithusProjectError(
        f'Could not write dependency file: {project_root}') from error
    return created

  @classmethod
  def create(cls, project_root: Path) -> Packages:
    """
      Create any missing packages configuration in the project root.

      Seeds whichever of packages.txt and local-packages.txt does
      not already exist, then returns a Packages over the resulting
      files. Existing dependency files are left untouched.

      :param project_root: The root directory of the Python project
      :return: The Packages model over the dependency files
      :raises DralithusProjectError: When a missing dependency file
        cannot be written, or an existing one cannot be read
    """
    cls.seed(project_root)
    return cls(project_root)

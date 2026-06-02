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
from pathlib import Path


class Packages3:
  """
    Represent the Milestone 42 packages3 dependency convention.

    This is a read-only proxy for the artifacts used by
    packages3.sh: packages.txt, local-packages.txt, and the implicit
    Milestone 42 development dependencies installed by packages3.sh.
  """
  _implicit_dev_dependencies = ('mypy', 'pylint', 'parameterized')

  def __init__(self, project_root: Path) -> None:
    """
      Initialize the packages3 proxy.

      :param project_root: The root directory of the Python project
      :return: None
    """
    raise NotImplementedError

  @classmethod
  def from_project_root(cls, project_root: Path) -> 'Packages3':
    """
      Create a packages3 proxy for a Python project root.

      :param project_root: The root directory of the Python project
      :return: The packages3 proxy
    """
    raise NotImplementedError

  @property
  def production_dependencies(self) -> list[str]:
    """
      Return the production dependencies from packages.txt.

      :return: The production dependency list
    """
    raise NotImplementedError

  @property
  def dev_dependencies(self) -> list[str]:
    """
      Return the implicit development dependencies.

      :return: The implicit development dependency list
    """
    raise NotImplementedError

  @property
  def local_dependencies(self) -> list[str]:
    """
      Return the editable local dependencies from local-packages.txt.

      :return: The local dependency list
    """
    raise NotImplementedError

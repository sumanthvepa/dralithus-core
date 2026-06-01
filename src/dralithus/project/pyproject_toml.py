"""
  pyproject_toml.py: Define the PyProjectToml class.
"""
# -------------------------------------------------------------------
# pyproject_toml.py: Define the PyProjectToml class.
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

from dralithus.project.packages import Packages


class PyProjectToml:
  """
    Represent a Milestone 42 pyproject.toml.

    Holds the variable fields of a pyproject.toml written for a
    Milestone 42 Python project. The non-variable fields
    (build-system block, readme, packages.find.where, namespaces)
    are baked-in invariants of the spec and live here as class
    constants.
  """
  _BUILD_REQUIRES = ['setuptools>=69', 'wheel']
  _BUILD_BACKEND = 'setuptools.build_meta'
  _README = 'README.md'
  _PACKAGES_WHERE = ['src']
  _NAMESPACES = True

  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def __init__(
    self,
    name: str,
    description: str,
    package_name: str,
    python_requirement: str,
    packages: Packages,
    version: str = '0.1.0'
  ) -> None:
    """
      Initialize the pyproject.toml.

      :param name: The project distribution name
      :param description: The project description
      :param package_name: The Python package name
      :param python_requirement: The Python version requirement
        (e.g. '>=3.13')
      :param packages: The project's dependency lists
      :param version: The project version
      :return: None
    """
    raise NotImplementedError()

  @property
  def name(self) -> str:
    """
      Return the project distribution name.

      :return: The project distribution name
    """
    raise NotImplementedError()

  @property
  def description(self) -> str:
    """
      Return the project description.

      :return: The project description
    """
    raise NotImplementedError()

  @property
  def package_name(self) -> str:
    """
      Return the Python package name.

      :return: The Python package name
    """
    raise NotImplementedError()

  @property
  def python_requirement(self) -> str:
    """
      Return the Python version requirement.

      :return: The Python version requirement
    """
    raise NotImplementedError()

  @property
  def packages(self) -> Packages:
    """
      Return the project's dependency lists.

      :return: The project's dependency lists
    """
    raise NotImplementedError()

  @property
  def version(self) -> str:
    """
      Return the project version.

      :return: The project version
    """
    raise NotImplementedError()

  def to_toml(self) -> str:
    """
      Render the pyproject.toml as text.

      :return: The pyproject.toml text
    """
    raise NotImplementedError()

  @classmethod
  def from_file(cls, path: Path) -> 'PyProjectToml':
    """
      Load a pyproject.toml from disk.

      Reads the file at the given path, parses it, and validates
      that it conforms to the Milestone 42 schema (build-system
      block, readme, packages.find.where, namespaces, and the
      M42 dev dependency baseline). Variable fields are extracted
      from the file and stored on the returned instance.

      :param path: The path to the pyproject.toml file
      :return: A PyProjectToml instance matching the file
      :raises DralithusProjectError: When the file cannot be read,
        contains invalid TOML, or does not conform to the
        Milestone 42 schema
    """
    raise NotImplementedError()

  def matches(self, expected: 'PyProjectToml') -> None:
    """
      Verify that this pyproject.toml matches expected.

      All variable fields are checked for strict equality, except
      for dev_dependencies which uses subset semantics: every dev
      dependency in expected must be present here, but extras
      are allowed.

      :param expected: The expected pyproject.toml
      :return: None
      :raises DralithusProjectError: When this pyproject.toml
        does not match expected
    """
    raise NotImplementedError()

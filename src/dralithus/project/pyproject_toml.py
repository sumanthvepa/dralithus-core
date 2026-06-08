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
import tomllib
from typing import Any

from dralithus.project.error import DralithusProjectError
from dralithus.project.packages3 import Packages3


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
    packages: Packages3,
    version: str = '0.1.0'
  ) -> None:
    """
      Initialize the pyproject.toml.

      :param name: The project distribution name
      :param description: The project description
      :param package_name: The Python package name
      :param python_requirement: The Python version requirement
        (e.g. '>=3.13')
      :param packages: The project's packages3 dependency model
      :param version: The project version
      :return: None
    """
    self._name = name
    self._description = description
    self._package_name = package_name
    self._python_requirement = python_requirement
    self._packages = packages
    self._version = version

  @property
  def name(self) -> str:
    """
      Return the project distribution name.

      :return: The project distribution name
    """
    return self._name

  @property
  def description(self) -> str:
    """
      Return the project description.

      :return: The project description
    """
    return self._description

  @property
  def package_name(self) -> str:
    """
      Return the Python package name.

      :return: The Python package name
    """
    return self._package_name

  @property
  def python_requirement(self) -> str:
    """
      Return the Python version requirement.

      :return: The Python version requirement
    """
    return self._python_requirement

  @property
  def packages(self) -> Packages3:
    """
      Return the project's packages3 dependency model.

      :return: The project's packages3 dependency model
    """
    return self._packages

  @property
  def version(self) -> str:
    """
      Return the project version.

      :return: The project version
    """
    return self._version

  @staticmethod
  def _toml_string(value: str) -> str:
    """
      Format a string as a basic TOML string.

      :param value: The string value to format
      :return: TOML string text
    """
    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'

  @classmethod
  def _toml_list(cls, values: list[str]) -> str:
    """
      Format a list of strings as a TOML array.

      :param values: The strings to format
      :return: TOML array text
    """
    quoted = [cls._toml_string(value) for value in values]
    return f'[{", ".join(quoted)}]'

  @staticmethod
  def _toml_bool(value: bool) -> str:
    """
      Format a boolean as TOML.

      :param value: The boolean value
      :return: TOML boolean text
    """
    return 'true' if value else 'false'

  def to_toml(self) -> str:
    """
      Render the pyproject.toml as text.

      :return: The pyproject.toml text
    """
    return (
      '[build-system]\n'
      f'requires = {self._toml_list(self._BUILD_REQUIRES)}\n'
      f'build-backend = {self._toml_string(self._BUILD_BACKEND)}\n'
      '\n'
      '[project]\n'
      f'name = {self._toml_string(self._name)}\n'
      f'version = {self._toml_string(self._version)}\n'
      f'description = {self._toml_string(self._description)}\n'
      f'readme = {self._toml_string(self._README)}\n'
      f'requires-python = {self._toml_string(self._python_requirement)}\n'
      'dependencies = '
      f'{self._toml_list(self._packages.production_dependencies)}\n'
      '\n'
      '[project.optional-dependencies]\n'
      f'dev = {self._toml_list(self._packages.dev_dependencies)}\n'
      '\n'
      '[tool.setuptools.packages.find]\n'
      f'where = {self._toml_list(self._PACKAGES_WHERE)}\n'
      f'include = {self._toml_list([f"{self._package_name}*"])}\n'
      f'namespaces = {self._toml_bool(self._NAMESPACES)}\n')

  @staticmethod
  def _read_file(path: Path) -> dict[str, Any]:
    """
      Read and parse a pyproject.toml file.

      :param path: The path to the pyproject.toml file
      :return: The parsed pyproject.toml data
      :raises DralithusProjectError: When pyproject.toml is not a
        file, contains invalid TOML, or cannot be read
    """
    try:
      with path.open('rb') as pyproject:
        data: dict[str, Any] = tomllib.load(pyproject)
    except IsADirectoryError as error:
      raise DralithusProjectError(
        f'pyproject.toml is not a file: {path}') from error
    except tomllib.TOMLDecodeError as error:
      raise DralithusProjectError(
        f'Invalid TOML: {path}') from error
    except OSError as error:
      raise DralithusProjectError(
        f'Could not read pyproject.toml: {path}') from error
    return data

  @staticmethod
  def _required(data: dict[str, Any], path: list[str]) -> Any:
    """
      Return a required nested TOML value.

      :param data: The parsed TOML data
      :param path: The path to the required value
      :return: The required value
      :raises DralithusProjectError: When the value is missing
    """
    value: Any = data
    for name in path:
      if not isinstance(value, dict) or name not in value:
        raise DralithusProjectError(
          f'Missing pyproject field: {".".join(path)}')
      value = value[name]
    return value

  @staticmethod
  def _require_equal(actual: Any, expected: Any, field: str) -> None:
    """
      Validate that a pyproject field has the expected value.

      :param actual: The actual value
      :param expected: The expected value
      :param field: The field name
      :return: None
      :raises DralithusProjectError: When values differ
    """
    if actual != expected:
      raise DralithusProjectError(
        f'Invalid pyproject field: {field}')

  @classmethod
  def _require_field(
    cls,
    data: dict[str, Any],
    path: list[str],
    expected: Any
  ) -> None:
    """
      Validate that a pyproject field exists and has the expected
      value.

      :param data: The parsed TOML data
      :param path: The path to the required field
      :param expected: The expected value
      :return: None
      :raises DralithusProjectError: When the field is missing or
        its value differs from expected
    """
    cls._require_equal(
      cls._required(data, path), expected, '.'.join(path))

  @classmethod
  def _validate_structural_invariants(
    cls,
    data: dict[str, Any]
  ) -> None:
    """
      Validate that the Milestone 42 invariants are present.

      :param data: The parsed pyproject.toml data
      :return: None
      :raises DralithusProjectError: When an invariant is violated
    """
    checks: list[tuple[list[str], Any]] = [
      (['build-system', 'requires'], cls._BUILD_REQUIRES),
      (['build-system', 'build-backend'], cls._BUILD_BACKEND),
      (['project', 'readme'], cls._README),
      (['tool', 'setuptools', 'packages', 'find', 'where'],
       cls._PACKAGES_WHERE),
      (['tool', 'setuptools', 'packages', 'find', 'namespaces'],
       cls._NAMESPACES),
    ]
    for field_path, expected in checks:
      cls._require_field(data, field_path, expected)

  @staticmethod
  def _validate_dev_dependencies(
    actual: list[str],
    expected: list[str]
  ) -> None:
    """
      Validate that the required dev dependencies are present.

      :param actual: The dev dependencies from pyproject.toml
      :param expected: The required dev dependencies
      :return: None
      :raises DralithusProjectError: When a dev dependency is missing
    """
    for dependency in expected:
      if dependency not in actual:
        raise DralithusProjectError(
          f'Missing pyproject dev dependency: {dependency}')

  @classmethod
  def _extract_package_name(cls, data: dict[str, Any]) -> str:
    """
      Extract the package name from the include pattern.

      :param data: The parsed pyproject.toml data
      :return: The package name (without trailing wildcard)
      :raises DralithusProjectError: When the include pattern is
        malformed
    """
    include = cls._required(
      data, ['tool', 'setuptools', 'packages', 'find', 'include'])
    valid = (
      isinstance(include, list)
      and len(include) == 1
      and isinstance(include[0], str)
      and include[0].endswith('*'))
    if not valid:
      raise DralithusProjectError(
        'Invalid pyproject field: '
        'tool.setuptools.packages.find.include')
    pattern: str = include[0]
    return pattern[:-1]

  @classmethod
  def from_file(cls, path: Path, packages: Packages3) -> 'PyProjectToml':
    """
      Load a pyproject.toml from disk.

      Reads the file at the given path, parses it, and validates
      that it conforms to the Milestone 42 schema (build-system
      block, readme, packages.find.where, namespaces, and dependency
      fields). Variable fields are extracted from the file and stored
      on the returned instance. Dependency fields are validated
      against packages3 artifacts and are not treated as a source of
      truth.

      :param path: The path to the pyproject.toml file
      :param packages: The authoritative packages3 dependency model
      :return: A PyProjectToml instance matching the file
      :raises DralithusProjectError: When the file cannot be read,
        contains invalid TOML, or does not conform to the
        Milestone 42 schema
    """
    data = cls._read_file(path)
    cls._validate_structural_invariants(data)
    name = cls._required(data, ['project', 'name'])
    description = cls._required(data, ['project', 'description'])
    version = cls._required(data, ['project', 'version'])
    python_requirement = cls._required(
      data, ['project', 'requires-python'])
    dependencies = cls._required(data, ['project', 'dependencies'])
    dev_dependencies = cls._required(
      data, ['project', 'optional-dependencies', 'dev'])
    cls._require_equal(
      dependencies,
      packages.production_dependencies,
      'project.dependencies')
    cls._validate_dev_dependencies(
      dev_dependencies,
      packages.dev_dependencies)
    package_name = cls._extract_package_name(data)
    return cls(
      name=name,
      description=description,
      package_name=package_name,
      python_requirement=python_requirement,
      packages=packages,
      version=version)

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
    pairs: list[tuple[str, Any, Any]] = [
      ('name', self.name, expected.name),
      ('version', self.version, expected.version),
      ('description', self.description, expected.description),
      ('package_name', self.package_name, expected.package_name),
      ('python_requirement',
       self.python_requirement, expected.python_requirement),
      ('dependencies',
       self.packages.production_dependencies,
       expected.packages.production_dependencies),
    ]
    for field, actual, expect in pairs:
      if actual != expect:
        raise DralithusProjectError(
          f'Mismatched pyproject field: {field}')
    for dependency in expected.packages.dev_dependencies:
      if dependency not in self.packages.dev_dependencies:
        raise DralithusProjectError(
          f'Missing pyproject dev dependency: {dependency}')

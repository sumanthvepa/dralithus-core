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
from pathlib import Path
import tomllib
from typing import Any

from typing_extensions import override

from dralithus.project.context import ProjectContext
from dralithus.project.execution_step import ExecutionStep
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages


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
    self._project_name = project_name
    self._project_description = project_description
    self._package_name = package_name
    self._project_version = project_version
    self._created_pyproject = False

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
  def _read_key_value_file(path: Path) -> dict[str, str]:
    """
      Read a key-value file that uses '=' separators.

      :param path: The path to read
      :return: The parsed key-value data
    """
    values: dict[str, str] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
      name, separator, value = line.partition('=')
      if separator == '=':
        values[name.strip()] = value.strip()
    return values

  @classmethod
  def _python_requirement(cls, context: ProjectContext) -> str:
    """
      Return the Python requirement for the project venv.

      :param context: The project creation context
      :return: The Python major/minor version requirement
      :raises DralithusProjectError: When the venv metadata is missing
    """
    pyvenv_cfg = context.venv_path / 'pyvenv.cfg'
    if not context.venv_path.is_dir():
      raise DralithusProjectError(
        f'Venv does not exist: {context.venv_path}')
    if not pyvenv_cfg.is_file():
      raise DralithusProjectError(
        f'Venv metadata does not exist: {pyvenv_cfg}')
    version = cls._read_key_value_file(pyvenv_cfg).get('version')
    if version is None:
      raise DralithusProjectError(
        f'Venv metadata has no version: {pyvenv_cfg}')
    parts = version.split('.')
    if len(parts) < 2:
      raise DralithusProjectError(f'Invalid venv Python version: {version}')
    return f'>={parts[0]}.{parts[1]}'

  @staticmethod
  def _packages(project_root: Path) -> Packages:
    """
      Return the project's dependency and dev dependency lists.

      Reads runtime dependencies from packages.txt. The dev
      dependencies are those that packages3.sh always installs.

      :param project_root: The project root directory
      :return: The project's dependencies and dev dependencies
    """
    dependencies: list[str] = []
    packages_txt = project_root / 'packages.txt'
    if packages_txt.exists():
      for line in packages_txt.read_text(encoding='utf-8').splitlines():
        package = line.split('#', maxsplit=1)[0].strip()
        if package != '':
          dependencies.append(package)
    dev_dependencies = ['mypy', 'pylint', 'parameterized']
    return Packages(dependencies, dev_dependencies)

  def _pyproject_text(
    self,
    context: ProjectContext,
    python_requirement: str
  ) -> str:
    """
      Return the pyproject.toml text for this project.

      :param context: The project creation context
      :param python_requirement: The Python version requirement
      :return: pyproject.toml text
    """
    packages = self._packages(context.project_root)
    return (
      '[build-system]\n'
      'requires = ["setuptools>=69", "wheel"]\n'
      'build-backend = "setuptools.build_meta"\n'
      '\n'
      '[project]\n'
      f'name = {self._toml_string(self._project_name)}\n'
      f'version = {self._toml_string(self._project_version)}\n'
      f'description = {self._toml_string(self._project_description)}\n'
      'readme = "README.md"\n'
      f'requires-python = {self._toml_string(python_requirement)}\n'
      f'dependencies = {self._toml_list(packages.dependencies)}\n'
      '\n'
      '[project.optional-dependencies]\n'
      f'dev = {self._toml_list(packages.dev_dependencies)}\n'
      '\n'
      '[tool.setuptools.packages.find]\n'
      'where = ["src"]\n'
      f'include = {self._toml_list([f"{self._package_name}*"])}\n'
      'namespaces = true\n')

  @staticmethod
  def _read_pyproject(path: Path) -> dict[str, Any]:
    """
      Read pyproject.toml.

      :param path: The path to pyproject.toml
      :return: The parsed pyproject.toml data
      :raises DralithusProjectError: When pyproject.toml is not a file,
        contains invalid TOML, or cannot be read
    """
    try:
      with path.open('rb') as pyproject:
        data: dict[str, Any] = tomllib.load(pyproject)
    except IsADirectoryError as error:
      raise DralithusProjectError(
        f'pyproject.toml is not a file: {path}') from error
    except tomllib.TOMLDecodeError as error:
      raise DralithusProjectError(f'Invalid TOML: {path}') from error
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
        raise DralithusProjectError(f'Missing pyproject field: {".".join(path)}')
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
      raise DralithusProjectError(f'Invalid pyproject field: {field}')

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
    cls._require_equal(cls._required(data, path), expected, '.'.join(path))

  def _validate_metadata(
    self,
    data: dict[str, Any],
    python_requirement: str
  ) -> None:
    """
      Validate the non-dependency fields of pyproject.toml.

      :param data: The parsed pyproject.toml data
      :param python_requirement: The Python version requirement
      :return: None
      :raises DralithusProjectError: When a metadata field is
        missing or has the wrong value
    """
    checks: list[tuple[list[str], Any]] = [
      (['build-system', 'requires'], ['setuptools>=69', 'wheel']),
      (['build-system', 'build-backend'], 'setuptools.build_meta'),
      (['project', 'name'], self._project_name),
      (['project', 'version'], self._project_version),
      (['project', 'description'], self._project_description),
      (['project', 'readme'], 'README.md'),
      (['project', 'requires-python'], python_requirement),
      (['tool', 'setuptools', 'packages', 'find', 'where'], ['src']),
      (['tool', 'setuptools', 'packages', 'find', 'include'],
       [f'{self._package_name}*']),
    ]
    for field_path, expected in checks:
      self._require_field(data, field_path, expected)

  def _validate_dependencies(
    self,
    data: dict[str, Any],
    packages: Packages
  ) -> None:
    """
      Validate the dependency fields of pyproject.toml.

      :param data: The parsed pyproject.toml data
      :param packages: The expected dependency lists
      :return: None
      :raises DralithusProjectError: When a dependency field is
        missing or has the wrong value
    """
    self._require_field(
      data, ['project', 'dependencies'], packages.dependencies)
    expected_dev_dependencies = packages.dev_dependencies
    actual_dev_dependencies = self._required(
      data, ['project', 'optional-dependencies', 'dev'])
    for dependency in expected_dev_dependencies:
      if dependency not in actual_dev_dependencies:
        raise DralithusProjectError(
          f'Missing pyproject dev dependency: {dependency}')

  def _validate_pyproject(
    self,
    context: ProjectContext,
    path: Path,
    python_requirement: str
  ) -> None:
    """
      Validate an existing pyproject.toml.

      :param context: The project creation context
      :param path: The pyproject.toml path
      :param python_requirement: The Python version requirement
      :return: None
      :raises DralithusProjectError: When pyproject.toml is invalid
    """
    data = self._read_pyproject(path)
    packages = self._packages(context.project_root)
    self._validate_metadata(data, python_requirement)
    self._validate_dependencies(data, packages)

  def _create_pyproject(
    self,
    context: ProjectContext,
    path: Path,
    python_requirement: str
  ) -> None:
    """
      Create pyproject.toml.

      :param context: The project creation context
      :param path: The pyproject.toml path
      :param python_requirement: The Python version requirement
      :return: None
      :raises DralithusProjectError: When the file cannot be written
    """
    try:
      path.write_text(
        self._pyproject_text(context, python_requirement),
        encoding='utf-8')
    except OSError as error:
      raise DralithusProjectError(
        f'Could not create pyproject.toml: {path}') from error

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the pyproject.toml creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
    """
    python_requirement = self._python_requirement(context)
    path = context.project_root / 'pyproject.toml'
    if path.exists():
      self._validate_pyproject(context, path, python_requirement)
    elif not dry_run:
      self._create_pyproject(context, path, python_requirement)
      self._created_pyproject = True

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the pyproject.toml creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
    """
    if self._created_pyproject and not dry_run:
      path = context.project_root / 'pyproject.toml'
      try:
        path.unlink()
      except OSError as error:
        raise DralithusProjectError(
          f'Could not remove pyproject.toml: {path}') from error
      self._created_pyproject = False

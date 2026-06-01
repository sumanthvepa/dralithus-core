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

from typing_extensions import override

from dralithus.project.context import ProjectContext
from dralithus.project.execution_step import ExecutionStep
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages
from dralithus.project.pyproject_toml import PyProjectToml


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

  def _expected_pyproject(
    self,
    context: ProjectContext
  ) -> PyProjectToml:
    """
      Build the expected pyproject.toml for this project.

      :param context: The project creation context
      :return: The expected pyproject.toml
      :raises DralithusProjectError: When the venv metadata is
        missing
    """
    return PyProjectToml(
      name=self._project_name,
      description=self._project_description,
      package_name=self._package_name,
      python_requirement=self._python_requirement(context),
      packages=self._packages(context.project_root),
      version=self._project_version)

  def _create_pyproject(
    self,
    expected: PyProjectToml,
    path: Path
  ) -> None:
    """
      Write the expected pyproject.toml to disk.

      :param expected: The expected pyproject.toml
      :param path: The pyproject.toml path
      :return: None
      :raises DralithusProjectError: When the file cannot be written
    """
    try:
      path.write_text(expected.to_toml(), encoding='utf-8')
    except OSError as error:
      raise DralithusProjectError(
        f'Could not create pyproject.toml: {path}') from error
    self._created_pyproject = True

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the pyproject.toml creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
    """
    expected = self._expected_pyproject(context)
    path = context.project_root / 'pyproject.toml'
    if path.exists():
      actual = PyProjectToml.from_file(path)
      actual.matches(expected)
    elif not dry_run:
      self._create_pyproject(expected, path)

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

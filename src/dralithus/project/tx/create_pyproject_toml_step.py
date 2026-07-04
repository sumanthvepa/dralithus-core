"""
  create_pyproject_toml_step.py: Define the CreatePyProjectTomlStep
  class.
"""
# -------------------------------------------------------------------
# create_pyproject_toml_step.py: Define the CreatePyProjectTomlStep
# class.
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
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages
from dralithus.project.pyproject_toml import PyProjectToml
from dralithus.project.tx.execution_step import ExecutionStep
from dralithus.project.tx.project_state import ProjectState


class CreatePyProjectTomlStep(ExecutionStep):
  """
    Represent a project creation step that creates pyproject.toml.

    prepare() derives the Python requirement from the venv's
    current-or-projected Python version, so a dry run validates
    pyproject.toml even before the venv exists. The dependency model
    is read from a real packages.txt, or taken as empty when the
    file is only claimed, matching the header-only files that
    CreatePackagesStep creates at commit time.
  """
  def _remove_created(self, path: Path) -> None:
    """
      Remove the pyproject.toml owned by this step.

      Files already removed externally are accepted silently.

      :param path: The pyproject.toml path
      :return: None
      :raises DralithusProjectError: When the file cannot be removed
    """
    try:
      path.unlink(missing_ok=True)
    except OSError as error:
      raise DralithusProjectError(
        f'Could not remove pyproject.toml: {path}') from error
    self._created_pyproject = False

  def _create_pyproject(
    self,
    expected: PyProjectToml,
    path: Path
  ) -> None:
    """
      Write the expected pyproject.toml by exclusive creation.

      Ownership is recorded the instant exclusive creation succeeds,
      before the content write. A file that appeared since the
      existence check is re-verified rather than overwritten.

      :param expected: The expected pyproject.toml
      :param path: The pyproject.toml path
      :return: None
      :raises DralithusProjectError: When the file cannot be created
        or written, or an appeared file does not match
    """
    try:
      # The with statement starts only after ownership is recorded.
      # pylint: disable-next=consider-using-with
      file = path.open('x', encoding='utf-8')
    except FileExistsError:
      self._verify_existing(path, expected)
    except OSError as error:
      raise DralithusProjectError(
        f'Could not create pyproject.toml: {path}') from error
    else:
      self._created_pyproject = True
      try:
        with file:
          file.write(expected.to_toml())
      except OSError as error:
        self._remove_created(path)
        raise DralithusProjectError(
          f'Could not write pyproject.toml: {path}') from error

  def _projected_python_requirement(self, state: ProjectState) -> str:
    """
      Return the Python requirement from the projected venv.

      :param state: The projected project state to read
      :return: The Python major/minor version requirement
      :raises DralithusProjectError: When no venv is current or
        claimed, or its version is invalid
    """
    version = state.venv_python_version(self._context.venv_path)
    if version is None:
      raise DralithusProjectError(
        f'Venv does not exist: {self._context.venv_path}')
    return self._requirement_from_version(version)

  def _python_requirement(self) -> str:
    """
      Return the Python requirement for the project venv.

      :return: The Python major/minor version requirement
      :raises DralithusProjectError: When the venv metadata is
        missing
    """
    pyvenv_cfg = self._context.venv_path / 'pyvenv.cfg'
    if not self._context.venv_path.is_dir():
      raise DralithusProjectError(
        f'Venv does not exist: {self._context.venv_path}')
    if not pyvenv_cfg.is_file():
      raise DralithusProjectError(
        f'Venv metadata does not exist: {pyvenv_cfg}')
    version = self._read_key_value_file(pyvenv_cfg).get('version')
    if version is None:
      raise DralithusProjectError(
        f'Venv metadata has no version: {pyvenv_cfg}')
    return self._requirement_from_version(version)

  def _projected_packages(self, state: ProjectState) -> Packages:
    """
      Return the current-or-projected dependency model.

      A real packages.txt is read. A packages.txt that is only
      claimed yields an empty model, matching the header-only files
      that CreatePackagesStep creates at commit time.

      :param state: The projected project state to read
      :return: The current-or-projected Packages dependency model
      :raises DralithusProjectError: When packages.txt is neither
        real nor claimed, or cannot be read
    """
    project_root = self._context.project_root
    packages_txt = project_root / Packages.PACKAGES_FILENAME
    if os.path.lexists(packages_txt):
      packages = Packages(project_root)
    elif state.is_file(packages_txt):
      packages = self._empty_packages()
    else:
      raise DralithusProjectError(
        f'Dependency file does not exist: {packages_txt}')
    return packages

  def _expected_pyproject(
    self,
    python_requirement: str,
    packages: Packages
  ) -> PyProjectToml:
    """
      Build the expected pyproject.toml for this project.

      :param python_requirement: The requires-python value
      :param packages: The dependency model for the project
      :return: The expected pyproject.toml
    """
    return PyProjectToml(
      name=self._project_name,
      description=self._project_description,
      package_name=self._package_name,
      python_requirement=python_requirement,
      packages=packages,
      version=self._project_version)

  @staticmethod
  def _verify_existing(path: Path, expected: PyProjectToml) -> bool:
    """
      Verify an existing pyproject.toml against the expected one.

      :param path: The pyproject.toml path
      :param expected: The expected pyproject.toml
      :return: True if an acceptable pyproject.toml exists at path,
        False when path is absent
      :raises DralithusProjectError: When an existing pyproject.toml
        cannot be read or does not match the expected content
    """
    exists = os.path.lexists(path)
    if exists:
      actual = PyProjectToml.from_file(path, expected.packages)
      actual.matches(expected)
    return exists

  @staticmethod
  def _requirement_from_version(version: str) -> str:
    """
      Convert a Python version string to a requires-python value.

      :param version: The Python version string
      :return: The Python major/minor version requirement
      :raises DralithusProjectError: When the version is not at
        least major.minor
    """
    parts = version.split('.')
    if len(parts) < 2:
      raise DralithusProjectError(
        f'Invalid venv Python version: {version}')
    return f'>={parts[0]}.{parts[1]}'

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

  @staticmethod
  def _empty_packages() -> Packages:
    """
      Build an empty dependency model.

      Matches the model produced by the header-only dependency
      files that CreatePackagesStep creates at commit time.

      :return: An empty Packages dependency model
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      (project_root / Packages.PACKAGES_FILENAME).write_text(
        '', encoding='utf-8')
      return Packages(project_root)

  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def __init__(
    self,
    context: ProjectContext,
    project_name: str,
    project_description: str,
    project_version: str = '0.1.0'
  ) -> None:
    """
      Initialize the pyproject.toml creation step.

      :param context: The shared project creation context
      :param project_name: The project distribution name
      :param project_description: The project description
      :param project_version: The project version
      :return: None
    """
    super().__init__(context)
    self._project_name = project_name
    self._project_description = project_description
    self._package_name = context.package_name
    self._project_version = project_version
    self._created_pyproject = False

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Validate pyproject.toml against the projected state and claim
      it.

      Reads the Python requirement from the venv's current or
      claimed Python version and the dependency model from a real
      packages.txt (empty when the file is only claimed), computes
      the expected pyproject.toml, and requires an existing
      pyproject.toml to match it. Claims pyproject.toml as a
      current-or-projected file.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When no venv is current or
        claimed, packages.txt is neither real nor claimed, or an
        existing pyproject.toml does not match the expected content
    """
    expected = self._expected_pyproject(
      self._projected_python_requirement(state),
      self._projected_packages(state))
    path = self._context.project_root / 'pyproject.toml'
    self._verify_existing(path, expected)
    state.claim_file(path)

  @override
  def commit(self) -> None:
    """
      Create pyproject.toml unless an acceptable one exists.

      Recomputes the expected content from the post-commit reality
      of the venv metadata and dependency files. An existing
      pyproject.toml must match the expected content and is left in
      place, unowned. An absent pyproject.toml is created by
      exclusive creation, with ownership recorded the instant
      creation succeeds, before the content write.

      :return: None
      :raises DralithusProjectError: When the file cannot be created
        or an existing file does not match the expected content
    """
    expected = self._expected_pyproject(
      self._python_requirement(),
      Packages(self._context.project_root))
    path = self._context.project_root / 'pyproject.toml'
    if not self._verify_existing(path, expected):
      self._create_pyproject(expected, path)

  @override
  def abort(self) -> None:
    """
      Remove a pyproject.toml this step created.

      A pre-existing pyproject.toml is left in place. Files already
      removed externally are accepted silently. Must be idempotent.

      :return: None
      :raises DralithusProjectError: When the owned pyproject.toml
        cannot be removed
    """
    if self._created_pyproject:
      self._remove_created(
        self._context.project_root / 'pyproject.toml')

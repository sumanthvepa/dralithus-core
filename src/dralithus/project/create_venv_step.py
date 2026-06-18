"""
  create_venv_step.py: Define the CreateVenvStep class.
"""
# -------------------------------------------------------------------
# create_venv_step.py: Define the CreateVenvStep class.
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
import shutil
import subprocess

from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.execution_step import ExecutionStep
from dralithus.project.error import DralithusProjectError


class CreateVenvStep(ExecutionStep):
  """
    Represent a project creation step that creates a Python venv.
  """
  def __init__(self, python_executable: Path, venv_name: str = 'venv') -> None:
    """
      Initialize the Python venv creation step.

      :param python_executable: The path to the Python executable
      :param venv_name: The name of the venv directory to create
      :return: None
      :raises DralithusProjectError: When venv_name is not a name
    """
    self._validate_venv(venv_name)
    self._python_version = self._validate_python(python_executable)
    self._python_executable = python_executable
    self._venv_name = venv_name
    self._created_venv = False

  @staticmethod
  def _validate_venv(venv_name: str) -> None:
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
  def _validate_python_version(python_executable: Path) -> str:
    """
      Validate that python_executable is a single Python executable,
      and return the version string reported by the executable.

      :param python_executable: The path to validate
      :return: The Python version reported by the executable
      :raises DralithusProjectError: When python_executable is not a
        runnable Python executable
    """
    try:
      result = subprocess.run(
        [str(python_executable), '--version'],
        capture_output=True,
        check=True,
        text=True)
    except OSError as error:
      raise DralithusProjectError(
        f'Could not run Python executable: {python_executable}') from error
    except subprocess.CalledProcessError as error:
      raise DralithusProjectError(
        f'Python executable failed version check: {python_executable}'
      ) from error
    version = result.stdout.strip() or result.stderr.strip()
    if not version.startswith('Python '):
      raise DralithusProjectError(
        f'Executable is not Python: {python_executable}')
    return version

  @staticmethod
  def _validate_python(python_executable: Path) -> str:
    """
      Validate that python_executable is a runnable Python executable.

      :param python_executable: The path to validate
      :return: The Python version reported by the executable
      :raises DralithusProjectError: When python_executable is not a
        runnable Python executable
    """
    if not python_executable.exists():
      raise DralithusProjectError(
        f'Python executable does not exist: {python_executable}')
    if not python_executable.is_file():
      raise DralithusProjectError(
        f'Python executable is not a file: {python_executable}')
    if not os.access(python_executable, os.X_OK):
      raise DralithusProjectError(
        f'Python executable is not executable: {python_executable}')
    return CreateVenvStep._validate_python_version(python_executable)

  @staticmethod
  def _is_venv(path: Path) -> bool:
    """
      Check if path looks like a Python virtual environment.

      :param path: The path to check
      :return: True if path contains Python venv metadata
    """
    return (path / 'pyvenv.cfg').is_file()

  def _venv_exists(self, project_root: Path) -> bool:
    """
      Check that a specified venv exists.

      :param project_root: The project root directory
      :return: True if path exists and is a venv, False otherwise.
      :raises DralithusProjectError: When path exists but is not a venv
    """
    venv_dir = project_root / self._venv_name
    if not venv_dir.exists():
      return False
    if not venv_dir.is_dir():
      raise DralithusProjectError(f'Venv path is not a directory: {venv_dir}')
    if not self._is_venv(venv_dir):
      raise DralithusProjectError(f'Path is not a venv: {venv_dir}')
    return True

  def _create_venv(self, project_root: Path, dry_run: bool) -> bool:
    """
      Create the virtual environment.

      :param project_root: The project root directory
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: True if the venv was created, False otherwise
      :raises DralithusProjectError: When venv creation fails
    """
    try:
      command: list[str] = [
        str(self._python_executable), '-m', 'venv', self._venv_name]
      if not dry_run:
        # print(f'Creating venv: {self._venv_name}: {" ".join(command)}')
        subprocess.run(command, cwd=project_root, check=True)
        return True  # successfully created the venv
    except OSError as error:
      raise DralithusProjectError(
        f'Could not create venv: {self._venv_name}') from error
    except subprocess.CalledProcessError as error:
      raise DralithusProjectError(
        f'Could not create venv: {self._venv_name}') from error
    return False

  def _delete_venv(self, project_root: Path) -> bool:
    """
      Delete the virtual environment.
      :param project_root: The project root directory
      :return: None
    """
    try:
      venv_dir = project_root / self._venv_name
      shutil.rmtree(venv_dir)
      return True
    except OSError as error:
      raise DralithusProjectError(
        f'Could not remove venv: {self._venv_name}') from error

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the Python venv creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When venv creation fails
    """
    if not self._venv_exists(context.project_root):
      self._created_venv = self._create_venv(context.project_root, dry_run)

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the Python venv creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When venv removal fails
    """
    if self._created_venv and not dry_run:
      self._created_venv = self._delete_venv(context.project_root)

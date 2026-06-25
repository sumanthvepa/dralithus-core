"""
  install_dependencies_step.py: Define the InstallDependenciesStep class.
"""
# -------------------------------------------------------------------
# install_dependencies_step.py: Define the InstallDependenciesStep class.
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
import contextlib
import os
from pathlib import Path
import subprocess
import tempfile

from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.execution_step import ExecutionStep
from dralithus.project.packages import Packages


class InstallDependenciesStep(ExecutionStep):
  """
    Install a project's dependency closure into its venv.

    Installs the production, development, and editable local
    dependencies modelled by Packages into the project virtual
    environment, then snapshots the resolved, version-pinned result to
    requirements.txt via pip freeze. This is the dralithus-native
    replacement for the legacy packages3.sh shell script.
  """
  REQUIREMENTS_FILENAME = 'requirements.txt'

  _requirements_created: bool

  def _install_and_snapshot(self) -> None:
    """
      Install the dependency closure and snapshot requirements.txt.

      :return: None
      :raises DralithusProjectError: When a prerequisite is missing or
        installation or snapshotting fails
    """
    project_root = self._context.project_root
    venv_python = self._context.venv_python
    if not venv_python.is_file() or not os.access(venv_python, os.X_OK):
      raise DralithusProjectError(
        f'Virtual environment not found: {venv_python}')
    packages = Packages(project_root)
    try:
      requirements = project_root / self.REQUIREMENTS_FILENAME
      self._verify_regular_file_or_absent(requirements)
      self._install(venv_python, project_root, packages)
      self._write_requirements(venv_python, project_root)
    except DralithusProjectError:
      self.rollback()
      raise

  def _install(
    self,
    venv_python: Path,
    project_root: Path,
    packages: Packages
  ) -> None:
    """
      Install pip, the production and dev dependencies, and the
      editable local dependencies, in that order.

      :param venv_python: The venv Python interpreter
      :param project_root: The project root directory
      :param packages: The dependency model for the project
      :return: None
      :raises DralithusProjectError: When a pip install fails
    """
    python = str(venv_python)
    commands = [
      [python, '-m', 'pip', 'install', '--upgrade', 'pip'],
      [python, '-m', 'pip', 'install',
       *packages.production_dependencies,
       *packages.dev_dependencies]]
    if packages.local_dependencies:
      editable = [python, '-m', 'pip', 'install']
      for dependency in packages.local_dependencies:
        editable.extend(['-e', dependency])
      commands.append(editable)
    for command in commands:
      self._run(command, project_root, 'Could not install dependencies')

  def _write_requirements(
    self,
    venv_python: Path,
    project_root: Path
  ) -> None:
    """
      Snapshot the installed dependencies to requirements.txt.

      The file is written atomically, via a temporary file in the same
      directory followed by os.replace, so a pre-existing file is never
      left truncated or partially written. Ownership is recorded only
      when the file was absent before this step created it.

      :param venv_python: The venv Python interpreter
      :param project_root: The project root directory
      :return: None
      :raises DralithusProjectError: When pip freeze or the write fails
    """
    result = self._run(
      [str(venv_python), '-m', 'pip', 'freeze'],
      project_root,
      'Could not read installed dependencies')
    requirements = project_root / self.REQUIREMENTS_FILENAME
    existed = requirements.exists()
    try:
      descriptor, temporary_name = tempfile.mkstemp(dir=project_root)
      temporary_path = Path(temporary_name)
      try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
          handle.write(result.stdout)
        os.replace(temporary_path, requirements)
      except OSError:
        with contextlib.suppress(OSError):
          temporary_path.unlink(missing_ok=True)
        raise
    except OSError as error:
      raise DralithusProjectError(
        f'Could not write dependency file: {requirements}') from error
    if not existed:
      self._requirements_created = True

  def _remove_requirements(self, project_root: Path) -> None:
    """
      Remove a requirements.txt that this step created.

      :param project_root: The project root directory
      :return: None
      :raises DralithusProjectError: When removal fails
    """
    requirements = project_root / self.REQUIREMENTS_FILENAME
    try:
      requirements.unlink(missing_ok=True)
    except OSError as error:
      raise DralithusProjectError(
        f'Could not remove dependency file: {requirements}') from error

  @staticmethod
  def _verify_regular_file_or_absent(path: Path) -> None:
    """
      Verify that a path is absent or an existing regular file.

      A symlink (valid, dangling, or wrong-type), a directory, or any
      other non-regular entry is rejected: requirements.txt is a
      regenerated artifact, so the step never writes through, replaces,
      or deletes such a thing.

      :param path: The path to verify
      :return: None
      :raises DralithusProjectError: When path is a symlink or an
        existing non-regular file
    """
    if path.is_symlink():
      raise DralithusProjectError(
        f'Requirements path is a symlink: {path}')
    if path.exists() and not path.is_file():
      raise DralithusProjectError(
        f'Requirements path is not a regular file: {path}')

  @staticmethod
  def _run(
    command: list[str],
    project_root: Path,
    error_message: str
  ) -> 'subprocess.CompletedProcess[str]':
    """
      Run a subprocess in the project root, wrapping failures.

      :param command: The command and arguments to run
      :param project_root: The working directory for the command
      :param error_message: The message for a wrapped failure
      :return: The completed process, with text streams
      :raises DralithusProjectError: When the command cannot be run or
        exits non-zero
    """
    try:
      return subprocess.run(
        command,
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True)
    except (OSError, subprocess.CalledProcessError) as error:
      raise DralithusProjectError(error_message) from error

  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the dependency installation step.

      :param context: The shared project creation context
      :return: None
    """
    super().__init__(context)
    self._requirements_created = False

  @override
  def run(self, dry_run: bool = False) -> None:
    """
      Install the dependencies and snapshot requirements.txt.

      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When installation or snapshotting
        fails
    """
    if not dry_run:
      self._install_and_snapshot()

  @override
  def rollback(self, dry_run: bool = False) -> None:
    """
      Roll back the dependency installation step.

      Removes only a requirements.txt this step created. The installed
      packages are not uninstalled here; the venv is owned by
      CreateVenvStep.

      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When removing requirements.txt
        fails
    """
    if not dry_run and self._requirements_created:
      self._remove_requirements(self._context.project_root)
      self._requirements_created = False

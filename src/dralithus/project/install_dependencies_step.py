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
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.execution_step import ExecutionStep


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

  def __init__(self, venv_name: str = 'venv') -> None:
    """
      Initialize the dependency installation step.

      :param venv_name: The name of the project venv directory
      :return: None
      :raises DralithusProjectError: When venv_name is not a single,
        non-traversing path component
    """
    self._venv_name = venv_name
    self._requirements_created = False

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Install the dependencies and snapshot requirements.txt.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When installation or snapshotting
        fails
    """
    raise NotImplementedError('run() is not yet implemented')

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the dependency installation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When removing requirements.txt
        fails
    """
    raise NotImplementedError('rollback() is not yet implemented')

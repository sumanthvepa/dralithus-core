"""
  install_dependencies_step.py: Define the InstallDependenciesStep
  class.
"""
# -------------------------------------------------------------------
# install_dependencies_step.py: Define the InstallDependenciesStep
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
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.tx.execution_step import ExecutionStep
from dralithus.project.tx.project_state import ProjectState


class InstallDependenciesStep(ExecutionStep):
  """
    Install a project's dependency closure into its venv.

    Installs the production, development, and editable local
    dependencies modelled by Packages into the project virtual
    environment, then snapshots the resolved, version-pinned result
    to requirements.txt via pip freeze.

    prepare() validates shallowly by necessity: it can confirm the
    venv Python is current-or-projected and the dependency files
    parse, but whether pip dependency resolution will succeed can
    only be discovered by running pip at commit time.
  """
  REQUIREMENTS_FILENAME = 'requirements.txt'

  # pylint: disable-next=super-init-not-called,unused-argument
  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the dependency installation step.

      :param context: The shared project creation context
      :return: None
    """
    raise NotImplementedError(
      'InstallDependenciesStep.__init__() is not implemented yet')

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Validate the installation prerequisites and claim
      requirements.txt.

      Requires the venv Python to be a current-or-projected
      executable and the dependency model to parse (empty when
      packages.txt is only claimed). The requirements.txt path must
      be absent or an existing regular file; a symlink or other
      non-regular entry is rejected, because requirements.txt is a
      regenerated artifact. Claims requirements.txt as a
      current-or-projected file.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When the venv Python is neither
        current nor claimed, the dependency files cannot be parsed,
        or the requirements.txt path is unusable
    """
    raise NotImplementedError(
      'prepare() is not implemented yet')

  @override
  def commit(self) -> None:
    """
      Install the dependencies and snapshot requirements.txt.

      Installs pip, the production and dev dependencies, and the
      editable local dependencies, then snapshots the result to
      requirements.txt atomically via a temporary file and
      os.replace. Ownership is recorded only when the file was
      absent before this step created it. On failure a
      requirements.txt this step created is removed before raising.

      :return: None
      :raises DralithusProjectError: When installation or
        snapshotting fails
    """
    raise NotImplementedError(
      'commit() is not implemented yet')

  @override
  def abort(self) -> None:
    """
      Remove a requirements.txt this step created.

      The installed packages are not uninstalled here; the venv is
      owned by CreateVenvStep. A pre-existing requirements.txt is
      left in place. Must be idempotent.

      :return: None
      :raises DralithusProjectError: When removing requirements.txt
        fails
    """
    raise NotImplementedError(
      'abort() is not implemented yet')

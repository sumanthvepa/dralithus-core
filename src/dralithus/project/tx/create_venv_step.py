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
from pathlib import Path
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.tx.execution_step import ExecutionStep
from dralithus.project.tx.project_state import ProjectState


class CreateVenvStep(ExecutionStep):
  """
    Represent a project creation step that creates a Python venv.

    The constructor validates the Python executable and probes its
    version, so the claim prepare() declares is derived from the
    same source the real run uses. Commit is irreducibly non-atomic,
    because a venv bakes absolute paths into its metadata; abort is
    the backstop.
  """
  # pylint: disable-next=super-init-not-called,unused-argument
  def __init__(
    self,
    context: ProjectContext,
    python_executable: Path
  ) -> None:
    """
      Initialize the Python venv creation step.

      :param context: The shared project creation context
      :param python_executable: The path to the Python executable
      :return: None
      :raises DralithusProjectError: When python_executable is not a
        runnable Python executable
    """
    raise NotImplementedError(
      'CreateVenvStep.__init__() is not implemented yet')

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Validate the venv path and claim the projected venv.

      An existing venv directory must contain venv metadata and is
      accepted as-is, with no claim declared: the real file system
      already answers queries about it. When the venv is absent,
      claims the venv with the probed Python version and claims the
      venv Python as a projected executable. A non-directory or
      non-venv occupant of the venv path is rejected.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When the venv path is occupied
        by something that is not a venv
    """
    raise NotImplementedError(
      'prepare() is not implemented yet')

  @override
  def commit(self) -> None:
    """
      Create the venv unless an acceptable one already exists.

      Records ownership when this step creates the venv, so abort
      removes only a venv this step created.

      :return: None
      :raises DralithusProjectError: When venv creation fails
    """
    raise NotImplementedError(
      'commit() is not implemented yet')

  @override
  def abort(self) -> None:
    """
      Remove the venv when this step created it.

      A pre-existing venv is left in place. Must be idempotent.

      :return: None
      :raises DralithusProjectError: When venv removal fails
    """
    raise NotImplementedError(
      'abort() is not implemented yet')

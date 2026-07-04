"""
  create_pylint_configuration_step.py: Define the
  CreatePylintConfigurationStep class.
"""
# -------------------------------------------------------------------
# create_pylint_configuration_step.py: Define the
# CreatePylintConfigurationStep class.
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


class CreatePylintConfigurationStep(ExecutionStep):
  """
    Represent a project creation step that creates Pylint
    configuration for a new Python project.

    The packaged pylintrc resource is the canonical default
    generated for new projects. Delegates every phase to an inner
    CreateFileStep built from that resource.
  """
  # pylint: disable-next=super-init-not-called,unused-argument
  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the Pylint configuration creation step.

      :param context: The shared project creation context
      :return: None
      :raises DralithusProjectError: When the packaged pylintrc
        resource cannot be read
    """
    raise NotImplementedError(
      'CreatePylintConfigurationStep.__init__() is not implemented '
      'yet')

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Prepare the inner file creation step.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When the pylintrc target cannot
        be accepted
    """
    raise NotImplementedError(
      'prepare() is not implemented yet')

  @override
  def commit(self) -> None:
    """
      Commit the inner file creation step.

      :return: None
      :raises DralithusProjectError: When pylintrc cannot be created
        or written
    """
    raise NotImplementedError(
      'commit() is not implemented yet')

  @override
  def abort(self) -> None:
    """
      Abort the inner file creation step.

      :return: None
      :raises DralithusProjectError: When an owned pylintrc cannot
        be removed
    """
    raise NotImplementedError(
      'abort() is not implemented yet')

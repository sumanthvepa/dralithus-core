"""
  create_mypy_configuration_step.py: Define the
  CreateMypyConfigurationStep class.
"""
# -------------------------------------------------------------------
# create_mypy_configuration_step.py: Define the
# CreateMypyConfigurationStep class.
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
from dralithus.project.context import ProjectContext
from dralithus.project.tx.composite_execution_step import (
  CompositeExecutionStep)


class CreateMypyConfigurationStep(CompositeExecutionStep):
  """
    Represent a project creation step that creates mypy
    configuration for a new Python project.

    Creates mypy.ini from the packaged resource, the
    stubs/parameterized directory tree with a .gitignore in each
    stub directory, and the parameterized __init__.pyi stub.
    Composes a CreateFileStep for each file and a MkdirStep for the
    stub tree; all phase logic, ownership, and rollback live in the
    children and in CompositeExecutionStep.
  """
  # pylint: disable-next=super-init-not-called,unused-argument
  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the mypy configuration creation step.

      :param context: The shared project creation context
      :return: None
      :raises DralithusProjectError: When a packaged resource cannot
        be read
    """
    raise NotImplementedError(
      'CreateMypyConfigurationStep.__init__() is not implemented '
      'yet')

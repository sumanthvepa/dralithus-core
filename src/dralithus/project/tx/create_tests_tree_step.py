"""
  create_tests_tree_step.py: Define the CreateTestsTreeStep class.
"""
# -------------------------------------------------------------------
# create_tests_tree_step.py: Define the CreateTestsTreeStep class.
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


class CreateTestsTreeStep(CompositeExecutionStep):
  """
    Create the tests package tree for a new Python project.

    Creates tests/<package_name>/test/ as a real package with a
    generated __init__.py, and an empty .gitignore in tests/,
    tests/<package_name>/ and tests/<package_name>/test/, following
    the tracked-directory principle. Composes a MkdirStep, three
    CreateGitIgnoreFileStep children, and a CreatePythonInitFileStep
    child; all phase logic, ownership, and rollback live in the
    children and in CompositeExecutionStep.
  """
  # pylint: disable-next=super-init-not-called,unused-argument
  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the tests tree creation step.

      :param context: The shared project creation context
      :return: None
    """
    raise NotImplementedError(
      'CreateTestsTreeStep.__init__() is not implemented yet')

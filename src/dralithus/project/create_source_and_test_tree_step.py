"""
  create_source_and_test_tree_step.py: Define the
  CreateSourceAndTestTreeStep class.
"""
# -------------------------------------------------------------------
# create_source_and_test_tree_step.py: Define the
# CreateSourceAndTestTreeStep class.
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
from dralithus.project.execution_step import ExecutionStep
from dralithus.project.mkdir_step import MkdirStep


class CreateSourceAndTestTreeStep(ExecutionStep):
  """
    Represent a project creation step that creates the source and
    test package trees for a new Milestone 42 Python project.

    Creates src/<package_name>/ (a namespace package, no __init__.py)
    and tests/<package_name>/test/ (a real package with a seeded
    __init__.py), plus an empty .gitignore in each. Existing
    directories and files are left untouched (convergent, never
    overwrite). Creation and rollback are owned entirely by this
    step: it records exactly the files and directories its own run
    created, and rollback removes only those.
  """
  def __init__(self, package_name: str) -> None:
    """
      Initialize the source and test tree creation step.

      :param package_name: The Python package name for the project
      :return: None
      :raises DralithusProjectError: When package_name is not a valid
        Python package name
    """
    self._package_name = package_name
    self._src_mkdir = MkdirStep(Path('src') / package_name)
    self._tests_mkdir = MkdirStep(
      Path('tests') / package_name / 'test')
    self._created_files: list[Path] = []

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the source and test tree creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When tree or file creation fails
    """
    raise NotImplementedError(
      'CreateSourceAndTestTreeStep.run() is not implemented yet')

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the source and test tree creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When tree or file removal fails
    """
    raise NotImplementedError(
      'CreateSourceAndTestTreeStep.rollback() is not implemented yet')

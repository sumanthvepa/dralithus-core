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
from pathlib import Path
from typing import override

from dralithus.project.composite_execution_step import (
  CompositeExecutionStep)
from dralithus.project.context import ProjectContext
from dralithus.project.create_gitignore_file_step import (
  CreateGitIgnoreFileStep)
from dralithus.project.create_python_init_file_step import (
  CreatePythonInitFileStep)
from dralithus.project.mkdir_step import MkdirStep


class CreateTestsTreeStep(CompositeExecutionStep):
  """
    Create the tests package tree for a new Milestone 42 Python project.

    Creates tests/<package_name>/test/ as a real package with a
    generated __init__.py, and an empty .gitignore in tests/,
    tests/<package_name>/ and tests/<package_name>/test/, following the
    tracked-directory principle. Composes a MkdirStep, three
    CreateGitIgnoreFileStep children, and a CreatePythonInitFileStep
    child; per-directory and per-file ownership and rollback live
    entirely in those children.
  """
  @override
  def _run_dry_run(self) -> None:
    """
      Validate the existing tests tree without changing it.

      Each child file step is validated only when its parent directory
      already exists, because MkdirStep does not create directories
      during a dry run.

      :return: None
      :raises DralithusProjectError: When existing tests tree state
        cannot be accepted
    """
    tests = self._context.project_root / 'tests'
    package = tests / self._context.package_name
    test_package = package / 'test'
    self._mkdir.run(dry_run=True)
    if tests.is_dir():
      self._tests_gitignore.run(dry_run=True)
    if package.is_dir():
      self._package_gitignore.run(dry_run=True)
    if test_package.is_dir():
      self._test_gitignore.run(dry_run=True)
      self._init_py.run(dry_run=True)

  def __init__(
    self,
    context: ProjectContext
  ) -> None:
    """
      Initialize the tests tree creation step.

      :param context: The shared project creation context
      :return: None
    """
    package_name = context.package_name
    tests = Path('tests')
    package = tests / package_name
    test_package = package / 'test'
    description = (
      f'{package_name}/test/__init__.py: '
      f'Unit tests for {package_name}.')
    self._mkdir = MkdirStep(context, test_package)
    self._tests_gitignore = CreateGitIgnoreFileStep(context, tests)
    self._package_gitignore = CreateGitIgnoreFileStep(context, package)
    self._test_gitignore = CreateGitIgnoreFileStep(context, test_package)
    self._init_py = CreatePythonInitFileStep(
      context, test_package, context.copyright_header, description)
    super().__init__(
      context,
      (self._mkdir,
       self._tests_gitignore,
       self._package_gitignore,
       self._test_gitignore,
       self._init_py))

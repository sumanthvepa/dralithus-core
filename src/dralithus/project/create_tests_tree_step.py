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

from dralithus.project.context import ProjectContext
from dralithus.project.create_gitignore_file_step import (
  CreateGitIgnoreFileStep)
from dralithus.project.create_python_init_file_step import (
  CreatePythonInitFileStep)
from dralithus.project.error import DralithusProjectError
from dralithus.project.execution_step import ExecutionStep
from dralithus.project.mkdir_step import MkdirStep


class CreateTestsTreeStep(ExecutionStep):
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
    super().__init__(context)
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
    self._steps: tuple[ExecutionStep, ...] = (
      self._mkdir,
      self._tests_gitignore,
      self._package_gitignore,
      self._test_gitignore,
      self._init_py)

  @override
  def run(self, dry_run: bool = False) -> None:
    """
      Run the tests tree creation step.

      Runs the directory, .gitignore and __init__.py children in
      order. On any failure the step rolls back its own completed
      children before re-raising, because the orchestrator never rolls
      back a step whose own run raised. In a dry run, each child file
      step is validated only when its parent directory already exists,
      because MkdirStep does not create directories during a dry run.

      :param dry_run: True if the step should validate without
        changing the file system
      :return: None
      :raises DralithusProjectError: When tests tree creation fails
    """
    if dry_run:
      self._run_dry_run()
    else:
      try:
        for step in self._steps:
          step.run()
      except DralithusProjectError:
        self.rollback()
        raise

  @override
  def rollback(self, dry_run: bool = False) -> None:
    """
      Roll back the tests tree creation step.

      Rolls back the children in reverse order. Each child removes
      only what its own run created; pre-existing directories and
      files are left in place.

      :param dry_run: True if the step should change nothing
      :return: None
      :raises DralithusProjectError: When tests tree removal fails
    """
    for step in reversed(self._steps):
      step.rollback(dry_run)

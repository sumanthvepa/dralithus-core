"""
  create_python_project_step.py: Define the CreatePythonProjectStep
  class.
"""
# -------------------------------------------------------------------
# create_python_project_step.py: Define the CreatePythonProjectStep
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
import os
from pathlib import Path
from typing import override

from dralithus.project.composite_execution_step import (
  CompositeExecutionStep)
from dralithus.project.context import ProjectContext
from dralithus.project.create_packages_step import CreatePackagesStep
from dralithus.project.create_source_tree_step import CreateSourceTreeStep
from dralithus.project.create_tests_tree_step import CreateTestsTreeStep
from dralithus.project.create_pylint_configuration_step import (
  CreatePylintConfigurationStep)
from dralithus.project.create_mypy_configuration_step import (
  CreateMypyConfigurationStep)
from dralithus.project.create_venv_step import CreateVenvStep
from dralithus.project.create_pyproject_toml_step import CreatePyProjectTomlStep
from dralithus.project.install_dependencies_step import InstallDependenciesStep
from dralithus.project.packages import Packages


# pylint: disable-next=too-many-instance-attributes
class CreatePythonProjectStep(CompositeExecutionStep):
  """
    Create a complete Milestone 42 Python project.

    Wire the leaf and composite project creation steps in dependency
    order and delegate orchestration, rollback, and dry-run validation
    to CompositeExecutionStep.
  """
  @override
  def _run_dry_run(self) -> None:
    """
      Validate existing project state without changing the file
      system.

      The independent children are always validated. The dependent
      pyproject and dependency children are validated only when the
      prerequisites that an earlier child would normally create
      already exist, because their validation reads those artifacts.

      :return: None
      :raises DralithusProjectError: When existing project state
        cannot be accepted
    """
    self._packages.run(dry_run=True)
    self._source_tree.run(dry_run=True)
    self._tests_tree.run(dry_run=True)
    self._pylint.run(dry_run=True)
    self._mypy.run(dry_run=True)
    self._venv.run(dry_run=True)
    if self._packages_file_exists() and self._venv_metadata_exists():
      self._pyproject.run(dry_run=True)
    if self._packages_file_exists() and self._venv_python_exists():
      self._dependencies.run(dry_run=True)

  def _packages_file_exists(self) -> bool:
    """
      Check that packages.txt exists as a readable regular file.

      :return: True if packages.txt is a regular file or a symlink
        that resolves to one
    """
    packages_file = (
      self._context.project_root / Packages.PACKAGES_FILENAME)
    return packages_file.is_file()

  def _venv_metadata_exists(self) -> bool:
    """
      Check that the venv exists with its pyvenv.cfg metadata.

      :return: True if the venv directory has a pyvenv.cfg file
    """
    return (self._context.venv_path / 'pyvenv.cfg').is_file()

  def _venv_python_exists(self) -> bool:
    """
      Check that the venv Python interpreter exists and is runnable.

      :return: True if the venv Python is an executable regular file
    """
    venv_python = self._context.venv_python
    return venv_python.is_file() and os.access(venv_python, os.X_OK)

  def __init__(
    self,
    context: ProjectContext,
    python_executable: Path
  ) -> None:
    """
      Initialize the Python project creation step.

      :param context: The shared project creation context
      :param python_executable: The Python executable used to create
        the project virtual environment
      :return: None
      :raises DralithusProjectError: When a child step constructor
        rejects its inputs
    """
    self._packages = CreatePackagesStep(context)
    self._source_tree = CreateSourceTreeStep(context)
    self._tests_tree = CreateTestsTreeStep(context)
    self._pylint = CreatePylintConfigurationStep(context)
    self._mypy = CreateMypyConfigurationStep(context)
    self._venv = CreateVenvStep(context, python_executable)
    self._pyproject = CreatePyProjectTomlStep(
      context,
      context.project_name,
      context.project_description,
      context.project_version)
    self._dependencies = InstallDependenciesStep(context)
    super().__init__(
      context,
      (self._packages,
       self._source_tree,
       self._tests_tree,
       self._pylint,
       self._mypy,
       self._venv,
       self._pyproject,
       self._dependencies))

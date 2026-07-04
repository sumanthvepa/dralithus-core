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
from pathlib import Path

from dralithus.project.context import ProjectContext
from dralithus.project.tx.composite_execution_step import (
  CompositeExecutionStep)
from dralithus.project.tx.create_packages_step import (
  CreatePackagesStep)
from dralithus.project.tx.create_source_tree_step import (
  CreateSourceTreeStep)
from dralithus.project.tx.create_tests_tree_step import (
  CreateTestsTreeStep)
from dralithus.project.tx.create_pylint_configuration_step import (
  CreatePylintConfigurationStep)
from dralithus.project.tx.create_mypy_configuration_step import (
  CreateMypyConfigurationStep)
from dralithus.project.tx.create_venv_step import CreateVenvStep
from dralithus.project.tx.create_pyproject_toml_step import (
  CreatePyProjectTomlStep)
from dralithus.project.tx.install_dependencies_step import (
  InstallDependenciesStep)


class CreatePythonProjectStep(CompositeExecutionStep):
  """
    Create a complete Python project.

    Wire the leaf and composite project creation steps in dependency
    order and delegate all phase logic to CompositeExecutionStep.
    Because every child declares its post-conditions as claims
    during prepare, a dry run validates every child deeply, with no
    prerequisite guards: the pyproject and dependency children
    validate against the venv and dependency files that earlier
    children will create at commit time.
  """
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
    super().__init__(
      context,
      (CreatePackagesStep(context),
       CreateSourceTreeStep(context),
       CreateTestsTreeStep(context),
       CreatePylintConfigurationStep(context),
       CreateMypyConfigurationStep(context),
       CreateVenvStep(context, python_executable),
       CreatePyProjectTomlStep(
         context,
         context.project_name,
         context.project_description,
         context.project_version),
       InstallDependenciesStep(context)))

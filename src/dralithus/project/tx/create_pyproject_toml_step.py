"""
  create_pyproject_toml_step.py: Define the CreatePyProjectTomlStep
  class.
"""
# -------------------------------------------------------------------
# create_pyproject_toml_step.py: Define the CreatePyProjectTomlStep
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


class CreatePyProjectTomlStep(ExecutionStep):
  """
    Represent a project creation step that creates pyproject.toml.

    prepare() derives the Python requirement from the venv's
    current-or-projected Python version, so a dry run validates
    pyproject.toml even before the venv exists. The dependency model
    is read from a real packages.txt, or taken as empty when the
    file is only claimed, matching the header-only files that
    CreatePackagesStep creates at commit time.
  """
  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  # pylint: disable-next=super-init-not-called,unused-argument
  def __init__(
    self,
    context: ProjectContext,
    project_name: str,
    project_description: str,
    project_version: str = '0.1.0'
  ) -> None:
    """
      Initialize the pyproject.toml creation step.

      :param context: The shared project creation context
      :param project_name: The project distribution name
      :param project_description: The project description
      :param project_version: The project version
      :return: None
    """
    raise NotImplementedError(
      'CreatePyProjectTomlStep.__init__() is not implemented yet')

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Validate pyproject.toml against the projected state and claim
      it.

      Reads the Python requirement from the venv's current or
      claimed Python version and the dependency model from a real
      packages.txt (empty when the file is only claimed), computes
      the expected pyproject.toml, and requires an existing
      pyproject.toml to match it. Claims pyproject.toml as a
      current-or-projected file.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When no venv is current or
        claimed, packages.txt is neither real nor claimed, or an
        existing pyproject.toml does not match the expected content
    """
    raise NotImplementedError(
      'prepare() is not implemented yet')

  @override
  def commit(self) -> None:
    """
      Create pyproject.toml unless an acceptable one exists.

      Recomputes the expected content from the post-commit reality
      of the venv metadata and dependency files. An existing
      pyproject.toml must match the expected content and is left in
      place, unowned. An absent pyproject.toml is created by
      exclusive creation, with ownership recorded the instant
      creation succeeds, before the content write.

      :return: None
      :raises DralithusProjectError: When the file cannot be created
        or an existing file does not match the expected content
    """
    raise NotImplementedError(
      'commit() is not implemented yet')

  @override
  def abort(self) -> None:
    """
      Remove a pyproject.toml this step created.

      A pre-existing pyproject.toml is left in place. Files already
      removed externally are accepted silently. Must be idempotent.

      :return: None
      :raises DralithusProjectError: When the owned pyproject.toml
        cannot be removed
    """
    raise NotImplementedError(
      'abort() is not implemented yet')

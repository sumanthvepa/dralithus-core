"""
  create_python_init_file_step.py: Define the
  CreatePythonInitFileStep class.
"""
# -------------------------------------------------------------------
# create_python_init_file_step.py: Define the
# CreatePythonInitFileStep class.
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
from dralithus.project.copyright_header import CopyrightHeader
from dralithus.project.tx.execution_step import ExecutionStep
from dralithus.project.tx.project_state import ProjectState


class CreatePythonInitFileStep(ExecutionStep):
  """
    Represent a project creation step that creates an __init__.py
    file with a copyright notice in one project-relative directory.

    Delegates every phase to an inner CreateFileStep whose content
    is rendered at construction time from the copyright header and
    description.
  """
  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  # pylint: disable-next=super-init-not-called,unused-argument
  def __init__(
    self,
    context: ProjectContext,
    directory: Path,
    copyright_header: CopyrightHeader,
    description: str
  ) -> None:
    """
      Initialize the Python __init__.py creation step.

      The generated __init__.py begins with a module docstring
      holding the description, followed by the copyright header that
      repeats the same description. Both are rendered here, because
      the project context is known at construction time.

      :param context: The shared project creation context
      :param directory: The project-relative directory that should
        contain the __init__.py file
      :param copyright_header: The copyright header renderer for the
        generated __init__.py file
      :param description: The file description for the docstring and
        the copyright header
      :return: None
      :raises DralithusProjectError: When directory is absolute
    """
    raise NotImplementedError(
      'CreatePythonInitFileStep.__init__() is not implemented yet')

  @property
  def init_filename(self) -> str:
    """
      Return the Python package initializer filename.

      :return: The initializer filename
    """
    raise NotImplementedError(
      'init_filename is not implemented yet')

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Prepare the inner file creation step.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When the __init__.py target
        cannot be accepted
    """
    raise NotImplementedError(
      'prepare() is not implemented yet')

  @override
  def commit(self) -> None:
    """
      Commit the inner file creation step.

      :return: None
      :raises DralithusProjectError: When the __init__.py file
        cannot be created or written
    """
    raise NotImplementedError(
      'commit() is not implemented yet')

  @override
  def abort(self) -> None:
    """
      Abort the inner file creation step.

      :return: None
      :raises DralithusProjectError: When the owned __init__.py file
        cannot be removed
    """
    raise NotImplementedError(
      'abort() is not implemented yet')

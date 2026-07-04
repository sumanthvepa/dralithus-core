"""
  create_source_tree_step.py: Define the CreateSourceTreeStep class.
"""
# -------------------------------------------------------------------
# create_source_tree_step.py: Define the CreateSourceTreeStep class.
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
from dralithus.project.tx.create_gitignore_file_step import (
  CreateGitIgnoreFileStep)
from dralithus.project.tx.mkdir_step import MkdirStep


class CreateSourceTreeStep(CompositeExecutionStep):
  """
    Create the src package tree for a new Python project.

    Creates src/<package_name>/ as a namespace package (no
    __init__.py) and an empty .gitignore in src/ and
    src/<package_name>/, following the tracked-directory principle.
    Composes a MkdirStep and two CreateGitIgnoreFileStep children;
    all phase logic, ownership, and rollback live in the children
    and in CompositeExecutionStep.
  """
  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the source tree creation step.

      :param context: The shared project creation context
      :return: None
    """
    package = Path('src') / context.package_name
    super().__init__(
      context,
      (MkdirStep(context, package),
       CreateGitIgnoreFileStep(context, Path('src')),
       CreateGitIgnoreFileStep(context, package)))

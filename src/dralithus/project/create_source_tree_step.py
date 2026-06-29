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
from typing import override

from dralithus.project.composite_execution_step import (
  CompositeExecutionStep)
from dralithus.project.context import ProjectContext
from dralithus.project.create_gitignore_file_step import (
  CreateGitIgnoreFileStep)
from dralithus.project.mkdir_step import MkdirStep


class CreateSourceTreeStep(CompositeExecutionStep):
  """
    Create the src package tree for a new Milestone 42 Python project.

    Creates src/<package_name>/ as a namespace package (no __init__.py)
    and an empty .gitignore in src/ and src/<package_name>/, following
    the tracked-directory principle. Composes a MkdirStep and two
    CreateGitIgnoreFileStep children; per-directory and per-file
    ownership and rollback live entirely in those children.
  """
  @override
  def _run_dry_run(self) -> None:
    """
      Validate the existing source tree without changing it.

      Each child .gitignore step is validated only when its parent
      directory already exists, because MkdirStep does not create
      directories during a dry run.

      :return: None
      :raises DralithusProjectError: When existing source tree state
        cannot be accepted
    """
    src = self._context.project_root / 'src'
    package = src / self._context.package_name
    self._mkdir.run(dry_run=True)
    if src.is_dir():
      self._src_gitignore.run(dry_run=True)
    if package.is_dir():
      self._package_gitignore.run(dry_run=True)

  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the source tree creation step.

      :param context: The shared project creation context
      :return: None
    """
    package = Path('src') / context.package_name
    self._mkdir = MkdirStep(context, package)
    self._src_gitignore = CreateGitIgnoreFileStep(context, Path('src'))
    self._package_gitignore = CreateGitIgnoreFileStep(context, package)
    super().__init__(
      context,
      (self._mkdir, self._src_gitignore, self._package_gitignore))

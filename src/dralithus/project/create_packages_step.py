"""
  create_packages_step.py: Define the CreatePackagesStep class.
"""
# -------------------------------------------------------------------
# create_packages_step.py: Define the CreatePackagesStep class.
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
from dralithus.project.error import DralithusProjectError
from dralithus.project.execution_step import ExecutionStep
from dralithus.project.packages import Packages


class CreatePackagesStep(ExecutionStep):
  """
    Represent a project creation step that seeds the Packages System
    dependency files (packages.txt and local-packages.txt)

    Creates whichever of packages.txt and local-packages.txt is
    missing from the project root, seeded with a header comment.
    Existing dependency files are left untouched. Rollback removes
    only the files this step created.
  """
  _created_files: list[Path]

  def _remove_created_files(self) -> None:
    """
      Remove the dependency files created by this step.

      Files already removed externally are accepted silently.

      :return: None
      :raises DralithusProjectError: When a created dependency file
        cannot be removed
    """
    for path in self._created_files:
      try:
        path.unlink(missing_ok=True)
      except OSError as error:
        raise DralithusProjectError(
          f'Could not remove dependency file: {path}') from error
    self._created_files = []

  @staticmethod
  def _missing_files(project_root: Path) -> list[Path]:
    """
      Return the dependency files missing from the project root.

      :param project_root: The project root directory
      :return: The dependency file paths that do not exist yet
    """
    candidates = [
      project_root / Packages.PACKAGES_FILENAME,
      project_root / Packages.LOCAL_PACKAGES_FILENAME]
    return [path for path in candidates if not path.exists()]

  def __init__(self) -> None:
    """
      Initialize the packages creation step.

      :return: None
    """
    self._created_files = []

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the packages creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When a missing dependency file
        cannot be written, or an existing one cannot be read
    """
    if not dry_run:
      # Record the files create will write before calling it, so a
      # failure after a partial write can still be rolled back.
      self._created_files.extend(self._missing_files(context.project_root))
      Packages.create(context.project_root)

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the packages creation step.

      Removes only the dependency files created by this step's run.
      Pre-existing dependency files are left in place.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When a created dependency file
        cannot be removed
    """
    if not dry_run:
      self._remove_created_files()

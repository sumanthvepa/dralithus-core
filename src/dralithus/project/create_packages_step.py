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
    Represent a project creation step that creates the Packages
    System dependency files (packages.txt and local-packages.txt)

    Creates whichever of packages.txt and local-packages.txt is
    missing from the project root, seeded with a header comment.
    Existing dependency files are left untouched. Creation and
    rollback are owned entirely by this step: it records exactly
    the files its own exclusive writes created, and rollback
    removes only those.
  """
  _PACKAGES_HEADER = (
    '# Third-party packages, one per line.\n'
    '# Append " [dev]" to mark a development-only dependency.\n')
  _LOCAL_PACKAGES_HEADER = (
    '# Local editable packages, one path per line.\n'
    '# Append " [dev]" to mark a development-only dependency.\n')

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

  def _create_missing_files(self, project_root: Path) -> None:
    """
      Create the missing dependency files in the project root.

      Records exactly the files this step created. On a write
      failure the files this step created are removed before
      raising, so nothing is left behind.

      :param project_root: The project root directory
      :return: None
      :raises DralithusProjectError: When a missing dependency file
        cannot be written
    """
    targets = (
      (project_root / Packages.PACKAGES_FILENAME,
       self._PACKAGES_HEADER),
      (project_root / Packages.LOCAL_PACKAGES_FILENAME,
       self._LOCAL_PACKAGES_HEADER))
    try:
      for path, content in targets:
        if self._create_file(path, content):
          self._created_files.append(path)
    except OSError as error:
      self._remove_created_files()
      raise DralithusProjectError(
        f'Could not write dependency file: {project_root}') from error

  @staticmethod
  def _create_file(path: Path, content: str) -> bool:
    """
      Write content to path unless the path already exists.

      Creation is exclusive, so a file that appears between any
      earlier existence check and the write is never overwritten,
      and the return value reports true ownership: True only when
      this call created the file.

      :param path: The dependency file to create
      :param content: The content to write
      :return: True if this call created the file, False if the
        path already existed (including as a dangling symlink)
      :raises OSError: When the file cannot be written
    """
    created = False
    try:
      with path.open('x', encoding='utf-8') as file:
        file.write(content)
      created = True
    except FileExistsError:
      pass
    return created

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
      # The failure cleanup is needed because the orchestrator
      # never rolls back a step whose own run raised.
      self._create_missing_files(context.project_root)
      try:
        Packages(context.project_root)
      except DralithusProjectError:
        self._remove_created_files()
        raise

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

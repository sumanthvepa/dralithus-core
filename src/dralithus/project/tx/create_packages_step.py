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
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.tx.execution_step import ExecutionStep
from dralithus.project.tx.project_state import ProjectState


class CreatePackagesStep(ExecutionStep):
  """
    Represent a project creation step that creates the Packages
    System dependency files (packages.txt and local-packages.txt)

    Creates whichever of packages.txt and local-packages.txt is
    missing from the project root, initialized with a header
    comment. Existing dependency files are left untouched. Creation
    and abort are owned entirely by this step: it records exactly
    the files its own exclusive writes created, and abort removes
    only those.

    Known limitation (deferred, not fixed): ownership is tracked by
    path only, so cleanup unlinks whatever currently occupies a
    created path without checking it is still the file this step
    created. If a created file is removed and replaced by a
    different file before failure cleanup or abort runs, the
    replacement is deleted - contradicting the contract above. The
    window is small within a single process, but is realistic under
    the concurrent, multi-agent filesystem access dralithus is
    intended to support. Any future fix must preserve immediate
    cleanup of empty or partially written files after a write
    failure, while preventing a later abort from deleting a
    replacement file. A residual check-to-unlink TOCTOU may remain,
    since name-based unlink cannot be made atomic with an identity
    or content check.
  """
  # pylint: disable-next=super-init-not-called,unused-argument
  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the packages creation step.

      :param context: The shared project creation context
      :return: None
    """
    raise NotImplementedError(
      'CreatePackagesStep.__init__() is not implemented yet')

  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Validate existing dependency files and claim both files.

      An existing dependency file must parse as a valid Packages
      System artifact; whichever file is missing is claimed as
      to-be-created. Both packages.txt and local-packages.txt are
      claimed as current-or-projected files.

      :param state: The projected project state to read and extend
      :return: None
      :raises DralithusProjectError: When an existing dependency
        file cannot be read or parsed
    """
    raise NotImplementedError(
      'prepare() is not implemented yet')

  @override
  def commit(self) -> None:
    """
      Create the missing dependency files by exclusive creation.

      Ownership is recorded the instant each exclusive creation
      succeeds, before the content write, so a write failure cannot
      leave an untracked partial file behind. A path that exists at
      commit time (including as a dangling symlink) is neither
      replaced nor claimed. After creation the combined dependency
      files are re-validated; on failure the files this step created
      are removed before raising.

      :return: None
      :raises DralithusProjectError: When a missing dependency file
        cannot be written, or the resulting files cannot be parsed
    """
    raise NotImplementedError(
      'commit() is not implemented yet')

  @override
  def abort(self) -> None:
    """
      Remove the dependency files created by this step's commit.

      Pre-existing dependency files are left in place. Files already
      removed externally are accepted silently. Must be idempotent.

      :return: None
      :raises DralithusProjectError: When a created dependency file
        cannot be removed
    """
    raise NotImplementedError(
      'abort() is not implemented yet')

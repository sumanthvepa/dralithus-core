"""
  creation_step.py: Define the CreationStep abstract base class.
"""
# -------------------------------------------------------------------
# creation_step.py: Define the CreationStep abstract base class.
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
from abc import ABC, abstractmethod

from dralithus.project.context import ProjectContext


class CreationStep(ABC):
  """
    Represent one idempotent project creation step.
  """
  @abstractmethod
  def run(
    self,
    context: ProjectContext,
    dry_run: bool = False
  ) -> None:
    """
      Run the project creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
    """
    raise NotImplementedError('run() must be implemented in derived class')

  @abstractmethod
  def rollback(
    self,
    context: ProjectContext,
    dry_run: bool = False
  ) -> None:
    """
      Roll back the project creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
    """
    raise NotImplementedError(
      'rollback() must be implemented in derived class')

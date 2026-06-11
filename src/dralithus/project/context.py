"""
  context.py: Define the ProjectContext class.
"""
# -------------------------------------------------------------------
# context.py: Define the ProjectContext class.
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
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectContext:
  """
    Hold shared state for project creation steps.
  """
  project_root: Path

  @property
  def venv_path(self) -> Path:
    """
      Return the virtual environment path.

      :return: The path to the project virtual environment
    """
    return self.project_root / 'venv'

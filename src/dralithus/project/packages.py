"""
  packages.py: Define the Packages NamedTuple.
"""
# -------------------------------------------------------------------
# packages.py: Define the Packages NamedTuple.
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
from typing import NamedTuple


class Packages(NamedTuple):
  """
    Hold the dependency lists for a Python project.

    The lists represent the contents of packages.txt for Milestone
    42 Python projects: runtime dependencies and dev dependencies.
  """
  dependencies: list[str]
  dev_dependencies: list[str]

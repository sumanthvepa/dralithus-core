"""
  error.py: Define project creation errors.
"""
# -------------------------------------------------------------------
# error.py: Define project creation errors.
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
from dralithus.errors import DralithusError, ExitCode


class DralithusProjectError(DralithusError):
  """
    Exception raised for errors related to project creation.
  """
  def __init__(self, message: str) -> None:
    """
      Initialize the project error with a message.

      :param message: The error message
      :return: None
    """
    super().__init__(message, exit_code=ExitCode.PROJECT_ERROR)

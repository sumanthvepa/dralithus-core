"""
  errors.py:  Define the DralithusError class
"""
# -------------------------------------------------------------------
# errors.py:  Define the DralithusError class
#
# Copyright (C) 2023-25 Sumanth Vepa.
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
from enum import IntEnum

class ExitCode(IntEnum):
  """
    Enumeration for program exit codes.

    Every DralithusError subclass should have a program exit code
    associated with it. This is the program exit code that will be
    returned when the error is raised but not caught by any
    exception handler, except for the top level exception handler in
    the main function (in drl.)

    Each exit code here corresponds to a specific exception class.
  """
  SUCCESS = 0 # Success
  INVALID_COMMAND_LINE = 1 # Associated with CommandLineError


class DralithusError(RuntimeError):
  """
    Base class for all Dralithus exceptions.

    Any error detected by the program should be raised as
    a subclass of DralithusError.

    Any other exception is an indication of a bug in the code
    and should not be caught. It should be fixed instead.
  """
  def __init__(self, message: str, exit_code: ExitCode) -> None:
    """
      Initialize the DralithusError with a message and an exit code.

      :param message: The error message
      :param exit_code: The program exit code that should be returned
    """
    super().__init__(message)
    self._exit_code = exit_code

  @property
  def exit_code(self) -> ExitCode:
    """
      The exit code of the error.

      :return: The exit code of the error
    """
    return self._exit_code

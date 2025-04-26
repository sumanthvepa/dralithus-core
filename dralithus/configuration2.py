"""
  configuration2.py: New configuration processing for dralithus
"""
# -------------------------------------------------------------------
# configuration2.py: New configuration processing for dralithus
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
from dralithus.errors import DralithusError, ExitCode


class CommandLineError(DralithusError):
  """
    Exception raised for invalid command line arguments passed
    by the user.

    Unlike other exceptions, this exception is caught by code
    that parses the command line and converted into a help command
    that is executed. The help command when executed will print
    the error, and then provide an appropriate help message.
  """
  def __init__(self, message: str) -> None:
    """
      Initialize the InvalidCommandLineError with a message.

      The exit code is set to ExitCode.INVALID_COMMAND_LINE.

      :param message: The error message
    """
    super().__init__(message, exit_code=ExitCode.INVALID_COMMAND_LINE)

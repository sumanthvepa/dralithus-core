"""
  errors.py:  Define the DralithusError class
"""
# -------------------------------------------------------------------
# errors.py:  Define the DralithusError class and subclasses.
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
  ENVIRONMENT_ERROR = 2 # Associated with EnvironmentError
  APPLICATION_ERROR = 3 # Associated with ApplicationError


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

  def __eq__(self, other: object) -> bool:
    """
      Check if two DralithusError instances are equal.

      :param other: The other error to compare with
      :return: True if the errors are equal, False otherwise
    """
    if not isinstance(other, DralithusError):
      return NotImplemented
    return (super().__eq__(other) and
      self.exit_code == other.exit_code and
      self.args == other.args)

  @property
  def exit_code(self) -> ExitCode:
    """
      The exit code of the error.

      :return: The exit code of the error
    """
    return self._exit_code


class CommandLineError(DralithusError):
  """
    Exception raised for invalid command line arguments passed
    by the user.

    Unlike other exceptions, this exception is caught by code
    that parses the command line and converted into a help command
    that is executed. The help command when executed will print
    the error, and then provide an appropriate help message.
  """
  def __init__(self, program: str, message: str) -> None:
    """
      Initialize the InvalidCommandLineError with a message.

      The exit code is set to ExitCode.INVALID_COMMAND_LINE.

      :param message: The error message
    """
    super().__init__(message, exit_code=ExitCode.INVALID_COMMAND_LINE)
    self._program = program

  def __eq__(self, other: object) -> bool:
    """
      Check if two command line errors are equal.

      :param other: The other command line error to compare with
      :return: True if the command line errors are equal, False otherwise
    """
    if not isinstance(other, CommandLineError):
      return NotImplemented
    return self.program == other.program and self.args == other.args

  @property
  def program(self) -> str:
    """
      The name of the program that caused the error.

      :return: The name of the program
    """
    return self._program


class DralithusEnvironmentError(DralithusError):
  """
    Exception raised for errors related to environments.

    We choose the name `DralithusEnvironmentError` to avoid
    confusion with the standard library's `EnvironmentError`

    This exception is used to indicate errors that occur while
    working with environments, such as loading or deploying them.
  """
  def __init__(self, message: str) -> None:
    """
      Initialize the EnvironmentError with a message.

      The exit code is set to ExitCode.INVALID_COMMAND_LINE.

      :param message: The error message
    """
    super().__init__(message, exit_code=ExitCode.ENVIRONMENT_ERROR)


class DralithusApplicationError(DralithusError):
  """
    Exception raised for errors related to applications.

    We choose the name `DralithusApplicationError` to keep
    consistency with the naming of `DralithusEnvironmentError`

    This exception is used to indicate errors that occur while
    working with applications, such as loading or deploying them.
  """
  def __init__(self, message: str) -> None:
    """
      Initialize the ApplicationError with a message.

      The exit code is set to ExitCode.INVALID_COMMAND_LINE.

      :param message: The error message
    """
    super().__init__(message, exit_code=ExitCode.APPLICATION_ERROR)

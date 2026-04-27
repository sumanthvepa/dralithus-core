"""
  help_command.py: Define the HelpCommand class.
"""
# -------------------------------------------------------------------
# help_command.py: Define the HelpCommand class.
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
from __future__ import annotations
from typing_extensions import override


from dralithus.command_line.command_line import CommandLine
from dralithus.command import Command
from dralithus.errors import ExitCode, CommandLineError

from dralithus.command_line.options import Options


class HelpCommand(Command):
  """
    Help command that displays the help message for the command line tool.

    This class represents a request for help from the user, either
    directly if they specify the help option on the command line,
    or indirectly, if there is an error on the command line.
  """
  @override
  def __init__(
      self,
      program_name: str,
      command_needing_help: str | None,
      error_message: str | None,
      verbosity: int) -> None:
    """
      Initialize the help command with a verbosity level.

      :param program_name: The name of the program
      :param command_needing_help: The name of the command that
        caused the help command to be invoked, or None if the help
        request was for global help.
      :param error_message: The error message from the exception that
        caused the help command to be invoked, or None if there was
        no error.
      :param verbosity: The verbosity level of the command
    """
    super().__init__('help', verbosity)
    self._program_name = program_name
    self._command_needing_help = command_needing_help
    self._error_message = error_message

  def __eq__(self, other: object) -> bool:
    """
      Check if two help commands are equal.

      :param other: The other command to compare with
      :return: True if the commands are equal, False otherwise
    """
    if not isinstance(other, HelpCommand):
      return NotImplemented
    # Uncomment when debugging equality issues
    # a = super().__eq__(other)
    # b = self.program_name == other.program_name
    # c = self.command_needing_help == other.command_needing_help
    # d = self.error == other.error
    # e = self.verbosity == other.verbosity
    # return a and b and c and d and e
    return (super().__eq__(other) and
      self.program_name == other.program_name and
      self.command_needing_help == other.command_needing_help and
      self.error_message == other._error_message and
      self.verbosity == other.verbosity)

  def __str__(self) -> str:
    """
      Return a string representation of the help command.

      :return: A string representation of the help command
    """
    return f'HelpCommand(program_name={self.program_name}, ' \
      + f'command_needing_help={self.command_needing_help}, ' \
      + f'error_message={self.error_message}, verbosity={self.verbosity})'

  @property
  def program_name(self) -> str:
    """
      The name of the program

      :return: The name of the program
    """
    return self._program_name

  @property
  def error_message(self) -> str | None:
    """
      The error that caused the help command to be executed

      :return: The error that caused the help command to be executed
    """
    return self._error_message

  @property
  def command_needing_help(self) -> str | None:
    """
      The name of the command that caused the help command
      to be invoked.

      :return: The name of the command that caused the help command
        to be invoked, or None if the help request was for global
        help.
    """
    return self._command_needing_help

  @override
  def execute(self) -> int:
    """
      Execute the 'help' command.

      :return: The program exit code
    """
    # TODO: Implement this
    if self.error_message is not None:
      print(f'Error: {self.error_message}')
    print (f'Help is not yet implemented for {self.program_name} '
      + f'at verbosity level {self.verbosity}.')
    return ExitCode.SUCCESS


def make_from_command_line(cmdln: CommandLine) -> HelpCommand:
  """
    Create a help command from the command line arguments.

    :param cmdln: The command line arguments
    :return: The help command object

  """
  return HelpCommand(
      program_name=cmdln.program,
      command_needing_help=cmdln.command_name,
      error_message=None,  # No error is passed to the help command
      verbosity=cmdln.verbosity)

def make_from_error(ex: CommandLineError) -> HelpCommand:
  """
    Create a help command from an error.

    :param ex: The error that caused the help command to be invoked
    :return: The help command object
  """
  return HelpCommand(
      program_name=ex.program,
      command_needing_help=ex.command,
      error_message=str(ex),
      verbosity=ex.verbosity)

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
from typing_extensions import override

from dralithus.configuration2 import CommandLineError
from dralithus.command import Command


class HelpCommand(Command):
  """
    Help command that displays the help message for the command line tool.

    This class represents a request for help from the user, either
    directly if they specify the help option on the command line,
    or indirectly, if there is an error on the command line.
  """
  def __init__(
      self,
      verbosity: int,
      command_name: str | None,
      error: CommandLineError | None) -> None:
    """
      Initialize the help command with a verbosity level.

      :param verbosity: The verbosity level of the command
    """
    super().__init__("help", verbosity)
    self._command_name = command_name
    self._error = error

  @property
  def error(self) -> CommandLineError | None:
    """
      The error that caused the help command to be executed

      :return: The error that caused the help command to be executed
    """
    return self._error

  @property
  def command_name(self) -> str | None:
    """
      The name of the command that caused the help command
      to be invoked.
    :return: The name of the command that caused the help command
      to be invoked, or None if the help request was for global
      help.
    """
    return self._command_name

  @override
  def execute(self) -> int:
    """
      Execute the 'help' command.

      :return: The program exit code
    """
    raise NotImplementedError("HelpCommand.execute() is not yet implemented")

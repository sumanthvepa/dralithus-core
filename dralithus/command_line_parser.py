"""
  command_line_parser.py: Define class CommandLineParser
"""
# -------------------------------------------------------------------
# command_line_parser.py: Define class CommandLineParser
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

from dralithus.errors import CommandLineError
from dralithus.command import Command
from dralithus.deploy_command import DeployCommand
from dralithus.help_command import HelpCommand
from dralithus.global_options import GlobalOptions
from dralithus.command_options import CommandOptions


class CommandLineParser:  # pylint: disable=too-few-public-methods
  """
    Command line parser that parses the command line arguments
    and returns the command to execute.

    The class encapsulates the logic for parsing different parts
    of the command line. This is a class rather than a function
    because a class enables the use of instance variables to
    pass state between the different parsing methods, thereby
    avoiding the need to pass the state as arguments to each
    method. This makes the code cleaner and easier to read.
  """
  def __init__(self, args: list[str]):
    """
      Initialize the command line with arguments

      :param args: The command line arguments
    """
    # Note that we copy the args list, since we will be modifying it
    # during parsing. We do not want to modify the original list.
    self._program_name: str = args[0]
    self._args: list[str] = args[1:]
    self._command_name: str | None = None
    self._global_options: GlobalOptions \
      = GlobalOptions(help=False, verbosity=0)
    self._command_options: CommandOptions \
      = CommandOptions(help=False, verbosity=0, environments=[], applications=[])

  def _parse_global_options(self) -> GlobalOptions:
    """
      Parse the command line arguments and return the global options

      :return: The global options. It removes all processed arguments
      from the args list passed in.
    """
    # This is a placeholder implementation. The actual implementation
    # would parse the command line arguments and return the options.
    raise NotImplementedError("parse_global_options() not yet implemented")

  def _parse_command_name(self) -> str:
    """
      Parse the command line arguments and return the command name

      :return: The command name
    """
    # This is a placeholder implementation. The actual implementation
    # would parse the command line arguments and return the command name.
    raise NotImplementedError("parse_command_name() not yet implemented")

  def _parse_command_options(self) -> CommandOptions:
    """
      Parse the command line arguments and return the command options

      :return: The command options
    """
    # This is a placeholder implementation. The actual implementation
    # would parse the command line arguments and return the command options.
    raise NotImplementedError("parse_command_options() not yet implemented")

  def _get_verbosity(self) -> int:
    """
      Get the verbosity level from the global and command options.

      :return: The verbosity level
    """
    return self._global_options['verbosity'] + self._command_options['verbosity']

  def _is_asking_for_help(self) -> bool:
    """
      Check if the user is asking for help.

      :return: True if the user is asking for help
    """
    return self._global_options['help'] \
      or self._command_options['help'] \
      or self._command_name == 'help'

  def _make_help_command(self, error: CommandLineError | None = None) -> HelpCommand:
    """
      Create the help command.

      :return: HelpCommand
    """
    return HelpCommand(
      program_name=self._program_name,
      command_needing_help=self._command_name,
      error=error,
      verbosity=self._get_verbosity())

  def _make_deploy_command(self) -> DeployCommand:
    """
      Create the 'deploy' command.

      :return: DeployCommand
    """
    return DeployCommand(
      environments=self._command_options["environments"],
      applications=self._command_options["applications"],
      verbosity=self._get_verbosity())

  def _make_command(self) -> Command:
    """
      Create the command from the name, global, command options
      and parameters.

      :return: Command
    """
    if self._is_asking_for_help():
      return self._make_help_command()
    if self._command_name  == 'deploy':
      return self._make_deploy_command()
    raise CommandLineError(f"Unknown command: {self._command_name}")

  def parse(self) -> Command:
    """
      Parse the command line arguments and return the command to execute

      :return: The command to execute
    """
    try:
      self._parse_global_options()
      self._parse_command_name()
      self._parse_command_options()
      return self._make_command()
    except CommandLineError as ex:
      # If an exception occurs during parsing, return a help command
      # with the error message and, the command name that was being parsed (if any.)
      return self._make_help_command(ex)

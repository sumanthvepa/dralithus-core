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
from typing import TypedDict

from dralithus.errors import CommandLineError
from dralithus.command import Command
from dralithus.deploy_command import DeployCommand
from dralithus.help_command import HelpCommand


class GlobalOptions(TypedDict):
  """
    Global options applicable to all commands

    This class should NOT be used outside of this module.

    Global options are options that appear before the command name
    and are applicable to all commands. There are two global options
    that are currently supported:
      -h, --help: Show an appropriate help message. This is a boolean
      option that is set to True if the help option was specified at
      least once.
      -v, --verbose, --verbosity: Set the verbosity level of the
      command. This is an integer option that can be specified
      multiple times either as a flag (-v or --verbose) or as an
      option with a value (-v 1 or --verbosity 1, or --verbose=2). The
      verbosity level is an integer and each appearance of the
      flag/option increases the verbosity by 1.

    This dictionary holds any global options that were specified
    on the command line. This class is used internally by the
    CommandLine class to store the global options during command
    line parsing.

    Options here are combined with command options to create the
    appropriate Command object during parsing.

    :param help: True if the help option was specified as a global option.
  """
  help: bool
  verbosity: int


class CommandOptions(TypedDict):
  """
    Options applicable to a specific command.

    This class should NOT be used outside of this module.

    Command options are options that appear after the command name
    and are applicable to the command. The options supported for
    each command are described below:
    help command:
      -v, --verbose, --verbosity: Set the verbosity level of the
      command. This is an integer option that can be specified
      multiple times either as a flag (-v or --verbose) or as an
      option with a value (-v 1 or --verbose=2). The verbosity
      level is an integer and each appearance of the flag/option
      increases the verbosity by 1.
    deploy command:
      -h, --help: Show help message about this command. This is a
      boolean option that is set to True if the help option was
      specified at least once.

      -v, --verbose, --verbosity: Set the verbosity level of the
      command. The semantics are the same as for the help command.
      -e, --env --environment: Specify the environment(s) to deploy
      to. This is a list of environment names. The environment names
      can be specified as a comma separated list after the flag: e.g.

      -e=env1,env2,env3 or -e env1,env2,env3 or --env env1,env2,env3
      or --environment env1,env2,env3. The environment names can also
      be specified my repeating the flag: e.g. -e env1 -e env2 -e env3
      (or -e env1 --env env2 --environment=env3,env4).
      The names of the environments must be valid environment names.
      For now the valid environment names are hardcoded to be:
      - local:  A default local environment
      - dev:    A default development environment
      - test:   A default test environment
      - stage: A default staging environment
      - prod:   A default production environment
      - all:    All environments

      Strictly speaking these environment names are actually aliases
      for the real environment names.

      applications: These are specified as a list of arguments passed
      to the command rather than as flags/options. The names must
      be valid application names. For now the valid application names
      are sample, which is hardcoded to be a sample application.
  """
  help: bool
  verbosity: int
  environments: list[str]
  applications: list[str]


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

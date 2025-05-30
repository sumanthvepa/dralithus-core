"""
  command.py: Define the Command abstract base class.
"""
# -------------------------------------------------------------------
# command.py: Define the Command abstract base class.
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
from abc import ABC, abstractmethod

from dralithus.command_line.command_line import parse
from dralithus.command_line.options import Options
from dralithus.errors import CommandLineError


class Command(ABC):
  """
    A dralithus command that can be executed
  """
  def __init__(self, name: str, verbosity: int) -> None:
    """
      Initialize the command with a verbosity level.

      :param verbosity: The verbosity level of the command
    """
    self._name = name
    self._verbosity = verbosity

  def __eq__(self, other: object) -> bool:
    """
      Check if two commands are equal.

      :param other: The other command to compare with
      :return: True if the commands are equal, False otherwise
    """
    if not isinstance(other, Command):
      return NotImplemented
    return self.name == other.name and self.verbosity == other.verbosity

  @property
  def name(self) -> str:
    """
      The name of the command.

      :return: The name of the command
    """
    return self._name

  @property
  def verbosity(self) -> int:
    """
      The verbosity level of the command.

      :return: The verbosity level of the command
    """
    return self._verbosity

  @abstractmethod
  def execute(self) -> int:
    """
      Execute the command.

      Any class derived from this class must implement this method
      to execute the actual command.

      :return: The program exit code
    """
    raise NotImplementedError('execute() must be implemented in derived class')

def is_help_requested(
    command_name: str | None,
    global_options: Options,
    command_options: Options) -> bool:
  """
    Check if help is requested for the command.

    :param command_name: The name of the command
    :param global_options: Global options
    :param command_options:  Command specific options
    :return: True if help is requested, False otherwise
  """
  help_requested = global_options.get('requires_help', False) \
                  or command_options.get('requires_help', False)
  assert isinstance(help_requested, bool)
  return command_name == 'help' or help_requested


def make(args: list[str]) -> Command:
  """
    Create a command from the command line arguments.

    :param args: The command line arguments
    :return: The command object
  """
  # We import the command modules here to avoid circular imports.
  # pylint: disable=import-outside-toplevel
  from dralithus.help_command import make as make_help, make_from_error as make_help_from_error
  from dralithus.deploy_command import make as make_deploy

  # The type ignore directives in the code below are to bypass
  # a bug in how mypy runs within IntelliJ IDEA. The error does
  # not occur when running mypy from the command line.
  try:
    cmdln = parse(args)

    if is_help_requested(cmdln.command_name, cmdln.global_options, cmdln.command_options):
      return make_help(  # type: ignore[return-value]
        cmdln.program, cmdln.command_name, cmdln.global_options, cmdln.command_options)

    if cmdln.command_name == 'deploy':
      return make_deploy(  # type: ignore[return-value]
        cmdln.program, cmdln.global_options, cmdln.command_options, cmdln.parameters)

    if cmdln.command_name is None:
      raise CommandLineError(cmdln.program,'No command specified')

    raise CommandLineError(cmdln.program,f'Unknown command \'{cmdln.command_name}\' specified')
  except CommandLineError as ex:
    return make_help_from_error(ex)  # type: ignore[return-value]

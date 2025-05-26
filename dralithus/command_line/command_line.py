"""
  command_line.py: Define the CommandLine class.
"""
# -------------------------------------------------------------------
# command_line.py: Define the CommandLine class.
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

from dralithus.command_line.options import Options
from dralithus.errors import CommandLineError


class CommandLine:
  """
    Represents parsed command line arguments.

    The CommandLine class takes a list of command line arguments,
    parses them, and provides methods to access the parsed arguments.
  """
  # pylint: disable=too-many-arguments
  def __init__(self,
      program: str,
      command_name: str | None,
      global_options: Options,
      command_options: Options,
      parameters: set[str]) -> None:
    """
      Initialize the command line with arguments

      :param program: The name of the program
      :param command_name: The name of the command
      :param global_options: Any global options specified before the command
      :param command_options: Any command specific options
      :param parameters: Any parameters specified after the options
    """
    self._program = program
    self._command_name = command_name
    self._global_options = global_options
    self._command_options = command_options
    self._parameters = parameters

  @property
  def program(self) -> str:
    """
      The name of the program.

      :return: The name of the program
    """
    return self._program

  @property
  def command_name(self) -> str | None:
    """
      The name of the command.

      :return: The name of the command
    """
    return self._command_name

  @property
  def global_options(self) -> Options:
    """
      The global options for the command line.

      :return: The global options
    """
    return self._global_options

  @property
  def command_options(self) -> Options:
    """
      The command options for the command line.

      :return: The command options
    """
    return self._command_options

  @property
  def parameters(self) -> set[str]:
    """
      The parameters for the command line.

      :return: The parameters
    """
    return self._parameters

def parse(args: list[str]) -> CommandLine:
  """
    Parse the command line arguments to create a CommandLine object.

    :param args: The command line arguments
    :return: A CommandLine object
    :raises: CommandLineError if the arguments are invalid
             AssertionError if there is bug in the code
  """
  try:
    assert len(args) > 0, "args must contain at least one argument (the name of the program)"
    program = args[0]
    global_options = Options(args[1:])
    command_name = args[global_options.end_index] if global_options.end_index < len(args) else None
    # will be an empty list if the index is out of range
    command_options = Options(args[global_options.end_index + 1:])
    parameters = set(args[command_options.end_index + 1:])
    return CommandLine(program, command_name, global_options, command_options, parameters)
  except ValueError as ex:
    raise CommandLineError(f"Invalid command line arguments: {ex}") from ex

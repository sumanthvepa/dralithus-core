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

class CommandLine:
  """
    Represents parsed command line arguments.

    The CommandLine class takes a list of command line arguments,
    parses them, and provides methods to access the parsed arguments.
  """
  def __init__(self,
      program: str,
      command_name: str,
      global_options: Options,
      command_options: Options) -> None:
    """
      Initialize the command line with arguments

      :param program: The name of the program
      :param command_name: The name of the command
      :param global_options: Any global options specified before the command
      :param command_options: Any command specific options
    """
    raise NotImplementedError("CommandLine class is not yet implemented.")

  @property
  def program(self) -> str:
    """
      The name of the program.

      :return: The name of the program
    """
    raise NotImplementedError("CommandLine class is not yet implemented.")

  @property
  def command_name(self) -> str:
    """
      The name of the command.

      :return: The name of the command
    """
    raise NotImplementedError("CommandLine class is not yet implemented.")

  @property
  def global_options(self) -> Options:
    """
      The global options for the command line.

      :return: The global options
    """
    raise NotImplementedError("CommandLine class is not yet implemented.")

  @property
  def command_options(self) -> Options:
    """
      The command options for the command line.

      :return: The command options
    """
    raise NotImplementedError("CommandLine class is not yet implemented.")

def parse(args: list[str]) -> CommandLine:
  """
    Parse the command line arguments to create a CommandLine object.

    :param args: The command line arguments
    :return: A CommandLine object
  """
  raise NotImplementedError("command_line.make() is not yet implemented.")

"""
  global_options.py: Define class GlobalOptions
"""
# -------------------------------------------------------------------
# global_options.py: Define class GlobalOptions
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


class GlobalOptions:
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

    :param requires_help: True if the help option was specified as a global option.
    :param verbosity: The verbosity level of the command.
  """
  def __init__(self, requires_help: bool, verbosity: int):
    """
      Initialize the global options with default values.

      :param requires_help: True if the help option was specified as a global option.
      :param verbosity: The verbosity level of the command.
    """
    self.requires_help = requires_help
    self.verbosity = verbosity

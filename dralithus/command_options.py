"""
  command_options.py: Define class CommandOptions
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

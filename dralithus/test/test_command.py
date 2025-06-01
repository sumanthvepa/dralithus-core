"""
  test_command.py: Unit tests for the dralithus.command module
"""
# -------------------------------------------------------------------
# test_command.py: Unit tests for the dralithus.command module
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

import unittest

from parameterized import parameterized

from dralithus.command import make
from dralithus.help_command import HelpCommand
from dralithus.test import CaseData, CaseExecutor2


def command_make_cases() -> list[tuple[str, CaseData]]:
  """
    Test cases for the make method of the Command class
  """
  # pylint: disable=line-too-long
  return [
    ('no_arguments', CaseData(args=[], expected=None, error=AssertionError)),
    ('program_name_only', CaseData(args=['drl'], expected=HelpCommand('drl', None, 'No command specified', 0), error=None)),
    ('program_name_and_help_command', CaseData(args=['drl', 'help'], expected=HelpCommand('drl', 'help', None, 0), error=None)),
    ('program_name_and_help_command_with_verbosity', CaseData(args=['drl', 'help', '-v'], expected=HelpCommand('drl', 'help', None, 1), error=None)),
    ('program_name_and_help_command_with_terminator', CaseData(args=['drl', 'help', '--', '-v'], expected=HelpCommand('drl', 'help', None, 0), error=None)),
    ('program_name_and_help_option', CaseData(args=['drl', '--help'], expected=HelpCommand('drl', None, None, 0), error=None)),
    ('program_name_and_help_option_with_verbosity', CaseData(args=['drl', '--help', '-v'], expected=HelpCommand('drl', None, None, 1), error=None)),
    ('program_name_and_help_option_with_terminator', CaseData(args=['drl', '--help', '--', '-v'], expected=HelpCommand('drl', None, None, 0), error=None)),
    ('program_name_and_help_option_with_command_and_terminator_with_verbosity', CaseData(args=['drl', '--help', 'deploy', '--', '-v'], expected=HelpCommand('drl', 'deploy',None, 0), error=None)),
    ('program_name_and_command_and_terminator_with_verbosity', CaseData(args=['drl', 'deploy', '--', '-v'], expected=HelpCommand('drl', 'deploy','No environments specified. Please specify at least one environment.', 0), error=None)),
    ('program_name_and_command_with_verbosity', CaseData(args=['drl', 'deploy', '-v'], expected=HelpCommand('drl', 'deploy','No environments specified. Please specify at least one environment.', 1), error=None)),
  ]


class TestCommand(unittest.TestCase, CaseExecutor2):
  """
    Unit tests for class Command
  """
  # pylint: disable=unused-argument
  # noinspection PyUnusedLocal
  @parameterized.expand(command_make_cases())
  def test_make(self, name: str, case: CaseData) -> None:
    """
      Test the make method of the Command class

      :param name: The name of the test case
      :param case: The test case
    """
    self.execute(make, case)

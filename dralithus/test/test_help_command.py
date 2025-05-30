"""
  test_help_command.py: Unit tests for the dralithus.help_command
  module
"""
# -------------------------------------------------------------------
# test_help_command.py: Unit tests for the dralithus.help_command
# module
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

from dralithus.help_command import HelpCommand, make, make_from_error
from dralithus.command_line.options import Options
from dralithus.errors import CommandLineError
from dralithus.test import CaseData, CaseExecutor2


def make_cases() -> list[tuple[str, CaseData]]:
  """
    A list of unittest cases for HelpCommand.make
    :return:
  """
  # pylint: disable=line-too-long
  return [
    ('help_command', CaseData(args=('drl', None, Options([]), Options([])), expected=HelpCommand('drl', None, None, 0), error=None)),
    ('help_command_global_verbosity', CaseData(args=('drl', None, Options(['-v=1']), Options([])), expected=HelpCommand('drl', None, None, 1), error=None)),
    ('help_command_command_verbosity', CaseData(args=('drl', None, Options([]), Options(['-v=1'])), expected=HelpCommand('drl', None, None, 1), error=None)),
    ('help_command_global_and_command_verbosity', CaseData(args=('drl', None, Options(['-v=1']), Options(['-v=1'])), expected=HelpCommand('drl', None, None, 2), error=None)),
    ('help_command_global_and_command_verbosity_more_than_3', CaseData(args=('drl', None, Options(['-v=2']), Options(['-v=2'])), expected=HelpCommand('drl', None, None, 3), error=None)),
    ('help_global_option', CaseData(args=('drl', None, Options(['--help']), Options([])), expected=HelpCommand('drl', None, None, 0), error=None)),
    ('help_global_option_global_verbosity', CaseData(args=('drl', None, Options(['-v', '--help']), Options([])), expected=HelpCommand('drl', None, None, 1), error=None)),
    ('help_global_option_command_verbosity', CaseData(args=('drl', None, Options(['--help']), Options(['-v', ])), expected=HelpCommand('drl', None, None, 1), error=None)),
    ('help_global_option_global_and_command_verbosity', CaseData(args=('drl', None, Options(['--help', '-v']), Options(['-v=1'])), expected=HelpCommand('drl', None, None, 2), error=None)),
    ('help_command_option', CaseData(args=('drl', None, Options([]), Options(['--help'])), expected=HelpCommand('drl', None, None, 0), error=None)),
    ('help_command_option_global_verbosity', CaseData(args=('drl', None, Options(['-v']), Options(['--help'])), expected=HelpCommand('drl', None, None, 1), error=None)),
    ('help_command_option_command_verbosity', CaseData(args=('drl', None, Options([]), Options(['--help', '-v', ])), expected=HelpCommand('drl', None, None, 1), error=None)),
    ('help_command_option_global_and_command_verbosity', CaseData(args=('drl', None, Options(['-v']), Options(['-v=1', '--help'])), expected=HelpCommand('drl', None, None, 2), error=None)),
    ('help_command_command_needing_help', CaseData(args=('drl', 'deploy', Options([]), Options([])), expected=HelpCommand('drl', 'deploy', None, 0), error=None)),
  ]


def make_error_cases() -> list[tuple[str, CaseData]]:
  """
    A list of unittest cases for HelpCommand.make_from_error
    :return:
  """
  # pylint: disable=line-too-long
  return [
    ('help_command_from_error', CaseData(args=(CommandLineError('drl', 'No command specified'),), expected=HelpCommand('drl', None, CommandLineError('drl', 'No command specified'), 0), error=None)),
  ]

class TestHelpCommand(unittest.TestCase, CaseExecutor2):
  """
  Unit tests for the HelpCommand class.
  """
  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  @parameterized.expand(make_cases())
  def test_make(self, name: str, case: CaseData) -> None:
    """
    Test the make method of the help_command module.
    """
    self.execute(lambda params: make(*params), case)

  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  @parameterized.expand(make_error_cases())
  def test_make_from_error(self, name: str, case: CaseData) -> None:
    """
    Test the make_from_error method of the help_command module.
    """
    self.execute(lambda params: make_from_error(*params), case)
    # command = make_from_error(CommandLineError('drl', 'No command specified'))
    #
    # self.assertIsInstance(command, HelpCommand)
    # self.assertEqual('help', command.name)
    # self.assertIsNone(command.command_needing_help)
    # self.assertIsInstance(command.error, CommandLineError)
    # self.assertEqual(0, command.verbosity)

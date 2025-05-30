"""
  test_command_line.py: Unit tests for the command_line module
"""
# -------------------------------------------------------------------
# test_command_line.py: Unit tests for the command_line module
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

from dralithus.command_line.command_line import parse, CommandLine
from dralithus.command_line.options import Options

from dralithus.test import CaseData, CaseExecutor2


def all_options() -> list[list[str]]:
  """
    A list of all possible options
    :return: A complete list of options
  """
  return [
    [], ['-h'], ['--help'],
    ['-v'], ['-v2'], ['-v=2'], ['-v', '2'],
    ['--verbose'], ['--verbose=2'], ['--verbose', '2'],
    ['--verbosity'], ['--verbosity=2'], ['--verbosity', '2'],
    ['-e=local'], ['-e', 'local'], ['-e=local,test'], ['-e', 'local,test'],
    ['--env=local'], ['--env', 'local'], ['--env=local,test'],
    ['--env', 'local,test'],
    ['--environment=local'], ['--environment', 'local'],
    ['--environment=local,test'], ['--environment', 'local,test']
  ]


def parse_correct_cases() -> list[tuple[str, CaseData]]:
  """
    Test cases for the CommandLine class
  """
  # pylint: disable=too-many-locals
  cases = [
    ('parse_case_0', CaseData(args=[], expected=None, error=AssertionError))
  ]
  programs = [['drl']]
  global_opts = all_options()
  command_names = [['help'], ['deploy']]
  command_opts = all_options()
  parameters = [set(), {'sample'}, {'sample', 'echo'}]

  case_number = 1
  for program in programs:
    for global_opt in global_opts:
      for command_name in command_names:
        for command_opt in command_opts:
          for parameter in parameters:
            name = f'parse_case_{case_number}'
            args = program + global_opt + command_name + command_opt + list(parameter)
            cmdline = CommandLine(
              program[0],
              command_name[0],
              Options(global_opt),
              Options(command_opt),
              parameter)
            case = (name, CaseData(args, expected=cmdline, error=None))
            cases.append(case)
            case_number += 1
  return cases

def parse_incorrect_cases() -> list[tuple[str, CaseData]]:
  """
    Test cases for the CommandLine class that are expected to fail
  """
  return [
    ('parse_incorrect_case_0', CaseData(args=[], expected=None, error=AssertionError)),
  ]

def parse_cases() -> list[tuple[str, CaseData]]:
  """
    Combine the correct and incorrect cases for the parse function
    :return: A list of test cases for the parse function
  """
  return parse_correct_cases() + parse_incorrect_cases()


class TestCommandLine(unittest.TestCase, CaseExecutor2):
  """
    Unit tests for the CommandLine class and the parse function
  """
  def __init__(self, *args, **kwargs):
    """
      Initialize the test case.
    """
    unittest.TestCase.__init__(self, *args, **kwargs)
    CaseExecutor2.__init__(self)

  # pylint: disable=unused-argument
  # noinspection PyUnusedLocal
  @parameterized.expand(parse_cases())
  def test_parse(self, name: str, case: CaseData) -> None:
    """
      Test the constructor of the CommandLine class
    """
    self.execute(parse, case)

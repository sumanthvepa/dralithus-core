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

from dralithus.command_line.command_line import parse

from dralithus.test import CaseData, CaseExecutor


def parse_cases() -> list[tuple[str, CaseData]]:
  """
    Test cases for the CommandLine class
  """
  return [
    ('no_arguments', CaseData(args=[], expected=None, error=AssertionError)),
  ]


class TestCommandLine(unittest.TestCase, CaseExecutor):
  """
    Unit tests for the CommandLine class and the parse function
  """
  def __init__(self, *args, **kwargs):
    """
      Initialize the test case.
    """
    unittest.TestCase.__init__(self, *args, **kwargs)
    CaseExecutor.__init__(self, parse)

  # pylint: disable=unused-argument
  # noinspection PyUnusedLocal
  @parameterized.expand(parse_cases())
  def test_parse(self, name: str, case: CaseData) -> None:
    """
      Test the constructor of the CommandLine class
    """
    self.execute(case)

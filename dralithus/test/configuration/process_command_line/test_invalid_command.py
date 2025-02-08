# -*- coding: utf-8 -*-
"""
  test_invalid_command.py: Unit tests to test an invalid command
  without any help flags on the command raises a command line error.
"""
from parameterized import parameterized

from dralithus.test.configuration.process_command_line import (
  Args,
  TestCaseData,
  CommandLineTestCase,
  all_test_cases,
  print_cases)

from dralithus.configuration import CommandLineError


def no_parameters_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with an invalid command
    and no parameters.
    i.e. drl invalid
  """
  args = Args(
    program='drl',
    global_options=[],
    command='invalid',
    command_options=[],
    parameters=[])
  return [(TestCaseData(
    args=args,
    expected=None,
    error={'error_type': CommandLineError, 'verbosity': 0}),)]


def invalid_base_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with an invalid command
    and various ways to specify the environment and applications.
  """
  cases: list[tuple[TestCaseData]] = []
  cases += no_parameters_test_cases()
  return cases


class TestInvalidCommand(CommandLineTestCase):
  """
    Test that an invalid command is handled correctly by the
    process_command_line function.
  """
  @parameterized.expand(all_test_cases(invalid_base_test_cases()))
  def test_case(self, case: TestCaseData) -> None:
    """ Execute all the test cases """
    self.execute_test(case)


if __name__ == '__main__':
  print_cases(all_test_cases(invalid_base_test_cases()))

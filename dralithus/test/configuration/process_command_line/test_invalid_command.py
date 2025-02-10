# -*- coding: utf-8 -*-
"""
  test_invalid_command.py: Unit tests to test an invalid command
  without any help flags on the command raises a command line error.
"""
from parameterized import parameterized

from dralithus.test.configuration.process_command_line import (
  Args,
  ErrorDict,
  TestCaseData,
  CommandLineTestCase,
  make_args_list,
  make_test_cases,
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


def global_option_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl invalid with some
    meaningless global options.
  :return:
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[
      ['--environment=env1'],
      ['--environment', 'env1'],
      ['-e', 'env2']],
    command_list=['invalid', '4number'],
    command_options_list=[[]],
    parameters_list=[[]])
  error: ErrorDict = {'error_type': CommandLineError, 'verbosity': 0}
  return make_test_cases(args_list, None, error)


def invalid_base_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with an invalid command
    and various ways to specify the environment and applications.
  """
  cases: list[tuple[TestCaseData]] = []
  cases += no_parameters_test_cases()
  cases += global_option_test_cases()
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

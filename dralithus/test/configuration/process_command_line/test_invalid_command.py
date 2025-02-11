# -*- coding: utf-8 -*-
"""
  test_invalid_command.py: Unit tests to test an invalid command
  without any help flags on the command raises a command line error.
"""
from parameterized import parameterized

from dralithus.test.configuration.process_command_line import (
  ErrorDict,
  TestCaseData,
  CommandLineTestCase,
  make_args_list,
  make_test_cases,
  all_test_cases,
  print_cases)

from dralithus.configuration import CommandLineError

def invalid_command_base_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with an invalid command and
    various ways to specify the environment and applications.

    :return: A list of test cases where an invalid command is specified.
"""
  args_list = make_args_list(
    program='drl',
    global_options_list=[
      [],
      ['--environment=env1'],
      ['--environment', 'env1'],
      ['-e', 'env2']],
    command_list=['invalid', '4number'],
    command_options_list=[
      [],
      ['--environment=env1'],
      ['--environment', 'env1'],
      ['-e', 'env2']],
    parameters_list=[[]])
  error: ErrorDict = {'error_type': CommandLineError, 'verbosity': 0}
  return make_test_cases(args_list, None, error)


class TestInvalidCommand(CommandLineTestCase):
  """
    Test that an invalid command is handled correctly by the
    process_command_line function.
  """
  @parameterized.expand(all_test_cases(invalid_command_base_test_cases()))
  def test_case(self, case: TestCaseData) -> None:
    """ Execute all the test cases """
    self.execute_test(case)


if __name__ == '__main__':
  # print_cases(invalid_base_test_cases())
  print_cases(all_test_cases(invalid_command_base_test_cases()))

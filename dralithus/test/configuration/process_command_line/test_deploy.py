# -*- coding: utf-8 -*-
"""
  test_deploy.py: Unit tests to test the 'deploy' command and its
  options on the command line interface (process_command_line) for the
  dralithus application.
"""
from parameterized import parameterized

from dralithus.configuration import Operation

from dralithus.test.configuration.process_command_line import (
  TestCaseData,
  CommandLineTestCase,
  make_args_list,
  make_test_cases,
  all_test_cases,
  print_cases)


def deploy_valid_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the 'deploy' command and
    various ways to CORRECTLY specify the environment and applications.

    :return: A list of test cases where the 'deploy' command is specified and
    the environment and applications are specified correctly.
"""
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[
      ['--environment=local'],
      ['--environment', 'local'],
      ['-elocal'],
      ['-e', 'local']],
    parameters_list=[[]])
  expected: Operation = {
    'command': 'deploy',
    'about': None,
    'environments': ['local'],
    'applications': ['sample'],
    'verbosity': 0}
  return make_test_cases(args_list, expected, None)


def deploy_base_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the 'deploy' command
    and various ways to specify the environment and applications.

  :return: A list of test cases where the 'deploy' command is specified.
  """
  # TODO: Complete this implementation
  cases: list[tuple[TestCaseData]] = []
  cases += deploy_valid_test_cases()
  return cases


class TestDeploy(CommandLineTestCase):
  """
    Test that the 'deploy' command is handled correctly by the
    process_command_line function.
  """
  @parameterized.expand(all_test_cases(deploy_base_test_cases()))
  def test_case(self, case: TestCaseData) -> None:
    """ Execute all the test cases """
    self.execute_test(case)


if __name__ == '__main__':
  # print_cases(deploy_test_cases())
  print_cases(all_test_cases(deploy_base_test_cases()))

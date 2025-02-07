# -*- coding: utf-8 -*-
"""
  test_deploy.py: Unit tests to test the 'deploy' command and its
  options on the command line interface (process_command_line) for the
  dralithus application.
"""
from parameterized import parameterized

from dralithus.test.configuration.process_command_line import (
  Args,
  TestCaseData,
  CommandLineTestCase,
  all_test_cases,
  print_cases)


def deploy_base_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the 'deploy' command
    and various ways to specify the environment and applications.
  """
  # TODO: Complete this implementation
  # This just one test case for now
  cases: list[tuple[TestCaseData]] = []
  case: TestCaseData = {
    'args': Args(
      program='drl',
      global_options=[],
      command='deploy',
      command_options=["--environment='local'"],
      parameters=['sample']),
    'expected': {
      'command': 'deploy',
      'about': None,
      'applications': ['sample'],
      'environments': ['local'],
      'verbosity': 0},
    'error': None
  }
  cases.append((case,))
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
  print_cases(all_test_cases(deploy_base_test_cases()))

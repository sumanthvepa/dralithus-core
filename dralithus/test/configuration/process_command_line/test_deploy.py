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

from dralithus.configuration import CommandLineError


def no_parameters_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the 'deploy' command
    and no parameters.
  """
  args = Args(program='drl', global_options=[], command='deploy', command_options=[], parameters=[])
  error =  {'error_type': CommandLineError, 'verbosity': 0}
  return [(TestCaseData(args=args, expected=None, error=error),)]

def deploy_base_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the 'deploy' command
    and various ways to specify the environment and applications.
  """
  # TODO: Complete this implementation
  cases: list[tuple[TestCaseData]] = []
  cases += no_parameters_test_cases()
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

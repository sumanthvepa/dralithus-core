# -*- coding: utf-8 -*-
"""
  test_deploy.py: Unit tests to test the 'deploy' command and its
  options on the command line interface (process_command_line) for the
  dralithus application.
"""
from parameterized import parameterized

from dralithus.configuration import Operation, CommandLineError

from dralithus.test.configuration.process_command_line import (
  ErrorDict,
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
      ['--env=local'],
      ['--env', 'local'],
      ['-elocal'],
      ['-e', 'local']],
    parameters_list=[['sample']])
  expected: Operation = {
    'command': 'deploy',
    'about': None,
    'environments': ['local'],
    'applications': ['sample'],
    'verbosity': 0}
  return make_test_cases(args_list, expected, None)


def deploy_valid_multi_environment_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the 'deploy' command and
    various ways to CORRECTLY specify multiple environments and applications.

    :return: A list of test cases where the 'deploy' command is specified and
    the environment and applications are specified correctly.
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[
      ['--environment=local', '--environment=dev'],
      ['--environment', 'local', '--environment', 'dev'],
      ['--env=local', '--env=dev'],
      ['--env', 'local', '--env', 'dev'],
      ['-elocal', '-edev'],
      ['-e', 'local', '-e', 'dev'],
      ['--environment=local,dev'],
      ['--environment', 'local,dev'],
      ['--env=local,dev'],
      ['--env', 'local,dev'],
      ['-elocal,dev'],
      ['-e', 'local,dev']],
    parameters_list=[['sample']])
  expected: Operation = {
    'command': 'deploy',
    'about': None,
    'environments': ['local', 'dev'],
    'applications': ['sample'],
    'verbosity': 0}
  return make_test_cases(args_list, expected, None)


def deploy_valid_multi_application_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the 'deploy' command and
    various ways to CORRECTLY specify multiple applications.

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
      ['--env=local'],
      ['--env', 'local'],
      ['-elocal'],
      ['-e', 'local']],
    parameters_list=[['sample', 'echo']])
  expected: Operation = {
    'command': 'deploy',
    'about': None,
    'environments': ['local'],
    'applications': ['sample', 'echo'],
    'verbosity': 0}
  return make_test_cases(args_list, expected, None)


def deploy_multi_environment_multi_application_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the 'deploy' command and
    various ways to CORRECTLY specify multiple environments and applications.

    :return: A list of test cases where the 'deploy' command is specified and
    the environment and applications are specified correctly.
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[
      ['--environment=local', '--environment=dev'],
      ['--environment', 'local', '--environment', 'dev'],
      ['--env=local', '--env=dev'],
      ['--env', 'local', '--env', 'dev'],
      ['-elocal', '-edev'],
      ['-e', 'local', '-e', 'dev'],
      ['--environment=local,dev'],
      ['--environment', 'local,dev'],
      ['--env=local,dev'],
      ['--env', 'local,dev'],
      ['-elocal,dev'],
      ['-e', 'local,dev']],
    parameters_list=[['sample', 'echo']])
  expected: Operation = {
    'command': 'deploy',
    'about': None,
    'environments': ['local', 'dev'],
    'applications': ['sample', 'echo'],
    'verbosity': 0}
  return make_test_cases(args_list, expected, None)


def deploy_missing_application_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases where the application name is missing
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[
      ['--environment=local'],
      ['--environment', 'local'],
      ['--env=local'],
      ['--env', 'local'],
      ['-elocal'],
      ['-e', 'local']],
    parameters_list=[[]])
  error: ErrorDict = {'error_type': CommandLineError, 'verbosity': 0 }
  return make_test_cases(args_list, None, error)


def deploy_missing_environment_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases where the environment name is missing
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[[]],
    parameters_list=[['sample']])
  error: ErrorDict = {'error_type': CommandLineError, 'verbosity': 0 }
  return make_test_cases(args_list, None, error)


def deploy_missing_environment_and_application_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases where the environment and application names are missing
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[[]],
    parameters_list=[[]])
  error: ErrorDict = {'error_type': CommandLineError, 'verbosity': 0 }
  return make_test_cases(args_list, None, error)


def deploy_invalid_environment_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases where the environment name is invalid
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[
      ['--environment=garbage'],
      ['--environment', 'garbage'],
      ['--env=garbage'],
      ['--env', 'garbage'],
      ['-egarbage'],
      ['-e', 'garbage']],
    parameters_list=[['sample']])
  error: ErrorDict = {'error_type': CommandLineError, 'verbosity': 0 }
  return make_test_cases(args_list, None, error)


def deploy_invalid_application_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases where the application name is invalid
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[
      ['--environment=local'],
      ['--environment', 'local'],
      ['--env=local'],
      ['--env', 'local'],
      ['-elocal'],
      ['-e', 'local']],
    parameters_list=[['garbage']])
  error: ErrorDict = {'error_type': CommandLineError, 'verbosity': 0 }
  return make_test_cases(args_list, None, error)


def deploy_invalid_environment_and_application_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases where the environment and application names are invalid
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[
      ['--environment=garbage'],
      ['--environment', 'garbage'],
      ['--env=garbage'],
      ['--env', 'garbage'],
      ['-egarbage'],
      ['-e', 'garbage']],
    parameters_list=[['garbage']])
  error: ErrorDict = {'error_type': CommandLineError, 'verbosity': 0 }
  return make_test_cases(args_list, None, error)


def deploy_invalid_multi_environment_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases where multiple environments are specified, but one of them is
    invalid.
  :return:
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[
      ['--environment=local,garbage'],
      ['--environment', 'local,garbage'],
      ['--env=local,garbage'],
      ['--env', 'local,garbage'],
      ['-elocal,garbage'],
      ['-e', 'local,garbage']],
    parameters_list=[['sample']])
  error: ErrorDict = {'error_type': CommandLineError, 'verbosity': 0 }
  return make_test_cases(args_list, None, error)


def test_invalid_multi_application_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases where multiple applications are specified, but one of them is
    invalid.
  :return:
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[
      ['--environment=local'],
      ['--environment', 'local'],
      ['--env=local'],
      ['--env', 'local'],
      ['-elocal'],
      ['-e', 'local']],
    parameters_list=[['sample', 'garbage'], ['garbage', 'sample']])
  error: ErrorDict = {'error_type': CommandLineError, 'verbosity': 0 }
  return make_test_cases(args_list, None, error)

def test_invalid_multi_environment_multi_application_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases where multiple environments and applications are specified, but one of them is
    invalid.
  :return:
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[
      ['--environment=local,garbage'],
      ['--environment', 'garbage,local'],
      ['--environment', 'local,garbage'],
      ['--environment', 'garbage,local'],
      ['--env=local,garbage'],
      ['--env=garbage,local'],
      ['--env', 'local,garbage'],
      ['--env', 'garbage,local'],
      ['-elocal,garbage'],
      ['-egarbage,local'],
      ['-e', 'local,garbage'],
      ['-e', 'garbage,local']],
    parameters_list=[['sample', 'garbage'], ['garbage', 'sample']])
  error: ErrorDict = {'error_type': CommandLineError, 'verbosity': 0 }
  return make_test_cases(args_list, None, error)


def deploy_base_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the 'deploy' command
    and various ways to specify the environment and applications.

  :return: A list of test cases where the 'deploy' command is specified.
  """
  cases: list[tuple[TestCaseData]] = []
  cases += deploy_valid_test_cases()
  cases += deploy_valid_multi_environment_test_cases()
  cases += deploy_valid_multi_application_test_cases()
  cases += deploy_missing_application_test_cases()
  cases += deploy_missing_environment_test_cases()
  cases += deploy_missing_environment_and_application_test_cases()
  cases += deploy_invalid_environment_test_cases()
  cases += deploy_invalid_application_test_cases()
  cases += deploy_invalid_environment_and_application_test_cases()
  cases += deploy_invalid_multi_environment_test_cases()
  cases += test_invalid_multi_application_test_cases()
  cases += test_invalid_multi_environment_multi_application_test_cases()
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
  # print_cases(deploy_base_test_cases())
  print_cases(all_test_cases(deploy_base_test_cases()))

"""
  test_environment_option.py: Unit tests for class EnvironmentOption
"""
import copy
import unittest
from typing import Any

from parameterized import parameterized

from dralithus.command_line.environment_option import EnvironmentOption
from dralithus.test import CaseData, CaseExecutor2


def is_option_cases() -> list[tuple[str, CaseData]]:
  """
    Generate test cases for the is_option method of EnvironmentOption class.
    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  return [
    ('short_no_value', CaseData(args=['-e', None], expected=False, error=None)),
    ('long_no_value', CaseData(args=['--env', None], expected=False, error=None)),
    ('long2_no_value', CaseData(args=['--environment', None], expected=False, error=None)),
    ('short_value_equal', CaseData(args=['-e=local', None], expected=True, error=None)),
    ('long_value_equal', CaseData(args=['--env=local', None], expected=True, error=None)),
    ('long2_value_equal', CaseData(args=['--environment=local', None], expected=True, error=None)),
    ('short_multi_value', CaseData(args=['-e=local,test', None], expected=True, error=None)),
    ('long_multi_value', CaseData(args=['--env=local,test', None], expected=True, error=None)),
    ('long2_multi_value', CaseData(args=['--environment=local,test', None], expected=True, error=None)),
    ('short_invalid_value', CaseData(args=['-e=invalid', None], expected=False, error=None)),
    ('long_invalid_value', CaseData(args=['--env=invalid', None], expected=False, error=None)),
    ('long2_invalid_value', CaseData(args=['--environment=invalid', None], expected=False, error=None)),
    ('short_one_invalid_multi_value', CaseData(args=['-e=local,invalid', None], expected=False, error=None)),
    ('short_one_invalid_multi_value_reversed', CaseData(args=['-e=invalid,local', None], expected=False, error=None)),
    ('long_one_invalid_multi_value', CaseData(args=['--env=local,invalid', None], expected=False, error=None)),
    ('long_one_invalid_multi_value_reversed', CaseData(args=['--env=invalid,local', None], expected=False, error=None)),
    ('long2_one_invalid_multi_value', CaseData(args=['--environment=local,invalid', None], expected=False, error=None)),
    ('long2_one_invalid_multi_value_reversed', CaseData(args=['--environment=invalid,local', None], expected=False, error=None)),
    ('wrong_short_option_no_value', CaseData(args=['-h', None], expected=False, error=None)),
    ('wrong_short_option_value', CaseData(args=['-h=True', None], expected=False, error=None)),
    ('wrong_long_option_no_value', CaseData(args=['--verbosity', None], expected=False, error=None)),
    ('wrong_long_option_value', CaseData(args=['--verbosity=True', None], expected=False, error=None)),
    ('not_option', CaseData(args=['parameter', None], expected=False, error=None)),
  ]


def add_to_cases() -> list[tuple[str, CaseData]]:
  """
    Generate test cases for the add_to method of EnvironmentOption class.

    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  return [
    ('add_local_to_empty_dict', CaseData(args=[EnvironmentOption('e', {'local'}), {}], expected={'environments': {'local'}}, error=None)),
    ('add_local_to_non_empty_dict', CaseData(args=[EnvironmentOption('e', {'local'}), {'environments': {'test'}}], expected={'environments': {'test', 'local'}}, error=None)),
    ('add_duplicate_to_non_empty_dict', CaseData(args=[EnvironmentOption('e', {'local'}), {'environments': {'test', 'local'}}], expected={'environments': {'test', 'local'}}, error=None))
  ]


def make_cases() -> list[tuple[str, CaseData]]:
  """
    Generate test cases for the EnvironmentOption class.

    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  return [
    ('short_equal_value_no_next_arg', CaseData(args=['-e=local', None], expected=(EnvironmentOption('e', {'local'}), False), error=None)),
    ('short_equal_multi_value_no_next_arg', CaseData(args=['-e=local,test', None], expected=(EnvironmentOption('e', {'local', 'test'}), False), error=None)),
    ('long_equal_value_no_next_arg', CaseData(args=['--env=local', None], expected=(EnvironmentOption('env', {'local'}), False), error=None)),
    ('long_equal_multi_value_no_next_arg', CaseData(args=['--env=local,test', None], expected=(EnvironmentOption('env', {'local', 'test'}), False), error=None)),
    ('long2_equal_value_no_next_arg', CaseData(args=['--environment=local', None], expected=(EnvironmentOption('environment', {'local'}), False), error=None)),
    ('long2_equal_multi_value_no_next_arg', CaseData(args=['--environment=local,test', None], expected=(EnvironmentOption('environment', {'local', 'test'}), False), error=None)),
    ('short_equal_value_next_arg', CaseData(args=['-e=local', 'parameter'], expected=(EnvironmentOption('e', {'local'}), False), error=None)),
    ('short_equal_multi_value_next_arg', CaseData(args=['-e=local,test', 'parameter'], expected=(EnvironmentOption('e', {'local', 'test'}), False), error=None)),
    ('long_equal_value_next_arg', CaseData(args=['--env=local', 'parameter'], expected=(EnvironmentOption('env', {'local'}), False), error=None)),
    ('long_equal_multi_value_next_arg', CaseData(args=['--env=local,test', 'parameter'], expected=(EnvironmentOption('env', {'local', 'test'}), False), error=None)),
    ('long2_equal_value_next_arg', CaseData(args=['--environment=local', 'parameter'], expected=(EnvironmentOption('environment', {'local'}), False), error=None)),
    ('long2_equal_multi_value_next_arg', CaseData(args=['--environment=local,test', 'parameter'], expected=(EnvironmentOption('environment', {'local', 'test'}), False), error=None)),
    ('short_next_arg_value', CaseData(args=['-e', 'local'], expected=(EnvironmentOption('e', {'local'}), True), error=None)),
    ('short_next_arg_multi_value', CaseData(args=['-e', 'local,test'], expected=(EnvironmentOption('e', {'local', 'test'}), True), error=None)),
    ('long_next_arg_value', CaseData(args=['--env', 'local'], expected=(EnvironmentOption('env', {'local'}), True), error=None)),
    ('long_next_arg_multi_value', CaseData(args=['--env', 'local,test'], expected=(EnvironmentOption('env', {'local', 'test'}), True), error=None)),
    ('long2_next_arg_value', CaseData(args=['--environment', 'local'], expected=(EnvironmentOption('environment', {'local'}), True), error=None)),
    ('long2_next_arg_multi_value', CaseData(args=['--environment', 'local,test'], expected=(EnvironmentOption('environment', {'local', 'test'}), True), error=None)),
    ('short_bad_value_equal', CaseData(args=['-e=bad_value', None], expected=None, error=AssertionError)),
    ('short_bad_value2_equal', CaseData(args=['-e=True', None], expected=None, error=AssertionError)),
    ('short_bad_value3_equal', CaseData(args=['-e=-2', None], expected=None, error=AssertionError)),
    ('long_bad_value_equal', CaseData(args=['--env=bad_value', None], expected=None, error=AssertionError)),
    ('long_bad_value2_equal', CaseData(args=['--env=True', None], expected=None, error=AssertionError)),
    ('long_bad_value3_equal', CaseData(args=['--env=-2', None], expected=None, error=AssertionError)),
    ('long2_bad_value_equal', CaseData(args=['--environment=bad_value', None], expected=None, error=AssertionError)),
    ('long2_bad_value2_equal', CaseData(args=['--environment=True', None], expected=None, error=AssertionError)),
    ('long2_bad_value3_equal', CaseData(args=['--environment=-2', None], expected=None, error=AssertionError)),
    ('short_next_arg_bad_value', CaseData(args=['-e', 'bad_value'], expected=None, error=AssertionError)),
    ('short_next_arg_bad_value2', CaseData(args=['-e', 'True'], expected=None, error=AssertionError)),
    ('short_next_arg_bad_value3', CaseData(args=['-e', '-2'], expected=None, error=AssertionError)),
    ('long_next_arg_bad_value', CaseData(args=['--env', 'bad_value'], expected=None, error=AssertionError)),
    ('long_next_arg_bad_value2', CaseData(args=['--env', 'True'], expected=None, error=AssertionError)),
    ('long_next_arg_bad_value3', CaseData(args=['--env', '-2'], expected=None, error=AssertionError)),
    ('long2_next_arg_bad_value', CaseData(args=['--environment', 'bad_value'], expected=None, error=AssertionError)),
    ('long2_next_arg_bad_value2', CaseData(args=['--environment', 'True'], expected=None, error=AssertionError)),
    ('long2_next_arg_bad_value3', CaseData(args=['--environment', '-2'], expected=None, error=AssertionError)),
    ('wrong_short_option_no_value', CaseData(args=['-h', None], expected=None, error=AssertionError)),
    ('wrong_short_option_value', CaseData(args=['-h=True', None], expected=None, error=AssertionError)),
    ('wrong_long_option_no_value', CaseData(args=['--verbosity', None], expected=None, error=AssertionError)),
    ('wrong_long_option_value', CaseData(args=['--verbosity=True', None], expected=None, error=AssertionError)),
    ('wrong_short_option_next_arg', CaseData(args=['-v', '1'], expected=None, error=AssertionError)),
    ('wrong_long_option_next_arg', CaseData(args=['--verbosity', '1'], expected=None, error=AssertionError)),
    ('wrong_no_option', CaseData(args=['parameter', None], expected=None, error=AssertionError)),
    ('short_invalid_environment_equal', CaseData(args=['-e=invalid', None], expected=None, error=AssertionError)),
    ('long_invalid_environment_equal', CaseData(args=['--env=invalid', None], expected=None, error=AssertionError)),
    ('long2_invalid_environment_equal', CaseData(args=['--environment=invalid', None], expected=None, error=AssertionError)),
    ('short_one_invalid_multi_environment_equal', CaseData(args=['-e=local,invalid', None], expected=None, error=AssertionError)),
    ('short_one_invalid_multi_environment_equal_reversed', CaseData(args=['-e=invalid,local', None], expected=None, error=AssertionError)),
    ('long_one_invalid_multi_environment_equal', CaseData(args=['--env=local,invalid', None], expected=None, error=AssertionError)),
    ('long_one_invalid_multi_environment_equal_reversed', CaseData(args=['--env=invalid,local', None], expected=None, error=AssertionError))
  ]


class TestEnvironmentOption(unittest.TestCase, CaseExecutor2):
  """
    Unit tests for class EnvironmentOption
  """
  def test_value(self) -> None:
    """
      Test the value of the environment option.
    """
    expected_environment = {'local'}
    option = EnvironmentOption('environment', expected_environment)
    self.assertSetEqual(expected_environment, option.value)

  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  @parameterized.expand(is_option_cases())
  def test_is_option(self, name: str, case: CaseData) -> None:
    """
      Test the is_option method with parameterized inputs.
      :param name: The name of the test case
      :param case: The test case
    """
    self.execute(
      lambda params: EnvironmentOption.is_option(params[0], params[1]), case)

  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  @parameterized.expand(add_to_cases())
  def test_add_to(self, name: str, case: CaseData) -> None:
    """
      Test the add_to method with parameterized inputs.
      :param name: The name of the test case
      :param case: The test case
    """
    # noinspection SpellCheckingInspection
    def wrapper(params: list[Any]) -> dict[str, None | bool | int | str | set[str]]:
      """
        Wrapper function around VerbosityOption.add_to() method
        to match its signature with that wichh the execute method
        is expecting.
      """
      dct= copy.deepcopy(params[1])
      params[0].add_to(dct)
      return dct
    self.execute(wrapper, case)

  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  @parameterized.expand(make_cases())
  def test_make(self, name: str, case: CaseData) -> None:
    """
      Test the make method with parameterized inputs
    """
    self.execute(lambda params: EnvironmentOption.make(params[0], params[1]), case)

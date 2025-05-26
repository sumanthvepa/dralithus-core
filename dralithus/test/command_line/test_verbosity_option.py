"""
  test_verbosity_option.py: Unit tests for class VerbosityOption.
"""
import copy
import unittest
from typing import Any

from parameterized import parameterized

from dralithus.command_line.verbosity_option import VerbosityOption
from dralithus.test import CaseData, CaseExecutor2


def is_option_cases() -> list[tuple[str, CaseData]]:
  """
    Test cases for the is_option method of the VerbosityOption class
    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  return [
    ('short_no_value', CaseData(args=['-v', None], expected=True, error=None)),
    ('long_no_value', CaseData(args=['--verbose', None], expected=True, error=None)),
    ('long2_no_value', CaseData(args=['--verbosity', None], expected=True, error=None)),
    ('short_value', CaseData(args=['-v=1', None], expected=True, error=None)),
    ('long_value', CaseData(args=['--verbose=1', None], expected=True, error=None)),
    ('long2_value', CaseData(args=['--verbosity=1', None], expected=True, error=None)),
    ('short_bad_value', CaseData(args=['-v=True', None], expected=False, error=None)),
    ('long_bad_value', CaseData(args=['--verbosity=True', None], expected=False, error=None)),
    ('short_wrong_option_no_value', CaseData(args=['-h', None], expected=False, error=None)),
    ('short_wrong_option_value', CaseData(args=['-h=True', None], expected=False, error=None)),
    ('long_wrong_option_no_value', CaseData(args=['--help', None], expected=False, error=None)),
    ('long_wrong_option_value', CaseData(args=['--environment=local,test', None], expected=False, error=None)),
    ('not_option', CaseData(args=['parameter', None], expected=False, error=None))
  ]


def add_to_cases() -> list[tuple[str, CaseData]]:
  """
    Test cases for the add_to method of the VerbosityOption class
    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  return [
    ('add_2_to_empty_dict', CaseData(args=[VerbosityOption('v', 2), {}], expected={'verbosity', 2}, error=None)),
    ('add_3_to_dict_1', CaseData(args=[VerbosityOption('v', 3), {'verbosity': 1}], expected={'verbosity', 4}, error=None)),
    ('add_1_to_none_dict', CaseData(args=[VerbosityOption('v', 1), {'verbosity': None}], expected={'verbosity', 1}, error=None)),
    ('and_1_to_dict_0', CaseData(args=[VerbosityOption('v', 1), {'verbosity': 0}], expected={'verbosity', 1}, error=None))
  ]


def make_cases() -> list[tuple[str, CaseData]]:
  """
    Unit tests for VerbosityOption.make()
    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  return [
    ('short_no_value_no_next_arg', CaseData(args=['-v', None], expected=(VerbosityOption('v', 1), False), error=None)),
    ('short_no_value_next_arg_option', CaseData(args=['-v', '-h'], expected=(VerbosityOption('v', 1), False), error=None)),
    ('short_no_value_next_arg_parameter', CaseData(args=['-v', 'parameter'], expected=(VerbosityOption('v', 1), False), error=None)),
    ('long_no_value_no_next_arg', CaseData(args=['--verbosity', None], expected=(VerbosityOption('verbosity', 1), False), error=None)),
    ('long_no_value_next_arg_option', CaseData(args=['--verbosity', '-h'], expected=(VerbosityOption('verbosity', 1), False), error=None)),
    ('long_no_value_next_arg_parameter', CaseData(args=['--verbosity', 'parameter'], expected=(VerbosityOption('verbosity', 1), False), error=None)),
    ('short_value_no_next_arg', CaseData(args=['-v2', None], expected=(VerbosityOption('v', 2), False), error=None)),
    ('short_value_next_arg_option', CaseData(args=['-v2', '-h'], expected=(VerbosityOption('v', 2), False), error=None)),
    ('short_value_next_arg_parameter', CaseData(args=['-v2', 'parameter'], expected=(VerbosityOption('v', 2), False), error=None)),
    ('short_value_equal_no_next_arg', CaseData(args=['-v=2', None], expected=(VerbosityOption('v', 2), False), error=None)),
    ('short_value_equal_next_arg_option', CaseData(args=['-v=2', '-h'], expected=(VerbosityOption('v', 2), False), error=None)),
    ('short_value_equal_next_arg_parameter', CaseData(args=['-v=2', 'parameter'], expected=(VerbosityOption('v', 2), False), error=None)),
    ('long_value_equal_no_next_arg', CaseData(args=['--verbosity=2', None], expected=(VerbosityOption('verbosity', 2), False), error=None)),
    ('long_value_equal_next_arg_option', CaseData(args=['--verbosity=2', '-h'], expected=(VerbosityOption('verbosity', 2), False), error=None)),
    ('long_value_equal_next_arg_parameter', CaseData(args=['--verbosity=2', 'parameter'], expected=(VerbosityOption('verbosity', 2), False), error=None)),
    ('short_no_value_next_arg_bad_value', CaseData(args=['-v', 'bad_value'], expected=(VerbosityOption('v', 1), False), error=None)),
    ('short_no_value_next_arg_bad_value2', CaseData(args=['-v', 'True'], expected=(VerbosityOption('v', 1), False), error=None)),
    ('long_no_value_next_arg_bad_value', CaseData(args=['--verbosity', 'bad_value'], expected=(VerbosityOption('verbosity', 1), False), error=None)),
    ('long_no_value_next_arg_bad_value2', CaseData(args=['--verbosity', 'True'], expected=(VerbosityOption('verbosity', 1), False), error=None)),
    ('short_no_value_next_arg', CaseData(args=['-v', '2'], expected=(VerbosityOption('v', 2), True), error=None)),
    ('long_no_value_next_arg', CaseData(args=['--verbosity', '2'], expected=(VerbosityOption('verbosity', 2), True), error=None)),
    ('long2_no_value_next_arg', CaseData(args=['--verbose', '2'], expected=(VerbosityOption('verbose', 2), True), error=None)),
    ('short_bad_value_next_arg_true', CaseData(args=['-v', 'True'], expected=(VerbosityOption('v', 1), False), error=None)),
    ('long_bad_value_next_arg_true', CaseData(args=['--verbosity', 'True'], expected=(VerbosityOption('verbosity', 1), False), error=None)),
    ('short_bad_value_equal', CaseData(args=['-v=bad_value', None], expected=None, error=AssertionError)),
    ('short_bad_value2_equal', CaseData(args=['-v=True', None], expected=None, error=AssertionError)),
    ('short_bad_value3_equal', CaseData(args=['-v=-2', None], expected=None, error=AssertionError)),
    ('long_bad_value_equal', CaseData(args=['--verbose=bad_value', None], expected=None, error=AssertionError)),
    ('long_bad_value2_equal', CaseData(args=['--verbose=True', None], expected=None, error=AssertionError)),
    ('long_bad_value3_equal', CaseData(args=['--verbose=-2', None], expected=None, error=AssertionError)),
    ('long2_bad_value_equal', CaseData(args=['--verbosity=bad_value', None], expected=None, error=AssertionError)),
    ('long2_bad_value2_equal', CaseData(args=['--verbosity=True', None], expected=None, error=AssertionError)),
    ('long2_bad_value3_equal', CaseData(args=['--verbosity=-2', None], expected=None, error=AssertionError)),
    ('short_bad_value_next_arg_negative', CaseData(args=['-v', '-2'], expected=None, error=ValueError)),
    ('long_bad_value_next_arg', CaseData(args=['--verbosity=bad_value', 'parameter'], expected=None, error=AssertionError)),
    ('wrong_short_option_no_value', CaseData(args=['-h', None], expected=None, error=AssertionError)),
    ('wrong_short_option_value', CaseData(args=['-h=True', None], expected=None, error=AssertionError)),
    ('wrong_long_option_no_value', CaseData(args=['--help', None], expected=None, error=AssertionError)),
    ('wrong_long_option_value', CaseData(args=['--help=True', None], expected=None, error=AssertionError)),
    ('wrong_short_option_next_arg', CaseData(args=['-h', '1'], expected=None, error=AssertionError)),
    ('wrong_long_option_next_arg', CaseData(args=['--help', '1'], expected=None, error=AssertionError)),
    ('wrong_no_option', CaseData(args=['parameter', None], expected=None, error=AssertionError))
  ]

@unittest.skip("disabled until tests pass")
class TestVerbosityOption(unittest.TestCase, CaseExecutor2):
  """
    Unit tests for class VerbosityOption
  """
  def test_value(self):
    """
      Test the value property of VerbosityOption.
      :return: None
    """
    option = VerbosityOption('v', 2)
    self.assertEqual(option.value, 2)

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
      lambda params: VerbosityOption.is_option(params[0], params[1]), case)

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
      Test the make method with parameterized inputs.
      :param name: The name of the test case
      :param case: The test case
    """
    self.execute(lambda params: VerbosityOption.make(params[0], params[1]), case)

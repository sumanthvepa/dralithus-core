"""
  test_option.py: Unit tests for the option module.
"""
from __future__ import annotations

import unittest

from parameterized import parameterized

from dralithus.command_line.option import Option
from dralithus.command_line.help_option import HelpOption
from dralithus.command_line.verbosity_option import VerbosityOption
from dralithus.command_line.multi_option import MultiOption

def make_correct_cases() \
    -> list[tuple[str, str, str | None, list[Option]]]:
  """
    Generate test cases for the MultiOption class.
    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  return [
    ('multi-option1', '-hv', None, [HelpOption('h'), VerbosityOption('v', 1)]),
    ('multi-option2', '-vh', None, [VerbosityOption('v', 1), HelpOption('h')]),
    ('multi-option3', '-vv', None, [VerbosityOption('v', 1), VerbosityOption('v', 1)]),
    ('multi-option4', '-vhv', None, [VerbosityOption('v', 1), HelpOption('h'), VerbosityOption('v', 1)]),
    ('multi-option5', '-hvh', None, [HelpOption('h'), VerbosityOption('v', 1), HelpOption('h')])]

def make_incorrect_cases():
  """
    Generate test cases for the MultiOption class with bad values.
    :return: A list of test cases
  """
  return [
    ('multi-option1', '-v', None, ValueError),
    ('multi-option2', '-h', None, ValueError),
    ('multi-option3', '-e=local', None, ValueError),
    ('multi-option4', '-eh', None, ValueError),
    ('multi-option5', '--help', None, ValueError),
    ('multi-option6', '--verbosity=1', None, ValueError),
    ('multi-option7', '-vhe=local', None, ValueError),
    ('multi-option8', '-x', None, ValueError),
    ('multi-option9', '-v', 'parameter', ValueError),
    ('multi-option10', '-h', 'parameter', ValueError),
    ('multi-option11', '-e=local', 'parameter', ValueError),
    ('multi-option12', '-eh', 'parameter', ValueError),
    ('multi-option13', '--help', 'parameter', ValueError),
    ('multi-option14', '--verbosity=1', 'parameter', ValueError),
    ('multi-option15', '-vhe=local', 'parameter', ValueError),
    ('multi-option16', '-x', 'parameter', ValueError)]


class TestMultiOption(unittest.TestCase):
  """
    Unit tests for the multi-option module.
  """
  def test_flag(self) -> None:
    """
      Test the flag property of the MultiOption class.
    """
    expected_flag = 'vh'
    multi_option = MultiOption([VerbosityOption('v', 1), HelpOption('h')])
    self.assertEqual(expected_flag, multi_option.flag)
    expected_flag = 'hv'
    multi_option = MultiOption([HelpOption('h'), VerbosityOption('v', 1)])
    self.assertEqual(expected_flag, multi_option.flag)

  def test_options(self) -> None:
    """
      Test the options property of the MultiOption class.
    """
    # Create a multi-option with -v and -h
    expected_options = [VerbosityOption('v', 1), HelpOption('h')]
    multi_option = MultiOption(expected_options)
    self.assertEqual(expected_options, multi_option.options)
    expected_options = [HelpOption('h'), VerbosityOption('v', 1)]
    multi_option = MultiOption(expected_options)
    self.assertListEqual(expected_options, multi_option.options)

  def test_add_to(self) -> None:
    """
      Test the add_to method of the MultiOption class.
    """
    multi_option = MultiOption([VerbosityOption('v', 1), HelpOption('h'), VerbosityOption('v', 1)])
    expected_dictionary: dict[str, None | bool | int | str | set[str]] = {
      'verbosity': 2,
      'requires_help': True,
      'environments': set()
    }
    initial_dictionary: dict[str, None | bool | int | str | set[str]] = {
      'requires_help': False,
      'verbosity': 0,
      'environments': set()
    }
    multi_option.add_to(initial_dictionary)
    self.assertEqual(expected_dictionary, initial_dictionary)

  # noinspection PyUnusedLocal
  @parameterized.expand([
    ('vh', '-vh', None, True),
    ('hv', '-hv', None, True),
    ('vv', '-vv', None, True),
    ('vhv', '-vhv', None, True),
    ('v', '-v', None, False),
    ('h', '-h', None, False),
    ('e', '-e=local', None, False),
    ('eh', '-eh', None, False),
    ('help', '--help', None, False),
    ('verbosity_value_equal', '--verbosity=1', None, False),
    ('vhe_value_equal', '-vhe=local', None, False),
    ('vhe', '-vhe', None, False)
  ])

  def test_is_option(self,
    name: str,  # pylint: disable=unused-argument
    arg: str,
    next_arg: str | None,
    expected_value: bool) -> None:
    """
      Test the is_option method of the MultiOption class.
    """
    self.assertEqual(expected_value, MultiOption.is_option(arg, next_arg))

  # noinspection PyUnusedLocal
  @parameterized.expand(make_correct_cases())
  def test_make(self,
    name: str,  # pylint: disable=unused-argument
    current_arg: str, next_arg: str | None,
    expected_options: list[Option]) -> None:
    """
      Test the make method of the MultiOption class.
    """
    multi_option, skip_next_arg = MultiOption.make(current_arg, next_arg)
    self.assertIsInstance(multi_option, MultiOption)
    # self.assertEqual(expected_options, multi_option.options)
    for expected_option, actual_option in zip(expected_options, multi_option.options):
      is_equal = expected_option == actual_option
      self.assertTrue(is_equal)
    self.assertFalse(skip_next_arg)

  # noinspection PyUnusedLocal
  @parameterized.expand(make_incorrect_cases())
  def text_make_incorrect_cases(self,
    name,  # pylint: disable=unused-argument
    current_arg: str,
    next_arg: str) -> None:
    """
      Test the make method of the MultiOption class incorrect cases.
    """
    with self.assertRaises(ValueError):
      MultiOption.make(current_arg, next_arg)

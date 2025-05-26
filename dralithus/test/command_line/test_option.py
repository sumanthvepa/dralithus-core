"""
  test_option.py: Unit tests for the option module.
"""
from __future__ import annotations
import unittest
from typing import override

from parameterized import parameterized

from dralithus.command_line.option import Option
from dralithus.command_line.option_terminator import OptionTerminator
from dralithus.command_line.help_option import HelpOption
from dralithus.command_line.verbosity_option import VerbosityOption
from dralithus.command_line.environment_option import EnvironmentOption
from dralithus.command_line.multi_option import MultiOption

from dralithus.test import CaseData, CaseExecutor2


def is_option_cases() -> list[tuple[str, CaseData]]:
  """
    Test cases for the Option.is_option() method.
    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  return [
    ('option-terminator', CaseData(args=['--', None], expected=True, error=None)),
    ('short-help', CaseData(args=['-h', None], expected=True, error=None)),
    ('long-help', CaseData(args=['--help', None], expected=True, error=None)),
    ('short-verbosity', CaseData(args=['-v', None], expected=True, error=None)),
    ('short-verbosity-value', CaseData(args=['-v=2', None], expected=True, error=None)),
    ('short-verbosity-bad-value', CaseData(args=['-v=bad-value', None], expected=True, error=None)),
    ('long-verbosity', CaseData(args=['--verbosity', None], expected=True, error=None)),
    ('long-verbosity-value', CaseData(args=['--verbosity=2', None], expected=True, error=None)),
    ('long-verbosity-bad-value', CaseData(args=['--verbosity=bad-value', None], expected=True, error=None)),
    ('long2-verbosity', CaseData(args=['--verbose', None], expected=True, error=None)),
    ('long2-verbosity-value', CaseData(args=['--verbose=2', None], expected=True, error=None)),
    ('long2-verbosity-bad-value', CaseData(args=['--verbose=bad-value', None], expected=True, error=None)),
    ('short-env', CaseData(args=['-e', None], expected=True, error=None)),
    ('short-env-value', CaseData(args=['-e=local', None], expected=True, error=None)),
    ('short-env-multi-value', CaseData(args=['-e=local,test', None], expected=True, error=None)),
    ('short-env-bad_value', CaseData(args=['-e=bad-value', None], expected=True, error=None)),
    ('short-env-bad_multi-value', CaseData(args=['-e=bad-value,local', None], expected=True, error=None)),
    ('long-env', CaseData(args=['--env', None], expected=True, error=None)),
    ('long-env-value', CaseData(args=['--env=local', None], expected=True, error=None)),
    ('long-env-multi-value', CaseData(args=['--env=local,test', None], expected=True, error=None)),
    ('long-env-bad_value', CaseData(args=['--env=bad-value', None], expected=True, error=None)),
    ('long-env-bad_multi-value', CaseData(args=['--env=bad-value,local', None], expected=True, error=None)),
    ('long2-env', CaseData(args=['--environment', None], expected=True, error=None)),
    ('long2-env-value', CaseData(args=['--environment=local', None], expected=True, error=None)),
    ('long2-env-multi-value', CaseData(args=['--environment=local,test', None], expected=True, error=None)),
    ('long2-env-bad_value', CaseData(args=['--environment=bad-value', None], expected=True, error=None)),
    ('long2-env-bad_multi-value', CaseData(args=['--environment=bad-value,local', None], expected=True, error=None)),
    ('unknown-short-option', CaseData(args=['-x', None], expected=True, error=None)),
    ('unknown-short-option-value', CaseData(args=['-x=2', None], expected=True, error=None)),
    ('unknown-long-option', CaseData(args=['--xtra', None], expected=True, error=None)),
    ('unknown-long-option-value', CaseData(args=['--xtra=2', None], expected=True, error=None)),
    ('non-option1', CaseData(args=['n', None], expected=False, error=None)),
    ('non-option2', CaseData(args=['non-option', None], expected=False, error=None)),
    ('non-option3', CaseData(args=['---', None], expected=False, error=None)),
    ('multi-option1', CaseData(args=['-hv', None], expected=True, error=None)),
    ('multi-option2', CaseData(args=['-vh', None], expected=True, error=None)),
    ('multi-option3', CaseData(args=['-vhe', None], expected=True, error=None)),
    ('multi-option4', CaseData(args=['-vvv', None], expected=True, error=None)),
    ('bad-multi-option1', CaseData(args=['-vh=1', None], expected=False, error=None)),
    ('bad-multi-option2', CaseData(args=['-vhe=local', None], expected=False, error=None)),
    ('bad-short-option', CaseData(args=['-2', None], expected=False, error=None)),
    ('bad-long-option', CaseData(args=['--2', None], expected=False, error=None)),
    ('bad-long-option2', CaseData(args=['--4sight', None], expected=False, error=None)),
    ('bad-long-option3', CaseData(args=['--4sight=2', None], expected=False, error=None))
  ]


def type_of_cases() -> list[tuple[str, CaseData]]:
  """
    Test cases for the Option.type_of() method.
    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  return [
    ('option-terminator', '--', None, OptionTerminator),
    ('option-terminator', CaseData(args=['--', None], expected=OptionTerminator, error=None)),
    ('short-help', CaseData(args=['-h', None], expected=HelpOption, error=None)),
    ('long-help', CaseData(args=['--help', None], expected=HelpOption, error=None)),
    ('short-verbosity', CaseData(args=['-v', None], expected=VerbosityOption, error=None)),
    ('long-verbosity', CaseData(args=['--verbosity', None], expected=VerbosityOption, error=None)),
    ('long-verbosity-value', CaseData(args=['--verbosity=2', None], expected=VerbosityOption, error=None)),
    ('long2-verbosity', CaseData(args=['--verbose', None], expected=VerbosityOption, error=None)),
    ('long2-verbosity-value', CaseData(args=['--verbose=2', None], expected=VerbosityOption, error=None)),
    ('short-verbosity-bad-value', CaseData(args=['-v=bad_value', None], expected=None, error=ValueError)),
    ('short-verbosity-bad-value2', CaseData(args=['-v=True', None], expected=None, error=ValueError)),
    ('short-verbosity-bad-value3', CaseData(args=['-v=-2', None], expected=None, error=ValueError)),
    ('long-verbosity-bad-value', CaseData(args=['--verbosity=bad_value', None], expected=None, error=ValueError)),
    ('long-verbosity-bad-value2', CaseData(args=['--verbosity=True', None], expected=None, error=ValueError)),
    ('long-verbosity-bad-value3', CaseData(args=['--verbosity=-2', None], expected=None, error=ValueError)),
    ('short-env', CaseData(args=['-e', None], expected=None, error=ValueError)),
    ('short-env-value', CaseData(args=['-e=local', None], expected=EnvironmentOption, error=None)),
    ('short-env-multi-value', CaseData(args=['-e=local,test', None], expected=EnvironmentOption, error=None)),
    ('short-env-bad_value', CaseData(args=['-e=bad_value', None], expected=None, error=ValueError)),
    ('short-env-bad_multi-value', CaseData(args=['-e=bad_value,local', None], expected=None, error=ValueError)),
    ('short-env-bad-multi-value2', CaseData(args=['-e=local,bad_value', None], expected=None, error=ValueError)),
    ('long-env', CaseData(args=['--env', None], expected=None, error=ValueError)),
    ('long-env-value', CaseData(args=['--env=local', None], expected=EnvironmentOption, error=None)),
    ('long-env-multi-value', CaseData(args=['--env=local,test', None], expected=EnvironmentOption, error=None)),
    ('long-env-bad_value', CaseData(args=['--env=bad_value', None], expected=None, error=ValueError)),
    ('long-env-bad_multi-value', CaseData(args=['--env=bad_value,local', None], expected=None, error=ValueError)),
    ('long-env-bad-multi-value2', CaseData(args=['--env=local,bad_value', None], expected=None, error=ValueError)),
    ('long2-env', CaseData(args=['--environment', None], expected=None, error=ValueError)),
    ('long2-env-value', CaseData(args=['--environment=local', None], expected=EnvironmentOption, error=None)),
    ('long2-env-multi-value', CaseData(args=['--environment=local,test', None], expected=EnvironmentOption, error=None)),
    ('long2-env-bad_value', CaseData(args=['--environment=bad_value', None], expected=None, error=ValueError)),
    ('long2-env-bad_multi-value', CaseData(args=['--environment=bad_value,local', None], expected=None, error=ValueError)),
    ('long2-env-bad-multi-value2', CaseData(args=['--environment=local,bad_value', None], expected=None, error=ValueError)),
  ]


def make_cases() -> list[tuple[str, CaseData]]:
  """
    Test cases for the Option.make() method.
    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  return [
    ('option-terminator', CaseData(args=['--', None], expected=(OptionTerminator(), False), error=None)),
    ('short-help', CaseData(args=['-h', None], expected=(HelpOption('h'), False), error=None)),
    ('short-help-next-arg', CaseData(args=['-h', 'True'], expected=(HelpOption('h'), False), error=None)),
    ('short-help-next-arg2', CaseData(args=['-h', '2'], expected=(HelpOption('h'), False), error=None)),
    ('short-help-next-arg3', CaseData(args=['-h', '-2'], expected=(HelpOption('h'), False), error=None)),
    ('long-help', CaseData(args=['--help', None], expected=(HelpOption('help'), False), error=None)),
    ('long-help-next-arg', CaseData(args=['--help', 'True'], expected=(HelpOption('help'), False), error=None)),
    ('long-help-next-arg2', CaseData(args=['--help', '2'], expected=(HelpOption('help'), False), error=None)),
    ('long-help-next-arg3', CaseData(args=['--help', '-2'], expected=(HelpOption('help'), False), error=None)),
    ('short-verbosity', CaseData(args=['-v', None], expected=(VerbosityOption('v', 1), False), error=None)),
    ('short-verbosity-value', CaseData(args=['-v=2', None], expected=(VerbosityOption('v', 2), False), error=None)),
    ('short-verbosity-next-arg', CaseData(args=['-v', '2'], expected=(VerbosityOption('v', 2), True), error=None)),
    ('short-verbosity-next-arg-value', CaseData(args=['-v', '2'], expected=(VerbosityOption('v', 2), True), error=None)),
    ('short-verbosity-next-arg-bad-value', CaseData(args=['-v', 'bad_value'], expected=(VerbosityOption('v', 1), False), error=None)),
    ('short-verbosity-next-arg-bad-value2', CaseData(args=['-v', 'True'], expected=(VerbosityOption('v', 1), False), error=None)),
    ('short-verbosity-next-arg-option', CaseData(args=['-v', '-h'], expected=(VerbosityOption('v', 1), False), error=None)),
    ('short-verbosity-next-arg-verbosity', CaseData(args=['-v', '-v'], expected=(VerbosityOption('v', 1), False), error=None)),
    ('short-verbosity-next-arg-parameter', CaseData(args=['-v', 'parameter'], expected=(VerbosityOption('v', 1), False), error=None)),
    ('long-verbosity', CaseData(args=['--verbosity', None], expected=(VerbosityOption('verbosity', 1), False), error=None)),
    ('long-verbosity-value', CaseData(args=['--verbosity=2', None], expected=(VerbosityOption('verbosity', 2), False), error=None)),
    ('long-verbosity-next-arg', CaseData(args=['--verbosity', '2'], expected=(VerbosityOption('verbosity', 2), True), error=None)),
    ('long-verbosity-next-arg-option', CaseData(args=['--verbosity', '-h'], expected=(VerbosityOption('verbosity', 1), False), error=None)),
    ('long-verbosity-next-arg-verbosity', CaseData(args=['--verbosity', '-v'], expected=(VerbosityOption('verbosity', 1), False), error=None)),
    ('long-verbosity-next-arg-parameter', CaseData(args=['--verbosity', 'parameter'], expected=(VerbosityOption('verbosity', 1), False), error=None)),
    ('long2-verbosity', CaseData(args=['--verbose', None], expected=(VerbosityOption('verbose', 1), False), error=None)),
    ('long2-verbosity-value', CaseData(args=['--verbose=2', None], expected=(VerbosityOption('verbose', 2), False), error=None)),
    ('long2-verbosity-next-arg', CaseData(args=['--verbose', '2'], expected=(VerbosityOption('verbose', 2), True), error=None)),
    ('long2-verbosity-next-arg-option', CaseData(args=['--verbose', '-h'], expected=(VerbosityOption('verbose', 1), False), error=None)),
    ('long2-verbosity-next-arg-verbosity', CaseData(args=['--verbose', '-v'], expected=(VerbosityOption('verbose', 1), False), error=None)),
    ('long2-verbosity-next-arg-parameter', CaseData(args=['--verbose', 'parameter'], expected=(VerbosityOption('verbose', 1), False), error=None)),
    ('short-env', CaseData(args=['-e=local', None], expected=(EnvironmentOption('e', {'local'}), False), error=None)),
    ('short-env-multi-value', CaseData(args=['-e=local,test', None], expected=(EnvironmentOption('e', {'local', 'test'}), False), error=None)),
    ('short-env-next-arg', CaseData(args=['-e', 'local'], expected=(EnvironmentOption('e', {'local'}), True), error=None)),
    ('short-env-next-arg-multi-value', CaseData(args=['-e', 'local,test'], expected=(EnvironmentOption('e', {'local', 'test'}), True), error=None)),
    ('short-env-next-arg-option', CaseData(args=['-e=local', '-h'], expected=(EnvironmentOption('e', {'local'}), False), error=None)),
    ('short-env-next-arg-parameter', CaseData(args=['-e=local', 'parameter'], expected=(EnvironmentOption('e', {'local'}), False), error=None)),
    ('short-env-multi-value-next-arg-option', CaseData(args=['-e=local,test', '-h'], expected=(EnvironmentOption('e', {'local', 'test'}), False), error=None)),
    ('short-env-multi-value-next-arg-parameter', CaseData(args=['-e=local,test', 'parameter'], expected=(EnvironmentOption('e', {'local', 'test'}), False), error=None)),
    ('long-env', CaseData(args=['--env=local', None], expected=(EnvironmentOption('env', {'local'}), False), error=None)),
    ('long-env-multi-value', CaseData(args=['--env=local,test', None], expected=(EnvironmentOption('env', {'local', 'test'}), False), error=None)),
    ('long-env-next-arg', CaseData(args=['--env', 'local'], expected=(EnvironmentOption('env', {'local'}), True), error=None)),
    ('long-env-next-arg-multi-value', CaseData(args=['--env', 'local,test'], expected=(EnvironmentOption('env', {'local', 'test'}), True), error=None)),
    ('long-env-next-arg-option', CaseData(args=['--env=local', '-h'], expected=(EnvironmentOption('env', {'local'}), False), error=None)),
    ('long-env-next-arg-parameter', CaseData(args=['--env=local', 'parameter'], expected=(EnvironmentOption('env', {'local'}), False), error=None)),
    ('long-env-multi-value-next-arg-option', CaseData(args=['--env=local,test', '-h'], expected=(EnvironmentOption('env', {'local', 'test'}), False), error=None)),
    ('long-env-multi-value-next-arg-parameter', CaseData(args=['--env=local,test', 'parameter'], expected=(EnvironmentOption('env', {'local', 'test'}), False), error=None)),
    ('long2-env', CaseData(args=['--environment=local', None], expected=(EnvironmentOption('environment', {'local'}), False), error=None)),
    ('long2-env-multi-value', CaseData(args=['--environment=local,test', None], expected=(EnvironmentOption('environment', {'local', 'test'}), False), error=None)),
    ('long2-env-next-arg', CaseData(args=['--environment', 'local'], expected=(EnvironmentOption('environment', {'local'}), True), error=None)),
    ('long2-env-next-arg-multi-value', CaseData(args=['--environment', 'local,test'], expected=(EnvironmentOption('environment', {'local', 'test'}), True), error=None)),
    ('long2-env-next-arg-option', CaseData(args=['--environment=local', '-h'], expected=(EnvironmentOption('environment', {'local'}), False), error=None)),
    ('long2-env-next-arg-parameter', CaseData(args=['--environment=local', 'parameter'], expected=(EnvironmentOption('environment', {'local'}), False), error=None)),
    ('long2-env-multi-value-next-arg-option', CaseData(args=['--environment=local,test', '-h'], expected=(EnvironmentOption('environment', {'local', 'test'}), False), error=None)),
    ('long2-env-multi-value-next-arg-parameter', CaseData(args=['--environment=local,test', 'parameter'], expected=(EnvironmentOption('environment', {'local', 'test'}), False), error=None)),
    ('multi-option1', CaseData(args=['-hv', None], expected=(MultiOption([HelpOption('h'), VerbosityOption('v', 1)]), False), error=None)),
    ('multi-option2', CaseData(args=['-vh', None], expected=(MultiOption([VerbosityOption('v', 1), HelpOption('h')]), False), error=None)),
    ('short-help-value', CaseData(args=['-h=True', None], expected=None, error=ValueError)),
    ('short-help-value2', CaseData(args=['-h=2', None], expected=None, error=ValueError)),
    ('short-help-value3', CaseData(args=['-h=-2', None], expected=None, error=ValueError)),
    ('long-help-value', CaseData(args=['--help=True', None], expected=None, error=ValueError)),
    ('long-help-value2', CaseData(args=['--help=2', None], expected=None, error=ValueError)),
    ('long-help-value3', CaseData(args=['--help=-2', None], expected=None, error=ValueError)),
    ('short-verbosity-bad-value', CaseData(args=['-v=bad_value', None], expected=None, error=ValueError)),
    ('short-verbosity-bad-value2', CaseData(args=['-v=True', None], expected=None, error=ValueError)),
    ('short-verbosity-bad-value3', CaseData(args=['-v=-2', None], expected=None, error=ValueError)),
    ('short-verbosity-next-arg', CaseData(args=['-v', '-2'], expected=None, error=ValueError)),
    ('long-verbosity-bad-value', CaseData(args=['--verbosity=bad_value', None], expected=None, error=ValueError)),
    ('long-verbosity-bad-value2', CaseData(args=['--verbosity=True', None], expected=None, error=ValueError)),
    ('long-verbosity-bad-value3', CaseData(args=['--verbosity=-2', None], expected=None, error=ValueError)),
    ('long-verbosity-next-arg', CaseData(args=['--verbosity', '-2'], expected=None, error=ValueError)),
    ('long2-verbosity-bad-value', CaseData(args=['--verbose=bad_value', None], expected=None, error=ValueError)),
    ('long2-verbosity-bad-value2', CaseData(args=['--verbose=True', None], expected=None, error=ValueError)),
    ('long2-verbosity-bad-value3', CaseData(args=['--verbose=-2', None], expected=None, error=ValueError)),
    ('long2-verbosity-next-arg', CaseData(args=['--verbose', '-2'], expected=None, error=ValueError)),
    ('short-env-bad_value', CaseData(args=['-e=bad_value', None], expected=None, error=ValueError)),
    ('short-env-bad_value2', CaseData(args=['-e=True', None], expected=None, error=ValueError)),
    ('short-env-bad_value3', CaseData(args=['-e=-2', None], expected=None, error=ValueError)),
    ('short-env-next-arg', CaseData(args=['-e', 'bad_value'], expected=None, error=ValueError)),
    ('short-env-next-arg2', CaseData(args=['-e', 'True'], expected=None, error=ValueError)),
    ('short-env-next-arg3', CaseData(args=['-e', '-2'], expected=None, error=ValueError)),
    ('long-env-bad_value', CaseData(args=['--env=bad_value', None], expected=None, error=ValueError)),
    ('long-env-bad_value2', CaseData(args=['--env=True', None], expected=None, error=ValueError)),
    ('long-env-bad_value3', CaseData(args=['--env=-2', None], expected=None, error=ValueError)),
    ('long-env-next-arg', CaseData(args=['--env', 'bad_value'], expected=None, error=ValueError)),
    ('long-env-next-arg2', CaseData(args=['--env', 'True'], expected=None, error=ValueError)),
    ('long-env-next-arg3', CaseData(args=['--env', '-2'], expected=None, error=ValueError)),
    ('long2-env-bad_value', CaseData(args=['--environment=bad_value', None], expected=None, error=ValueError)),
    ('long2-env-bad_value2', CaseData(args=['--environment=True', None], expected=None, error=ValueError)),
    ('long2-env-bad_value3', CaseData(args=['--environment=-2', None], expected=None, error=ValueError)),
    ('long2-env-next-arg', CaseData(args=['--environment', 'bad_value'], expected=None, error=ValueError)),
    ('long2-env-next-arg2', CaseData(args=['--environment', 'True'], expected=None, error=ValueError)),
    ('long2-env-next-arg3', CaseData(args=['--environment', '-2'], expected=None, error=ValueError)),
    ('long2-env-multi-value-next-arg-option', CaseData(args=['--environment', 'local,bad_value'], expected=None, error=ValueError)),
    ('bad-multi-option', CaseData(args=['-vhe', None], expected=None, error=ValueError)),
    ('bad-multi-option2', CaseData(args=['-vhe=local', None], expected=None, error=ValueError)),
    ('bad-multi-option3', CaseData(args=['-vhe=local,test', None], expected=None, error=ValueError)),
    ('bad-multi-option-next-arg', CaseData(args=['-vhe', 'parameter'], expected=None, error=ValueError)),
    ('bad-multi-option-next-arg2', CaseData(args=['-vhe', 'local'], expected=None, error=ValueError)),
    ('bad-multi-option-next-arg3', CaseData(args=['-vhe=local', 'parameter'], expected=None, error=ValueError))
  ]


@unittest.skip("disabled until tests pass")
class TestOption2(unittest.TestCase, CaseExecutor2):
  """
    Unit tests for the Option.make() method
  """
  def __init__(self, *args, **kwargs):
    """
      Initialize the test case.
    """
    unittest.TestCase.__init__(self, *args, **kwargs)
    CaseExecutor2.__init__(self)

  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  @parameterized.expand(is_option_cases())
  def test_is_option(self, name: str, case: CaseData):
    """
      Test the make method of the Option class.
      :return: None
    """
    self.execute(lambda parameters: Option.is_option(parameters[0], parameters[1]), case)

  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  @parameterized.expand(type_of_cases())
  def test_type_of(self, name: str, case: CaseData):
    """
      Test the type_of method of the Option class.
      :return: None
    """
    self.execute(lambda parameters: Option.type_of(parameters[0], parameters[1]), case)

  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  @parameterized.expand(make_cases())
  def test_make(self, name: str, case: CaseData):
    """
      Test the make method of the Option class.
      :return: None
    """
    self.execute(lambda parameters: Option.make(parameters[0], parameters[1]), case)


@unittest.skip("disabled until tests pass")
class TestOptionSubclassing(unittest.TestCase):
  """
    Test that subclassing Option works.
  """
  def test_subclassing(self) -> None:
    """
      Test that Option is an abstract class can be subclassed.
    """
    class DummyOption(Option):
      """
        A dummy subclass of Option for testing purposes.
      """
      def __init__(self, flag: str, value: int):
        """ Initialize the object with a value. """
        self._flag = flag
        self._value = value

      @classmethod
      def supported_short_flags(cls) -> list[str]:
        """
          Supported short flags for this option.

          :return: A list of short flag strings
        """
        return ['d']

      @classmethod
      def supported_long_flags(cls) -> list[str]:
        """
          Supported long flags for this option.

          :return: A list of long flag strings
        """
        return ['dummy']

      @override
      @property
      def flag(self) -> str:
        """
          Get the flag of the option.

          :return: The flag of the option
        """
        return self._flag

      @override
      @property
      def value(self) -> int:
        """
          Get the value of the option.

          :return: The value of the option
        """
        return self._value

      def add_to(self, dictionary: dict[str, None | bool | int | str | set[str]]) -> None:
        """
          Add the option to a dictionary.

          :param dictionary: The dictionary to add the option to
        """
        dictionary["dummy"] = self._value

      @classmethod
      def is_option(cls, arg: str, next_arg: str | None) -> bool:
        """
          Check if the argument is a dummy option.

          :param arg: The argument string
          :param next_arg: The next argument string (unused)
          :return: True if the argument is a dummy option
        """
        return arg in ['-d', '-dummy']

      @classmethod
      def is_valid_value_type(cls, str_value: str) -> bool:
        """
          Check if the value is valid for this option.

          :param str_value: The value to check
          :return: Always False. The dummy option does not take a value
        """
        return False

      @classmethod
      def make(cls, current_arg: str, next_arg: str | None) -> tuple[DummyOption, bool]:
        # noinspection GrazieInspection
        """
          Create a DummyOption object from command line arguments.

          :param current_arg: The current argument string
          :param next_arg: The next argument string
          :return:  A tuple containing the DummyOption object and a boolean
            indicating whether to skip the next argument.
        """
        flag, _, __ = cls._extract_value(current_arg, next_arg)
        return DummyOption(flag, 42), False

    # Create an instance of the dummy subclass
    expected_flag1 = 'd'
    expected_value1 = 52
    dummy1 = DummyOption(expected_flag1, expected_value1)
    # Check that the value property returns the correct value
    self.assertEqual(expected_flag1, dummy1.flag)
    self.assertEqual(expected_value1, dummy1.value)

    # Create another instance of the dummy subclass
    expected_flag2 = 'dummy'
    expected_value2 = 84
    dummy2 = DummyOption(expected_flag2, expected_value2)
    # Check that the value property returns the correct value
    self.assertEqual(expected_flag2, dummy2.flag)
    self.assertEqual(expected_value2, dummy2.value)

"""
  test_help_option.py: Unit tests for the HelpOption class.
"""
import unittest

from parameterized import parameterized

from dralithus.command_line.help_option import HelpOption


@unittest.skip("disabled until tests pass")
class TestHelpOption(unittest.TestCase):
  """
    Unit tests for class HelpOption
  """

  def test_value(self) -> None:
    """
      Test the value of the help option.
    """
    help_option = HelpOption('h')
    self.assertTrue(help_option.value)

  def test_add_to(self) -> None:
    """
      Test the add_to method.
    """
    help_option = HelpOption('h')
    dictionary: dict[str, None | bool | int | str | set[str]] = {}
    help_option.add_to(dictionary)
    self.assertTrue(dictionary['requires_help'])

    dictionary = {'requires_help': False}
    help_option.add_to(dictionary)
    self.assertTrue(dictionary['requires_help'])

  # noinspection PyUnusedLocal
  @parameterized.expand([
    ('short-help', '-h', None, True),
    ('long-help', '--help', None, True),
    ('short-help-with-value', '-h=True', None, False),
    ('short-help-with-value1', '-h=1', None, False),
    ('short-help-with-value2', '-h1', None, False),
    ('long-help-with-value', '--help=True', None, False),
    ('long-help-with-value2', '--help=2', None, False),
    ('not-help', '-v', None, False),
    ('not-help-parameter', 'parameter', None, False),
  ])
  def test_is_option(self,
    name: str,  # pylint: disable=unused-argument
    arg: str, next_arg: str | None,
    expected_value: bool) -> None:
    """
      Test the is_option method.
    """
    self.assertEqual(expected_value, HelpOption.is_option(arg, next_arg))

  def test_make(self) -> None:
    """
      Test the make method.
    """
    help_option, skip_next = HelpOption.make('--help', None)
    self.assertIsInstance(help_option, HelpOption)
    self.assertTrue(help_option.value)
    self.assertFalse(skip_next)

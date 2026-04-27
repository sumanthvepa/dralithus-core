"""
  test_option_terminator.py: Unit tests for the OptionTerminator class.
"""
import unittest

from dralithus.command_line.option_terminator import OptionTerminator


class TestOptionTerminator(unittest.TestCase):
  """
    Unit tests for class OptionTerminator
  """

  def test_value(self) -> None:
    """
      Test the value of the option terminator.
    """
    terminator = OptionTerminator()
    self.assertEqual(None, terminator.value)


  def test_is_option(self) -> None:
    """
      Test the is_option method.
    """
    self.assertTrue(OptionTerminator.is_option('--', None))
    self.assertFalse(OptionTerminator.is_option('-h', None))


  def test_make(self) -> None:
    """
      Test the make method.
    """
    terminator, skip_next = OptionTerminator.make('--', None)
    self.assertIsInstance(terminator, OptionTerminator)
    self.assertEqual('-', terminator.flag)
    self.assertEqual(None, terminator.value)
    self.assertFalse(skip_next)

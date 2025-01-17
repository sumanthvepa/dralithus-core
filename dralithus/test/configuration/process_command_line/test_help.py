"""
  test_help.py: Unit tests to test the --help global option in the command line
  interface (process_command_line) for the dralithus application.

  The --help option is a global option that can be used with any command
  to get help for that command. Or, it can be used without a command to get
  help for the drl program as a whole.
"""
import unittest

from dralithus.test.configuration.process_command_line import TestCaseData

from dralithus.configuration import CommandLineError, process_command_line

class TestHelp(unittest.TestCase):
  """
    Test that the --help option is handled correctly by the
    process_command_line function.
  """
  def execute_test(self, case: TestCaseData) -> None:
    """ Execute a test using the test case data """
    # Convert the structured test case data to a list of arguments
    args: list[str] = list(case['args'])
    if case['expected'] is not None:
      # We convert the expected and actual results to dictionaries
      # so that we can compare them using assertDictEqual
      result = dict(process_command_line(args))
      expected = dict(case['expected'])
      self.assertDictEqual(result, expected)
    elif case['error'] is not None:
      # The 'elif' above is not strictly necessary. At this point case['error']
      # is guaranteed to be not None. It there to stop mypy from complaining
      # about incompatible types in the next line where the right side is
      # type[CommandLineError] | None and the left side is type[CommandLineError]
      error: type[CommandLineError] = case['error']
      self.assertRaises(error, process_command_line, args)

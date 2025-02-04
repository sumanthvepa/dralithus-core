"""
  process_command_line: Unit tests and helper classes/functions to test the
  dralithus.configuration.process_command_line function.
"""
import copy
import unittest
from typing import Callable, Iterator, TypedDict

from dralithus.configuration import Operation, CommandLineError, process_command_line


# pylint: disable=too-few-public-methods
class Args:
  """
    A class that holds arguments to be passed to process_command_line

    The purpose of this data structure is to allow the args list
    to be manipulated more easily. In particular, it enables one
    to construct a new test case by modifying the argument list
    of an existing test case.

    This makes test case construction easier and more readable.

    This dictionary contains the following keys:
    - program: The name of the program
    - global_options: A list of global options
    - command: The command to execute
    - command_options: A list of command options
    - parameters: A list of parameters
  """
  # pylint: disable=too-many-arguments
  def __init__(
      self,
      program: str,
      global_options: list[str],
      command: str,
      command_options: list[str],
      parameters: list[str]):
    """ Create an Args object """
    self.program = program
    self.global_options = global_options
    self.command = command
    self.command_options = command_options
    self.parameters = parameters

  def __iter__(self) -> Iterator[str]:
    """
      Return an iterator to the argument list

      This is useful to convert an object type Args into a list. For example:
      ```
      args_obj = Args(...)
      args = list(args_obj)
      ```
    """
    if self.command == '':
      return iter([
        self.program,
        *self.global_options,
        *self.command_options,
        *self.parameters
      ])
    return iter([
      self.program,
      *self.global_options,
      self.command,
      *self.command_options,
      *self.parameters
    ])

  def __str__(self):
    """ Convert the Args object to a string """
    return str(list(self))

  def __repr__(self):
    """ Convert the Args object to a string """
    return str(self)

class ErrorDict(TypedDict):
  """
    A dictionary that holds the expected error type and verbosity level

    This data structure is used to define the expected output of a
    process_command_line test when the function is expected to fail.

    These are the fields:
    - error_type: The expected error type
    - verbosity: The expected verbosity level
  """
  error_type: type[CommandLineError]
  verbosity: int

class TestCaseData(TypedDict):
  """
    Test case data for process_command_line test cases

    This data structure is used to define the input and the expected
    output of a process_command_line test.

    This makes it easier to construct a large number of data driven
    tests. In particular, it should be possible to take an existing
    TestCaseData object and create new test case by modifying the
    args field and the expected field slightly.

    These are the fields:
    - args: The argument list passed to process_command_line
    - expected: The expected output of process_command_line, if the
        function is expected to succeed. It is None if the function
        is expected to fail.
    - error: The expected error message, if the function is expected
        to fail. It is None if the function is expected to succeed.
  """
  args: Args
  expected: Operation | None
  error: ErrorDict | None


class CommandLineTestCase(unittest.TestCase):
  """
  Base class for test cases for the process_command_line function

  This class provides a method to execute a test using a TestCaseData object
"""
  def execute_test(self, case: TestCaseData) -> None:
    """ Execute a test using the test case data """
    # Convert the structured test case data to a list of arguments
    args: list[str] = list(case['args'])
    if case['expected'] is not None:
      # We convert the expected and actual results to dictionaries
      # so that we can compare them using assertDictEqual
      expected = dict(case['expected'])
      try:
        result = dict(process_command_line(args))
        self.assertDictEqual(result, expected,
                             'Failed test case:\n' + str(case['args']) \
                             + '\nexpected: ' + str(expected) + '\nactual: ' + str(result))
      except CommandLineError as ex:
        self.fail('Failed test case:\n' + str(case['args'])
                  + '\nexpected: ' + str(expected) + '\nactual: ' + str(ex))
    elif case['error'] is not None:
      # The 'elif' above is not strictly necessary. At this point case['error']
      # is guaranteed to be not None. It there to stop mypy from complaining
      # about incompatible types in the next line where the right side is
      # type[CommandLineError] | None and the left side is type[CommandLineError]
      error: ErrorDict = case['error']
      assert_message = 'Failed test case:\n' \
                       + str(case['args']) \
                       + '\nexpected: CommandLineError(verbosity=' \
                       + str(error['verbosity']) + ')'

      # This code uses a context to capture the exception raised by the
      # process_command_line function. The with clause ensures checks
      # that the exception is raised and that it is of the correct type.
      # It also captures the exception in the context variable.
      # The assertEqual statement checks that the verbosity level of the
      # captured exception object.
      with self.assertRaises(error['error_type'], msg=assert_message) as context:
        process_command_line(args)
      self.assertEqual(context.exception.verbosity, error['verbosity'])


def make_args_list(
    program: str,
    global_options_list: list[list[str]],
    command_list: list[str],
    command_options_list: list[list[str]],
    parameters_list: list[list[str]]) -> list[Args]:
  """" Generate a list of Args objects based on the given parameters """
  args_list: list[Args] = []
  for global_options in global_options_list:
    for command in command_list:
      for command_options in command_options_list:
        for parameters in parameters_list:
          args = Args(program, global_options, command, command_options, parameters)
          args_list.append(args)
  return args_list

def make_verbose_test_case(
    case: TestCaseData,
    count: int,
    generator: Callable[[int], list[str]],
    global_option) -> TestCaseData:
  """ Generate a verbosity test case """
  args = copy.deepcopy(case['args'])
  expected = copy.deepcopy(case['expected'])
  error = copy.deepcopy(case['error'])
  if global_option:
    args.global_options = args.global_options + generator(count)
  else:
    args.command_options = args.command_options + generator(count)
  if expected is not None:
    expected['verbosity'] = count
  if error is not None:
    error['verbosity'] = count
  return {'args': args, 'expected': expected, 'error': error}


def make_verbose_test_cases(case: TestCaseData) -> list[tuple[TestCaseData]]:
  """
  Create a list of test cases based on the given case, where
  the verbosity level is set to between 1 and 4 in all the
  ways that it is allowed to set the verbosity level.

  :param case The test case to use as a template
  :return:
  """
  verbose_cases: list[tuple[TestCaseData]] = []
  verbose_flags_generators: list[Callable[[int], list[str]]] = [
    lambda count: ['-v'] * count,  # E.g #-v -v -v
    lambda count: [f'-{"v" * count}'], # E.g. -vvv
    lambda count: [f'-v={count}'], # E.g. -v=3
    lambda count: ['-v', str(count)], # E.g. -v 3
    lambda count: ['--verbose'] * count, # E.g. --verbose --verbose
    lambda count: [f'--verbose={count}'], # E.g. --verbose=3
    lambda count: ['--verbose', str(count)] # E.g. --verbose 3
  ]

  for verbosity_count in range(1, 4):
    for flags_generator in verbose_flags_generators:
      # Skip the second flags generator if the verbosity count is 1, since it is
      # equivalent to the first flags generator.
      if flags_generator == verbose_flags_generators[1] and verbosity_count == 1:
        continue
      global_case \
        = make_verbose_test_case(case, verbosity_count, flags_generator, global_option=True)
      verbose_cases.append((global_case,))
      if case['args'].command != '':
        command_case \
          = make_verbose_test_case(case, verbosity_count, flags_generator, global_option=False)
        verbose_cases.append((command_case,))

  return verbose_cases

def all_test_cases(cases: list[tuple[TestCaseData]]) -> list[tuple[TestCaseData]]:
  """ Generate all the test cases for the help option """
  verbose_cases: list[tuple[TestCaseData]] = []
  for case in cases:
    verbose_cases += make_verbose_test_cases(case[0])
  return cases + verbose_cases


def print_cases(cases: list[tuple[TestCaseData]]) -> None:
  """
    Print the test cases in list
    :param cases: The list of test cases to print
    :return: None
  """
  for case in cases:
    print(case)

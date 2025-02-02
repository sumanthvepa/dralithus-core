"""
  test_help.py: Unit tests to test the --help global option in the command line
  interface (process_command_line) for the dralithus application.

  The --help option is a global option that can be used with any command
  to get help for that command. Or, it can be used without a command to get
  help for the drl program as a whole.
"""
import copy
import unittest
from typing import Callable

from parameterized import parameterized

from dralithus.test.configuration.process_command_line import Args, ErrorDict, TestCaseData

from dralithus.configuration import (
  CommandLineError,
   Operation,
  is_valid_command,
  process_command_line)


def interleave_into(list1: list[str], list2: list[str]) -> list[list[str]]:
  """ Interleave the elements of two lists into a list of lists """
  interleaved: list[list[str]] = []
  for item1 in list1:
    for index in range(len(list2)+1):
      result = list2[:index] + [item1] + list2[index:]
      interleaved.append(result)
  return interleaved

def interleave_lists(list1: list[str], lists: list[list[str]]) -> list[list[str]]:
  """ Interleave the elements of a list into a list of lists """
  interleaved: list[list[str]] = []
  for list2 in lists:
    interleaved += interleave_into(list1, list2)
  return interleaved

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

def make_test_cases(args_list: list[Args]) -> list[tuple[TestCaseData]]:
  """ Generate a list of test cases based on the given list of Args objects """
  cases: list[tuple[TestCaseData]] = []
  for args in args_list:
    expected: Operation = {
      'command': 'help',
      'about': args.command if is_valid_command(args.command) else None,
      'applications': None,
      'environments': None,
      'verbosity': 0
    }
    case: tuple[TestCaseData] = ({'args': args, 'expected': expected, 'error': None},) \
      if is_valid_command(args.command) \
  else ({
      'args': args,
      'expected': None,
      'error': {'error_type': CommandLineError, 'verbosity': 0}
    },)
    cases.append(case)
  return cases

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

def no_parameters_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with no parameters
    i.e. just drl.
  """
  args = Args(program='drl', global_options=[], command='', command_options=[], parameters=[])
  return [(TestCaseData(
    args=args, expected=None, error={'error_type': CommandLineError, 'verbosity': 0}),)]

def global_option_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the --help global option
    and nothing else. i.e. drl --help or drl -h
  """
  # pylint: disable=line-too-long
  args_list = make_args_list('drl', [['-h'], ['--help']], [''], [[]],[[]])
  expected: Operation = {'command': 'help', 'about': None, 'applications': None, 'environments': None, 'verbosity': 0 }
  return [({'args': args, 'expected': expected, 'error': None},) for args in args_list]


def global_option_with_other_args_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the --help global option
    other non-verbosity flag arguments.
    E.g. drl --help deploy
    or drl --help deploy --environment=local sample
    or invalid arguments like drl --help --environment=local
    or even invalid commands like:
    drl --help invalid, or
    drl --help invalid --environment=local sample

    In each case, the --help flag should be recognized and the other arguments
    should be ignored, except for the command name. The command name should be
    recognized and passed as the value of the 'about' key in the Operation
    dictionary.
  """
  # Both command and command_options should not be simultaneously
  # empty ('' or [] respectively) when generating test cases. Otherwise,
  # an incorrect test case like 'drl -h' will be generated, which
  # has been handled in an earlier test case.
  # To solve this problem, we set command_list to ['deploy', 'invalid']
  # and command_options_list to [[], ['--environment=local'], ['--environment', 'local']]
  # and then generate test cases for all possible combinations of these
  # And separately generate test cases for the case where command is empty
  # and command_options is not empty.
  args_list = make_args_list(
    program='drl',
    global_options_list=[['-h'], ['--help']],
    command_list=['deploy', 'invalid'],
    command_options_list=[[], ['--environment=local'], ['--environment', 'local']],
    parameters_list=[[], ['sample']])
  args_list += make_args_list(
    program='drl',
    global_options_list=[['-h'], ['--help']],
    command_list=[''],
    command_options_list=[['--environment=local'], ['--environment', 'local']],
    parameters_list=[[], ['sample']])
  return make_test_cases(args_list)


def command_option_with_other_args_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with the --help
    passed as a command option
    E.g. drl deploy --help
    or drl deploy --environment=local --help
    or drl deploy --help --environment=local
    or drl deploy --help --environment=local sample
    or drl deploy --environment=local --help sample
    or drl deploy --environment=local sample --help
    or even invalid arguments like drl --help --environment=local
    or invalid commands like:
    drl deploy invalid --help

    In each case, the --help flag should be recognized and the other arguments
    should be ignored, except for the command name. The command name should be
    recognized and passed as the value of the 'about' key in the Operation
    dictionary.
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy', 'invalid'],
    command_options_list=interleave_lists(
      ['-h', '--help'], [[], ['--environment=local'], ['--environment', 'local']]),
    parameters_list=[[], ['sample']])
  return make_test_cases(args_list)

def all_test_cases() -> list[tuple[TestCaseData]]:
  """ Generate all the test cases for the help option """
  cases: list[tuple[TestCaseData]] = []
  cases += no_parameters_test_cases()
  # cases += global_option_test_cases()
  # cases += global_option_with_other_args_test_cases()
  # cases += command_option_with_other_args_test_cases()
  verbose_cases: list[tuple[TestCaseData]] = []
  for case in cases:
    verbose_cases += make_verbose_test_cases(case[0])
  cases += verbose_cases
  return cases


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

  @parameterized.expand(all_test_cases())
  def test_case(self, case: TestCaseData):
    """ Execute all the test cases """
    self.execute_test(case)



def print_all_cases():
  """ Print all the test cases """
  cases = all_test_cases()
  for case in cases:
    print(case)


if __name__ == '__main__':
  print_all_cases()
  # unittest.main()

"""
  test_help.py: Unit tests to test the --help global option in the command line
  interface (process_command_line) for the dralithus application.

  The --help option is a global option that can be used with any command
  to get help for that command. Or, it can be used without a command to get
  help for the drl program as a whole.
"""
from parameterized import parameterized

from dralithus.configuration import (
  CommandLineError,
  Operation,
  merge_option_values)

from dralithus.test.configuration.process_command_line import (
  Args,
  TestCaseData,
  CommandLineTestCase,
  insert_every_element_everywhere,
  insert_every_element_everywhere_for_all_lists,
  all_combinations,
  demerge_option_values,
  make_args_list,
  make_test_cases,
  all_test_cases,
  print_cases)

from dralithus.test.configuration.process_command_line.test_deploy import (
  deploy_valid_test_cases,
  deploy_invalid_base_test_cases)


def no_parameters_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing invocation of drl with no parameters
    i.e. just drl.
  """
  args = Args(program='drl', global_options=[], command='', command_options=[], parameters=[])
  return [(TestCaseData(
    args=args, expected=None, error={'error_type': CommandLineError, 'verbosity': 0}),)]


def help_valid_global_no_command_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing a valid invocation of drl with the help as
    a global option, but no command.
    i.e. drl -h or drl --help

    :return: list[tuple[TestCaseData]] - A list of test cases encased in a tuple
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[['-h'], ['--help']],
    command_list=[''],
    command_options_list=[[]],
    parameters_list=[[]])
  expected: Operation = {
    'command': 'help',
    'about': None,
    'applications': None,
    'environments': None,
    'verbosity': 0 }
  return make_test_cases(args_list, expected, None)


def help_valid_global_deploy_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing a valid invocation of drl with the help as
    a global option, and a command.
    i.e. drl -h deploy or drl --help deploy

    :return: list[tuple[TestCaseData]] - A list of test cases encased in a tuple
  """
  # First, generate test cases for the 'deploy' command
  base_cases = deploy_valid_test_cases()

  # Then iterate over the base cases making cases with global help options
  cases: list[tuple[TestCaseData]] = []
  for tuple_list in base_cases:
    case: TestCaseData = tuple_list[0]
    args: Args = case['args']
    args_list: list[Args] = make_args_list(
      program=args.program,
      global_options_list=[['-h'], ['--help']],
      command_list=[args.command],
      command_options_list=[args.command_options],
      parameters_list=[args.parameters])
    expected: Operation = {
      'command': 'help',
      'about': args.command,
      'applications': None,
      'environments': None,
      'verbosity': 0 }
    cases += make_test_cases(args_list, expected, None)
  return cases


def help_valid_deploy_help_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing a valid invocation of drl with just the help
    flag as a command option.

    i.e. drl deploy -h or drl deploy --help

    :return: list[tuple[TestCaseData]] - A list of test cases encased in a tuple
  :return:
  """
  expected: Operation = {
    'command': 'help',
    'about': 'deploy',
    'applications': None,
    'environments': None,
    'verbosity': 0 }
  cases: list[tuple[TestCaseData]] = []
  # Add valid cases where the help flag is passed as a command option
  # to the 'deploy' command with no other options or parameters. This
  # is not handled in the valid base cases for the 'deploy' command
  # without help since 'deploy' with no options or parameters is
  # invalid.
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=[['-h'], ['--help']],
    parameters_list=[[]])
  cases += make_test_cases(args_list, expected, None)
  base_cases = deploy_valid_test_cases()
  for tuple_list in base_cases:
    case: TestCaseData = tuple_list[0]
    args: Args = case['args']
    help_options = ['-h', '--help']
    merged_command_options = merge_option_values(args.command_options)
    merged_command_options_with_help_list = insert_every_element_everywhere(
      help_options,
      merged_command_options)
    command_options_list: list[list[str]] = []
    for merged_command_options_with_help in merged_command_options_with_help_list:
      command_options = demerge_option_values(merged_command_options_with_help)
      command_options_list.append(command_options)
    args_list: list[Args] = make_args_list(
        program=args.program,
        global_options_list=[[]],
        command_list=[args.command],
        command_options_list=command_options_list,
        parameters_list=[args.parameters])
    cases += make_test_cases(args_list, expected, None)
  return cases


def help_invalid_global_no_command_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing an invalid invocation of drl with the help as
    a global option, but no command.
    For example: drl -h --env=local or drl --help -e local
    In the examples above, the help option is followed by an invalid
    global option, which should result in a CommandLineError.

    :return: list[tuple[TestCaseData]] - A list of test cases encased in a tuple
  """
  base_global_options_list = [
    ['--environment=local'],
    ['--environment', 'local']]
  help_options_list = [['-h'], ['--help']]
  global_options_list = all_combinations(help_options_list, base_global_options_list)
  args_list = make_args_list(
    program='drl',
    global_options_list=global_options_list,
    command_list=[''],
    command_options_list=[[]],
    parameters_list=[[]])
  error = {'error_type': CommandLineError, 'verbosity': 0}
  return make_test_cases(args_list, None, error)

def help_invalid_global_deploy_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing an invalid invocation of drl with the help as
    a global option, and an invalid command.
    i.e. drl -h invalid or drl --help invalid

    :return: list[tuple[TestCaseData]] - A list of test cases encased in a tuple
  """
  base_cases: list[tuple[TestCaseData]] = deploy_invalid_base_test_cases()
  cases: list[tuple[TestCaseData]] = []
  for tuple_list in base_cases:
    case: TestCaseData = tuple_list[0]
    args: Args = case['args']
    args_list: list[Args] = make_args_list(
      program=args.program,
      global_options_list=[['-h'], ['--help']],
      command_list=[args.command],
      command_options_list=[args.command_options],
      parameters_list=[args.parameters])
    error = {'error_type': CommandLineError, 'verbosity': 0}
    cases += make_test_cases(args_list, None, error)
  return cases

def help_invalid_deploy_help_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing an invalid invocation of drl with just the help
    flag as a command option.

    E.g. drl deploy -h --environment=local  # missing an application
    or drl deploy --help sample # missing an environment.

    :return: list[tuple[TestCaseData]] - A list of test cases encased in a tuple
  """
  help_options = ['-h', '--help']
  base_cases: list[tuple[TestCaseData]] = deploy_invalid_base_test_cases()
  cases: list[tuple[TestCaseData]] = []
  for tuple_list in base_cases:
    case: TestCaseData = tuple_list[0]
    args: Args = case['args']
    command_options_list = insert_every_element_everywhere(help_options, args.command_options)
    args_list: list[Args] = make_args_list(
      program=args.program,
      global_options_list=[[]],
      command_list=[args.command],
      command_options_list=command_options_list,
      parameters_list=[args.parameters])
    error = {'error_type': CommandLineError, 'verbosity': 0}
    cases += make_test_cases(args_list, None, error)

  command_options_list = [
    ['--environment', '-h', 'local'],
    ['-e', '-h', 'local'],
    ['--env', '-h', 'local'],
    ['--environment', '--help', 'local'],
    ['-e', '--help', 'local'],
    ['--env', '--help', 'local']
  ]
  args_list = make_args_list(
    program='drl',
    global_options_list=[[]],
    command_list=['deploy'],
    command_options_list=command_options_list,
    parameters_list=[['sample']])
  error = {'error_type': CommandLineError, 'verbosity': 0}
  cases += make_test_cases(args_list, None, error)
  return cases


def help_invalid_global_invalid_command_test_cases() -> list[tuple[TestCaseData]]:
  """
    Test cases representing an invalid invocation of drl with the help as
    a global option, and an invalid command.
    E.g. drl -h invalid or drl --help invalid

    :return: list[tuple[TestCaseData]] - A list of test cases encased in a tuple
  """
  args_list = make_args_list(
    program='drl',
    global_options_list=[['-h'], ['--help']],
    command_list=['invalid'],
    command_options_list=[
      [],
      ['--environment=local'],
      ['--environment', 'local'],
      ['-elocal'],
      ['-e', 'local'],
      ['--environment=local,dev'],
      ['--environment', 'local,dev'],
      ['--unknown'],
      ['--unknown=value'],
      ['--unknown', 'value'],
      ['-uvalue'],
      ['-u', 'value']
    ],
    parameters_list=[
      [],
      ['sample'],
      ['sample', 'echo '],
      ['garbage', 'unknown']
    ])
  error = {'error_type': CommandLineError, 'verbosity': 0}
  return make_test_cases(args_list, None, error)


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
  cases: list[tuple[TestCaseData]] = []
  global_options_list = [['-h'], ['--help']]
  command_options_list = [[], ['--environment=local'], ['--environment', 'local']]
  parameters_list = [[], ['sample']]

  empty_command_args_list = make_args_list(
    'drl', global_options_list,[''], command_options_list, parameters_list)
  expected: Operation = {
    'command': 'help',
    'about': None,
    'applications': None,
    'environments': None,
    'verbosity': 0 }
  cases += make_test_cases(empty_command_args_list, expected, None)

  invalid_command_args_list = make_args_list(
    'drl', global_options_list, ['invalid'], command_options_list, parameters_list)
  error = {'error_type': CommandLineError, 'verbosity': 0}
  cases += make_test_cases(invalid_command_args_list, None, error)

  deploy_command_args_list = make_args_list(
    'drl', global_options_list, ['deploy'], command_options_list, parameters_list)
  expected = {
    'command': 'help',
    'about': 'deploy',
    'applications': None,
    'environments': None,
    'verbosity': 0 }
  cases += make_test_cases(deploy_command_args_list, expected, None)
  return cases


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
  cases: list[tuple[TestCaseData]] = []
  global_options_list = [[]]
  command_options_list = insert_every_element_everywhere_for_all_lists(
    ['-h', '--help'],
    [[], ['--environment=local'], ['--environment', 'local']])
  parameters_list = [[], ['sample']]

  deploy_args_list = make_args_list(
    'drl', global_options_list, ['deploy'], command_options_list, parameters_list)
  expected = {
    'command': 'help',
    'about': 'deploy',
    'applications': None,
    'environments': None,
    'verbosity': 0 }
  cases += make_test_cases(deploy_args_list, expected, None)

  invalid_args_list = make_args_list(
    'drl', global_options_list, ['invalid'], command_options_list, parameters_list)
  error = {'error_type': CommandLineError, 'verbosity': 0}
  cases += make_test_cases(invalid_args_list, None, error)
  return cases


def help_base_test_cases() -> list[tuple[TestCaseData]]:
  """ Generate the base test cases for the help option """
  cases: list[tuple[TestCaseData]] = []

  cases += no_parameters_test_cases()
  cases += help_valid_global_no_command_test_cases()
  cases += help_valid_global_deploy_test_cases()
  cases += help_valid_deploy_help_test_cases()
  cases += help_invalid_global_no_command_test_cases()
  cases += help_invalid_global_deploy_test_cases()
  cases += help_invalid_global_invalid_command_test_cases()
  cases += help_invalid_deploy_help_test_cases()
  return cases

def old_help_base_test_cases() -> list[tuple[TestCaseData]]:
  """ Generate the base test cases for the help option """
  cases: list[tuple[TestCaseData]] = []

  cases += no_parameters_test_cases()
  cases += global_option_test_cases()
  cases += global_option_with_other_args_test_cases()
  cases += command_option_with_other_args_test_cases()
  return cases

class TestHelp(CommandLineTestCase):
  """
    Test that the --help option is handled correctly by the
    process_command_line function.
  """
  @parameterized.expand(all_test_cases(help_base_test_cases()))
  def test_case(self, case: TestCaseData):
    """ Execute all the test cases """
    self.execute_test(case)


if __name__ == '__main__':
  # print_cases(help_base_test_cases())
  print_cases(old_help_base_test_cases())
  # print_cases(all_test_cases(help_base_test_cases()))
  # unittest.main()

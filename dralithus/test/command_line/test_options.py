"""
  test_options.py: Unit tests for the Options class
"""
import unittest

from parameterized import parameterized

from dralithus.command_line.options import Options
from dralithus.test import CaseData, CaseExecutor2


def empty_case() -> list[tuple[str, CaseData]]:
  """
    Generate the empty test case.
    :return: Return the empty test case in a single element list
  """
  # pylint: disable=line-too-long
  return [
    ('empty', CaseData(args=[], expected=({'requires_help': False, 'verbosity': 0, 'environments': set()}, 0), error=None))
  ]


def single_option_cases() -> list[tuple[str, CaseData]]:
  """
    Generate a list of single option test cases.

    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  return [
    ('help-short', CaseData(args=['-h'], expected=({'requires_help': True, 'verbosity': 0, 'environments': set()}, 1), error=None)),
    ('help-long', CaseData(args=['--help'], expected=({'requires_help': True, 'verbosity': 0, 'environments': set()}, 1), error=None)),
    ('verbosity-short', CaseData(args=['-v'], expected=({'requires_help': False, 'verbosity': 1, 'environments': set()}, 1), error=None)),
    ('verbosity-long', CaseData(args=['--verbose'], expected=({'requires_help': False, 'verbosity': 1, 'environments': set()}, 1), error=None)),
    ('verbosity-long-value-equal', CaseData(args=['--verbose=2'], expected=({'requires_help': False, 'verbosity': 2, 'environments': set()}, 1), error=None)),
    ('verbosity-long-value-space', CaseData(args=['--verbose', '2'], expected=({'requires_help': False, 'verbosity': 2, 'environments': set()}, 2), error=None)),
    ('verbosity-long2', CaseData(args=['--verbosity'], expected=({'requires_help': False, 'verbosity': 1, 'environments': set()}, 1), error=None)),
    ('verbosity-long2-value-equal', CaseData(args=['--verbosity=2'], expected=({'requires_help': False, 'verbosity': 2, 'environments': set()}, 1), error=None)),
    ('verbosity-long2-value-space', CaseData(args=['--verbosity', '2'], expected=({'requires_help': False, 'verbosity': 2, 'environments': set()}, 2), error=None)),
    ('environment-short', CaseData(args=['-e=local'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local'}}, 1), error=None)),
    ('environment-short2', CaseData(args=['-e=development'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development'}}, 1), error=None)),
    ('environment-short-space', CaseData(args=['-e', 'local'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local'}}, 2), error=None)),
    ('environment-short-space2', CaseData(args=['-e', 'development'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development'}}, 2), error=None)),
    ('environment-short-multiple', CaseData(args=['-e=local,test'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local', 'test'}}, 1), error=None)),
    ('environment-short-multiple2', CaseData(args=['-e=development,staging'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development', 'staging'}}, 1), error=None)),
    ('environment-short-multiple-space', CaseData(args=['-e', 'local,test'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local', 'test'}}, 2), error=None)),
    ('environment-short-multiple-space2', CaseData(args=['-e', 'development,staging'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development', 'staging'}}, 2), error=None)),
    ('environment-long', CaseData(args=['--env=local'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local'}}, 1), error=None)),
    ('environment-long2', CaseData(args=['--env=development'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development'}}, 1), error=None)),
    ('environment-long-space', CaseData(args=['--env', 'local'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local'}}, 2), error=None)),
    ('environment-long-space2', CaseData(args=['--env', 'development'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development'}}, 2), error=None)),
    ('environment-long-multiple', CaseData(args=['--env=local,test'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local', 'test'}}, 1), error=None)),
    ('environment-long-multiple2', CaseData(args=['--env=development,staging'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development', 'staging'}}, 1), error=None)),
    ('environment-long-multiple-space', CaseData(args=['--env', 'local,test'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local', 'test'}}, 2), error=None)),
    ('environment-long-multiple-space2', CaseData(args=['--env', 'development,staging'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development', 'staging'}}, 2), error=None)),
    ('environment2-long', CaseData(args=['--environment=local'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local'}}, 1), error=None)),
    ('environment2-long2', CaseData(args=['--environment=development'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development'}}, 1), error=None)),
    ('environment2-long-space', CaseData(args=['--environment', 'local'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local'}}, 2), error=None)),
    ('environment2-long2-space', CaseData(args=['--environment', 'development'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development'}}, 2), error=None)),
    ('environment2-long-multiple', CaseData(args=['--environment=local,test'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local', 'test'}}, 1), error=None)),
    ('environment2-long2-multiple', CaseData(args=['--environment=development,staging'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development', 'staging'}}, 1), error=None)),
    ('environment2-long-multiple-space', CaseData(args=['--environment', 'local,test'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local', 'test'}}, 2), error=None)),
    ('environment2-long2-multiple-space', CaseData(args=['--environment', 'development,staging'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'development', 'staging'}}, 2), error=None))
  ]

def multi_option_cases() -> list[tuple[str, CaseData]]:
  """
    Generate a list of multi-option test cases.
    :return: A list of test cases
  """
  # pylint: disable=line-too-long
  # noinspection SpellCheckingInspection
  return [
    ('multi-option', CaseData(args=['-vh'], expected=({'requires_help': True, 'verbosity': 1, 'environments': set()}, 1), error=None)),
    ('multi-option2', CaseData(args=['-hv'], expected=({'requires_help': True, 'verbosity': 1, 'environments': set()}, 1), error=None)),
    ('multi-option2', CaseData(args=['-hv'], expected=({'requires_help': True, 'verbosity': 1, 'environments': set()}, 1), error=None)),
    ('multi-option3', CaseData(args=['-vv'], expected=({'requires_help': False, 'verbosity': 2, 'environments': set()}, 1), error=None)),
    ('multi-option4', CaseData(args=['-vvhvh', '-e', 'local'], expected=({'requires_help': True, 'verbosity': 3, 'environments': {'local'}}, 3), error=None)),
  ]


def combine_cases(
    name1: str, case1: CaseData,
    name2: str | None, case2: CaseData | None,
    insert_terminator: bool = False) -> tuple[str, CaseData]:
  """
    Combine two test cases into a single test case.

    Case 2 can be None and an optional terminator can be inserted between the two cases.
    The terminator, if specified, is always inserted after the first case, and
    the second case, if not none is always appended to the end of that combination.

    :param name1: The name of the first test case
    :param case1: The first test case
    :param name2: The name of the second test case
    :param case2: The second test case
    :param insert_terminator: True if an option terminator should be inserted between the two cases
    :return: The combined test case
  """
  if not insert_terminator:
    if case2 is None:
      combined_args = case1.args
      requires_help = case1.expected[0]['requires_help']
      verbosity = case1.expected[0]['verbosity']
      environments = case1.expected[0]['environments']
      end_index = len(combined_args)
    else:
      combined_args = case1.args + case2.args
      requires_help = case1.expected[0]['requires_help'] or case2.expected[0]['requires_help']
      verbosity = case1.expected[0]['verbosity'] + case2.expected[0]['verbosity']
      environments = case1.expected[0]['environments'] | case2.expected[0]['environments']
      end_index = len(combined_args)
    name = f'{name1}-' if name2 is None else f'{name1}-{name2}'
  else:
    if case2 is None:
      combined_args = case1.args + ['--']
      requires_help = case1.expected[0]['requires_help']
      verbosity = case1.expected[0]['verbosity']
      environments = case1.expected[0]['environments']
      end_index = len(combined_args)
    else:
      combined_args = case1.args + ['--'] + case2.args
      requires_help = case1.expected[0]['requires_help']
      verbosity = case1.expected[0]['verbosity']
      environments = case1.expected[0]['environments']
      end_index = len(case1.args) + 1
    name = f'{name1}-terminator' if name2 is None else f'{name1}-terminator-{name2}'
  combined_expected = (
    {'requires_help': requires_help, 'verbosity': verbosity, 'environments': environments},
    end_index)
  case = CaseData(args=combined_args, expected=combined_expected, error=None)
  return name, case

def double_option_cases() -> list[tuple[str, CaseData]]:
  """
    Generate a list of double option test cases.

    i.e. cases where the args list has two options.
    These are generated by combining single option cases.

    :return: A list of test cases
  """
  input_cases = single_option_cases()
  output_cases: list[tuple[str, CaseData]] = []
  for name1, case1 in input_cases:
    for name2, case2 in input_cases:
      output_cases.append(
        combine_cases(name1, case1, name2, case2, insert_terminator=False))
      if name1 != name2:
        # pylint: disable=arguments-out-of-order
        output_cases.append(
          combine_cases(name2, case2, name1, case1, insert_terminator=False))
  return output_cases


def option_terminator_cases() -> list[tuple[str, CaseData]]:
  """
    Make valid cases with option terminators.

    :return: A list of test cases
  """
  input_cases = single_option_cases()
  output_cases: list[tuple[str, CaseData]] = []
  for name1, case1 in input_cases:
    # Add option terminator to the end of the args list in the following
    # three combinations: case1 --,  case1 -- case2, case2 -- case1
    output_cases.append(
      combine_cases(name1, case1, None, None, insert_terminator=True))
    for name2, case2 in input_cases:
      output_cases.append(
        combine_cases(name1, case1, name2, case2, insert_terminator=True))
      output_cases.append(
        combine_cases(name2, case2, name1, case1, insert_terminator=True))
  return output_cases


def cases_with_extra_args() -> list[tuple[str, CaseData]]:
  """
    Generate a list of test cases with extra args.

    :return: A list of test cases
  """
  input_cases \
    = empty_case() \
      + single_option_cases() \
      + double_option_cases() \
      + option_terminator_cases()
  output_cases: list[tuple[str, CaseData]] = []
  for name, case in input_cases:
    # Add extra args to the end of the args list
    extra_args = ['extra_arg1', 'extra_arg2']
    case_with_extra_args = CaseData(args=case.args + extra_args, expected=case.expected, error=None)
    output_cases.append((f'{name}-extra-args', case_with_extra_args))
  return output_cases

def edge_cases() -> list[tuple[str, CaseData]]:
  """
    Make edge cases to test the option class.

    These are cases that don't fall into any particular category

  :return:
  """
  # pylint: disable=line-too-long
  return [
    ('bad-help-value', CaseData(args=['-h', 'True', '-v', '1'], expected=({'requires_help': True, 'verbosity': 0, 'environments': set()}, 1), error=None)),
    ('option-after-first-parameter', CaseData(args=['-v', '1', 'parameter', '-h'], expected=({'requires_help': False, 'verbosity': 1, 'environments': set()}, 2), error=None)),
    ('terminator-before-option-value', CaseData(args=['-v', '--', '3', '-h'], expected=({'requires_help': False, 'verbosity': 1, 'environments': set()}, 2), error=None)),
    ('multiple-terminators', CaseData(args=['-v', '--', '3', '--', '-h'], expected=({'requires_help': False, 'verbosity': 1, 'environments': set()}, 2), error=None)),
    ('terminator-before-environment-value', CaseData(args=['-e=local,test', '--', '-e=development,staging'], expected=({'requires_help': False, 'verbosity': 0, 'environments': {'local', 'test'}}, 2), error=None))
  ]

def correct_cases() -> list[tuple[str, CaseData]]:
  """
    Generate a list of correct cases for the Options class.
  """
  return \
      empty_case() \
      + single_option_cases() \
      + double_option_cases() \
      + multi_option_cases() \
      + option_terminator_cases() \
      + cases_with_extra_args() \
      + edge_cases()


def incorrect_cases() -> list[tuple[str, CaseData]]:
  """
    Generate a list of incorrect cases for the Options class.
  """
  # pylint: disable=line-too-long
  return [
    ('error-short-help-value-equal', CaseData(args=['-h=True'], expected=None, error=ValueError)),
    ('error-short-help-value-equal2', CaseData(args=['-h=2'], expected=None, error=ValueError)),
    ('error-long-help-value-equal', CaseData(args=['--help=True'], expected=None, error=ValueError)),
    ('error-long-help-value-equal2', CaseData(args=['--help=2'], expected=None, error=ValueError)),
    ('error-short-version-bad-value', CaseData(args=['-v=bad-value'], expected=None, error=ValueError)),
    ('error-short-version-bad-value2', CaseData(args=['-v=True'], expected=None, error=ValueError)),
    ('error-long-version-bad-value', CaseData(args=['--verbose=bad-value'], expected=None, error=ValueError)),
    ('error-long-version-bad-value2', CaseData(args=['--verbose=True'], expected=None, error=ValueError)),
    ('error-long-version2-bad-value', CaseData(args=['--verbosity=bad-value'], expected=None, error=ValueError)),
    ('error-long-version2-bad-value2', CaseData(args=['--verbosity=True'], expected=None, error=ValueError)),
    ('error-short-environment-bad-value', CaseData(args=['-e=bad-value'], expected=None, error=ValueError)),
    ('error-short-environment-bad-value2', CaseData(args=['-e=True'], expected=None, error=ValueError)),
    ('error-short-environment-bad-value-multiple', CaseData(args=['-e=bad-value,local'], expected=None, error=ValueError)),
    ('error-short-environment-bad-value-multiple2', CaseData(args=['-e=local,bad-value'], expected=None, error=ValueError)),
    ('error-long-environment-bad-value', CaseData(args=['--env=bad-value'], expected=None, error=ValueError)),
    ('error-long-environment-bad-value2', CaseData(args=['--env=True'], expected=None, error=ValueError)),
    ('error-long-environment-bad-value-multiple', CaseData(args=['--env=bad-value,local'], expected=None, error=ValueError)),
    ('error-long-environment-bad-value-multiple2', CaseData(args=['--env=local,bad-value'], expected=None, error=ValueError)),
    ('error-long-environment2-bad-value', CaseData(args=['--environment=bad-value'], expected=None, error=ValueError)),
    ('error-long-environment2-bad-value2', CaseData(args=['--environment=True'], expected=None, error=ValueError)),
    ('error-long-environment2-bad-value-multiple', CaseData(args=['--environment=bad-value,local'], expected=None, error=ValueError)),
    ('error-long-environment2-bad-value-multiple2', CaseData(args=['--environment=local,bad-value'], expected=None, error=ValueError)),
    ('error-short-help-value-correct-verbosity', CaseData(args=['-h=1', '-v'], expected=None, error=ValueError)),
    ('error-short-help-value-correct-verbosity', CaseData(args=['-v', '-h=1'], expected=None, error=ValueError)),
    ('error-terminator-before-environment-value', CaseData(args=['--environment', '--', 'local,test'], expected=None, error=ValueError))
  ]

def all_cases() -> list[tuple[str, CaseData]]:
  """
    Generate all test cases for the Options class.

    :return: A list of test cases
  """
  return correct_cases() + incorrect_cases()


@unittest.skip
class TestOptions(unittest.TestCase, CaseExecutor2):
  """
    Unit tests for the Options class.
  """
  def __init__(self, *args, **kwargs):
    """
      Initialize the test case.
    """
    unittest.TestCase.__init__(self, *args, **kwargs)
    CaseExecutor2.__init__(self)

  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  @parameterized.expand(all_cases())
  def test_constructor(self, name: str, case: CaseData) -> None:
    """
      Test the constructor of the Options class.
    """
    self.execute(Options, case)

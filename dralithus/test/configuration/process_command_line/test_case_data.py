"""
  test_case_data.py: Define classes to hold test case data for
  process_command_line test cases.
"""
from typing import TypedDict

from dralithus.test.configuration.process_command_line.args import Args

from dralithus.configuration import Operation, CommandLineError


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
  error: CommandLineError | None

"""
  process_command_line: Unit tests and helper classes/functions to test the
  dralithus.configuration.process_command_line function.
"""
from typing import Iterator, TypedDict

from dralithus.configuration import Operation, CommandLineError


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
    return iter([
      self.program,
      *self.global_options,
      self.command,
      *self.command_options,
      *self.parameters
    ])


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
  error: type[CommandLineError] | None

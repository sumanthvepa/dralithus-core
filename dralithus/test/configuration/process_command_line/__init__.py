# -*- coding: utf-8 -*-
"""
  dralithus/test/configuration/process_command_line/__init__.py: Unit
  tests and helper classes/functions to test the
  dralithus.configuration.process_command_line function.
"""
# -------------------------------------------------------------------
# dralithus/test/configuration/process_command_line/__init__.py: Unit
# tests and helper classes/functions to test the
# dralithus.configuration.process_command_line function.
#
# Copyright (C) 2023-25 Sumanth Vepa.
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License a
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <https://www.gnu.org/licenses/>.
# -------------------------------------------------------------------
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

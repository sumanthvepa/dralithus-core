# -*- coding: utf-8 -*-
"""
dralithus/test/__init__.py: Helper classes and functions for unit tests
"""
# -------------------------------------------------------------------
# dralithus/test/__init__.py: Helper classes and functions for unit
# tests
#
# Copyright 2023-25. Sumanth Vepa. svepa@milestone42.com
#
# This file is part of dralithus-core.
#
# dralithus-core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dralithus-core is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dralithus-core. If not, see <https://www.gnu.org/licenses/>.
# -------------------------------------------------------------------
from typing import Any, Callable, Protocol

class CaseData:
  """
    A test case for dralithus
  """
  def __init__(self,
      args: Any,
      expected: Any,
      error: type[Exception] | None):
    """
      Initialize the test case.

      :param args: The input to the test case
      :param expected: The expected output of the test case
      :param error: The expected error of the test case
    """
    assert ((expected is not None) and (error is None)) \
           or ((expected is None) and (error is not None)), \
      'If expected is set, then error must be none, and vice versa.'
    self._args = args
    self._expected = expected
    self._error = error

  @property
  def args(self) -> Any:
    """
      Get the input of the test case.

      :return: The input of the test case
    """
    return self._args

  @property
  def expected(self) -> Any:
    """
      Get the expected output of the test case.

      :return: The expected output of the test case
    """
    return self._expected

  @property
  def error(self) -> type[Exception] | None:
    """
      Get the expected error of the test case.

      :return: The expected error of the test case
    """
    return self._error


class RequiresAsserts(Protocol):
  """ Protocol for objects that require 'assert*' methods usable by CaseExecutor. """
  # pylint: disable=invalid-name
  # noinspection PyPep8Naming
  def assertEqual(self, first: Any, second: Any, msg: str | None = None) -> None:
    """ Assert that two values are equal. """

  # pylint: disable=invalid-name
  # noinspection PyPep8Naming
  def assertRaises(self, expected_exception:  type[BaseException] | tuple[type[BaseException], ...], *args: Any, **kwargs: Any) -> Any:
    """ Assert that an exception is raised. """


# pylint: disable=too-few-public-methods
class CaseExecutor(RequiresAsserts):
  """
    A class to execute test cases.
  """
  def __init__(self, function: Callable[[list[str]], Any]) -> None:
    """
      Initialize the CaseExecutor.
    """
    self.function = function

  def execute(self, case: CaseData) -> None:
    """
      Execute a test case.

      :param case: The test case to execute
    """
    if case.expected is not None:
      self.assertEqual(case.expected, self.function(case.args))
    else:
      assert case.error is not None
      with self.assertRaises(case.error):
        self.function(case.args)


class CaseExecutor2(RequiresAsserts):
  """
    A class to execute test cases.
  """
  def execute(self, function: Callable[..., Any], case: CaseData) -> None:
    """
      Execute a test case.

      :param function: The function to execute
      :param case: The test case to execute
    """
    if case.expected is not None:
      expected = case.expected
      # Since we use None to indicate that an error is expected, we cannot
      # use None as an expected value when the function under test returns None.
      # To overcome this, test cases that expect None as the output of the
      # function, should pass a list with a single None element. This code
      # checks for that, and sets expected to None if the expected value is a
      # list with a single None element. Of course, one hopes that the function
      # under test does not return a list with a single None element. This
      # framework will not work for such situations.
      if isinstance(case.expected, list) and len(case.expected) == 1 and case.expected[0] is None:
        expected = None
      actual = function(case.args)
      self.assertEqual(expected, actual, f'Expected {expected} but got {actual}')
    else:
      assert case.error is not None
      with self.assertRaises(case.error):
        function(case.args)

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


# Private sentinel used to detect whether a caller supplied an
# expected value. It lets a literal None be a valid expected result,
# distinct from "no expected value was given".
_UNSET: Any = object()


class CaseData:
  """
    A test case for dralithus
  """
  def __init__(
        self,
        args: Any,
        expected: Any = _UNSET,
        error: type[Exception] | None = None,
        error_message: str | None = None):
    """
      Initialize the test case.

      Exactly one outcome must be supplied: either an expected value
      (a normal-result case, including a literal None) or an error
      type (an exception case). An error message may accompany an
      error.

      :param args: The input to the test case
      :param expected: The expected output of the test case
      :param error: The expected error of the test case
      :param error_message: The expected error message
    """
    expected_supplied = expected is not _UNSET
    assert expected_supplied != (error is not None), (
      'Exactly one of expected or error must be supplied.')
    assert error_message is None or error is not None, (
      'An error message can only be specified when an error is expected.')
    self._args = args
    self._expected = expected
    self._error = error
    self._error_message = error_message

  @property
  def args(self) -> Any:
    """
      Get the input of the test case.

      :return: The input of the test case
    """
    return self._args

  @property
  def expects_error(self) -> bool:
    """
      Return whether this case expects an exception.

      :return: True for an exception case, False for a normal case
    """
    return self._expected is _UNSET

  @property
  def expected(self) -> Any:
    """
      Get the expected output of the test case.

      :return: The expected output of the test case
    """
    assert not self.expects_error, (
      'expected is not defined for an exception case.')
    return self._expected

  @property
  def error(self) -> type[Exception] | None:
    """
      Get the expected error of the test case.

      :return: The expected error of the test case
    """
    return self._error

  @property
  def error_message(self) -> str | None:
    """
      Get the expected error message of the test case.

      :return: The expected error message
    """
    return self._error_message


class RequiresAsserts(Protocol):
  """ Protocol for objects requiring assert methods used by CaseExecutor. """
  # pylint: disable=invalid-name
  # noinspection PyPep8Naming
  def assertEqual(self, first: Any, second: Any, msg: str | None = None) -> None:
    """ Assert that two values are equal. """

  # pylint: disable=invalid-name
  # noinspection PyPep8Naming
  def assertRaises(
    self,
    expected_exception:  type[BaseException] | tuple[type[BaseException], ...],
    *args: Any,
    **kwargs: Any) -> Any:
    """ Assert that an exception is raised. """


class CaseExecutor(RequiresAsserts):
  """
    A class to execute test cases.
  """
  def execute(self, function: Callable[..., Any], case: CaseData) -> None:
    """
      Execute a test case.

      :param function: The function to execute
      :param case: The test case to execute
    """
    if case.expects_error:
      assert case.error is not None
      # IntelliJ IDEA's type checker is not smart enough to figure out
      # that case.error cannot be None at this point.
      # noinspection PyTypeChecker
      with self.assertRaises(case.error) as context:
        function(case.args)
      if case.error_message is not None:
        self.assertEqual(
          case.error_message,
          str(context.exception))
    else:
      expected = case.expected
      actual = function(case.args)
      self.assertEqual(
        expected, actual, f'Expected {expected} but got {actual}')

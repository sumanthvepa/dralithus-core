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
from typing import Callable, Protocol


class CaseData:
  """
    A test case for dralithus
  """
  def __init__(self,
      args: list[str],
      expected: tuple[dict[str, None | bool | int | str | set[str]], set[str]] | None,
      error: type[Exception] | None):
    """
      Initialize the test case.

      :param args: The input to the test case
      :param expected: The expected output of the test case
      :param error: The expected error of the test case
    """
    assert ((expected is not None) and (error is None)) \
           or ((expected is None) and (error is not None)), \
      "If expected is set, then error must be none, and vice versa."
    self._args = args
    self._expected = expected
    self._error = error

  @property
  def args(self) -> list[str]:
    """
      Get the input of the test case.

      :return: The input of the test case
    """
    return self._args

  @property
  def expected(self) -> tuple[dict[str, None | bool | int | str | set[str]], set[str]] | None:
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
  def assertDictEqual(
      self,
      first: dict[str, None | bool | int | str | set[str]],
      second: dict[str, None | bool | int | str | set[str]]) -> None:
    """ Compare two dictionaries for equality. """

  # pylint: disable=invalid-name
  # noinspection PyPep8Naming
  def assertSetEqual(
      self,
      first: set[str],
      second: set[str]) -> None:
    """ Compare two sets for equality. """

  # pylint: disable=invalid-name
  # noinspection PyPep8Naming
  def assertRaises(self, expected_exception, *args, **kwargs):
    """ Assert that an exception is raised. """


# pylint: disable=too-few-public-methods
class CaseExecutor(RequiresAsserts):
  """
    A class to execute test cases.
  """
  def __init__(self,
    function: Callable[[list[str]], tuple[dict[str, None | bool | int | str | set[str]], set[str]]]):
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
      expected_options, expected_parameters = case.expected
      options, parameters = self.function(case.args)
      self.assertDictEqual(expected_options, options)
      self.assertSetEqual(expected_parameters, parameters)
    else:
      assert case.error is not None
      with self.assertRaises(case.error):
        self.function(case.args)

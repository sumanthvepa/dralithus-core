"""
  test_case_executor.py: Unit tests for CaseData and CaseExecutor.
"""
# -------------------------------------------------------------------
# test_case_executor.py: Unit tests for CaseData and CaseExecutor.
#
# Copyright (C) 2026 Sumanth Vepa.
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
import unittest
from typing import Any

from dralithus.project.error import DralithusProjectError
from dralithus.test import CaseData, CaseExecutor


def return_none(_args: Any) -> None:
  """
    Return None regardless of input.

    :param _args: The (ignored) input
    :return: None
  """
  return None


def return_singleton_none(_args: Any) -> list[None]:
  """
    Return a list containing a single None element.

    :param _args: The (ignored) input
    :return: A list whose only element is None
  """
  return [None]


def raise_project_error(message: str) -> None:
  """
    Raise a project error with the supplied message.

    :param message: The error message
    :return: None
    :raises DralithusProjectError: Always
  """
  raise DralithusProjectError(message)


def raise_value_error(message: str) -> None:
  """
    Raise a value error with the supplied message.

    :param message: The error message
    :return: None
    :raises ValueError: Always
  """
  raise ValueError(message)


class TestCaseData(unittest.TestCase):
  """
    Unit tests for CaseData.
  """
  def test_error_message_without_error_is_rejected(self) -> None:
    """
      Verify an error message requires an expected error.

      :return: None
    """
    with self.assertRaises(AssertionError):
      CaseData(
        args=None,
        error_message='Expected message')

  def test_expected_none_is_accepted_as_normal_case(self) -> None:
    """
      Verify a literal None expected value is a normal-result case.

      :return: None
    """
    case = CaseData(args=None, expected=None)
    self.assertFalse(case.expects_error)
    self.assertIsNone(case.expected)

  def test_singleton_none_expected_is_preserved(self) -> None:
    """
      Verify a literal [None] expected value is preserved.

      :return: None
    """
    case = CaseData(args=None, expected=[None])
    self.assertFalse(case.expects_error)
    self.assertEqual(case.expected, [None])

  def test_error_case_may_omit_expected(self) -> None:
    """
      Verify an exception case need not supply expected.

      :return: None
    """
    case = CaseData(args=None, error=ValueError)
    self.assertTrue(case.expects_error)
    self.assertEqual(case.error, ValueError)

  def test_normal_case_may_omit_error(self) -> None:
    """
      Verify a normal-result case need not supply error.

      :return: None
    """
    case = CaseData(args=None, expected='result')
    self.assertFalse(case.expects_error)
    self.assertEqual(case.expected, 'result')

  def test_neither_outcome_is_rejected(self) -> None:
    """
      Verify a case with neither expected nor error is rejected.

      :return: None
    """
    with self.assertRaises(AssertionError):
      CaseData(args=None)

  def test_both_outcomes_are_rejected(self) -> None:
    """
      Verify a case with both expected and error is rejected.

      :return: None
    """
    with self.assertRaises(AssertionError):
      CaseData(args=None, expected='result', error=ValueError)

  def test_expected_none_with_error_is_rejected(self) -> None:
    """
      Verify the old None sentinel form is now rejected.

      :return: None
    """
    with self.assertRaises(AssertionError):
      CaseData(args=None, expected=None, error=ValueError)


class TestCaseExecutor(unittest.TestCase, CaseExecutor):
  """
    Unit tests for CaseExecutor.
  """
  def test_error_type_only_ignores_message(self) -> None:
    """
      Verify an error case without a message checks only its type.

      :return: None
    """
    case = CaseData(
      args='Actual message',
      error=DralithusProjectError)

    self.execute(raise_project_error, case)

  def test_matching_error_message_passes(self) -> None:
    """
      Verify an error case accepts an exact matching message.

      :return: None
    """
    case = CaseData(
      args='Expected message',
      error=DralithusProjectError,
      error_message='Expected message')

    self.execute(raise_project_error, case)

  def test_different_error_message_fails(self) -> None:
    """
      Verify an error case rejects a different message.

      :return: None
    """
    case = CaseData(
      args='Actual message',
      error=DralithusProjectError,
      error_message='Expected message')

    with self.assertRaises(AssertionError):
      self.execute(raise_project_error, case)

  def test_empty_error_message_is_checked(self) -> None:
    """
      Verify an empty expected message is still checked.

      :return: None
    """
    case = CaseData(
      args='Actual message',
      error=DralithusProjectError,
      error_message='')

    with self.assertRaises(AssertionError):
      self.execute(raise_project_error, case)

  def test_non_dralithus_error_message_is_checked(self) -> None:
    """
      Verify message checking works for a non-Dralithus error.

      :return: None
    """
    case = CaseData(
      args='Actual message',
      error=ValueError,
      error_message='Expected message')

    with self.assertRaises(AssertionError):
      self.execute(raise_value_error, case)

  def test_matching_non_dralithus_error_message_passes(self) -> None:
    """
      Verify a matching message passes for a non-Dralithus error.

      :return: None
    """
    case = CaseData(
      args='Expected message',
      error=ValueError,
      error_message='Expected message')

    self.execute(raise_value_error, case)

  def test_none_result_matches_expected_none(self) -> None:
    """
      Verify a function returning None matches expected=None.

      :return: None
    """
    case = CaseData(args=None, expected=None)
    self.execute(return_none, case)

  def test_singleton_none_result_matches_literally(self) -> None:
    """
      Verify a [None] result matches expected=[None] literally.

      :return: None
    """
    case = CaseData(args=None, expected=[None])
    self.execute(return_singleton_none, case)

  def test_none_result_does_not_match_singleton_none(self) -> None:
    """
      Verify [None] is no longer translated to None.

      :return: None
    """
    case = CaseData(args=None, expected=[None])
    with self.assertRaises(AssertionError):
      self.execute(return_none, case)

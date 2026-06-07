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

from dralithus.project.error import DralithusProjectError
from dralithus.test import CaseData, CaseExecutor


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
        expected='result',
        error=None,
        error_message='Expected message')


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
      expected=None,
      error=DralithusProjectError)

    self.execute(raise_project_error, case)

  def test_matching_error_message_passes(self) -> None:
    """
      Verify an error case accepts an exact matching message.

      :return: None
    """
    case = CaseData(
      args='Expected message',
      expected=None,
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
      expected=None,
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
      expected=None,
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
      expected=None,
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
      expected=None,
      error=ValueError,
      error_message='Expected message')

    self.execute(raise_value_error, case)

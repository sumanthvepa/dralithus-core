"""
  test_create_option.py: Unit tests for the CreateOption class.
"""
# -------------------------------------------------------------------
# test_create_option.py: Unit tests for the CreateOption class.
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


class TestCreateOption(unittest.TestCase):
  """
    Unit tests for the CreateOption class.
  """
  def test_is_option_accepts_long_flag(self) -> None:
    """
      Verify that is_option accepts --create.

      :return: None
    """
    self.fail(
      'TODO checkpoint 10: add red assertion for '
      'CreateOption.is_option("--create", None)')

  def test_make_rejects_value(self) -> None:
    """
      Verify that make rejects values for --create.

      :return: None
    """
    self.fail(
      'TODO checkpoint 10: add red assertion for '
      'CreateOption.make("--create=true", None) value rejection')

  def test_add_to_sets_create_project_key(self) -> None:
    """
      Verify that add_to sets the create_project dictionary key.

      :return: None
    """
    self.fail(
      'TODO checkpoint 10: add red assertion for '
      'CreateOption.add_to() dictionary update')

  def test_options_integration_records_create_project(self) -> None:
    """
      Verify that Options records the create_project flag.

      :return: None
    """
    self.fail(
      'TODO checkpoint 10: add red assertion for '
      'Options(["--create"]) integration')

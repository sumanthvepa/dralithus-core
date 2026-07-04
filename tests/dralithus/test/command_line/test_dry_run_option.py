"""
  test_dry_run_option.py: Unit tests for the DryRunOption class.
"""
# -------------------------------------------------------------------
# test_dry_run_option.py: Unit tests for the DryRunOption class.
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

from dralithus.command_line.dry_run_option import DryRunOption
from dralithus.command_line.options import Options


class TestDryRunOption(unittest.TestCase):
  """
    Unit tests for the DryRunOption class.
  """
  def test_is_option_accepts_long_flag(self) -> None:
    """
      Verify that is_option accepts --dry-run.

      :return: None
    """
    self.assertTrue(DryRunOption.is_option('--dry-run', None))

  def test_make_rejects_value(self) -> None:
    """
      Verify that make rejects values for --dry-run.

      :return: None
    """
    with self.assertRaises(ValueError):
      DryRunOption.make('--dry-run=true', None)

  def test_add_to_sets_dry_run_key(self) -> None:
    """
      Verify that add_to sets the dry_run dictionary key.

      :return: None
    """
    option = DryRunOption('dry-run')
    dictionary: dict[str, None | bool | int | str | set[str]] = {}
    option.add_to(dictionary)
    self.assertTrue(dictionary['dry_run'])

  def test_options_integration_records_dry_run(self) -> None:
    """
      Verify that Options records the dry_run flag.

      :return: None
    """
    options = Options(['--dry-run'])
    self.assertFalse(options['create_project'])
    self.assertTrue(options['dry_run'])

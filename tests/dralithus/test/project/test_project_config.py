"""
  test_project_config.py: Unit tests for ProjectConfig.
"""
# -------------------------------------------------------------------
# test_project_config.py: Unit tests for ProjectConfig.
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
from pathlib import Path
import unittest


class TestProjectConfig(unittest.TestCase):
  """
    Unit tests for the ProjectConfig class.
  """
  _CONFIG_PATH = Path('/tmp/project.toml')

  def test_from_toml_file_accepts_valid_python_config(self) -> None:
    """
      Verify from_toml_file accepts a valid Python project config.

      :return: None
    """
    self.fail(
      'TODO checkpoint 6: add red assertion for valid Python '
      'ProjectConfig TOML shape')

  def test_from_toml_file_rejects_pyproject_toml_case_insensitively(
      self
  ) -> None:
    """
      Verify from_toml_file rejects pyproject.toml by filename.

      :return: None
    """
    self.fail(
      'TODO checkpoint 6: add red assertion for pyproject.toml '
      'case-insensitive filename rejection')

  def test_from_toml_file_rejects_unknown_sections_and_keys(self) -> None:
    """
      Verify from_toml_file rejects unknown sections and keys.

      :return: None
    """
    self.fail(
      'TODO checkpoint 6: add red assertion for unknown TOML '
      'sections and keys')

  def test_from_toml_file_requires_all_explicit_fields(self) -> None:
    """
      Verify from_toml_file requires every explicit config field.

      :return: None
    """
    self.fail(
      'TODO checkpoint 6: add red assertion for missing explicit '
      'ProjectConfig fields')

  def test_from_toml_file_rejects_missing_or_unsupported_language(
      self
  ) -> None:
    """
      Verify from_toml_file rejects missing or unsupported language.

      :return: None
    """
    self.fail(
      'TODO checkpoint 6: add red assertion for unsupported or '
      'missing language section')

  def test_from_toml_file_resolves_relative_project_root(self) -> None:
    """
      Verify from_toml_file resolves a relative project root.

      :return: None
    """
    self.fail(
      'TODO checkpoint 6: add red assertion for project.root '
      'resolution relative to the config file')

  def test_from_toml_file_resolves_command_name_python_executable(
      self
  ) -> None:
    """
      Verify from_toml_file resolves a command-name executable.

      :return: None
    """
    self.fail(
      'TODO checkpoint 6: add red assertion for command-name Python '
      'executable resolution')

  def test_from_toml_file_rejects_python_executable_inside_venv(
      self
  ) -> None:
    """
      Verify from_toml_file rejects Python executables inside venv.

      :return: None
    """
    self.fail(
      'TODO checkpoint 6: add red assertion for Python executable '
      'inside the target venv path')

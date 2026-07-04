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
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

from dralithus.project.error import DralithusProjectError
from dralithus.project.project import PythonProject
from dralithus.project.project_config import ProjectConfig


class TestProjectConfig(unittest.TestCase):
  """
    Unit tests for the ProjectConfig class.
  """
  _CONFIG_PATH = Path('/tmp/project.toml')
  _PYTHON = Path(sys.executable)

  @classmethod
  def _config_text(
      cls,
      project_root: str = '.',
      extra_project_lines: str = '',
      language_section: str = '[python]\nexecutable = "python3.14"\n',
      extra_sections: str = ''
  ) -> str:
    """
      Return TOML text for a project config test case.

      :param project_root: The project.root value
      :param extra_project_lines: Extra lines for the project section
      :param language_section: The language section text
      :param extra_sections: Extra trailing sections
      :return: The TOML text for a config file
    """
    return (
      '[project]\n'
      'name = "sample"\n'
      'description = "Sample Project"\n'
      'version = "0.1.0"\n'
      f'root = "{project_root}"\n'
      'package = "sample"\n'
      'venv = "venv"\n'
      f'{extra_project_lines}'
      '\n'
      f'{language_section}'
      '\n'
      '[copyright]\n'
      'holder = "Sumanth Vepa"\n'
      'year = 2026\n'
      'license = "GPL-3.0-or-later"\n'
      f'{extra_sections}')

  @staticmethod
  def _write_config(config_path: Path, contents: str) -> None:
    """
      Write a TOML config file for a test.

      :param config_path: The config file to write
      :param contents: The TOML contents to write
      :return: None
    """
    config_path.write_text(contents, encoding='utf-8')

  def test_from_toml_file_accepts_valid_python_config(self) -> None:
    """
      Verify from_toml_file accepts a valid Python project config.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      config_directory = Path(temp_directory)
      project_root = config_directory / 'workspace'
      project_root.mkdir()
      config_path = config_directory / 'project.toml'
      self._write_config(
        config_path,
        self._config_text(project_root='workspace'))

      with mock.patch('shutil.which', return_value=str(self._PYTHON)):
        config = ProjectConfig.from_toml_file(config_path)

      self.assertEqual(project_root, config.context.project_root)
      self.assertEqual('sample', config.context.project_name)
      self.assertEqual('Sample Project', config.context.project_description)
      self.assertEqual('0.1.0', config.context.project_version)
      self.assertEqual('sample', config.context.package_name)
      self.assertEqual('venv', config.context.venv_name)
      self.assertEqual(self._PYTHON, config.python_executable)
      self.assertIsInstance(config.project(), PythonProject)

  def test_from_toml_file_rejects_pyproject_toml_case_insensitively(
      self
  ) -> None:
    """
      Verify from_toml_file rejects pyproject.toml by filename.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      config_directory = Path(temp_directory)
      project_root = config_directory / 'workspace'
      project_root.mkdir()
      config_path = config_directory / 'PyProject.ToMl'
      self._write_config(
        config_path,
        self._config_text(project_root='workspace'))

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Config filename must not be pyproject.toml'
      ):
        ProjectConfig.from_toml_file(config_path)

  def test_from_toml_file_rejects_unknown_sections_and_keys(self) -> None:
    """
      Verify from_toml_file rejects unknown sections and keys.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      config_directory = Path(temp_directory)
      project_root = config_directory / 'workspace'
      project_root.mkdir()
      cases = {
        'unknown section': self._config_text(
          project_root='workspace',
          extra_sections='[node]\nversion = "22"\n'),
        'unknown key': self._config_text(
          project_root='workspace',
          extra_project_lines='owner = "Milestone 42"\n'),
      }
      for label, contents in cases.items():
        with self.subTest(label=label):
          config_path = config_directory / f'{label}.toml'
          self._write_config(config_path, contents)
          with self.assertRaises(DralithusProjectError):
            ProjectConfig.from_toml_file(config_path)

  def test_from_toml_file_requires_all_explicit_fields(self) -> None:
    """
      Verify from_toml_file requires every explicit config field.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      config_directory = Path(temp_directory)
      project_root = config_directory / 'workspace'
      project_root.mkdir()
      missing_cases = {
        'project.name': (
          '[project]\n'
          'description = "Sample Project"\n'
          'version = "0.1.0"\n'
          'root = "workspace"\n'
          'package = "sample"\n'
          'venv = "venv"\n\n'
          '[python]\n'
          'executable = "python3.14"\n\n'
          '[copyright]\n'
          'holder = "Sumanth Vepa"\n'
          'year = 2026\n'
          'license = "GPL-3.0-or-later"\n'),
        'python.executable': (
          '[project]\n'
          'name = "sample"\n'
          'description = "Sample Project"\n'
          'version = "0.1.0"\n'
          'root = "workspace"\n'
          'package = "sample"\n'
          'venv = "venv"\n\n'
          '[python]\n\n'
          '[copyright]\n'
          'holder = "Sumanth Vepa"\n'
          'year = 2026\n'
          'license = "GPL-3.0-or-later"\n'),
        'copyright.license': (
          '[project]\n'
          'name = "sample"\n'
          'description = "Sample Project"\n'
          'version = "0.1.0"\n'
          'root = "workspace"\n'
          'package = "sample"\n'
          'venv = "venv"\n\n'
          '[python]\n'
          'executable = "python3.14"\n\n'
          '[copyright]\n'
          'holder = "Sumanth Vepa"\n'
          'year = 2026\n'),
      }
      for label, contents in missing_cases.items():
        with self.subTest(label=label):
          config_path = config_directory / f'{label}.toml'
          self._write_config(config_path, contents)
          with self.assertRaises(DralithusProjectError):
            ProjectConfig.from_toml_file(config_path)

  def test_from_toml_file_rejects_missing_or_unsupported_language(
      self
  ) -> None:
    """
      Verify from_toml_file rejects missing or unsupported language.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      config_directory = Path(temp_directory)
      project_root = config_directory / 'workspace'
      project_root.mkdir()
      cases = {
        'missing language': self._config_text(
          project_root='workspace',
          language_section=''),
        'unsupported language': self._config_text(
          project_root='workspace',
          language_section='[node]\nversion = "22"\n'),
      }
      for label, contents in cases.items():
        with self.subTest(label=label):
          config_path = config_directory / f'{label}.toml'
          self._write_config(config_path, contents)
          with self.assertRaises(DralithusProjectError):
            ProjectConfig.from_toml_file(config_path)

  def test_from_toml_file_resolves_relative_project_root(self) -> None:
    """
      Verify from_toml_file resolves a relative project root.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      config_directory = Path(temp_directory) / 'configs'
      project_root = config_directory / 'projects' / 'sample'
      project_root.mkdir(parents=True)
      config_path = config_directory / 'project.toml'
      self._write_config(
        config_path,
        self._config_text(project_root='projects/sample'))

      with mock.patch('shutil.which', return_value=str(self._PYTHON)):
        config = ProjectConfig.from_toml_file(config_path)

      self.assertEqual(project_root, config.context.project_root)

  def test_from_toml_file_resolves_command_name_python_executable(
      self
  ) -> None:
    """
      Verify from_toml_file resolves a command-name executable.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      config_directory = Path(temp_directory)
      project_root = config_directory / 'workspace'
      project_root.mkdir()
      config_path = config_directory / 'project.toml'
      self._write_config(
        config_path,
        self._config_text(
          project_root='workspace',
          language_section='[python]\n'
          'executable = "python3.14"\n'))

      with mock.patch('shutil.which', return_value=str(self._PYTHON)):
        config = ProjectConfig.from_toml_file(config_path)

      self.assertEqual(self._PYTHON, config.python_executable)

  def test_from_toml_file_rejects_python_executable_inside_venv(
      self
  ) -> None:
    """
      Verify from_toml_file rejects Python executables inside venv.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      config_directory = Path(temp_directory)
      project_root = config_directory / 'workspace'
      project_root.mkdir()
      config_path = config_directory / 'project.toml'
      self._write_config(
        config_path,
        self._config_text(
          project_root='workspace',
          language_section='[python]\n'
          'executable = "workspace/venv/bin/python"\n'))

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Python executable must not be inside the target venv'
      ):
        ProjectConfig.from_toml_file(config_path)

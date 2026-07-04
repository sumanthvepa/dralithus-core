"""
  test_project_command.py: Unit tests for ProjectCommand.
"""
# -------------------------------------------------------------------
# test_project_command.py: Unit tests for ProjectCommand.
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
from unittest import mock

from dralithus.command_line.command_line import CommandLine
from dralithus.command_line.options import Options
from dralithus.errors import CommandLineError, ExitCode
from dralithus.project.context import ProjectContext
from dralithus.project.copyright_header import CopyrightHeader
from dralithus.project.project_config import ProjectConfig
from dralithus.project_command import ProjectCommand, make


class TestProjectCommand(unittest.TestCase):
  """
    Unit tests for the ProjectCommand module.
  """
  @staticmethod
  def _config() -> ProjectConfig:
    """
      Return a minimal ProjectConfig for command tests.

      :return: A minimal ProjectConfig instance
    """
    return ProjectConfig(
      ProjectContext(
        project_name='sample',
        project_description='Sample Project',
        project_version='0.1.0',
        project_copyright=CopyrightHeader(
          'Copyright header\n',
          'Sumanth Vepa',
          2026),
        project_root=Path.cwd(),
        package_name='sample',
        venv_name='venv'),
      Path('/usr/bin/python3'))

  def test_make_requires_create_option(self) -> None:
    """
      Verify make rejects a project command without --create.

      :return: None
    """
    cmdln = CommandLine(
      program='drl',
      command_name='project',
      global_options=Options([]),
      command_options=Options([]),
      parameters={'project.toml'})

    with self.assertRaises(CommandLineError):
      make(cmdln)

  def test_make_requires_exactly_one_config_parameter(self) -> None:
    """
      Verify make rejects zero or multiple config parameters.

      :return: None
    """
    cases = (
      CommandLine(
        program='drl',
        command_name='project',
        global_options=Options([]),
        command_options=Options(['--create']),
        parameters=set()),
      CommandLine(
        program='drl',
        command_name='project',
        global_options=Options([]),
        command_options=Options(['--create']),
        parameters={'a.toml', 'b.toml'}))

    for cmdln in cases:
      with self.subTest(parameters=cmdln.parameters):
        with self.assertRaises(CommandLineError):
          make(cmdln)

  def test_make_loads_project_config_from_toml_file(self) -> None:
    """
      Verify make loads ProjectConfig from the config path.

      :return: None
    """
    config = self._config()
    cmdln = CommandLine(
      program='drl',
      command_name='project',
      global_options=Options([]),
      command_options=Options(['--create']),
      parameters={'project.toml'})

    with mock.patch(
      'dralithus.project_command.ProjectConfig.from_toml_file',
      return_value=config
    ) as from_toml_file:
      with self.assertRaises(NotImplementedError):
        make(cmdln)

    from_toml_file.assert_called_once_with(Path('project.toml'))

  def test_make_passes_dry_run_flag_to_project_command(self) -> None:
    """
      Verify make passes the parsed dry-run flag into ProjectCommand.

      :return: None
    """
    config = self._config()
    cmdln = CommandLine(
      program='drl',
      command_name='project',
      global_options=Options([]),
      command_options=Options(['--create', '--dry-run']),
      parameters={'project.toml'})

    with mock.patch(
      'dralithus.project_command.ProjectConfig.from_toml_file',
      return_value=config
    ):
      command = make(cmdln)

    self.assertTrue(command.create_project)
    self.assertTrue(command.dry_run)
    self.assertEqual(config, command.config)
    self.assertEqual(cmdln.verbosity, command.verbosity)

  def test_execute_calls_project_create_with_dry_run_flag(self) -> None:
    """
      Verify execute calls project.create(dry_run=...).

      :return: None
    """
    config = self._config()
    command = ProjectCommand(
      config=config,
      create_project=True,
      dry_run=True,
      verbosity=0)
    project = mock.Mock()

    with mock.patch.object(config, 'project', return_value=project):
      command.execute()

    project.create.assert_called_once_with(dry_run=True)

  def test_execute_returns_success_on_success(self) -> None:
    """
      Verify execute returns ExitCode.SUCCESS on success.

      :return: None
    """
    config = self._config()
    command = ProjectCommand(
      config=config,
      create_project=True,
      dry_run=False,
      verbosity=0)

    with mock.patch.object(config, 'project', return_value=mock.Mock()):
      exit_code = command.execute()

    self.assertEqual(ExitCode.SUCCESS, exit_code)

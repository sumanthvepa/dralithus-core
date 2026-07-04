"""
  project_command.py: Define the ProjectCommand class.
"""
# -------------------------------------------------------------------
# project_command.py: Define the ProjectCommand class.
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
from __future__ import annotations
from pathlib import Path
from typing import override

from dralithus.command import Command
from dralithus.command_line.command_line import CommandLine
from dralithus.errors import CommandLineError, ExitCode
from dralithus.project.project_config import ProjectConfig


class ProjectCommand(Command):
  """
    Represent the project command facade.

    This command remains a thin command-layer wrapper around
    ProjectConfig and the concrete Project facade it produces.
  """
  @override
  def __init__(
      self,
      config: ProjectConfig,
      create_project: bool,
      dry_run: bool,
      verbosity: int
  ) -> None:
    """
      Initialize the project command.

      :param config: The validated project configuration
      :param create_project: True when the command should create
        the project
      :param dry_run: True when execution should be simulated
      :param verbosity: The verbosity level of the command
      :return: None
    """
    super().__init__('project', verbosity)
    self._config = config
    self._create_project = create_project
    self._dry_run = dry_run

  def __eq__(self, other: object) -> bool:
    """
      Check whether two project commands are equal.

      :param other: The other command to compare with
      :return: True when both commands are equal
    """
    if not isinstance(other, ProjectCommand):
      return NotImplemented
    return (
      super().__eq__(other)
      and self.config == other.config
      and self.create_project == other.create_project
      and self.dry_run == other.dry_run)

  @property
  def config(self) -> ProjectConfig:
    """
      Return the validated project configuration.

      :return: The validated project configuration
    """
    return self._config

  @property
  def create_project(self) -> bool:
    """
      Return whether this command should create the project.

      :return: True when the command should create the project
    """
    return self._create_project

  @property
  def dry_run(self) -> bool:
    """
      Return whether this command should run in dry-run mode.

      :return: True when execution should be simulated
    """
    return self._dry_run

  @override
  def execute(self) -> int:
    """
      Execute the project command.

      :return: The program exit code
    """
    project = self.config.project()
    project.create(dry_run=self.dry_run)
    return ExitCode.SUCCESS


def _command_error(cmdln: CommandLine, message: str) -> CommandLineError:
  """
    Build a command-line error for the project command.

    :param cmdln: The parsed command line
    :param message: The validation error message
    :return: The command-line error to raise
  """
  return CommandLineError(
    cmdln.program,
    cmdln.command_name,
    cmdln.verbosity,
    message)


def make(cmdln: CommandLine) -> ProjectCommand:
  """
    Build a project command from parsed command-line input.

    :param cmdln: The parsed command line
    :return: The project command
    :raises CommandLineError: When the command line is invalid
  """
  create_project = cmdln.command_options.get('create_project', False)
  assert isinstance(create_project, bool)
  dry_run = cmdln.command_options.get('dry_run', False)
  assert isinstance(dry_run, bool)

  if cmdln.command_name != 'project':
    raise _command_error(cmdln, 'Unknown command \'project\' specified')
  if not create_project:
    raise _command_error(
      cmdln,
      'No project action specified. Please specify --create.')
  if len(cmdln.parameters) != 1:
    raise _command_error(
      cmdln,
      'Exactly one project config file must be specified.')

  config_parameter = next(iter(cmdln.parameters))
  config = ProjectConfig.from_toml_file(Path(config_parameter))
  return ProjectCommand(config, create_project, dry_run, cmdln.verbosity)

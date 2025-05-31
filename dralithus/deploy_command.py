"""
  deploy_command.py: Define the DeployCommand class.
"""
# -------------------------------------------------------------------
# deploy_command.py: Define the DeployCommand class.
#
# Copyright (C) 2023-25 Sumanth Vepa.
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
from typing_extensions import override

from dralithus.command import Command
from dralithus.command_line.options import Options
from dralithus.environment import Environment
from dralithus.application import Application
from dralithus.errors import ExitCode, CommandLineError


class DeployCommand(Command):
  """
    Command to deploy an application to a target environment.
  """
  @override
  def __init__(
      self, environments: set[Environment],
      applications: set[Application],
      verbosity: int) -> None:
    """
      Initialize the 'deploy' command with a verbosity level.

      :param environments: The environments to deploy the application to
      :param applications: The applications to deploy
      :param verbosity: The verbosity level of the command
    """
    super().__init__("deploy", verbosity)
    assert len(environments) > 0, 'Environments cannot be an empty set.'
    self._environments = environments
    assert len(applications) > 0, 'Applications cannot be an empty set.'
    self._applications = applications

  def __eq__(self, other: object) -> bool:
    """
      Check if two deploy commands are equal.

      :param other: The other command to compare with
      :return: True if the commands are equal, False otherwise
    """
    if not isinstance(other, DeployCommand):
      return NotImplemented
    return (super().__eq__(other)
      and self.environments == other.environments
      and self.applications == other.applications)


  @property
  def environments(self) -> set[Environment]:
    """
      The environments to deploy the application to.

      :return: The environments to deploy the application to
    """
    return self._environments

  @property
  def applications(self) -> set[Application]:
    """
      The applications to deploy.

      :return: The applications to deploy
    """
    return self._applications

  @override
  def execute(self) -> int:
    """
      Execute the 'deploy' command.

      :return: The program exit code
    """
    # TODO: Implement this
    application_names = ', '.join(app.name for app in self.applications)
    environment_names = ', '.join(env.name for env in self.environments)
    print(f'deploy ({application_names}) to ({environment_names}). verbosity={self.verbosity} ')
    return ExitCode.SUCCESS


def make_environments(
    program: str,
    global_options: Options,
    command_options: Options) -> set[Environment]:
  """
    Create a set of environments from the global and command options.

    :param program: The name of the program
    :param global_options: The global options for the command line
    :param command_options: The command options for the command line
    :return: A set of Environment objects
  """
  global_environment_names = global_options.get('environments', set())
  assert (isinstance(global_environment_names, set)
    and all(isinstance(env, str) for env in global_environment_names))
  command_environment_names = command_options.get('environments', set())
  assert (isinstance(command_environment_names, set)
    and all(isinstance(env, str) for env in command_environment_names))
  environment_names = global_environment_names | command_environment_names
  environments = set(Environment.load(name) for name in environment_names)
  if len(environments) == 0:
    raise CommandLineError(
      program,
      'No environments specified. ' \
      + 'Please specify at least one environment.')
  return environments


def make_applications(parameters: set[str]) -> set[Application]:
  """
    Create a set of applications from the command line parameters.

    :param parameters: The parameters for the command line
    :return: A set of Application objects
  """
  applications = set(Application.load(name) for name in parameters)
  assert len(applications) > 0
  return applications


def make_verbosity(global_options: Options, command_options: Options) -> int:
  """
    Determine the verbosity level from the global and command options.

    :param global_options: The global options for the command line
    :param command_options: The command options for the command line
    :return: The verbosity level as an integer
  """
  global_verbosity = global_options.get('verbosity', 0)
  assert isinstance(global_verbosity, int)
  command_verbosity = command_options.get('verbosity', 0)
  assert isinstance(command_verbosity, int)
  return min(global_verbosity + command_verbosity, 3)


def make(
    program: str,
    global_options: Options,
    command_options: Options,
    parameters: set[str]) -> DeployCommand:
  """
    Create a help command from the command line arguments.

    :param program: The name of the program
    :param global_options: The global options for the command line
    :param command_options: The command options for the command line
    :param parameters: The parameters for the command line
    :return: The help command object
  """
  environments = make_environments(program, global_options, command_options)
  applications = make_applications(parameters)
  verbosity = make_verbosity(global_options, command_options)
  return DeployCommand(environments, applications, verbosity)

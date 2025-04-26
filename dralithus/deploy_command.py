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
from typing_extensions import override

from dralithus.command import Command


class DeployCommand(Command):
  """
    Command to deploy an application to a target environment.
  """
  def __init__(self, environments: list[str], applications: list[str], verbosity: int) -> None:
    """
      Initialize the 'deploy' command with a verbosity level.

      :param environments: The environments to deploy the application to
      :param applications: The applications to deploy
      :param verbosity: The verbosity level of the command
    """
    super().__init__("deploy", verbosity)
    self._environments = environments
    self._applications = applications

  @property
  def environments(self) -> list[str]:
    """
      The environments to deploy the application to.

      :return: The environments to deploy the application to
    """
    return self._environments

  @property
  def applications(self) -> list[str]:
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
    raise NotImplementedError("DeployCommand.execute() is not yet implemented")

"""
  test_deploy_command.py: Unit tests for the dralithus.deploy_command
  module
"""
# -------------------------------------------------------------------
# test_deploy_command.py: Unit tests for the dralithus.deploy_command
# module
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

import unittest

from parameterized import parameterized

from dralithus.command_line.command_line import CommandLine
from dralithus.deploy_command import DeployCommand, make
from dralithus.environment import Environment
from dralithus.application import Application
from dralithus.command_line.options import Options
from dralithus.errors import CommandLineError, DralithusEnvironmentError, DralithusApplicationError
from dralithus.test import CaseData, CaseExecutor2


def make_cases() -> list[tuple[str, CaseData]]:
  """
    A list of unittest cases for DeployCommand.make
    :return:
  """
  # pylint: disable=line-too-long
  return [
    ('deploy_command_no_args', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options([]), command_options=Options([]), parameters=set()), expected=None, error=CommandLineError)),
    ('deploy_command_invalid_environment_invalid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options([]), command_options=Options(['--environment=invalid']), parameters={'invalid'}), expected=None, error=DralithusEnvironmentError)),
    ('deploy_command_invalid_environment2_invalid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['--environment=invalid']), command_options=Options([]), parameters={'invalid'}), expected=None, error=DralithusEnvironmentError)),
    ('deploy_command_invalid_environment3_invalid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['--environment=local,invalid']), command_options=Options([]), parameters={'invalid'}), expected=None, error=DralithusEnvironmentError)),
    ('deploy_command_invalid_environment4_invalid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['--environment=invalid,local']), command_options=Options([]), parameters={'invalid'}), expected=None, error=DralithusEnvironmentError)),
    ('deploy_command_valid_environment_invalid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options([]), command_options=Options(['--environment=local']), parameters={'invalid'}), expected=None, error=DralithusApplicationError)),
    ('deploy_command_valid_environment2_invalid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['--environment=local']), command_options=Options([]), parameters={'invalid'}), expected=None, error=DralithusApplicationError)),
    ('deploy_command_valid_environment3_invalid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['--environment=local,development']), command_options=Options([]), parameters={'invalid'}), expected=None, error=DralithusApplicationError)),
    ('deploy_command_invalid_environment_valid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options([]), command_options=Options(['--environment=invalid']), parameters={'sample'}), expected=None, error=DralithusEnvironmentError)),
    ('deploy_command_invalid_environment2_valid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['--environment=invalid']), command_options=Options([]), parameters={'sample'}), expected=None, error=DralithusEnvironmentError)),
    ('deploy_command_invalid_environment3_valid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['--environment=local,invalid']), command_options=Options([]), parameters={'sample'}), expected=None, error=DralithusEnvironmentError)),
    ('deploy_command_invalid_environment4_valid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['--environment=invalid,local']), command_options=Options([]), parameters={'sample'}), expected=None, error=DralithusEnvironmentError)),
    ('deploy_command_valid_environment_valid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options([]), command_options=Options(['--environment=local']), parameters={'sample'}), expected=DeployCommand(environments={Environment.load('local')}, applications={Application.load('sample')}, verbosity=0), error=None)),
    ('deploy_command_valid_environment2_valid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['--environment=local']), command_options=Options([]), parameters={'sample'}), expected=DeployCommand(environments={Environment.load('local')}, applications={Application.load('sample')}, verbosity=0), error=None)),
    ('deploy_command_valid_environment3_valid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options([]), command_options=Options(['--environment=local,development']), parameters={'sample'}), expected=DeployCommand(environments={Environment.load('local'), Environment.load('development')}, applications={Application.load('sample')}, verbosity=0), error=None)),
    ('deploy_command_valid_environment4_valid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['--environment=local,development']), command_options=Options([]), parameters={'sample'}), expected=DeployCommand(environments={Environment.load('local'), Environment.load('development')}, applications={Application.load('sample')}, verbosity=0), error=None)),
    ('deploy_command_valid_environment4_valid_application2', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['--environment=local,development']), command_options=Options([]), parameters={'sample', 'dralithus'}), expected=DeployCommand(environments={Environment.load('local'), Environment.load('development')}, applications={Application.load('sample'), Application.load('dralithus')}, verbosity=0), error=None)),
    ('deploy_command_verbosity_valid_environment_valid_application', CaseData(args=CommandLine(program='drl', command_name='deploy', global_options=Options(['-v']), command_options=Options(['--environment=local']), parameters={'sample'}), expected=DeployCommand(environments={Environment.load('local')}, applications={Application.load('sample')}, verbosity=1), error=None)),
  ]


class TestDeployCommand(unittest.TestCase, CaseExecutor2):
  """
  Unit tests for the HelpCommand class.
  """
  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  @parameterized.expand(make_cases())
  def test_make(self, name: str, case: CaseData) -> None:
    """
    Test the make method of the deploy_command module.
    """
    self.execute(make, case)

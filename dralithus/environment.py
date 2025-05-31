"""
  environment.py: Define the Environment class.
"""
# -------------------------------------------------------------------
# environment.py: Define the Environment class.
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

from dralithus.errors import DralithusEnvironmentError


class Environment:
  """
  Environment class that represents a deployment environment.

  This class encapsulates the details of a deployment environment,
  such as its name, description, and any other relevant metadata.
  """

  def __init__(self, name: str, description: str) -> None:
    """
    Initialize the environment with a name and an optional description.

    :param name: The name of the environment
    :param description: A brief description of the environment
    """
    self._name = name
    self._description = description

  def __str__(self) -> str:
    """
    Return a string representation of the environment.

    :return: A string representation of the environment
    """
    return f'Environment(name={self._name}, description={self._description})'

  @property
  def name(self) -> str:
    """The name of the environment."""
    return self._name

  @property
  def description(self) -> str:
    """A brief description of the environment."""
    return self._description

  @classmethod
  def load(cls, name: str) -> Environment:
    """
    Load an environment by its name.

    This function simulates loading an environment from a data source.
    In a real application, this might involve reading from a database
    or configuration file.

    :param name: The name of the environment to load
    :return: An Environment object representing the loaded environment
    """
    try:
      # TODO: Implement actual loading logic from a data source.
      # Simulated data for demonstration purposes
      environments = {
        'local': Environment('local', 'Local development environment'),
        'development': Environment('development', 'Development environment'),
        'test': Environment('test', 'Test environment'),
        'staging': Environment('staging', 'Staging environment'),
        'production': Environment('production', 'Production environment'),
      }
      return environments[name]
    except KeyError as ex:
      raise DralithusEnvironmentError(f'Environment not found: {name}') from ex

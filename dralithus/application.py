"""
  application.py: Define the Application class.
"""
# -------------------------------------------------------------------
# application.py: Define the Application class.
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
from dralithus.errors import DralithusApplicationError


class Application:
  """
  Application class that represents a deployable application.

  This class encapsulates the details of an application, such as its
  name, version, and any other relevant metadata.
  """

  def __init__(self, name: str, description: str) -> None:
    """
    Initialize the application with a name and version.

    :param name: The name of the application
    :param description: A brief description of the application
    """
    self._name = name
    self._description = description

  def __hash__(self) -> int:
    """
    Return the hash of the application based on its name.

    :return: The hash value of the application
    """
    return hash(self._name)

  def __eq__(self, other: object) -> bool:
    """
    Check if two applications are equal based on their name and description.

    :param other: The other application to compare with
    :return: True if both applications have the same name and description, False otherwise
    """
    if not isinstance(other, Application):
      return NotImplemented
    return self._name == other._name

  def __str__(self) -> str:
    """
    Return a string representation of the application.

    :return: A string representation of the application
    """
    return f'Application(name={self._name}, description={self._description})'

  @property
  def name(self) -> str:
    """The name of the application."""
    return self._name

  @property
  def description(self) -> str:
    """A brief description of the application."""
    return self._description

  @classmethod
  def load(cls, name: str) -> Application:
    """
    Load an application by its name.

    This function simulates loading an application from a data source.
    In a real application, this might involve reading from a database
    or configuration file.

    :param name: The name of the application to load
    :return: An Application instance representing the loaded application
    """
    # Simulate loading an application with a fixed description
    try:
      applications = {
        'dralithus': Application('dralithus', 'The Dralithus application deployment system'),
        'sample': Application('sample', 'A sample application for demonstration purposes')
      }
      return applications[name]
    except KeyError as ex:
      raise DralithusApplicationError(f'Application \'{name}\' not found') from ex

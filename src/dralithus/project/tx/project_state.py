"""
  project_state.py: Define the ProjectState class.
"""
# -------------------------------------------------------------------
# project_state.py: Define the ProjectState class.
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


class ProjectState:
  """
    Model the projected post-commit state of the project tree.

    Overlays the claims declared during prepare() on top of the real
    file system rooted at the project root, so a step can validate
    against artifacts that an earlier step will create at commit
    time. Claims are only projections: ownership of a real artifact
    is established at commit time by exclusive creation, never here.

    All paths are absolute and must lie within the project root.
  """
  # pylint: disable-next=unused-argument
  def __init__(self, project_root: Path) -> None:
    """
      Initialize the projected project state.

      :param project_root: The root directory of the project
      :return: None
    """
    raise NotImplementedError(
      'ProjectState.__init__() is not implemented yet')

  def claim_directory(self, path: Path) -> None:
    """
      Declare that a step will create a directory at path.

      :param path: The absolute path of the projected directory
      :return: None
      :raises DralithusProjectError: When path is not within the
        project root
    """
    raise NotImplementedError(
      'claim_directory() is not implemented yet')

  def claim_file(self, path: Path) -> None:
    """
      Declare that a step will create a regular file at path.

      :param path: The absolute path of the projected file
      :return: None
      :raises DralithusProjectError: When path is not within the
        project root
    """
    raise NotImplementedError(
      'claim_file() is not implemented yet')

  def claim_executable(self, path: Path) -> None:
    """
      Declare that a step will create an executable file at path.

      :param path: The absolute path of the projected executable
      :return: None
      :raises DralithusProjectError: When path is not within the
        project root
    """
    raise NotImplementedError(
      'claim_executable() is not implemented yet')

  def claim_venv(self, path: Path, python_version: str) -> None:
    """
      Declare that a step will create a virtual environment at path.

      :param path: The absolute path of the projected virtual
        environment directory
      :param python_version: The Python version the virtual
        environment will provide
      :return: None
      :raises DralithusProjectError: When path is not within the
        project root
    """
    raise NotImplementedError(
      'claim_venv() is not implemented yet')

  def is_dir(self, path: Path) -> bool:
    """
      Check whether path is a current or projected directory.

      :param path: The absolute path to check
      :return: True if path is a directory on the real file system
        or is claimed as a directory
    """
    raise NotImplementedError(
      'is_dir() is not implemented yet')

  def is_file(self, path: Path) -> bool:
    """
      Check whether path is a current or projected regular file.

      :param path: The absolute path to check
      :return: True if path is a regular file on the real file
        system or is claimed as a file
    """
    raise NotImplementedError(
      'is_file() is not implemented yet')

  def is_executable(self, path: Path) -> bool:
    """
      Check whether path is a current or projected executable file.

      :param path: The absolute path to check
      :return: True if path is an executable file on the real file
        system or is claimed as an executable
    """
    raise NotImplementedError(
      'is_executable() is not implemented yet')

  def venv_python_version(self, path: Path) -> str | None:
    """
      Return the Python version of a current or projected venv.

      :param path: The absolute path of the virtual environment
        directory
      :return: The Python version the virtual environment at path
        provides, or None when no venv exists or is claimed there
    """
    raise NotImplementedError(
      'venv_python_version() is not implemented yet')

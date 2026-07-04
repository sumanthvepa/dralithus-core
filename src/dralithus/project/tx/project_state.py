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
import os
from pathlib import Path

from dralithus.project.error import DralithusProjectError


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
  def _validate_path(self, path: Path) -> Path:
    """
      Validate that a path is absolute and within the project root.

      :param path: The path to validate
      :return: The validated path
      :raises DralithusProjectError: When path is relative or lies
        outside the project root
    """
    if not path.is_absolute():
      raise DralithusProjectError(f'Path must be absolute: {path}')
    if not path.is_relative_to(self._project_root):
      raise DralithusProjectError(
        f'Path is not within the project root: {path}')
    return path

  @staticmethod
  def _real_is_dir(path: Path) -> bool:
    """
      Check whether path is a directory on the real file system.

      :param path: The path to check
      :return: True if path is a real directory
      :raises DralithusProjectError: When the path cannot be
        inspected
    """
    try:
      return path.is_dir()
    except OSError as error:
      raise DralithusProjectError(
        f'Could not inspect path: {path}') from error

  @staticmethod
  def _real_is_file(path: Path) -> bool:
    """
      Check whether path is a regular file on the real file system.

      :param path: The path to check
      :return: True if path is a real regular file
      :raises DralithusProjectError: When the path cannot be
        inspected
    """
    try:
      return path.is_file()
    except OSError as error:
      raise DralithusProjectError(
        f'Could not inspect path: {path}') from error

  @staticmethod
  def _real_is_executable(path: Path) -> bool:
    """
      Check whether path is an executable file on the real file
      system.

      :param path: The path to check
      :return: True if path is a real executable regular file
      :raises DralithusProjectError: When the path cannot be
        inspected
    """
    try:
      return path.is_file() and os.access(path, os.X_OK)
    except OSError as error:
      raise DralithusProjectError(
        f'Could not inspect path: {path}') from error

  @staticmethod
  def _read_venv_version(pyvenv_cfg: Path) -> str | None:
    """
      Read the Python version from a venv's pyvenv.cfg file.

      :param pyvenv_cfg: The pyvenv.cfg path to read
      :return: The version value, or None when the file has no
        version entry
      :raises DralithusProjectError: When the file cannot be read
    """
    version: str | None = None
    try:
      for line in pyvenv_cfg.read_text(encoding='utf-8').splitlines():
        name, separator, value = line.partition('=')
        if separator == '=' and name.strip() == 'version':
          version = value.strip()
          break
    except (OSError, UnicodeError) as error:
      raise DralithusProjectError(
        f'Could not read venv metadata: {pyvenv_cfg}') from error
    return version

  def __init__(self, project_root: Path) -> None:
    """
      Initialize the projected project state.

      :param project_root: The root directory of the project
      :return: None
    """
    self._project_root = project_root
    self._directories: set[Path] = set()
    self._files: set[Path] = set()
    self._executables: set[Path] = set()
    self._venvs: dict[Path, str] = {}

  def claim_directory(self, path: Path) -> None:
    """
      Declare that a step will create a directory at path.

      :param path: The absolute path of the projected directory
      :return: None
      :raises DralithusProjectError: When path is not within the
        project root
    """
    self._directories.add(self._validate_path(path))

  def claim_file(self, path: Path) -> None:
    """
      Declare that a step will create a regular file at path.

      :param path: The absolute path of the projected file
      :return: None
      :raises DralithusProjectError: When path is not within the
        project root
    """
    self._files.add(self._validate_path(path))

  def claim_executable(self, path: Path) -> None:
    """
      Declare that a step will create an executable file at path.

      :param path: The absolute path of the projected executable
      :return: None
      :raises DralithusProjectError: When path is not within the
        project root
    """
    self._executables.add(self._validate_path(path))

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
    self._venvs[self._validate_path(path)] = python_version

  def is_dir(self, path: Path) -> bool:
    """
      Check whether path is a current or projected directory.

      :param path: The absolute path to check
      :return: True if path is a directory on the real file system
        or is claimed as a directory
      :raises DralithusProjectError: When path is not within the
        project root or cannot be inspected
    """
    path = self._validate_path(path)
    return (
      path in self._directories
      or path in self._venvs
      or self._real_is_dir(path))

  def is_file(self, path: Path) -> bool:
    """
      Check whether path is a current or projected regular file.

      :param path: The absolute path to check
      :return: True if path is a regular file on the real file
        system or is claimed as a file
      :raises DralithusProjectError: When path is not within the
        project root or cannot be inspected
    """
    path = self._validate_path(path)
    return (
      path in self._files
      or path in self._executables
      or self._real_is_file(path))

  def is_executable(self, path: Path) -> bool:
    """
      Check whether path is a current or projected executable file.

      :param path: The absolute path to check
      :return: True if path is an executable file on the real file
        system or is claimed as an executable
      :raises DralithusProjectError: When path is not within the
        project root or cannot be inspected
    """
    path = self._validate_path(path)
    return (
      path in self._executables
      or self._real_is_executable(path))

  def venv_python_version(self, path: Path) -> str | None:
    """
      Return the Python version of a current or projected venv.

      A venv claim takes precedence over a real venv at the same
      path, because the claim projects the post-commit state.

      :param path: The absolute path of the virtual environment
        directory
      :return: The Python version the virtual environment at path
        provides, or None when no venv exists or is claimed there
      :raises DralithusProjectError: When path is not within the
        project root or the venv metadata cannot be read
    """
    path = self._validate_path(path)
    version = self._venvs.get(path)
    if version is None:
      pyvenv_cfg = path / 'pyvenv.cfg'
      if self._real_is_file(pyvenv_cfg):
        version = self._read_venv_version(pyvenv_cfg)
    return version

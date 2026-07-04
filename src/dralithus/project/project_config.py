"""
  project_config.py: Define the ProjectConfig class.
"""
# -------------------------------------------------------------------
# project_config.py: Define the ProjectConfig class.
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
import shutil
import tomllib
from typing import Self

from dralithus.project.copyright_header import CopyrightHeader
from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.project import Project, PythonProject


class ProjectConfig:
  """
    Hold validated project-creation configuration.

    This command-facing model is distinct from ProjectContext. It
    stores the validated context and the resolved Python executable
    needed to build the concrete project facade.
  """
  _PROJECT_SECTION = 'project'
  _PYTHON_SECTION = 'python'
  _COPYRIGHT_SECTION = 'copyright'

  @staticmethod
  def _validate_config_filename(config_path: Path) -> None:
    """
      Validate that config_path is not named pyproject.toml.

      :param config_path: The configuration file path
      :return: None
      :raises DralithusProjectError: When the filename is forbidden
    """
    if config_path.name.lower() == 'pyproject.toml':
      raise DralithusProjectError(
        'Config filename must not be pyproject.toml')

  @staticmethod
  def _load_toml(config_path: Path) -> dict[str, object]:
    """
      Load a TOML configuration file.

      :param config_path: The configuration file path
      :return: The parsed TOML document
      :raises DralithusProjectError: When the file cannot be read or
        parsed as TOML
    """
    try:
      with config_path.open('rb') as config_file:
        data = tomllib.load(config_file)
    except (OSError, tomllib.TOMLDecodeError) as error:
      raise DralithusProjectError(
        f'Could not load project config: {config_path}') from error
    return data

  @staticmethod
  def _require_dict(
    mapping: dict[str, object],
    key: str
  ) -> dict[str, object]:
    """
      Return a required nested table from a TOML mapping.

      :param mapping: The source mapping
      :param key: The required table name
      :return: The nested table mapping
      :raises DralithusProjectError: When the table is missing or not
        a TOML table
    """
    value = mapping.get(key)
    if isinstance(value, dict):
      section = value
    else:
      raise DralithusProjectError(f'Missing required section: {key}')
    return section

  @staticmethod
  def _reject_unknown_keys(
    mapping: dict[str, object],
    allowed_keys: set[str],
    section_name: str
  ) -> None:
    """
      Reject unknown keys in a TOML mapping.

      :param mapping: The mapping to validate
      :param allowed_keys: The allowed keys in the mapping
      :param section_name: The human-readable section name
      :return: None
      :raises DralithusProjectError: When unknown keys are present
    """
    unknown_keys = set(mapping) - allowed_keys
    if unknown_keys:
      key_list = ', '.join(sorted(unknown_keys))
      raise DralithusProjectError(
        f'Unknown keys in {section_name}: {key_list}')

  @staticmethod
  def _require_str(
    mapping: dict[str, object],
    key: str,
    section_name: str
  ) -> str:
    """
      Return a required string value from a TOML mapping.

      :param mapping: The source mapping
      :param key: The required key
      :param section_name: The human-readable section name
      :return: The string value
      :raises DralithusProjectError: When the key is missing or not a
        string
    """
    value = mapping.get(key)
    if isinstance(value, str):
      result = value
    else:
      raise DralithusProjectError(
        f'Missing required field: {section_name}.{key}')
    return result

  @staticmethod
  def _require_int(
    mapping: dict[str, object],
    key: str,
    section_name: str
  ) -> int:
    """
      Return a required integer value from a TOML mapping.

      :param mapping: The source mapping
      :param key: The required key
      :param section_name: The human-readable section name
      :return: The integer value
      :raises DralithusProjectError: When the key is missing or not an
        integer
    """
    value = mapping.get(key)
    if isinstance(value, int) and not isinstance(value, bool):
      result = value
    else:
      raise DralithusProjectError(
        f'Missing required field: {section_name}.{key}')
    return result

  @staticmethod
  def _is_path_like(value: str) -> bool:
    """
      Return whether a Python executable value should be treated as a path.

      :param value: The executable value from the config
      :return: True when the value contains a path separator
    """
    separators = {os.sep}
    if os.altsep is not None:
      separators.add(os.altsep)
    return any(separator in value for separator in separators)

  @classmethod
  def _resolve_python_executable(
    cls,
    config_directory: Path,
    executable_value: str
  ) -> Path:
    """
      Resolve the configured Python executable.

      :param config_directory: The config file's parent directory
      :param executable_value: The configured executable string
      :return: The resolved executable path
      :raises DralithusProjectError: When a command name cannot be
        resolved
    """
    if cls._is_path_like(executable_value):
      executable_path = Path(executable_value)
      if executable_path.is_absolute():
        resolved = executable_path
      else:
        resolved = config_directory / executable_path
    else:
      resolved_command = shutil.which(executable_value)
      if resolved_command is None:
        raise DralithusProjectError(
          f'Could not resolve Python executable: {executable_value}')
      resolved = Path(resolved_command)
    return resolved

  @staticmethod
  def _validate_python_executable_not_inside_venv(
    python_executable: Path,
    context: ProjectContext
  ) -> None:
    """
      Reject a Python executable inside the target venv path.

      :param python_executable: The resolved Python executable path
      :param context: The project context whose venv path to inspect
      :return: None
      :raises DralithusProjectError: When the executable is inside the
        target venv path
    """
    executable_parts = python_executable.resolve(
      strict=False).parts
    venv_parts = context.venv_path.resolve(strict=False).parts
    if executable_parts[:len(venv_parts)] == venv_parts:
      raise DralithusProjectError(
        'Python executable must not be inside the target venv')

  @classmethod
  def _validate_top_level(
    cls,
    data: dict[str, object]
  ) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    """
      Validate the top-level TOML layout and return its sections.

      :param data: The parsed TOML document
      :return: The project, python, and copyright sections
      :raises DralithusProjectError: When the top-level layout is
        invalid
    """
    cls._reject_unknown_keys(
      data,
      {
        cls._PROJECT_SECTION,
        cls._PYTHON_SECTION,
        cls._COPYRIGHT_SECTION,
      },
      'top-level config')
    project_section = cls._require_dict(data, cls._PROJECT_SECTION)
    copyright_section = cls._require_dict(
      data, cls._COPYRIGHT_SECTION)
    if cls._PYTHON_SECTION in data:
      python_section = cls._require_dict(data, cls._PYTHON_SECTION)
    else:
      raise DralithusProjectError('Missing required section: python')
    return project_section, python_section, copyright_section

  @classmethod
  def _build_context(
    cls,
    config_directory: Path,
    project_section: dict[str, object],
    copyright_section: dict[str, object]
  ) -> ProjectContext:
    """
      Build a ProjectContext from validated TOML sections.

      :param config_directory: The config file's parent directory
      :param project_section: The validated project table
      :param copyright_section: The validated copyright table
      :return: The built project context
      :raises DralithusProjectError: When required values are missing
        or invalid
    """
    cls._reject_unknown_keys(
      project_section,
      {'name', 'description', 'version', 'root', 'package', 'venv'},
      'project')
    cls._reject_unknown_keys(
      copyright_section,
      {'holder', 'year', 'license'},
      'copyright')
    project_root_value = cls._require_str(
      project_section, 'root', 'project')
    project_root = config_directory / Path(project_root_value)
    return ProjectContext(
      project_name=cls._require_str(project_section, 'name', 'project'),
      project_description=cls._require_str(
        project_section, 'description', 'project'),
      project_version=cls._require_str(
        project_section, 'version', 'project'),
      project_copyright=CopyrightHeader.from_license(
        cls._require_str(copyright_section, 'license', 'copyright'),
        cls._require_str(copyright_section, 'holder', 'copyright'),
        cls._require_int(copyright_section, 'year', 'copyright')),
      project_root=project_root,
      package_name=cls._require_str(
        project_section, 'package', 'project'),
      venv_name=cls._require_str(project_section, 'venv', 'project'))

  def __init__(
      self,
      context: ProjectContext,
      python_executable: Path
  ) -> None:
    """
      Initialize the project configuration.

      :param context: The validated project creation context
      :param python_executable: The resolved Python executable
      :return: None
    """
    self._context = context
    self._python_executable = python_executable

  @property
  def context(self) -> ProjectContext:
    """
      Return the validated project context.

      :return: The validated project context
    """
    return self._context

  @property
  def python_executable(self) -> Path:
    """
      Return the resolved Python executable.

      :return: The resolved Python executable
    """
    return self._python_executable

  def project(self) -> Project:
    """
      Build the concrete project facade for this configuration.

      :return: The project facade for this configuration
    """
    return PythonProject(self.context, self.python_executable)

  @classmethod
  def from_toml_file(cls, config_path: Path) -> Self:
    """
      Create a ProjectConfig from a TOML configuration file.

      :param config_path: The TOML configuration file path
      :return: The validated project configuration
      :raises DralithusProjectError: When the config is invalid
    """
    cls._validate_config_filename(config_path)
    data = cls._load_toml(config_path)
    project_section, python_section, copyright_section = (
      cls._validate_top_level(data))
    cls._reject_unknown_keys(python_section, {'executable'}, 'python')
    config_directory = config_path.parent
    context = cls._build_context(
      config_directory, project_section, copyright_section)
    python_executable = cls._resolve_python_executable(
      config_directory,
      cls._require_str(python_section, 'executable', 'python'))
    cls._validate_python_executable_not_inside_venv(
      python_executable,
      context)
    return cls(context, python_executable)

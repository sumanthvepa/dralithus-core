"""
  project/__init__.py: Unit tests for project creation classes.
"""
# -------------------------------------------------------------------
# project/__init__.py: Unit tests for project creation classes.
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
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import IO

from dralithus.project.context import ProjectContext
from dralithus.project.copyright_header import CopyrightHeader
from dralithus.project.packages import Packages


_IMPLICIT_DEV_DEPENDENCIES = ['mypy', 'pylint', 'parameterized']
_COPYRIGHT_TEMPLATE = (
  '{{ description }}\n'
  'Copyright (C) {{ copyright_year }} {{ copyright_holder }}.\n')


def write_package_artifacts(
  project_root: Path,
  production_dependencies: list[str] | None = None,
  dev_dependencies: list[str] | None = None,
  local_dependencies: list[str] | None = None,
  local_dev_dependencies: list[str] | None = None
) -> Packages:
  """
    Write package artifacts and return their Packages model.

    :param project_root: The project root directory
    :param production_dependencies: The packages.txt dependencies
    :param dev_dependencies: The full expected dev dependency list
    :param local_dependencies: The local-packages.txt dependencies
    :param local_dev_dependencies: The local dev dependencies
    :return: The Packages model
  """
  if production_dependencies is None:
    production_dependencies = []
  if dev_dependencies is None:
    dev_dependencies = _IMPLICIT_DEV_DEPENDENCIES
  if local_dependencies is None:
    local_dependencies = []
  if local_dev_dependencies is None:
    local_dev_dependencies = []
  extra_dev_dependencies = [
    dependency for dependency in dev_dependencies
    if dependency not in _IMPLICIT_DEV_DEPENDENCIES]
  package_lines = [
    *production_dependencies,
    *[f'{dependency} [dev]'
      for dependency in extra_dev_dependencies]]
  local_lines = [
    *local_dependencies,
    *[f'{dependency} [dev]'
      for dependency in local_dev_dependencies]]
  (project_root / Packages.PACKAGES_FILENAME).write_text(
    '\n'.join(package_lines),
    encoding='utf-8')
  if local_lines:
    (project_root / Packages.LOCAL_PACKAGES_FILENAME).write_text(
      '\n'.join(local_lines),
      encoding='utf-8')
  return Packages(project_root)


@contextmanager
def project_context(
  venv_name: str = 'venv'
) -> Iterator[tuple[Path, ProjectContext]]:
  """
    Yield a temporary project root and matching ProjectContext.

    :param venv_name: The virtual environment directory name
    :return: An iterator yielding the project root and context
  """
  with TemporaryDirectory() as temp_directory:
    project_root = Path(temp_directory)
    copyright_header = CopyrightHeader(
      _COPYRIGHT_TEMPLATE,
      'Sumanth Vepa',
      2026)
    yield project_root, ProjectContext(
      project_root=project_root,
      package_name='sample',
      copyright_header=copyright_header,
      venv_name=venv_name)


class FailingWriteFile:
  """
    Wrap a real open file and fail every write.

    Simulates a write failure (such as a full disk) that strikes
    after an exclusive open has already created the file on disk.
  """
  def __init__(self, file: IO[str]) -> None:
    """
      Initialize the failing write wrapper.

      :param file: The real open file to wrap
      :return: None
    """
    self._file = file

  def __enter__(self) -> 'FailingWriteFile':
    """
      Enter the context manager.

      :return: This wrapper
    """
    return self

  def __exit__(self, *exc_info: object) -> None:
    """
      Close the wrapped file on context exit.

      :param exc_info: The exception information, if any
      :return: None
    """
    self._file.close()

  def write(self, _content: str) -> int:
    """
      Fail the write.

      :param _content: The content that would have been written
      :return: Never returns
      :raises OSError: Always
    """
    raise OSError('simulated write failure')

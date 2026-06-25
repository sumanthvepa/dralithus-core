# -*- coding: utf-8 -*-
"""
dralithus/test/__init__.py: Helper classes and functions for unit tests
"""
# -------------------------------------------------------------------
# dralithus/test/__init__.py: Helper classes and functions for unit
# tests
#
# Copyright 2023-25. Sumanth Vepa. svepa@milestone42.com
#
# This file is part of dralithus-core.
#
# dralithus-core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dralithus-core is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dralithus-core. If not, see <https://www.gnu.org/licenses/>.
# -------------------------------------------------------------------
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Callable, IO, Protocol

from dralithus.project.context import ProjectContext
from dralithus.project.packages import Packages


# Private sentinel used to detect whether a caller supplied an
# expected value. It lets a literal None be a valid expected result,
# distinct from "no expected value was given".
_UNSET: Any = object()
_IMPLICIT_DEV_DEPENDENCIES = ['mypy', 'pylint', 'parameterized']


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
    yield project_root, ProjectContext(
      project_root=project_root,
      package_name='sample',
      copyright_holder='Sumanth Vepa',
      copyright_year=2026,
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


class CaseData:
  """
    A test case for dralithus
  """
  def __init__(
        self,
        args: Any,
        expected: Any = _UNSET,
        error: type[Exception] | None = None,
        error_message: str | None = None):
    """
      Initialize the test case.

      Exactly one outcome must be supplied: either an expected value
      (a normal-result case, including a literal None) or an error
      type (an exception case). An error message may accompany an
      error.

      :param args: The input to the test case
      :param expected: The expected output of the test case
      :param error: The expected error of the test case
      :param error_message: The expected error message
    """
    expected_supplied = expected is not _UNSET
    assert expected_supplied != (error is not None), (
      'Exactly one of expected or error must be supplied.')
    assert error_message is None or error is not None, (
      'An error message can only be specified when an error is expected.')
    self._args = args
    self._expected = expected
    self._error = error
    self._error_message = error_message

  @property
  def args(self) -> Any:
    """
      Get the input of the test case.

      :return: The input of the test case
    """
    return self._args

  @property
  def expects_error(self) -> bool:
    """
      Return whether this case expects an exception.

      :return: True for an exception case, False for a normal case
    """
    return self._expected is _UNSET

  @property
  def expected(self) -> Any:
    """
      Get the expected output of the test case.

      :return: The expected output of the test case
    """
    assert not self.expects_error, (
      'expected is not defined for an exception case.')
    return self._expected

  @property
  def error(self) -> type[Exception] | None:
    """
      Get the expected error of the test case.

      :return: The expected error of the test case
    """
    return self._error

  @property
  def error_message(self) -> str | None:
    """
      Get the expected error message of the test case.

      :return: The expected error message
    """
    return self._error_message


class RequiresAsserts(Protocol):
  """ Protocol for objects requiring assert methods used by CaseExecutor. """
  # pylint: disable=invalid-name
  # noinspection PyPep8Naming
  def assertEqual(self, first: Any, second: Any, msg: str | None = None) -> None:
    """ Assert that two values are equal. """

  # pylint: disable=invalid-name
  # noinspection PyPep8Naming
  def assertRaises(
    self,
    expected_exception:  type[BaseException] | tuple[type[BaseException], ...],
    *args: Any,
    **kwargs: Any) -> Any:
    """ Assert that an exception is raised. """


class CaseExecutor(RequiresAsserts):
  """
    A class to execute test cases.
  """
  def execute(self, function: Callable[..., Any], case: CaseData) -> None:
    """
      Execute a test case.

      :param function: The function to execute
      :param case: The test case to execute
    """
    if case.expects_error:
      assert case.error is not None
      # IntelliJ IDEA's type checker is not smart enough to figure out
      # that case.error cannot be None at this point.
      # noinspection PyTypeChecker
      with self.assertRaises(case.error) as context:
        function(case.args)
      if case.error_message is not None:
        self.assertEqual(
          case.error_message,
          str(context.exception))
    else:
      expected = case.expected
      actual = function(case.args)
      self.assertEqual(
        expected, actual, f'Expected {expected} but got {actual}')

"""
  test_create_venv_step.py: Unit tests for create_venv_step.
"""
# -------------------------------------------------------------------
# test_create_venv_step.py: Unit tests for create_venv_step.
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
import stat
import sys
import unittest

from dralithus.test import project_context
from dralithus.project.create_venv_step import CreateVenvStep
from dralithus.project.error import DralithusProjectError


class TestCreateVenvStep(unittest.TestCase):
  """
    Unit tests for the CreateVenvStep class.
  """
  @staticmethod
  def _python_executable() -> Path:
    """
      Return the Python executable used to run the test suite. This
      uses the executable running the test suite itself as the python
      interpreter to ensure compatibility with the test

      :return: The Python executable path
    """
    return Path(sys.executable)

  def test_run_creates_default_venv(self) -> None:
    """
      Verify that run creates a default project-relative venv.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = project_root / 'venv'

      step.run()

      self.assertTrue(target.is_dir())
      self.assertTrue((target / 'pyvenv.cfg').is_file())

  def test_run_creates_named_venv_directory(self) -> None:
    """
      Verify that run creates the context-named venv directory.

      :return: None
    """
    with project_context(venv_name='env') as (_project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = context.venv_path

      step.run()

      self.assertTrue(target.is_dir())
      self.assertTrue((target / 'pyvenv.cfg').is_file())

  def test_run_dry_run_does_not_create_venv(self) -> None:
    """
      Verify that dry-run mode does not create a venv.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())

      step.run(dry_run=True)

      self.assertFalse((project_root / 'venv').exists())

  def test_run_dry_run_validates_existing_file(self) -> None:
    """
      Verify that dry-run mode validates the venv path.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / 'venv').touch()
      step = CreateVenvStep(context, self._python_executable())

      with self.assertRaises(DralithusProjectError):
        step.run(dry_run=True)

  def test_rollback_removes_venv_created_by_step(self) -> None:
    """
      Verify that rollback removes the venv created by the step.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = project_root / 'venv'

      step.run()
      step.rollback()

      self.assertFalse(target.exists())

  def test_rollback_removes_venv_after_multiple_runs(self) -> None:
    """
      Verify rollback removes a venv after multiple run calls.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = project_root / 'venv'

      step.run()
      self.assertTrue(target.is_dir())
      step.run()
      step.rollback()

      self.assertFalse(target.exists())

  def test_rollback_dry_run_does_not_remove_venv(self) -> None:
    """
      Verify that rollback dry-run mode leaves the venv in place.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = project_root / 'venv'

      step.run()
      step.rollback(dry_run=True)

      self.assertTrue(target.is_dir())

  def test_rollback_does_not_remove_preexisting_venv(self) -> None:
    """
      Verify that rollback leaves a preexisting venv in place.

      :return: None
    """
    with project_context() as (project_root, context):
      target = project_root / 'venv'
      step = CreateVenvStep(context, self._python_executable())
      step.run()
      step = CreateVenvStep(context, self._python_executable())

      step.run()
      step.rollback()

      self.assertTrue(target.is_dir())
      self.assertTrue((target / 'pyvenv.cfg').is_file())

  def test_run_raises_error_when_venv_path_is_plain_directory(self) -> None:
    """
      Verify that run raises an error when venv path is not a venv.

      :return: None
    """
    with project_context() as (project_root, context):
      target = project_root / 'venv'
      target.mkdir()
      step = CreateVenvStep(context, self._python_executable())

      with self.assertRaisesRegex(DralithusProjectError, 'Path is not a venv'):
        step.run()

      self.assertTrue(target.is_dir())

  def test_init_rejects_missing_python_executable(self) -> None:
    """
      Verify that missing Python executables are rejected.

      :return: None
    """
    with project_context() as (project_root, context):
      executable = project_root / 'missing-python'

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Python executable does not exist'
      ):
        CreateVenvStep(context, executable)

  def test_init_rejects_python_executable_directory(self) -> None:
    """
      Verify that Python executable directories are rejected.

      :return: None
    """
    with project_context() as (project_root, context):
      executable = project_root

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Python executable is not a file'
      ):
        CreateVenvStep(context, executable)

  def test_init_rejects_non_executable_python_file(self) -> None:
    """
      Verify that non-executable Python files are rejected.

      :return: None
    """
    with project_context() as (project_root, context):
      executable = project_root / 'python'
      executable.write_text('#!/bin/sh\n', encoding='utf-8')

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Python executable is not executable'
      ):
        CreateVenvStep(context, executable)

  def test_init_rejects_executable_that_is_not_python(self) -> None:
    """
      Verify that executable non-Python files are rejected.

      :return: None
    """
    with project_context() as (project_root, context):
      executable = project_root / 'not-python'
      executable.write_text(
        '#!/bin/sh\n'
        'echo "not python"\n',
        encoding='utf-8')
      executable.chmod(
        executable.stat().st_mode
        | stat.S_IXUSR
        | stat.S_IXGRP
        | stat.S_IXOTH)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Executable is not Python'
      ):
        CreateVenvStep(context, executable)

  def test_run_raises_error_when_venv_path_is_file(self) -> None:
    """
      Verify that run raises an error when venv path is a file.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / 'venv').touch()
      step = CreateVenvStep(context, self._python_executable())

      with self.assertRaises(DralithusProjectError):
        step.run()

  def test_init_wraps_python_execution_failure(self) -> None:
    """
      Verify that Python execution failures are wrapped.

      :return: None
    """
    with project_context() as (project_root, context):
      executable = project_root / 'not-python'
      executable.write_text('#!/bin/sh\nexit 1\n', encoding='utf-8')
      executable.chmod(
        executable.stat().st_mode
        | stat.S_IXUSR
        | stat.S_IXGRP
        | stat.S_IXOTH)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Python executable failed version check'
      ):
        CreateVenvStep(context, executable)

  def test_rollback_wraps_venv_removal_failure(self) -> None:
    """
      Verify that venv removal failures are wrapped.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = project_root / 'venv'

      step.run()
      step.rollback(dry_run=True)
      target.rename(project_root / 'saved-venv')
      target.touch()

      with self.assertRaises(DralithusProjectError):
        step.rollback()

      self.assertTrue(target.is_file())

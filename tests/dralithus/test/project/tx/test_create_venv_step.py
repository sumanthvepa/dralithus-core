"""
  test_create_venv_step.py: Unit tests for
  dralithus.project.tx.create_venv_step.
"""
# -------------------------------------------------------------------
# test_create_venv_step.py: Unit tests for
# dralithus.project.tx.create_venv_step.
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
import subprocess
import sys
import unittest

from dralithus.test.project import project_context
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.create_venv_step import CreateVenvStep
from dralithus.project.tx.project_state import ProjectState


# pylint: disable-next=too-many-public-methods
class TestCreateVenvStep(unittest.TestCase):
  """
    Unit tests for the CreateVenvStep class.

    These tests port the behavioral contract of the run/rollback
    CreateVenvStep to prepare/commit/abort. The constructor still
    validates and probes the Python executable, so prepare() can
    claim the projected venv with a version derived from the same
    source the real run uses.
  """
  @staticmethod
  def _python_executable() -> Path:
    """
      Return the Python executable used to run the test suite. This
      uses the executable running the test suite itself as the
      python interpreter to ensure compatibility with the test.

      :return: The Python executable path
    """
    return Path(sys.executable)

  @classmethod
  def _probed_version(cls) -> str:
    """
      Return the version the test interpreter reports, without the
      'Python ' prefix.

      :return: The interpreter version string
    """
    result = subprocess.run(
      [str(cls._python_executable()), '--version'],
      capture_output=True,
      check=True,
      text=True)
    version = result.stdout.strip() or result.stderr.strip()
    return version.removeprefix('Python ')

  @staticmethod
  def _make_fake_venv(venv_path: Path, version: str = '3.13.1') -> None:
    """
      Create a fake venv directory with pyvenv.cfg metadata.

      :param venv_path: The venv directory to create
      :param version: The version to record in pyvenv.cfg
      :return: None
    """
    venv_path.mkdir()
    (venv_path / 'pyvenv.cfg').write_text(
      f'version = {version}\n', encoding='utf-8')

  # constructor

  def test_init_rejects_missing_python_executable(self) -> None:
    """
      Verify the constructor rejects a missing Python executable.

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
      Verify the constructor rejects a directory as the Python
      executable.

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
      Verify the constructor rejects a file without execute
      permission.

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
      Verify the constructor rejects an executable that does not
      report a Python version.

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

  def test_init_wraps_python_execution_failure(self) -> None:
    """
      Verify the constructor wraps a failure running the Python
      executable.

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

  # prepare

  def test_prepare_claims_venv_with_probed_version(self) -> None:
    """
      Verify prepare claims the absent venv as a projected
      directory whose Python version matches the probed executable,
      and claims the venv Python as a projected executable.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertTrue(state.is_dir(context.venv_path))
      self.assertEqual(
        self._probed_version(),
        state.venv_python_version(context.venv_path))
      self.assertTrue(state.is_executable(context.venv_python))

  def test_prepare_accepts_preexisting_venv(self) -> None:
    """
      Verify prepare accepts an existing venv directory with venv
      metadata, declaring no claim of its own.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context.venv_path, version='3.13.1')
      step = CreateVenvStep(context, self._python_executable())
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertEqual(
        '3.13.1', state.venv_python_version(context.venv_path))

  def test_prepare_rejects_plain_directory_venv_path(self) -> None:
    """
      Verify prepare rejects a venv path occupied by a directory
      without venv metadata.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / 'venv').mkdir()
      step = CreateVenvStep(context, self._python_executable())

      with self.assertRaisesRegex(
        DralithusProjectError, 'Path is not a venv'
      ):
        step.prepare(ProjectState(project_root))

  def test_prepare_rejects_file_venv_path(self) -> None:
    """
      Verify prepare rejects a venv path occupied by a regular
      file.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / 'venv').touch()
      step = CreateVenvStep(context, self._python_executable())

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_creates_nothing_on_disk(self) -> None:
    """
      Verify prepare performs no file system mutation.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())

      step.prepare(ProjectState(project_root))

      self.assertFalse((project_root / 'venv').exists())

  # commit

  def test_commit_creates_default_venv(self) -> None:
    """
      Verify commit creates a venv in the default venv directory.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = project_root / 'venv'

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertTrue(target.is_dir())
      self.assertTrue((target / 'pyvenv.cfg').is_file())

  def test_commit_creates_named_venv_directory(self) -> None:
    """
      Verify commit creates the venv in the context's named venv
      directory.

      :return: None
    """
    with project_context(venv_name='env') as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = context.venv_path

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertTrue(target.is_dir())
      self.assertTrue((target / 'pyvenv.cfg').is_file())

  def test_commit_preserves_preexisting_venv(self) -> None:
    """
      Verify commit accepts an existing venv without recreating it
      and without taking ownership of it.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context.venv_path, version='3.13.1')
      step = CreateVenvStep(context, self._python_executable())

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertEqual(
        'version = 3.13.1\n',
        (context.venv_path / 'pyvenv.cfg').read_text(encoding='utf-8'))

  def test_repeated_commits_are_convergent(self) -> None:
    """
      Verify committing twice leaves one venv and abort still
      removes it.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = project_root / 'venv'

      # The phase-call sequence repeats across step suites; a future
      # refactoring could extract a shared helper.
      # pylint: disable=duplicate-code
      step.prepare(ProjectState(project_root))
      step.commit()
      step.commit()
      step.abort()

      self.assertFalse(target.exists())

  # abort

  def test_abort_removes_venv_created_by_commit(self) -> None:
    """
      Verify abort removes a venv created by commit.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = project_root / 'venv'

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse(target.exists())

  def test_abort_is_idempotent(self) -> None:
    """
      Verify abort can be called again after removing the venv.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = project_root / 'venv'

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()
      step.abort()

      self.assertFalse(target.exists())

  def test_abort_preserves_preexisting_venv(self) -> None:
    """
      Verify abort leaves a pre-existing venv in place.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context.venv_path, version='3.13.1')
      step = CreateVenvStep(context, self._python_executable())

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertTrue(context.venv_path.is_dir())
      self.assertTrue((context.venv_path / 'pyvenv.cfg').is_file())

  def test_abort_wraps_venv_removal_failure(self) -> None:
    """
      Verify abort wraps a failure removing the created venv.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateVenvStep(context, self._python_executable())
      target = project_root / 'venv'

      step.prepare(ProjectState(project_root))
      step.commit()
      target.rename(project_root / 'saved-venv')
      target.touch()

      with self.assertRaises(DralithusProjectError):
        step.abort()

      self.assertTrue(target.is_file())

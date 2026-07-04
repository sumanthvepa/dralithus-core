"""
  test_project_state.py: Unit tests for
  dralithus.project.tx.project_state.
"""
# -------------------------------------------------------------------
# test_project_state.py: Unit tests for
# dralithus.project.tx.project_state.
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
import unittest

from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.project_state import ProjectState


@contextmanager
def _project_state() -> Iterator[tuple[Path, ProjectState]]:
  """
    Yield a temporary project root and a ProjectState over it.

    :return: An iterator yielding the project root and state
  """
  with TemporaryDirectory() as temp_directory:
    project_root = Path(temp_directory)
    yield project_root, ProjectState(project_root)


# pylint: disable-next=too-many-public-methods
class TestProjectState(unittest.TestCase):
  """
    Unit tests for the ProjectState class.

    ProjectState overlays claims declared during prepare() on top of
    the real file system rooted at the project root. These tests
    cover the overlay semantics: real-only, claim-only, and
    claim-over-real, plus each query against each claim kind, and
    the containment rule that every path must lie within the project
    root.
  """
  # containment

  def test_claims_reject_path_outside_project_root(self) -> None:
    """
      Verify every claim method rejects an absolute path that lies
      outside the project root.

      :return: None
    """
    with _project_state() as (project_root, state):
      outside = project_root.parent / 'outside'
      with self.assertRaises(DralithusProjectError):
        state.claim_directory(outside)
      with self.assertRaises(DralithusProjectError):
        state.claim_file(outside)
      with self.assertRaises(DralithusProjectError):
        state.claim_executable(outside)
      with self.assertRaises(DralithusProjectError):
        state.claim_venv(outside, '3.14.2')

  def test_claims_reject_relative_path(self) -> None:
    """
      Verify every claim method rejects a relative path.

      :return: None
    """
    with _project_state() as (_project_root, state):
      relative = Path('src')
      with self.assertRaises(DralithusProjectError):
        state.claim_directory(relative)
      with self.assertRaises(DralithusProjectError):
        state.claim_file(relative)
      with self.assertRaises(DralithusProjectError):
        state.claim_executable(relative)
      with self.assertRaises(DralithusProjectError):
        state.claim_venv(relative, '3.14.2')

  def test_queries_reject_path_outside_project_root(self) -> None:
    """
      Verify every query method rejects an absolute path that lies
      outside the project root.

      :return: None
    """
    with _project_state() as (project_root, state):
      outside = project_root.parent / 'outside'
      with self.assertRaises(DralithusProjectError):
        state.is_dir(outside)
      with self.assertRaises(DralithusProjectError):
        state.is_file(outside)
      with self.assertRaises(DralithusProjectError):
        state.is_executable(outside)
      with self.assertRaises(DralithusProjectError):
        state.venv_python_version(outside)

  # is_dir

  def test_is_dir_true_for_real_directory(self) -> None:
    """
      Verify is_dir sees a directory on the real file system.

      :return: None
    """
    with _project_state() as (project_root, state):
      (project_root / 'src').mkdir()

      self.assertTrue(state.is_dir(project_root / 'src'))

  def test_is_dir_true_for_claimed_directory(self) -> None:
    """
      Verify is_dir sees a claimed directory that does not exist on
      the real file system.

      :return: None
    """
    with _project_state() as (project_root, state):
      state.claim_directory(project_root / 'src')

      self.assertTrue(state.is_dir(project_root / 'src'))

  def test_is_dir_true_for_claimed_venv(self) -> None:
    """
      Verify is_dir sees a claimed virtual environment directory.

      :return: None
    """
    with _project_state() as (project_root, state):
      state.claim_venv(project_root / 'venv', '3.14.2')

      self.assertTrue(state.is_dir(project_root / 'venv'))

  def test_is_dir_false_for_absent_path(self) -> None:
    """
      Verify is_dir is False for a path neither real nor claimed.

      :return: None
    """
    with _project_state() as (project_root, state):
      self.assertFalse(state.is_dir(project_root / 'src'))

  def test_is_dir_false_for_real_file(self) -> None:
    """
      Verify is_dir is False for a regular file on the real file
      system.

      :return: None
    """
    with _project_state() as (project_root, state):
      (project_root / 'src').write_text('content\n', encoding='utf-8')

      self.assertFalse(state.is_dir(project_root / 'src'))

  def test_is_dir_false_for_claimed_file(self) -> None:
    """
      Verify is_dir is False for a path claimed as a regular file.

      :return: None
    """
    with _project_state() as (project_root, state):
      state.claim_file(project_root / 'config.ini')

      self.assertFalse(state.is_dir(project_root / 'config.ini'))

  def test_claim_over_real_directory_is_accepted(self) -> None:
    """
      Verify claiming a directory that already exists on the real
      file system is accepted and is_dir remains True.

      :return: None
    """
    with _project_state() as (project_root, state):
      (project_root / 'src').mkdir()

      state.claim_directory(project_root / 'src')

      self.assertTrue(state.is_dir(project_root / 'src'))

  # is_file

  def test_is_file_true_for_real_file(self) -> None:
    """
      Verify is_file sees a regular file on the real file system.

      :return: None
    """
    with _project_state() as (project_root, state):
      (project_root / 'config.ini').write_text(
        'setting = value\n', encoding='utf-8')

      self.assertTrue(state.is_file(project_root / 'config.ini'))

  def test_is_file_true_for_claimed_file(self) -> None:
    """
      Verify is_file sees a claimed file that does not exist on the
      real file system.

      :return: None
    """
    with _project_state() as (project_root, state):
      state.claim_file(project_root / 'config.ini')

      self.assertTrue(state.is_file(project_root / 'config.ini'))

  def test_is_file_true_for_claimed_executable(self) -> None:
    """
      Verify is_file sees a claimed executable, because a projected
      executable is also a projected regular file.

      :return: None
    """
    with _project_state() as (project_root, state):
      state.claim_executable(project_root / 'venv' / 'bin' / 'python')

      self.assertTrue(
        state.is_file(project_root / 'venv' / 'bin' / 'python'))

  def test_is_file_false_for_absent_path(self) -> None:
    """
      Verify is_file is False for a path neither real nor claimed.

      :return: None
    """
    with _project_state() as (project_root, state):
      self.assertFalse(state.is_file(project_root / 'config.ini'))

  def test_is_file_false_for_real_directory(self) -> None:
    """
      Verify is_file is False for a directory on the real file
      system.

      :return: None
    """
    with _project_state() as (project_root, state):
      (project_root / 'src').mkdir()

      self.assertFalse(state.is_file(project_root / 'src'))

  def test_is_file_false_for_claimed_directory(self) -> None:
    """
      Verify is_file is False for a path claimed as a directory.

      :return: None
    """
    with _project_state() as (project_root, state):
      state.claim_directory(project_root / 'src')

      self.assertFalse(state.is_file(project_root / 'src'))

  # is_executable

  def test_is_executable_true_for_real_executable_file(self) -> None:
    """
      Verify is_executable sees an executable file on the real file
      system.

      :return: None
    """
    with _project_state() as (project_root, state):
      executable = project_root / 'script.sh'
      executable.write_text('#!/bin/sh\n', encoding='utf-8')
      executable.chmod(0o755)

      self.assertTrue(state.is_executable(executable))

  def test_is_executable_true_for_claimed_executable(self) -> None:
    """
      Verify is_executable sees a claimed executable that does not
      exist on the real file system.

      :return: None
    """
    with _project_state() as (project_root, state):
      state.claim_executable(project_root / 'venv' / 'bin' / 'python')

      self.assertTrue(
        state.is_executable(project_root / 'venv' / 'bin' / 'python'))

  def test_is_executable_false_for_non_executable_real_file(
    self
  ) -> None:
    """
      Verify is_executable is False for a real file without execute
      permission.

      :return: None
    """
    with _project_state() as (project_root, state):
      plain = project_root / 'config.ini'
      plain.write_text('setting = value\n', encoding='utf-8')
      plain.chmod(0o644)

      self.assertFalse(state.is_executable(plain))

  def test_is_executable_false_for_absent_path(self) -> None:
    """
      Verify is_executable is False for a path neither real nor
      claimed.

      :return: None
    """
    with _project_state() as (project_root, state):
      self.assertFalse(
        state.is_executable(project_root / 'script.sh'))

  def test_is_executable_false_for_claimed_plain_file(self) -> None:
    """
      Verify is_executable is False for a path claimed as a plain
      regular file.

      :return: None
    """
    with _project_state() as (project_root, state):
      state.claim_file(project_root / 'config.ini')

      self.assertFalse(
        state.is_executable(project_root / 'config.ini'))

  # venv_python_version

  def test_venv_python_version_returns_claimed_version(self) -> None:
    """
      Verify venv_python_version returns the version recorded by a
      venv claim.

      :return: None
    """
    with _project_state() as (project_root, state):
      state.claim_venv(project_root / 'venv', '3.14.2')

      self.assertEqual(
        '3.14.2',
        state.venv_python_version(project_root / 'venv'))

  def test_venv_python_version_reads_real_venv_configuration(
    self
  ) -> None:
    """
      Verify venv_python_version reads the version of a real venv
      from its pyvenv.cfg.

      :return: None
    """
    with _project_state() as (project_root, state):
      venv_path = project_root / 'venv'
      venv_path.mkdir()
      (venv_path / 'pyvenv.cfg').write_text(
        'home = /usr/local/bin\n'
        'include-system-site-packages = false\n'
        'version = 3.13.1\n',
        encoding='utf-8')

      self.assertEqual(
        '3.13.1', state.venv_python_version(venv_path))

  def test_venv_python_version_prefers_claim_over_real_venv(
    self
  ) -> None:
    """
      Verify a venv claim takes precedence over a real venv at the
      same path, because the claim projects the post-commit state.

      :return: None
    """
    with _project_state() as (project_root, state):
      venv_path = project_root / 'venv'
      venv_path.mkdir()
      (venv_path / 'pyvenv.cfg').write_text(
        'version = 3.13.1\n', encoding='utf-8')

      state.claim_venv(venv_path, '3.14.2')

      self.assertEqual(
        '3.14.2', state.venv_python_version(venv_path))

  def test_venv_python_version_none_for_absent_venv(self) -> None:
    """
      Verify venv_python_version is None when no venv exists or is
      claimed at the path.

      :return: None
    """
    with _project_state() as (project_root, state):
      self.assertIsNone(
        state.venv_python_version(project_root / 'venv'))

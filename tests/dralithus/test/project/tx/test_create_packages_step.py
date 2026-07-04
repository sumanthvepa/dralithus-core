"""
  test_create_packages_step.py: Unit tests for
  dralithus.project.tx.create_packages_step.
"""
# -------------------------------------------------------------------
# test_create_packages_step.py: Unit tests for
# dralithus.project.tx.create_packages_step.
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
import unittest
from unittest import mock

from dralithus.test.project import FailingWriteFile, project_context
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages
from dralithus.project.tx.create_packages_step import (
  CreatePackagesStep)
from dralithus.project.tx.project_state import ProjectState


# pylint: disable-next=too-many-public-methods
class TestCreatePackagesStep(unittest.TestCase):
  """
    Unit tests for the CreatePackagesStep class.

    These tests port the behavioral contract of the run/rollback
    CreatePackagesStep to prepare/commit/abort, carrying over the
    exclusive-create ownership rule and the documented symlink,
    dangling-symlink and TOCTOU handling. prepare() additionally
    validates existing dependency files, which the old dry run
    never did.
  """
  @staticmethod
  def _packages_txt(project_root: Path) -> Path:
    """
      Return the project packages.txt path.

      :param project_root: The project root directory
      :return: The packages.txt path
    """
    return project_root / Packages.PACKAGES_FILENAME

  @staticmethod
  def _local_packages_txt(project_root: Path) -> Path:
    """
      Return the project local-packages.txt path.

      :param project_root: The project root directory
      :return: The local-packages.txt path
    """
    return project_root / Packages.LOCAL_PACKAGES_FILENAME

  # prepare

  def test_prepare_claims_both_dependency_files(self) -> None:
    """
      Verify prepare claims packages.txt and local-packages.txt as
      current-or-projected files.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreatePackagesStep(context)
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertTrue(state.is_file(self._packages_txt(project_root)))
      self.assertTrue(
        state.is_file(self._local_packages_txt(project_root)))

  def test_prepare_accepts_existing_dependency_files(self) -> None:
    """
      Verify prepare accepts existing dependency files that parse.

      :return: None
    """
    with project_context() as (project_root, context):
      self._packages_txt(project_root).write_text(
        'requests\n', encoding='utf-8')
      self._local_packages_txt(project_root).write_text(
        '../common-lib\n', encoding='utf-8')
      step = CreatePackagesStep(context)
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertTrue(state.is_file(self._packages_txt(project_root)))
      self.assertTrue(
        state.is_file(self._local_packages_txt(project_root)))

  def test_prepare_rejects_unreadable_packages_txt(self) -> None:
    """
      Verify prepare rejects an existing packages.txt that cannot
      be read.

      :return: None
    """
    with project_context() as (project_root, context):
      self._packages_txt(project_root).mkdir()
      step = CreatePackagesStep(context)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Could not read dependency file'
      ):
        step.prepare(ProjectState(project_root))

  def test_prepare_rejects_dangling_local_packages_symlink(
    self
  ) -> None:
    """
      Verify prepare rejects a dangling local-packages.txt symlink.

      :return: None
    """
    with project_context() as (project_root, context):
      local_packages_txt = self._local_packages_txt(project_root)
      local_packages_txt.symlink_to(project_root / 'does-not-exist')
      step = CreatePackagesStep(context)

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Could not read dependency file'
      ):
        step.prepare(ProjectState(project_root))

      self.assertTrue(local_packages_txt.is_symlink())

  def test_prepare_creates_nothing_on_disk(self) -> None:
    """
      Verify prepare performs no file system mutation.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))

      self.assertFalse(self._packages_txt(project_root).exists())
      self.assertFalse(self._local_packages_txt(project_root).exists())

  # commit

  def test_commit_creates_packages_files(self) -> None:
    """
      Verify commit creates both dependency files when absent.

      :return: None
    """
    with project_context() as (project_root, context):
      packages_txt = self._packages_txt(project_root)
      local_packages_txt = self._local_packages_txt(project_root)
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertTrue(packages_txt.is_file())
      self.assertTrue(local_packages_txt.is_file())
      self.assertTrue(
        packages_txt.read_text(encoding='utf-8').startswith('#'))
      self.assertTrue(
        local_packages_txt.read_text(encoding='utf-8').startswith('#'))

  def test_commit_writes_header_content(self) -> None:
    """
      Verify the created dependency files contain the expected
      header comments.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      packages_text = self._packages_txt(project_root).read_text(
        encoding='utf-8')
      local_text = self._local_packages_txt(project_root).read_text(
        encoding='utf-8')
      self.assertEqual(
        '# Third-party packages, one per line.\n'
        '# Append " [dev]" to mark a development-only dependency.\n',
        packages_text)
      self.assertEqual(
        '# Local editable packages, one path per line.\n'
        '# Append " [dev]" to mark a development-only dependency.\n',
        local_text)

  def test_commit_keeps_existing_packages_txt(self) -> None:
    """
      Verify commit preserves a pre-existing packages.txt and
      creates only the missing local-packages.txt.

      :return: None
    """
    with project_context() as (project_root, context):
      packages_txt = self._packages_txt(project_root)
      packages_txt.write_text('requests\n', encoding='utf-8')
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertEqual(
        'requests\n', packages_txt.read_text(encoding='utf-8'))
      self.assertTrue(self._local_packages_txt(project_root).is_file())

  def test_commit_keeps_existing_local_packages_txt(self) -> None:
    """
      Verify commit preserves a pre-existing local-packages.txt and
      creates only the missing packages.txt.

      :return: None
    """
    with project_context() as (project_root, context):
      local_packages_txt = self._local_packages_txt(project_root)
      local_packages_txt.write_text('../common-lib\n', encoding='utf-8')
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertEqual(
        '../common-lib\n',
        local_packages_txt.read_text(encoding='utf-8'))
      self.assertTrue(self._packages_txt(project_root).is_file())

  def test_commit_write_failure_removes_partially_created_files(
    self
  ) -> None:
    """
      Verify a write failure on the second file removes the files
      this commit already created.

      :return: None
    """
    real_open = Path.open

    def fail_local_open(
      path: Path,
      mode: str = 'r',
      encoding: str | None = None
    ) -> object:
      if mode == 'x' and path.name == Packages.LOCAL_PACKAGES_FILENAME:
        raise OSError('simulated write failure')
      # The caller is responsible for closing.
      # pylint: disable-next=consider-using-with
      return real_open(path, mode, encoding=encoding)

    with project_context() as (project_root, context):
      step = CreatePackagesStep(context)
      step.prepare(ProjectState(project_root))

      with mock.patch.object(Path, 'open', fail_local_open):
        with self.assertRaises(DralithusProjectError) as context_manager:
          step.commit()

      self.assertEqual(
        f'Could not write dependency file: {project_root}',
        str(context_manager.exception))
      self.assertFalse(self._packages_txt(project_root).exists())
      self.assertFalse(self._local_packages_txt(project_root).exists())

  def test_commit_write_failure_after_creation_removes_file(
    self
  ) -> None:
    """
      Verify a content-write failure after exclusive creation
      removes the created file, because ownership was recorded
      before the write.

      :return: None
    """
    real_open = Path.open

    def failing_open(
      path: Path,
      mode: str = 'r',
      encoding: str | None = None
    ) -> object:
      # The wrapper (or the caller) is responsible for closing.
      # pylint: disable-next=consider-using-with
      file = real_open(path, mode, encoding=encoding)
      if mode == 'x' and path.name == Packages.PACKAGES_FILENAME:
        return FailingWriteFile(file)
      return file

    with project_context() as (project_root, context):
      step = CreatePackagesStep(context)
      step.prepare(ProjectState(project_root))

      with mock.patch.object(Path, 'open', failing_open):
        with self.assertRaises(DralithusProjectError) as context_manager:
          step.commit()

      self.assertEqual(
        f'Could not write dependency file: {project_root}',
        str(context_manager.exception))
      self.assertFalse(self._packages_txt(project_root).exists())
      self.assertFalse(self._local_packages_txt(project_root).exists())

  def test_commit_removes_created_files_when_validation_fails(
    self
  ) -> None:
    """
      Verify commit removes the files it created when the combined
      dependency files fail validation, such as when a dangling
      local-packages.txt symlink appeared after prepare (TOCTOU).

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreatePackagesStep(context)
      step.prepare(ProjectState(project_root))

      local_packages_txt = self._local_packages_txt(project_root)
      local_packages_txt.symlink_to(project_root / 'does-not-exist')

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Could not read dependency file'
      ):
        step.commit()

      self.assertTrue(local_packages_txt.is_symlink())
      self.assertFalse(self._packages_txt(project_root).exists())

  # abort

  def test_abort_removes_created_files(self) -> None:
    """
      Verify abort removes the dependency files created by commit.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse(self._packages_txt(project_root).exists())
      self.assertFalse(self._local_packages_txt(project_root).exists())

  def test_abort_is_idempotent(self) -> None:
    """
      Verify abort can be called again after removing the created
      files.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()
      step.abort()

      self.assertFalse(self._packages_txt(project_root).exists())
      self.assertFalse(self._local_packages_txt(project_root).exists())

  def test_abort_keeps_preexisting_files(self) -> None:
    """
      Verify abort preserves pre-existing dependency files.

      :return: None
    """
    with project_context() as (project_root, context):
      packages_txt = self._packages_txt(project_root)
      packages_txt.write_text('requests\n', encoding='utf-8')
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertEqual(
        'requests\n', packages_txt.read_text(encoding='utf-8'))
      self.assertFalse(self._local_packages_txt(project_root).exists())

  def test_abort_preserves_preexisting_local_packages_txt(
    self
  ) -> None:
    """
      Verify abort removes only the created packages.txt when
      local-packages.txt existed before commit.

      :return: None
    """
    with project_context() as (project_root, context):
      local_packages_txt = self._local_packages_txt(project_root)
      local_packages_txt.write_text('../common-lib\n', encoding='utf-8')
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertEqual(
        '../common-lib\n',
        local_packages_txt.read_text(encoding='utf-8'))
      self.assertFalse(self._packages_txt(project_root).exists())

  def test_abort_accepts_already_removed_file(self) -> None:
    """
      Verify abort accepts a created file that was removed
      externally.

      :return: None
    """
    with project_context() as (project_root, context):
      packages_txt = self._packages_txt(project_root)
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      packages_txt.unlink()
      step.abort()

      self.assertFalse(packages_txt.exists())
      self.assertFalse(self._local_packages_txt(project_root).exists())

  def test_abort_wraps_removal_failure(self) -> None:
    """
      Verify abort wraps a failure removing a created file.

      :return: None
    """
    with project_context() as (project_root, context):
      packages_txt = self._packages_txt(project_root)
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      packages_txt.unlink()
      packages_txt.mkdir()

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Could not remove dependency file'
      ):
        step.abort()

  def test_repeated_commits_are_convergent(self) -> None:
    """
      Verify committing twice leaves one set of files and abort
      still removes them.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreatePackagesStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.commit()
      step.abort()

      self.assertFalse(self._packages_txt(project_root).exists())
      self.assertFalse(self._local_packages_txt(project_root).exists())

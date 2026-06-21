"""
  test_create_packages_step.py: Unit tests for create_packages_step.
"""
# -------------------------------------------------------------------
# test_create_packages_step.py: Unit tests for create_packages_step.
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
from tempfile import TemporaryDirectory
from typing import IO
import unittest
from unittest import mock

from dralithus.project.context import ProjectContext
from dralithus.project.create_packages_step import CreatePackagesStep
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages


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


class TestCreatePackagesStep(unittest.TestCase):
  """
    Unit tests for the CreatePackagesStep class.
  """
  def test_run_creates_packages_files(self) -> None:
    """
      Verify that run creates both dependency files in an empty
      project root.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      local_packages_txt = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME)
      step = CreatePackagesStep()

      step.run(context)

      self.assertTrue(packages_txt.is_file())
      self.assertTrue(local_packages_txt.is_file())
      self.assertTrue(
        packages_txt.read_text(encoding='utf-8').startswith('#'))
      self.assertTrue(
        local_packages_txt.read_text(encoding='utf-8').startswith('#'))

  def test_run_keeps_existing_packages_txt(self) -> None:
    """
      Verify that run leaves an existing packages.txt untouched and
      creates only the missing local-packages.txt.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      packages_txt.write_text('requests\n', encoding='utf-8')
      step = CreatePackagesStep()

      step.run(context)

      self.assertEqual(
        'requests\n', packages_txt.read_text(encoding='utf-8'))
      self.assertTrue(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).is_file())

  def test_run_keeps_existing_local_packages_txt(self) -> None:
    """
      Verify that run leaves an existing local-packages.txt untouched
      and creates only the missing packages.txt.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      local_packages_txt = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME)
      local_packages_txt.write_text('../common-lib\n', encoding='utf-8')
      step = CreatePackagesStep()

      step.run(context)

      self.assertEqual(
        '../common-lib\n',
        local_packages_txt.read_text(encoding='utf-8'))
      self.assertTrue(
        (project_root / Packages.PACKAGES_FILENAME).is_file())

  def test_run_dry_run_creates_nothing(self) -> None:
    """
      Verify that dry-run mode does not create dependency files.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePackagesStep()

      step.run(context, dry_run=True)

      self.assertFalse(
        (project_root / Packages.PACKAGES_FILENAME).exists())
      self.assertFalse(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).exists())

  def test_run_raises_when_packages_txt_unreadable(self) -> None:
    """
      Verify that run raises when an existing packages.txt cannot be
      read.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      packages_txt.mkdir()
      step = CreatePackagesStep()

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Could not read dependency file'
      ):
        step.run(context)

  def test_run_writes_header_content(self) -> None:
    """
      Verify the created dependency files contain exactly the
      header comments.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePackagesStep()

      step.run(context)

      packages_text = (
        project_root / Packages.PACKAGES_FILENAME).read_text(
          encoding='utf-8')
      local_text = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME).read_text(
          encoding='utf-8')
      self.assertEqual(
        '# Third-party packages, one per line.\n'
        '# Append " [dev]" to mark a development-only dependency.\n',
        packages_text)
      self.assertEqual(
        '# Local editable packages, one path per line.\n'
        '# Append " [dev]" to mark a development-only dependency.\n',
        local_text)

  def test_run_write_failure_removes_partially_created_files(
    self
  ) -> None:
    """
      Verify a run that fails writing a dependency file removes the
      files it already created before raising.

      The first dependency file is written for real; the write of
      the second is forced to fail. The failed run must not leave
      the first file behind.

      :return: None
    """
    real_create_file = (
      CreatePackagesStep._create_file)  # pylint: disable=protected-access

    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePackagesStep()

      def fail_local(path: Path, content: str) -> None:
        if path.name == Packages.LOCAL_PACKAGES_FILENAME:
          raise OSError('simulated write failure')
        real_create_file(step, path, content)

      with mock.patch.object(
        CreatePackagesStep, '_create_file', side_effect=fail_local
      ):
        with self.assertRaises(DralithusProjectError) as context_manager:
          step.run(context)

      self.assertEqual(
        f'Could not write dependency file: {project_root}',
        str(context_manager.exception))
      self.assertFalse(
        (project_root / Packages.PACKAGES_FILENAME).exists())
      self.assertFalse(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).exists())

  def test_run_write_failure_after_creation_removes_file(self) -> None:
    """
      Verify a run whose write fails after exclusive creation
      removes the created file before raising.

      The exclusive open creates packages.txt on disk, but writing
      its content then fails. The failed run must not leave the
      empty partially written file behind, where a later run would
      accept it as a pre-existing dependency file.

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

    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePackagesStep()

      with mock.patch.object(Path, 'open', failing_open):
        with self.assertRaises(DralithusProjectError) as context_manager:
          step.run(context)

      self.assertEqual(
        f'Could not write dependency file: {project_root}',
        str(context_manager.exception))
      self.assertFalse(
        (project_root / Packages.PACKAGES_FILENAME).exists())
      self.assertFalse(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).exists())

  def test_run_failure_removes_partially_created_files(self) -> None:
    """
      Verify that a failed run removes the dependency files it
      created before failing.

      An unreadable packages.txt is detected only after the missing
      local-packages.txt has been created; the failed run must not
      leave the created file behind.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      (project_root / Packages.PACKAGES_FILENAME).mkdir()
      step = CreatePackagesStep()

      with self.assertRaises(DralithusProjectError):
        step.run(context)

      self.assertFalse(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).exists())

  def test_rollback_removes_created_files(self) -> None:
    """
      Verify that rollback removes the dependency files created by
      the step.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePackagesStep()

      step.run(context)
      step.rollback(context)

      self.assertFalse(
        (project_root / Packages.PACKAGES_FILENAME).exists())
      self.assertFalse(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).exists())

  def test_rollback_keeps_preexisting_files(self) -> None:
    """
      Verify that rollback leaves pre-existing dependency files in
      place while removing the files the step created.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      packages_txt.write_text('requests\n', encoding='utf-8')
      step = CreatePackagesStep()

      step.run(context)
      step.rollback(context)

      self.assertEqual(
        'requests\n', packages_txt.read_text(encoding='utf-8'))
      self.assertFalse(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).exists())

  def test_rollback_removes_files_after_multiple_runs(self) -> None:
    """
      Verify rollback removes created files after multiple run calls.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePackagesStep()

      step.run(context)
      step.run(context)
      step.rollback(context)

      self.assertFalse(
        (project_root / Packages.PACKAGES_FILENAME).exists())
      self.assertFalse(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).exists())

  def test_rollback_dry_run_keeps_files(self) -> None:
    """
      Verify that rollback dry-run mode leaves created files in
      place.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePackagesStep()

      step.run(context)
      step.rollback(context, dry_run=True)

      self.assertTrue(
        (project_root / Packages.PACKAGES_FILENAME).is_file())
      self.assertTrue(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).is_file())

  def test_rollback_accepts_already_removed_file(self) -> None:
    """
      Verify that rollback succeeds when a created dependency file
      has already been removed externally.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      step = CreatePackagesStep()

      step.run(context)
      packages_txt.unlink()
      step.rollback(context)

      self.assertFalse(packages_txt.exists())
      self.assertFalse(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).exists())

  def test_run_raises_on_dangling_local_packages_symlink(self) -> None:
    """
      Verify run fails loudly on a dangling local-packages.txt
      symlink rather than silently accepting it.

      The step refuses to claim the existing symlink, so it creates
      only the missing packages.txt. Validation then constructs a
      Packages model, which cannot read the dangling symlink and
      raises. The failed run removes the packages.txt it created and
      leaves the user-owned symlink in place.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      local_packages_txt = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME)
      local_packages_txt.symlink_to(project_root / 'does-not-exist')
      step = CreatePackagesStep()

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Could not read dependency file'
      ):
        step.run(context)

      self.assertTrue(local_packages_txt.is_symlink())
      self.assertFalse(
        (project_root / Packages.PACKAGES_FILENAME).exists())

  def test_rollback_preserves_file_appearing_after_stale_check(
    self
  ) -> None:
    """
      Verify rollback preserves a file the step did not create.

      Simulates the time-of-check to time-of-use race: an existing
      local-packages.txt is hidden from Path.exists during run, as
      it would be for a file created concurrently after the check.
      Ownership must come from exclusive creation, so rollback must
      leave the file alone.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      local_packages_txt = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME)
      local_packages_txt.write_text('../common-lib\n', encoding='utf-8')
      step = CreatePackagesStep()

      with mock.patch.object(Path, 'exists', return_value=False):
        step.run(context)
      step.rollback(context)

      self.assertEqual(
        '../common-lib\n',
        local_packages_txt.read_text(encoding='utf-8'))
      self.assertFalse(
        (project_root / Packages.PACKAGES_FILENAME).exists())

  def test_rollback_wraps_removal_failure(self) -> None:
    """
      Verify that dependency file removal failures are wrapped.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      packages_txt = project_root / Packages.PACKAGES_FILENAME
      step = CreatePackagesStep()

      step.run(context)
      packages_txt.unlink()
      packages_txt.mkdir()

      with self.assertRaisesRegex(
        DralithusProjectError,
        'Could not remove dependency file'
      ):
        step.rollback(context)

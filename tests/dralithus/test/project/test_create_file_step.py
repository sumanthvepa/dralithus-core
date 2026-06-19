"""
  test_create_file_step.py: Unit tests for create_file_step.
"""
# -------------------------------------------------------------------
# test_create_file_step.py: Unit tests for create_file_step.
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
from dralithus.project.create_file_step import CreateFileStep
from dralithus.project.error import DralithusProjectError


class FailingWriteFile:
  """
    Wrap a real open file and fail every write.
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


# pylint: disable-next=too-many-public-methods
class TestCreateFileStep(unittest.TestCase):
  """
    Unit tests for the CreateFileStep class.
  """
  _FILENAME = Path('config.ini')
  _CONTENT = 'setting = value\n'

  def _target(self, project_root: Path) -> Path:
    """
      Return the target path for a test project root.

      :param project_root: The project root directory
      :return: The target file path
    """
    return project_root / self._FILENAME

  def test_init_rejects_absolute_filename(self) -> None:
    """
      Verify that the constructor rejects an absolute filename.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      with self.assertRaises(DralithusProjectError):
        CreateFileStep(Path(temp_directory) / self._FILENAME, self._CONTENT)

  def test_from_file_reads_source_content(self) -> None:
    """
      Verify the file factory reads UTF-8 source content.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      source = project_root / 'source.txt'
      source.write_text(self._CONTENT, encoding='utf-8')
      step = CreateFileStep.from_file(self._FILENAME, source)

      step.run(context)

      self.assertEqual(
        self._CONTENT,
        self._target(project_root).read_text(encoding='utf-8'))

  def test_from_file_wraps_source_read_failure(self) -> None:
    """
      Verify the file factory wraps a source-file read failure.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      source = Path(temp_directory) / 'missing.txt'

      with self.assertRaises(DralithusProjectError):
        CreateFileStep.from_file(self._FILENAME, source)

  def test_from_resource_reads_resource_content(self) -> None:
    """
      Verify the resource factory reads UTF-8 package content.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreateFileStep.from_resource(
        self._FILENAME,
        'dralithus.project',
        'error.py')

      step.run(context)

      expected = (
        Path(__file__).parents[4]
        / 'src' / 'dralithus' / 'project' / 'error.py'
      ).read_text(encoding='utf-8')
      self.assertEqual(
        expected,
        self._target(project_root).read_text(encoding='utf-8'))

  def test_from_resource_wraps_resource_read_failure(self) -> None:
    """
      Verify the resource factory wraps a resource read failure.

      :return: None
    """
    with self.assertRaises(DralithusProjectError):
      CreateFileStep.from_resource(
        self._FILENAME,
        'dralithus.project',
        'missing-resource.txt')

  def test_run_creates_file_with_supplied_content(self) -> None:
    """
      Verify run creates a file with the supplied literal content.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      step.run(context)

      self.assertEqual(
        self._CONTENT,
        self._target(project_root).read_text(encoding='utf-8'))

  def test_run_preserves_trailing_newline(self) -> None:
    """
      Verify run preserves a trailing newline in supplied content.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      content = 'first line\nsecond line\n'
      step = CreateFileStep(self._FILENAME, content)

      step.run(context)

      self.assertEqual(
        content,
        self._target(project_root).read_text(encoding='utf-8'))

  def test_run_raises_when_parent_directory_missing(self) -> None:
    """
      Verify run fails loudly when the parent directory is missing.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreateFileStep(Path('missing') / self._FILENAME, self._CONTENT)

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_reports_missing_parent_directory(self) -> None:
    """
      Verify run reports a missing parent directory precisely.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      filename = Path('missing') / self._FILENAME
      step = CreateFileStep(filename, self._CONTENT)

      with self.assertRaisesRegex(
        DralithusProjectError,
        f'Parent directory does not exist: {project_root / filename.parent}'
      ):
        step.run(context)

  def test_run_reports_parent_path_that_is_not_directory(self) -> None:
    """
      Verify run reports a wrong-type parent path precisely.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      parent = project_root / 'parent'
      parent.write_text('not a directory\n', encoding='utf-8')
      step = CreateFileStep(
        Path(parent.name) / self._FILENAME,
        self._CONTENT)

      with self.assertRaisesRegex(
        DralithusProjectError,
        f'Parent path is not a directory: {parent}'
      ):
        step.run(context)

  def test_run_accepts_valid_symlink_to_parent_directory(self) -> None:
    """
      Verify run accepts a parent symlink resolving to a directory.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      real_parent = project_root / 'real-parent'
      real_parent.mkdir()
      (project_root / 'linked-parent').symlink_to(
        real_parent, target_is_directory=True)
      filename = Path('linked-parent') / self._FILENAME
      step = CreateFileStep(filename, self._CONTENT)

      step.run(context)

      self.assertEqual(
        self._CONTENT,
        (real_parent / self._FILENAME).read_text(encoding='utf-8'))

  def test_run_preserves_preexisting_regular_file(self) -> None:
    """
      Verify run preserves a pre-existing regular file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = self._target(project_root)
      target.write_text('user content\n', encoding='utf-8')
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      step.run(context)

      self.assertEqual(
        'user content\n', target.read_text(encoding='utf-8'))

  def test_run_preserves_valid_symlink_to_regular_file(self) -> None:
    """
      Verify run preserves a valid symlink to a regular file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      symlink_target = project_root / 'user-config.ini'
      symlink_target.write_text('user content\n', encoding='utf-8')
      target = self._target(project_root)
      target.symlink_to(symlink_target)
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      step.run(context)

      self.assertTrue(target.is_symlink())
      self.assertEqual(
        'user content\n', symlink_target.read_text(encoding='utf-8'))

  def test_run_rejects_target_directory(self) -> None:
    """
      Verify run rejects a directory at the target path.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._target(project_root).mkdir()
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_dangling_target_symlink(self) -> None:
    """
      Verify run rejects a dangling symlink at the target path.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = self._target(project_root)
      target.symlink_to(project_root / 'missing-target')
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_symlink_to_non_regular_target(self) -> None:
    """
      Verify run rejects a symlink resolving to a directory.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      directory = project_root / 'directory'
      directory.mkdir()
      self._target(project_root).symlink_to(
        directory, target_is_directory=True)
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_wraps_target_read_failure(self) -> None:
    """
      Verify run wraps a failure reading an existing target.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = self._target(project_root)
      target.write_text('user content\n', encoding='utf-8')
      step = CreateFileStep(self._FILENAME, self._CONTENT)
      real_open = Path.open

      def fail_target_read(
        path: Path,
        mode: str = 'r',
        encoding: str | None = None
      ) -> IO[str]:
        if path == target and mode == 'r':
          raise OSError('simulated read failure')
        return real_open(path, mode, encoding=encoding)

      with mock.patch.object(Path, 'open', fail_target_read):
        with self.assertRaises(DralithusProjectError):
          step.run(context)

  def test_run_write_failure_removes_created_file(self) -> None:
    """
      Verify a write failure removes the exclusively created file.

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
      if mode == 'x':
        return FailingWriteFile(file)
      return file

    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      with mock.patch.object(Path, 'open', failing_open):
        with self.assertRaises(DralithusProjectError):
          step.run(context)

      self.assertFalse(self._target(project_root).exists())

  def test_rollback_removes_created_file(self) -> None:
    """
      Verify rollback removes a file created by the step.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      step.run(context)
      step.rollback(context)

      self.assertFalse(self._target(project_root).exists())

  def test_rollback_preserves_preexisting_file(self) -> None:
    """
      Verify rollback preserves a pre-existing regular file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = self._target(project_root)
      target.write_text('user content\n', encoding='utf-8')
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      step.run(context)
      step.rollback(context)

      self.assertEqual(
        'user content\n', target.read_text(encoding='utf-8'))

  def test_rollback_preserves_preexisting_valid_symlink(self) -> None:
    """
      Verify rollback preserves a pre-existing valid symlink.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      symlink_target = project_root / 'user-config.ini'
      symlink_target.write_text('user content\n', encoding='utf-8')
      target = self._target(project_root)
      target.symlink_to(symlink_target)
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      step.run(context)
      step.rollback(context)

      self.assertTrue(target.is_symlink())
      self.assertEqual(
        'user content\n', symlink_target.read_text(encoding='utf-8'))

  def test_rollback_accepts_created_file_removed_externally(self) -> None:
    """
      Verify rollback accepts a created file removed externally.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = self._target(project_root)
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      step.run(context)
      target.unlink()
      step.rollback(context)

      self.assertFalse(target.exists())

  def test_rollback_wraps_removal_failure(self) -> None:
    """
      Verify rollback wraps a failure removing a created file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = self._target(project_root)
      step = CreateFileStep(self._FILENAME, self._CONTENT)
      step.run(context)
      real_unlink = Path.unlink

      def fail_target_unlink(
        path: Path,
        missing_ok: bool = False
      ) -> None:
        if path == target:
          raise OSError('simulated removal failure')
        real_unlink(path, missing_ok=missing_ok)

      with mock.patch.object(Path, 'unlink', fail_target_unlink):
        with self.assertRaises(DralithusProjectError):
          step.rollback(context)

  def test_rollback_clears_ownership_and_preserves_recreated_file(
    self
  ) -> None:
    """
      Verify rollback clears ownership so a second rollback preserves
      a recreated file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = self._target(project_root)
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      step.run(context)
      step.rollback(context)

      target.write_text('foreign user content\n', encoding='utf-8')
      step.rollback(context)

      self.assertTrue(target.exists())
      self.assertEqual(
        'foreign user content\n', target.read_text(encoding='utf-8'))

  def test_failed_run_clears_ownership_and_can_be_retried(self) -> None:
    """
      Verify a failed run clears ownership and can be retried.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = self._target(project_root)
      step = CreateFileStep(self._FILENAME, self._CONTENT)
      real_open = Path.open
      fail_write = True

      def fail_first_write(
        path: Path,
        mode: str = 'r',
        encoding: str | None = None
      ) -> object:
        nonlocal fail_write
        # The wrapper (or the caller) is responsible for closing.
        # pylint: disable-next=consider-using-with
        file = real_open(path, mode, encoding=encoding)
        if mode == 'x' and fail_write:
          fail_write = False
          return FailingWriteFile(file)
        return file

      with mock.patch.object(Path, 'open', fail_first_write):
        with self.assertRaises(DralithusProjectError):
          step.run(context)
        step.run(context)

      step.rollback(context)
      self.assertFalse(target.exists())

  def test_repeated_runs_are_convergent_and_rollback_removes_file(
    self
  ) -> None:
    """
      Verify repeated runs preserve ownership for later rollback.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = self._target(project_root)
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      step.run(context)
      step.run(context)
      step.rollback(context)

      self.assertFalse(target.exists())

  def test_run_dry_run_validates_but_creates_nothing(self) -> None:
    """
      Verify dry run validates state but creates nothing.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      step.run(context, dry_run=True)

      self.assertFalse(self._target(project_root).exists())

  def test_run_dry_run_rejects_unusable_existing_state(self) -> None:
    """
      Verify dry run rejects an unusable existing target.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._target(project_root).mkdir()
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      with self.assertRaises(DralithusProjectError):
        step.run(context, dry_run=True)

  def test_rollback_dry_run_changes_nothing(self) -> None:
    """
      Verify dry-run rollback leaves a created file in place.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = self._target(project_root)
      step = CreateFileStep(self._FILENAME, self._CONTENT)

      step.run(context)
      step.rollback(context, dry_run=True)

      self.assertEqual(
        self._CONTENT, target.read_text(encoding='utf-8'))

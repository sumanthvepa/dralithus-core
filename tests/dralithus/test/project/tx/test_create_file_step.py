"""
  test_create_file_step.py: Unit tests for
  dralithus.project.tx.create_file_step.
"""
# -------------------------------------------------------------------
# test_create_file_step.py: Unit tests for
# dralithus.project.tx.create_file_step.
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
from importlib import resources
from pathlib import Path
from typing import IO
import unittest
from unittest import mock

from dralithus.test.project import FailingWriteFile, project_context
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.create_file_step import CreateFileStep
from dralithus.project.tx.project_state import ProjectState


# pylint: disable-next=too-many-public-methods
class TestCreateFileStep(unittest.TestCase):
  """
    Unit tests for the CreateFileStep class.

    These tests port the behavioral contract of the run/rollback
    CreateFileStep to prepare/commit/abort: prepare validates the
    parent against the current-or-projected state and claims the
    file without touching the file system, commit creates the file
    exclusively with ownership recorded before the content write,
    and abort removes the file only when this step created it. The
    symlink, dangling-symlink, and TOCTOU re-verification cases are
    carried over from the old suite.
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

  @staticmethod
  def _prepare_and_commit(
      step: CreateFileStep,
      project_root: Path
  ) -> None:
    """
      Prepare a step against a fresh state and commit it.

      :param step: The step to prepare and commit
      :param project_root: The project root directory
      :return: None
      :raises DralithusProjectError: When prepare or commit fails
    """
    step.prepare(ProjectState(project_root))
    step.commit()

  # constructor and factories

  def test_init_rejects_absolute_filename(self) -> None:
    """
      Verify the constructor rejects an absolute filename.

      :return: None
    """
    with project_context() as (project_root, context):
      with self.assertRaises(DralithusProjectError):
        CreateFileStep(
          context, project_root / self._FILENAME, self._CONTENT)

  def test_from_file_reads_source_content(self) -> None:
    """
      Verify the file factory reads UTF-8 source content that
      commit then writes to the target.

      :return: None
    """
    with project_context() as (project_root, context):
      source = project_root / 'source.txt'
      source.write_text(self._CONTENT, encoding='utf-8')
      step = CreateFileStep.from_file(context, self._FILENAME, source)

      self._prepare_and_commit(step, project_root)

      self.assertEqual(
        self._CONTENT,
        self._target(project_root).read_text(encoding='utf-8'))

  def test_from_file_wraps_source_read_failure(self) -> None:
    """
      Verify the file factory wraps a source-file read failure.

      :return: None
    """
    with project_context() as (project_root, context):
      source = project_root / 'missing.txt'

      with self.assertRaises(DralithusProjectError):
        CreateFileStep.from_file(context, self._FILENAME, source)

  def test_from_resource_reads_resource_content(self) -> None:
    """
      Verify the resource factory reads UTF-8 package content that
      commit then writes to the target.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateFileStep.from_resource(
        context,
        self._FILENAME,
        'dralithus.project',
        'error.py')

      self._prepare_and_commit(step, project_root)

      expected = (
        Path(__file__).parents[5]
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
    with project_context() as (_project_root, context):
      with self.assertRaises(DralithusProjectError):
        CreateFileStep.from_resource(
          context,
          self._FILENAME,
          'dralithus.project',
          'missing-resource.txt')

  def test_from_template_resource_renders_context_values(self) -> None:
    """
      Verify the template resource factory renders project context
      values.

      :return: None
    """
    with project_context(venv_name='env') as (project_root, context):
      template_directory = project_root / 'templates'
      template_directory.mkdir()
      template = template_directory / 'config.ini.j2'
      template.write_text(
        'root={{ project_root }}\n'
        'venv={{ venv_name }}\n',
        encoding='utf-8')
      with mock.patch.object(
        resources, 'files', return_value=template_directory
      ):
        step = CreateFileStep.from_template_resource(
          context,
          self._FILENAME,
          'example.templates',
          'config.ini.j2')

      self._prepare_and_commit(step, project_root)

      self.assertEqual(
        f'root={project_root}\n'
        'venv=env\n',
        self._target(project_root).read_text(encoding='utf-8'))

  def test_from_template_resource_wraps_resource_read_failure(
    self
  ) -> None:
    """
      Verify the template resource factory wraps a read failure.

      :return: None
    """
    with project_context() as (_project_root, context):
      with self.assertRaises(DralithusProjectError):
        CreateFileStep.from_template_resource(
          context,
          self._FILENAME,
          'dralithus.project',
          'missing-resource.txt')

  # prepare

  def test_prepare_claims_file(self) -> None:
    """
      Verify prepare claims the target file so a later step sees it
      as a projected file.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertTrue(state.is_file(self._target(project_root)))

  def test_prepare_creates_nothing_on_disk(self) -> None:
    """
      Verify prepare performs no file system mutation.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      step.prepare(ProjectState(project_root))

      self.assertFalse(self._target(project_root).exists())

  def test_prepare_accepts_claimed_parent_directory(self) -> None:
    """
      Verify prepare accepts a parent directory that exists only as
      a claim declared by an earlier step.

      :return: None
    """
    with project_context() as (project_root, context):
      filename = Path('src') / self._FILENAME
      step = CreateFileStep(context, filename, self._CONTENT)
      state = ProjectState(project_root)
      state.claim_directory(project_root / 'src')

      step.prepare(state)

      self.assertTrue(state.is_file(project_root / filename))

  def test_prepare_reports_missing_parent_directory(self) -> None:
    """
      Verify prepare reports a parent directory that is neither
      real nor claimed, precisely.

      :return: None
    """
    with project_context() as (project_root, context):
      filename = Path('missing') / self._FILENAME
      step = CreateFileStep(context, filename, self._CONTENT)

      with self.assertRaisesRegex(
        DralithusProjectError,
        f'Parent directory does not exist: '
        f'{project_root / filename.parent}'
      ):
        step.prepare(ProjectState(project_root))

  def test_prepare_reports_parent_path_that_is_not_directory(
    self
  ) -> None:
    """
      Verify prepare reports a wrong-type parent path precisely.

      :return: None
    """
    with project_context() as (project_root, context):
      parent = project_root / 'parent'
      parent.write_text('not a directory\n', encoding='utf-8')
      step = CreateFileStep(
        context,
        Path(parent.name) / self._FILENAME,
        self._CONTENT)

      with self.assertRaisesRegex(
        DralithusProjectError,
        f'Parent path is not a directory: {parent}'
      ):
        step.prepare(ProjectState(project_root))

  def test_prepare_accepts_valid_symlink_to_parent_directory(
    self
  ) -> None:
    """
      Verify prepare accepts a parent symlink resolving to a
      directory.

      :return: None
    """
    with project_context() as (project_root, context):
      real_parent = project_root / 'real-parent'
      real_parent.mkdir()
      (project_root / 'linked-parent').symlink_to(
        real_parent, target_is_directory=True)
      filename = Path('linked-parent') / self._FILENAME
      step = CreateFileStep(context, filename, self._CONTENT)

      self._prepare_and_commit(step, project_root)

      self.assertEqual(
        self._CONTENT,
        (real_parent / self._FILENAME).read_text(encoding='utf-8'))

  def test_prepare_accepts_preexisting_regular_file(self) -> None:
    """
      Verify prepare accepts an acceptable pre-existing regular
      file and claims it (convergence).

      :return: None
    """
    with project_context() as (project_root, context):
      target = self._target(project_root)
      target.write_text('user content\n', encoding='utf-8')
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertTrue(state.is_file(target))

  def test_prepare_accepts_valid_symlink_to_regular_file(self) -> None:
    """
      Verify prepare accepts a valid symlink to a readable regular
      file.

      :return: None
    """
    with project_context() as (project_root, context):
      symlink_target = project_root / 'user-config.ini'
      symlink_target.write_text('user content\n', encoding='utf-8')
      self._target(project_root).symlink_to(symlink_target)
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      step.prepare(ProjectState(project_root))

  def test_prepare_rejects_target_directory(self) -> None:
    """
      Verify prepare rejects a directory at the target path.

      :return: None
    """
    with project_context() as (project_root, context):
      self._target(project_root).mkdir()
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_rejects_dangling_target_symlink(self) -> None:
    """
      Verify prepare rejects a dangling symlink at the target path.

      :return: None
    """
    with project_context() as (project_root, context):
      target = self._target(project_root)
      target.symlink_to(project_root / 'missing-target')
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_rejects_symlink_to_non_regular_target(self) -> None:
    """
      Verify prepare rejects a symlink resolving to a directory.

      :return: None
    """
    with project_context() as (project_root, context):
      directory = project_root / 'directory'
      directory.mkdir()
      self._target(project_root).symlink_to(
        directory, target_is_directory=True)
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_wraps_target_read_failure(self) -> None:
    """
      Verify prepare wraps a failure reading an existing target.

      :return: None
    """
    with project_context() as (project_root, context):
      target = self._target(project_root)
      target.write_text('user content\n', encoding='utf-8')
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)
      state = ProjectState(project_root)
      real_open = Path.open

      def fail_target_read(
        path: Path,
        mode: str = 'r',
        encoding: str | None = None
      ) -> IO[str]:
        if path == target and mode == 'r':
          raise OSError('simulated read failure')
        # noinspection PyTypeChecker
        return real_open(path, mode, encoding=encoding)

      with mock.patch.object(Path, 'open', fail_target_read):
        with self.assertRaises(DralithusProjectError):
          step.prepare(state)

  # commit

  def test_commit_creates_file_with_supplied_content(self) -> None:
    """
      Verify commit creates a file with the supplied literal
      content.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      self._prepare_and_commit(step, project_root)

      self.assertEqual(
        self._CONTENT,
        self._target(project_root).read_text(encoding='utf-8'))

  def test_commit_preserves_trailing_newline(self) -> None:
    """
      Verify commit preserves a trailing newline in supplied
      content.

      :return: None
    """
    with project_context() as (project_root, context):
      content = 'first line\nsecond line\n'
      step = CreateFileStep(context, self._FILENAME, content)

      self._prepare_and_commit(step, project_root)

      self.assertEqual(
        content,
        self._target(project_root).read_text(encoding='utf-8'))

  def test_commit_preserves_preexisting_regular_file(self) -> None:
    """
      Verify commit preserves a pre-existing regular file and does
      not take ownership of it.

      :return: None
    """
    with project_context() as (project_root, context):
      target = self._target(project_root)
      target.write_text('user content\n', encoding='utf-8')
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      self._prepare_and_commit(step, project_root)

      self.assertEqual(
        'user content\n', target.read_text(encoding='utf-8'))

  def test_commit_preserves_valid_symlink_to_regular_file(self) -> None:
    """
      Verify commit preserves a valid symlink to a regular file.

      :return: None
    """
    with project_context() as (project_root, context):
      symlink_target = project_root / 'user-config.ini'
      symlink_target.write_text('user content\n', encoding='utf-8')
      target = self._target(project_root)
      target.symlink_to(symlink_target)
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      self._prepare_and_commit(step, project_root)

      self.assertTrue(target.is_symlink())
      self.assertEqual(
        'user content\n', symlink_target.read_text(encoding='utf-8'))

  def test_commit_write_failure_removes_created_file(self) -> None:
    """
      Verify a write failure removes the exclusively created file,
      because ownership was recorded before the write.

      :return: None
    """
    real_open = Path.open

    def failing_open(
      path: Path,
      mode: str = 'r',
      encoding: str | None = None
    ) -> object:
      # The wrapper (or the caller) is responsible for closing.
      # noinspection PyTypeChecker
      # pylint: disable-next=consider-using-with
      file = real_open(path, mode, encoding=encoding)
      if mode == 'x':
        return FailingWriteFile(file)
      return file

    with project_context() as (project_root, context):
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)
      step.prepare(ProjectState(project_root))

      with mock.patch.object(Path, 'open', failing_open):
        with self.assertRaises(DralithusProjectError):
          step.commit()

      self.assertFalse(self._target(project_root).exists())

  def test_commit_rejects_unacceptable_file_created_after_prepare(
    self
  ) -> None:
    """
      Verify commit re-verifies a target that appeared between
      prepare and commit and rejects an unacceptable one (TOCTOU).

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)
      step.prepare(ProjectState(project_root))

      self._target(project_root).mkdir()

      with self.assertRaises(DralithusProjectError):
        step.commit()

      self.assertTrue(self._target(project_root).is_dir())

  def test_failed_commit_clears_ownership_and_can_be_retried(
    self
  ) -> None:
    """
      Verify a failed commit clears ownership and can be retried.

      :return: None
    """
    with project_context() as (project_root, context):
      target = self._target(project_root)
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)
      step.prepare(ProjectState(project_root))
      real_open = Path.open
      fail_write = True

      def fail_first_write(
        path: Path,
        mode: str = 'r',
        encoding: str | None = None
      ) -> object:
        nonlocal fail_write
        # The wrapper (or the caller) is responsible for closing.
        # noinspection PyTypeChecker
        # pylint: disable-next=consider-using-with
        file = real_open(path, mode, encoding=encoding)
        if mode == 'x' and fail_write:
          fail_write = False
          return FailingWriteFile(file)
        return file

      with mock.patch.object(Path, 'open', fail_first_write):
        with self.assertRaises(DralithusProjectError):
          step.commit()
        step.commit()

      self.assertTrue(target.exists())
      step.abort()
      self.assertFalse(target.exists())

  def test_repeated_commits_are_convergent_and_abort_removes_file(
    self
  ) -> None:
    """
      Verify repeated commits preserve ownership so a later abort
      removes the file.

      :return: None
    """
    with project_context() as (project_root, context):
      target = self._target(project_root)
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.commit()
      step.abort()

      self.assertFalse(target.exists())

  # abort

  def test_abort_removes_created_file(self) -> None:
    """
      Verify abort removes a file created by commit.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      self._prepare_and_commit(step, project_root)
      step.abort()

      self.assertFalse(self._target(project_root).exists())

  def test_abort_preserves_preexisting_file(self) -> None:
    """
      Verify abort preserves a pre-existing regular file.

      :return: None
    """
    with project_context() as (project_root, context):
      target = self._target(project_root)
      target.write_text('user content\n', encoding='utf-8')
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      self._prepare_and_commit(step, project_root)
      step.abort()

      self.assertEqual(
        'user content\n', target.read_text(encoding='utf-8'))

  def test_abort_preserves_preexisting_valid_symlink(self) -> None:
    """
      Verify abort preserves a pre-existing valid symlink.

      :return: None
    """
    with project_context() as (project_root, context):
      symlink_target = project_root / 'user-config.ini'
      symlink_target.write_text('user content\n', encoding='utf-8')
      target = self._target(project_root)
      target.symlink_to(symlink_target)
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      self._prepare_and_commit(step, project_root)
      step.abort()

      self.assertTrue(target.is_symlink())
      self.assertEqual(
        'user content\n', symlink_target.read_text(encoding='utf-8'))

  def test_abort_accepts_created_file_removed_externally(self) -> None:
    """
      Verify abort accepts a created file that was removed
      externally.

      :return: None
    """
    with project_context() as (project_root, context):
      target = self._target(project_root)
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      self._prepare_and_commit(step, project_root)
      target.unlink()
      step.abort()

      self.assertFalse(target.exists())

  def test_abort_wraps_removal_failure(self) -> None:
    """
      Verify abort wraps a failure removing a created file.

      :return: None
    """
    with project_context() as (project_root, context):
      target = self._target(project_root)
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)
      self._prepare_and_commit(step, project_root)
      real_unlink = Path.unlink

      def fail_target_unlink(
        path: Path,
        missing_ok: bool = False
      ) -> None:
        if path == target:
          raise OSError('simulated removal failure')
        # noinspection PyTypeChecker
        real_unlink(path, missing_ok=missing_ok)

      with mock.patch.object(Path, 'unlink', fail_target_unlink):
        with self.assertRaises(DralithusProjectError):
          step.abort()

  def test_abort_clears_ownership_and_preserves_recreated_file(
    self
  ) -> None:
    """
      Verify abort clears ownership so a second abort preserves a
      file recreated externally at the same path.

      :return: None
    """
    with project_context() as (project_root, context):
      target = self._target(project_root)
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      self._prepare_and_commit(step, project_root)
      step.abort()

      target.write_text('foreign user content\n', encoding='utf-8')
      step.abort()

      self.assertTrue(target.exists())
      self.assertEqual(
        'foreign user content\n',
        target.read_text(encoding='utf-8'))

  def test_abort_without_commit_changes_nothing(self) -> None:
    """
      Verify abort after prepare alone is a no-op.

      :return: None
    """
    with project_context() as (project_root, context):
      target = self._target(project_root)
      target.write_text('user content\n', encoding='utf-8')
      step = CreateFileStep(context, self._FILENAME, self._CONTENT)

      step.prepare(ProjectState(project_root))
      step.abort()

      self.assertEqual(
        'user content\n', target.read_text(encoding='utf-8'))

"""
  test_create_gitignore_file_step.py: Unit tests for
  dralithus.project.tx.create_gitignore_file_step.
"""
# -------------------------------------------------------------------
# test_create_gitignore_file_step.py: Unit tests for
# dralithus.project.tx.create_gitignore_file_step.
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

from dralithus.test.project import project_context
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.create_gitignore_file_step import (
  CreateGitIgnoreFileStep)
from dralithus.project.tx.project_state import ProjectState


class TestCreateGitIgnoreFileStep(unittest.TestCase):
  """
    Unit tests for the CreateGitIgnoreFileStep class.

    The step delegates every phase to an inner CreateFileStep, so
    these tests cover the delegation and the .gitignore-specific
    behavior rather than re-testing the inner step's exhaustive
    file-type handling, which is covered by its own suite.
  """
  _DIRECTORY = Path('src')

  @classmethod
  def _gitignore(cls, project_root: Path) -> Path:
    """
      Return the generated .gitignore path.

      :param project_root: The project root directory
      :return: The .gitignore path
    """
    return project_root / cls._DIRECTORY / '.gitignore'

  # prepare

  def test_prepare_rejects_missing_directory(self) -> None:
    """
      Verify prepare fails when the target directory is neither
      real nor claimed.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateGitIgnoreFileStep(context, self._DIRECTORY)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_accepts_claimed_directory(self) -> None:
    """
      Verify prepare accepts a target directory that exists only as
      a claim declared by an earlier step.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateGitIgnoreFileStep(context, self._DIRECTORY)
      state = ProjectState(project_root)
      state.claim_directory(project_root / self._DIRECTORY)

      step.prepare(state)

      self.assertTrue(state.is_file(self._gitignore(project_root)))

  def test_prepare_rejects_unusable_existing_target(self) -> None:
    """
      Verify prepare rejects an unusable .gitignore target.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir()
      self._gitignore(project_root).mkdir()
      step = CreateGitIgnoreFileStep(context, self._DIRECTORY)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_creates_nothing_on_disk(self) -> None:
    """
      Verify prepare performs no file system mutation.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir()
      step = CreateGitIgnoreFileStep(context, self._DIRECTORY)

      step.prepare(ProjectState(project_root))

      self.assertFalse(self._gitignore(project_root).exists())

  # commit

  def test_commit_creates_empty_gitignore(self) -> None:
    """
      Verify commit creates an empty .gitignore file in the
      directory.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir()
      step = CreateGitIgnoreFileStep(context, self._DIRECTORY)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertEqual(
        '', self._gitignore(project_root).read_text(encoding='utf-8'))

  def test_commit_preserves_preexisting_gitignore(self) -> None:
    """
      Verify commit preserves a pre-existing .gitignore file.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir()
      gitignore = self._gitignore(project_root)
      gitignore.write_text('*.log\n', encoding='utf-8')
      step = CreateGitIgnoreFileStep(context, self._DIRECTORY)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertEqual(
        '*.log\n', gitignore.read_text(encoding='utf-8'))

  # abort

  def test_abort_removes_created_gitignore(self) -> None:
    """
      Verify abort removes a .gitignore created by commit.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir()
      step = CreateGitIgnoreFileStep(context, self._DIRECTORY)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse(self._gitignore(project_root).exists())

  def test_abort_preserves_preexisting_gitignore(self) -> None:
    """
      Verify abort preserves a pre-existing .gitignore file.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir()
      gitignore = self._gitignore(project_root)
      gitignore.write_text('*.log\n', encoding='utf-8')
      step = CreateGitIgnoreFileStep(context, self._DIRECTORY)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertEqual(
        '*.log\n', gitignore.read_text(encoding='utf-8'))

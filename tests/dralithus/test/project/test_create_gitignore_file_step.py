"""
  test_create_gitignore_file_step.py: Unit tests for
  create_gitignore_file_step.
"""
# -------------------------------------------------------------------
# test_create_gitignore_file_step.py: Unit tests for
# create_gitignore_file_step.
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
import unittest

from dralithus.project.context import ProjectContext
from dralithus.project.create_gitignore_file_step import (
  CreateGitIgnoreFileStep)
from dralithus.project.error import DralithusProjectError


class TestCreateGitIgnoreFileStep(unittest.TestCase):
  """
    Unit tests for the CreateGitIgnoreFileStep class.
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

  def test_run_creates_empty_gitignore(self) -> None:
    """
      Verify run creates an empty .gitignore file in the directory.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_holder='Sumanth Vepa',
        copyright_year=2026)
      (project_root / self._DIRECTORY).mkdir()
      step = CreateGitIgnoreFileStep(self._DIRECTORY)

      step.run(context)

      self.assertEqual(
        '', self._gitignore(project_root).read_text(encoding='utf-8'))

  def test_run_preserves_preexisting_gitignore(self) -> None:
    """
      Verify run preserves a pre-existing .gitignore file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_holder='Sumanth Vepa',
        copyright_year=2026)
      (project_root / self._DIRECTORY).mkdir()
      gitignore = self._gitignore(project_root)
      gitignore.write_text('*.log\n', encoding='utf-8')
      step = CreateGitIgnoreFileStep(self._DIRECTORY)

      step.run(context)

      self.assertEqual('*.log\n', gitignore.read_text(encoding='utf-8'))

  def test_run_rejects_missing_directory(self) -> None:
    """
      Verify run fails when the target directory is missing.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      context = ProjectContext(
        project_root=Path(temp_directory),
        package_name='sample',
        copyright_holder='Sumanth Vepa',
        copyright_year=2026)
      step = CreateGitIgnoreFileStep(self._DIRECTORY)

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_rollback_removes_created_gitignore(self) -> None:
    """
      Verify rollback removes a .gitignore created by the step.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_holder='Sumanth Vepa',
        copyright_year=2026)
      (project_root / self._DIRECTORY).mkdir()
      step = CreateGitIgnoreFileStep(self._DIRECTORY)

      step.run(context)
      step.rollback(context)

      self.assertFalse(self._gitignore(project_root).exists())

  def test_rollback_preserves_preexisting_gitignore(self) -> None:
    """
      Verify rollback preserves a pre-existing .gitignore file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_holder='Sumanth Vepa',
        copyright_year=2026)
      (project_root / self._DIRECTORY).mkdir()
      gitignore = self._gitignore(project_root)
      gitignore.write_text('*.log\n', encoding='utf-8')
      step = CreateGitIgnoreFileStep(self._DIRECTORY)

      step.run(context)
      step.rollback(context)

      self.assertEqual('*.log\n', gitignore.read_text(encoding='utf-8'))

  def test_run_dry_run_creates_nothing(self) -> None:
    """
      Verify dry run creates no .gitignore file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_holder='Sumanth Vepa',
        copyright_year=2026)
      (project_root / self._DIRECTORY).mkdir()
      step = CreateGitIgnoreFileStep(self._DIRECTORY)

      step.run(context, dry_run=True)

      self.assertFalse(self._gitignore(project_root).exists())

  def test_run_dry_run_rejects_unusable_existing_target(self) -> None:
    """
      Verify dry run rejects an unusable .gitignore target.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        package_name='sample',
        copyright_holder='Sumanth Vepa',
        copyright_year=2026)
      (project_root / self._DIRECTORY).mkdir()
      self._gitignore(project_root).mkdir()
      step = CreateGitIgnoreFileStep(self._DIRECTORY)

      with self.assertRaises(DralithusProjectError):
        step.run(context, dry_run=True)

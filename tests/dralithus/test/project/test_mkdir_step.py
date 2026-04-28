"""
  test_mkdir_step.py: Unit tests for the dralithus.project.mkdir_step
  module.
"""
# -------------------------------------------------------------------
# test_mkdir_step.py: Unit tests for dralithus.project.mkdir_step.
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
from dralithus.project.error import DralithusProjectError
from dralithus.project.mkdir_step import MkdirStep


class TestMkdirStep(unittest.TestCase):
  """
    Unit tests for the MkdirStep class.
  """
  def test_run_creates_relative_directory(self) -> None:
    """
      Verify that run creates a project-relative directory.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = MkdirStep(Path('src'))

      step.run(context)

      self.assertTrue((project_root / 'src').is_dir())

  def test_run_creates_parent_directories(self) -> None:
    """
      Verify that run creates parent directories as needed.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = Path('src') / 'dralithus' / 'project'
      step = MkdirStep(target)

      step.run(context)

      self.assertTrue((project_root / target).is_dir())

  def test_run_dry_run_does_not_create_directory(self) -> None:
    """
      Verify that dry-run mode does not create a directory.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = MkdirStep(Path('src'))

      step.run(context, dry_run=True)

      self.assertFalse((project_root / 'src').exists())

  def test_rollback_removes_directory_created_by_step(self) -> None:
    """
      Verify that rollback removes a directory created by the step.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = MkdirStep(Path('src'))

      step.run(context)
      step.rollback(context)

      self.assertFalse((project_root / 'src').exists())

  def test_rollback_removes_parent_directories_created_by_step(
    self
  ) -> None:
    """
      Verify rollback removes parent directories created by the step.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = Path('src') / 'dralithus' / 'project'
      step = MkdirStep(target)

      step.run(context)
      step.rollback(context)

      self.assertFalse((project_root / target).exists())
      self.assertFalse((project_root / 'src' / 'dralithus').exists())
      self.assertFalse((project_root / 'src').exists())

  def test_rollback_only_removes_parent_directories_created_by_step(
    self
  ) -> None:
    """
      Verify rollback preserves preexisting parent directories.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      preexisting_parent = project_root / 'src'
      target = Path('src') / 'dralithus' / 'project'
      preexisting_parent.mkdir()
      step = MkdirStep(target)

      step.run(context)
      step.rollback(context)

      self.assertFalse((project_root / target).exists())
      self.assertFalse((project_root / 'src' / 'dralithus').exists())
      self.assertTrue(preexisting_parent.is_dir())

  def test_rollback_dry_run_does_not_remove_directory(self) -> None:
    """
      Verify that rollback dry-run mode does not remove a directory.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = MkdirStep(Path('src'))

      step.run(context)
      step.rollback(context, dry_run=True)

      self.assertTrue((project_root / 'src').is_dir())

  def test_rollback_does_not_remove_preexisting_directory(self) -> None:
    """
      Verify that rollback leaves preexisting directories alone.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = project_root / 'src'
      target.mkdir()
      step = MkdirStep(Path('src'))

      step.run(context)
      step.rollback(context)

      self.assertTrue(target.is_dir())

  def test_rollback_raises_error_for_non_empty_directory(self) -> None:
    """
      Verify rollback raises an error for non-empty directories.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      target = project_root / 'src'
      step = MkdirStep(Path('src'))

      step.run(context)
      (target / 'module.py').touch()

      with self.assertRaises(DralithusProjectError):
        step.rollback(context)

      self.assertTrue(target.is_dir())
      self.assertTrue((target / 'module.py').is_file())

  def test_run_rejects_absolute_directory(self) -> None:
    """
      Verify that absolute directory paths are rejected.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)

      with self.assertRaises(DralithusProjectError):
        step = MkdirStep(project_root / 'src')
        step.run(context)

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
import unittest
from unittest import mock

from dralithus.project.context import ProjectContext
from dralithus.project.create_packages_step import CreatePackagesStep
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages


class TestCreatePackagesStep(unittest.TestCase):
  """
    Unit tests for the CreatePackagesStep class.
  """
  def test_run_creates_packages_files(self) -> None:
    """
      Verify that run seeds both dependency files in an empty
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

  def test_run_failure_removes_partially_created_files(self) -> None:
    """
      Verify that a failed run removes the dependency files it
      created before failing.

      An unreadable packages.txt is detected only after the missing
      local-packages.txt has been seeded; the failed run must not
      leave the seeded file behind.

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

  def test_rollback_preserves_dangling_symlink(self) -> None:
    """
      Verify rollback does not delete a user-owned dangling symlink.

      A dangling symlink fails Path.exists, so ownership tracking
      based on an existence check would wrongly claim it. The step
      must not remove it on rollback.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      local_packages_txt = (
        project_root / Packages.LOCAL_PACKAGES_FILENAME)
      local_packages_txt.symlink_to(project_root / 'does-not-exist')
      step = CreatePackagesStep()

      step.run(context)
      step.rollback(context)

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

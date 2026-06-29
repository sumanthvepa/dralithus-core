"""
  test_create_python_init_file_step.py: Unit tests for
  create_python_init_file_step.
"""
# -------------------------------------------------------------------
# test_create_python_init_file_step.py: Unit tests for
# create_python_init_file_step.
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

from dralithus.test.project import copyright_header, project_context
from dralithus.project.context import ProjectContext
from dralithus.project.copyright_header import CopyrightHeader
from dralithus.project.create_python_init_file_step import (
  CreatePythonInitFileStep)
from dralithus.project.error import DralithusProjectError


class TestCreatePythonInitFileStep(unittest.TestCase):
  """
    Unit tests for the CreatePythonInitFileStep class.
  """
  _DIRECTORY = Path('tests') / 'mypkg' / 'test'
  _DESCRIPTION = 'mypkg/test/__init__.py: Unit tests for mypkg.'

  @classmethod
  def _directory(cls, project_root: Path) -> Path:
    """
      Return the generated package directory path.

      :param project_root: The project root directory
      :return: The generated package directory path
    """
    return project_root / cls._DIRECTORY

  @classmethod
  def _init_py(cls, project_root: Path) -> Path:
    """
      Return the generated __init__.py path.

      :param project_root: The project root directory
      :return: The __init__.py path
    """
    return project_root / cls._DIRECTORY / '__init__.py'

  def _step(
    self,
    context: ProjectContext,
    header: CopyrightHeader | None = None
  ) -> CreatePythonInitFileStep:
    """
      Return a configured Python __init__.py creation step.

      :param context: The shared project context
      :param header: Optional copyright header to use
      :return: The configured Python __init__.py creation step
    """
    if header is None:
      header = copyright_header()
    return CreatePythonInitFileStep(
      context,
      self._DIRECTORY,
      header,
      self._DESCRIPTION)

  def test_run_creates_init_py_with_copyright_header(self) -> None:
    """
      Verify run creates __init__.py with the copyright header.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      header = copyright_header()
      step = self._step(context, header)

      step.run()

      self.assertEqual(
        '"""\n'
        f'  {self._DESCRIPTION}\n'
        '"""\n'
        f'# {self._DESCRIPTION}\n'
        f'# Copyright (C) {header.copyright_year} {header.copyright_holder}.\n',
        self._init_py(project_root).read_text(encoding='utf-8'))

  def test_run_preserves_preexisting_init_py(self) -> None:
    """
      Verify run preserves a pre-existing __init__.py file.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      init_py = self._init_py(project_root)
      init_py.write_text('# existing\n', encoding='utf-8')
      step = self._step(context)

      step.run()

      self.assertEqual('# existing\n', init_py.read_text(encoding='utf-8'))

  def test_run_rejects_missing_directory(self) -> None:
    """
      Verify run fails when the target directory is missing.

      :return: None
    """
    with project_context() as (_, context):
      step = self._step(context)

      with self.assertRaises(DralithusProjectError):
        step.run()

  def test_run_rejects_unusable_existing_init_py(self) -> None:
    """
      Verify run rejects an unusable existing __init__.py target.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      self._init_py(project_root).mkdir()
      step = self._step(context)

      with self.assertRaises(DralithusProjectError):
        step.run()

  def test_rollback_removes_created_init_py(self) -> None:
    """
      Verify rollback removes an __init__.py created by the step.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      step = self._step(context)

      step.run()
      step.rollback()

      self.assertFalse(self._init_py(project_root).exists())

  def test_rollback_preserves_preexisting_init_py(self) -> None:
    """
      Verify rollback preserves a pre-existing __init__.py file.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      init_py = self._init_py(project_root)
      init_py.write_text('# existing\n', encoding='utf-8')
      step = self._step(context)

      step.run()
      step.rollback()

      self.assertEqual('# existing\n', init_py.read_text(encoding='utf-8'))

  def test_run_dry_run_creates_nothing(self) -> None:
    """
      Verify dry run creates no __init__.py file.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      step = self._step(context)

      step.run(dry_run=True)

      self.assertFalse(self._init_py(project_root).exists())

  def test_run_dry_run_rejects_unusable_existing_init_py(self) -> None:
    """
      Verify dry run rejects an unusable existing __init__.py target.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      self._init_py(project_root).mkdir()
      step = self._step(context)

      with self.assertRaises(DralithusProjectError):
        step.run(dry_run=True)

  def test_repeated_runs_are_convergent_and_rollback_removes_init_py(
    self
  ) -> None:
    """
      Verify repeated runs stay convergent and rollback removes
      created __init__.py.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      step = self._step(context)

      step.run()
      step.run()
      step.rollback()

      self.assertFalse(self._init_py(project_root).exists())

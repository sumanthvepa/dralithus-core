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

from dralithus.test.project import project_context
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
  _TEMPLATE = (
    '{{ description }}\n'
    'Copyright (C) {{ copyright_year }} {{ copyright_holder }}.\n')

  @classmethod
  def _init_py(cls, project_root: Path) -> Path:
    """
      Return the generated __init__.py path.

      :param project_root: The project root directory
      :return: The __init__.py path
    """
    return project_root / cls._DIRECTORY / '__init__.py'

  @staticmethod
  def _copyright_header(
    copyright_holder: str = 'Milestone 42',
    copyright_year: int = 2020
  ) -> CopyrightHeader:
    """
      Return the copyright header renderer for the tests.

      :param copyright_holder: The copyright holder name
      :param copyright_year: The copyright year
      :return: The copyright header renderer
    """
    return CopyrightHeader(
      TestCreatePythonInitFileStep._TEMPLATE,
      copyright_holder,
      copyright_year)

  def test_run_creates_init_py_with_copyright_header(self) -> None:
    """
      Verify run creates __init__.py with the copyright header.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir(parents=True)
      step = CreatePythonInitFileStep(
        context,
        self._DIRECTORY,
        self._copyright_header(),
        self._DESCRIPTION)

      step.run()

      self.assertEqual(
        '"""\n'
        f'  {self._DESCRIPTION}\n'
        '"""\n'
        f'# {self._DESCRIPTION}\n'
        '# Copyright (C) 2020 Milestone 42.\n',
        self._init_py(project_root).read_text(encoding='utf-8'))

  def test_run_uses_copyright_header_values(self) -> None:
    """
      Verify run uses the fixed values from the copyright header.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir(parents=True)
      step = CreatePythonInitFileStep(
        context,
        self._DIRECTORY,
        self._copyright_header('Acme Tools', 2020),
        self._DESCRIPTION)

      step.run()

      self.assertEqual(
        '"""\n'
        f'  {self._DESCRIPTION}\n'
        '"""\n'
        f'# {self._DESCRIPTION}\n'
        '# Copyright (C) 2020 Acme Tools.\n',
        self._init_py(project_root).read_text(encoding='utf-8'))

  def test_run_preserves_preexisting_init_py(self) -> None:
    """
      Verify run preserves a pre-existing __init__.py file.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir(parents=True)
      init_py = self._init_py(project_root)
      init_py.write_text('# existing\n', encoding='utf-8')
      step = CreatePythonInitFileStep(
        context,
        self._DIRECTORY,
        self._copyright_header(),
        self._DESCRIPTION)

      step.run()

      self.assertEqual('# existing\n', init_py.read_text(encoding='utf-8'))

  def test_run_rejects_missing_directory(self) -> None:
    """
      Verify run fails when the target directory is missing.

      :return: None
    """
    with project_context() as (_, context):
      step = CreatePythonInitFileStep(
        context,
        self._DIRECTORY,
        self._copyright_header(),
        self._DESCRIPTION)

      with self.assertRaises(DralithusProjectError):
        step.run()

  def test_run_rejects_unusable_existing_init_py(self) -> None:
    """
      Verify run rejects an unusable existing __init__.py target.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir(parents=True)
      self._init_py(project_root).mkdir()
      step = CreatePythonInitFileStep(
        context,
        self._DIRECTORY,
        self._copyright_header(),
        self._DESCRIPTION)

      with self.assertRaises(DralithusProjectError):
        step.run()

  def test_rollback_removes_created_init_py(self) -> None:
    """
      Verify rollback removes an __init__.py created by the step.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir(parents=True)
      step = CreatePythonInitFileStep(
        context,
        self._DIRECTORY,
        self._copyright_header(),
        self._DESCRIPTION)

      step.run()
      step.rollback()

      self.assertFalse(self._init_py(project_root).exists())

  def test_rollback_preserves_preexisting_init_py(self) -> None:
    """
      Verify rollback preserves a pre-existing __init__.py file.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir(parents=True)
      init_py = self._init_py(project_root)
      init_py.write_text('# existing\n', encoding='utf-8')
      step = CreatePythonInitFileStep(
        context,
        self._DIRECTORY,
        self._copyright_header(),
        self._DESCRIPTION)

      step.run()
      step.rollback()

      self.assertEqual('# existing\n', init_py.read_text(encoding='utf-8'))

  def test_run_dry_run_creates_nothing(self) -> None:
    """
      Verify dry run creates no __init__.py file.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir(parents=True)
      step = CreatePythonInitFileStep(
        context,
        self._DIRECTORY,
        self._copyright_header(),
        self._DESCRIPTION)

      step.run(dry_run=True)

      self.assertFalse(self._init_py(project_root).exists())

  def test_run_dry_run_rejects_unusable_existing_init_py(self) -> None:
    """
      Verify dry run rejects an unusable existing __init__.py target.

      :return: None
    """
    with project_context() as (project_root, context):
      (project_root / self._DIRECTORY).mkdir(parents=True)
      self._init_py(project_root).mkdir()
      step = CreatePythonInitFileStep(
        context,
        self._DIRECTORY,
        self._copyright_header(),
        self._DESCRIPTION)

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
      (project_root / self._DIRECTORY).mkdir(parents=True)
      step = CreatePythonInitFileStep(
        context,
        self._DIRECTORY,
        self._copyright_header(),
        self._DESCRIPTION)

      step.run()
      step.run()
      step.rollback()

      self.assertFalse(self._init_py(project_root).exists())

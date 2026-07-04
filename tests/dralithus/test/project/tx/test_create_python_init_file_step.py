"""
  test_create_python_init_file_step.py: Unit tests for
  dralithus.project.tx.create_python_init_file_step.
"""
# -------------------------------------------------------------------
# test_create_python_init_file_step.py: Unit tests for
# dralithus.project.tx.create_python_init_file_step.
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
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.create_python_init_file_step import (
  CreatePythonInitFileStep)
from dralithus.project.tx.project_state import ProjectState


class TestCreatePythonInitFileStep(unittest.TestCase):
  """
    Unit tests for the CreatePythonInitFileStep class.

    The step delegates every phase to an inner CreateFileStep whose
    content is rendered at construction time, so these tests cover
    the delegation and the rendered content rather than re-testing
    the inner step's exhaustive file-type handling, which is covered
    by its own suite.
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

  # prepare

  def test_prepare_rejects_missing_directory(self) -> None:
    """
      Verify prepare fails when the target directory is neither
      real nor claimed.

      :return: None
    """
    with project_context() as (project_root, context):
      step = self._step(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_accepts_claimed_directory(self) -> None:
    """
      Verify prepare accepts a target directory that exists only as
      a claim declared by an earlier step.

      :return: None
    """
    with project_context() as (project_root, context):
      step = self._step(context)
      state = ProjectState(project_root)
      state.claim_directory(self._directory(project_root))

      step.prepare(state)

      self.assertTrue(state.is_file(self._init_py(project_root)))

  def test_prepare_rejects_unusable_existing_init_py(self) -> None:
    """
      Verify prepare rejects an unusable __init__.py target.

      :return: None
    """
    with project_context() as (project_root, context):
      self._init_py(project_root).mkdir(parents=True)
      step = self._step(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_creates_nothing_on_disk(self) -> None:
    """
      Verify prepare performs no file system mutation.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      step = self._step(context)

      step.prepare(ProjectState(project_root))

      self.assertFalse(self._init_py(project_root).exists())

  # commit

  def test_commit_creates_init_py_with_copyright_header(self) -> None:
    """
      Verify commit creates an __init__.py with the module
      docstring and the rendered copyright header.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      header = copyright_header()
      step = self._step(context, header)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertEqual(
        '"""\n'
        f'  {self._DESCRIPTION}\n'
        '"""\n'
        f'# {self._DESCRIPTION}\n'
        f'# Copyright (C) {header.copyright_year} '
        f'{header.copyright_holder}.\n',
        self._init_py(project_root).read_text(encoding='utf-8'))

  def test_commit_preserves_preexisting_init_py(self) -> None:
    """
      Verify commit preserves a pre-existing __init__.py file.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      init_py = self._init_py(project_root)
      init_py.write_text('# existing\n', encoding='utf-8')
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertEqual(
        '# existing\n', init_py.read_text(encoding='utf-8'))

  def test_repeated_commits_are_convergent_and_abort_removes_init_py(
    self
  ) -> None:
    """
      Verify repeated commits preserve ownership so a later abort
      removes the __init__.py.

      :return: None
    """
    with project_context() as (project_root, context):
      # The phase-call sequence repeats across step suites; a future
      # refactoring could extract a shared helper.
      # pylint: disable=duplicate-code
      self._directory(project_root).mkdir(parents=True)
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.commit()
      step.abort()

      self.assertFalse(self._init_py(project_root).exists())

  # abort

  def test_abort_removes_created_init_py(self) -> None:
    """
      Verify abort removes an __init__.py created by commit.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse(self._init_py(project_root).exists())

  def test_abort_preserves_preexisting_init_py(self) -> None:
    """
      Verify abort preserves a pre-existing __init__.py file.

      :return: None
    """
    with project_context() as (project_root, context):
      self._directory(project_root).mkdir(parents=True)
      init_py = self._init_py(project_root)
      # The phase-call sequence repeats across step suites; a future
      # refactoring could extract a shared helper.
      # pylint: disable=duplicate-code
      init_py.write_text('# existing\n', encoding='utf-8')
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertEqual(
        '# existing\n', init_py.read_text(encoding='utf-8'))

"""
  test_create_mypy_configuration_step.py: Unit tests for
  dralithus.project.tx.create_mypy_configuration_step.
"""
# -------------------------------------------------------------------
# test_create_mypy_configuration_step.py: Unit tests for
# dralithus.project.tx.create_mypy_configuration_step.
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
import unittest

from dralithus.test.project import project_context
from dralithus.project.error import DralithusProjectError
from dralithus.project.tx.create_mypy_configuration_step import (
  CreateMypyConfigurationStep)
from dralithus.project.tx.execution_step import execute
from dralithus.project.tx.project_state import ProjectState


class TestCreateMypyConfigurationStep(unittest.TestCase):
  """
    Unit tests for the CreateMypyConfigurationStep class.

    CreateMypyConfigurationStep composes file and directory children
    with no phase logic of its own, so these tests cover the wiring
    and the generated artifact set through the execute() driver: a
    full real run, a deep dry run with no guarded skipping, and
    prepare-time rejection of unusable targets. The children's
    exhaustive file-type handling is covered by their own suites.
  """
  @staticmethod
  def _mypy_ini(project_root: Path) -> Path:
    """
      Return the project mypy configuration path.

      :param project_root: The project root directory
      :return: The mypy.ini path
    """
    return project_root / 'mypy.ini'

  @staticmethod
  def _stubs(project_root: Path) -> Path:
    """
      Return the project stubs directory path.

      :param project_root: The project root directory
      :return: The stubs directory path
    """
    return project_root / 'stubs'

  @classmethod
  def _stubs_gitignore(cls, project_root: Path) -> Path:
    """
      Return the stubs .gitignore path.

      :param project_root: The project root directory
      :return: The stubs .gitignore path
    """
    return cls._stubs(project_root) / '.gitignore'

  @classmethod
  def _parameterized(cls, project_root: Path) -> Path:
    """
      Return the parameterized stub package directory path.

      :param project_root: The project root directory
      :return: The parameterized stub package directory path
    """
    return cls._stubs(project_root) / 'parameterized'

  @classmethod
  def _parameterized_gitignore(cls, project_root: Path) -> Path:
    """
      Return the parameterized .gitignore path.

      :param project_root: The project root directory
      :return: The parameterized .gitignore path
    """
    return cls._parameterized(project_root) / '.gitignore'

  @classmethod
  def _parameterized_stub(cls, project_root: Path) -> Path:
    """
      Return the generated parameterized stub path.

      :param project_root: The project root directory
      :return: The parameterized __init__.pyi path
    """
    return cls._parameterized(project_root) / '__init__.pyi'

  @staticmethod
  def _mypy_template_content() -> str:
    """
      Read the packaged mypy configuration template.

      :return: The packaged mypy.ini resource text
    """
    return resources.files('dralithus.project.templates').joinpath(
      'mypy.ini').read_text(encoding='utf-8')

  @staticmethod
  def _stub_template_content() -> str:
    """
      Read the packaged parameterized stub template.

      :return: The packaged parameterized __init__.pyi resource text
    """
    return resources.files(
      'dralithus.project.templates.parameterized').joinpath(
        '__init__.pyi').read_text(encoding='utf-8')

  def test_mypy_ini_resource_can_be_read(self) -> None:
    """
      Verify that the packaged mypy.ini resource can be read.

      :return: None
    """
    self.assertNotEqual('', self._mypy_template_content())

  def test_parameterized_stub_resource_can_be_read(self) -> None:
    """
      Verify that the packaged parameterized stub can be read.

      :return: None
    """
    self.assertNotEqual('', self._stub_template_content())

  # execute: real run

  def test_execute_creates_full_artifact_set(self) -> None:
    """
      Verify execute creates the full mypy configuration artifact
      set.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateMypyConfigurationStep(context)

      execute(step, context)

      self.assertTrue(self._mypy_ini(project_root).is_file())
      self.assertTrue(self._stubs(project_root).is_dir())
      self.assertTrue(self._stubs_gitignore(project_root).is_file())
      self.assertTrue(self._parameterized(project_root).is_dir())
      self.assertTrue(
        self._parameterized_gitignore(project_root).is_file())
      self.assertTrue(self._parameterized_stub(project_root).is_file())

  def test_execute_creates_mypy_ini_from_resource(self) -> None:
    """
      Verify execute creates mypy.ini from the packaged resource.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateMypyConfigurationStep(context)

      execute(step, context)

      self.assertEqual(
        self._mypy_template_content(),
        self._mypy_ini(project_root).read_text(encoding='utf-8'))

  def test_execute_creates_parameterized_stub_from_resource(
    self
  ) -> None:
    """
      Verify execute creates the parameterized stub from the
      resource.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateMypyConfigurationStep(context)

      execute(step, context)

      self.assertEqual(
        self._stub_template_content(),
        self._parameterized_stub(project_root).read_text(
          encoding='utf-8'))

  def test_execute_creates_empty_gitignore_files(self) -> None:
    """
      Verify execute creates empty .gitignore files in the stub
      directories.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateMypyConfigurationStep(context)

      execute(step, context)

      self.assertEqual(
        '',
        self._stubs_gitignore(project_root).read_text(
          encoding='utf-8'))
      self.assertEqual(
        '',
        self._parameterized_gitignore(project_root).read_text(
          encoding='utf-8'))

  def test_execute_preserves_representative_preexisting_artifacts(
    self
  ) -> None:
    """
      Verify execute preserves representative pre-existing
      artifacts.

      :return: None
    """
    with project_context() as (project_root, context):
      self._mypy_ini(project_root).write_text(
        'user mypy config\n',
        encoding='utf-8')
      self._parameterized(project_root).mkdir(parents=True)
      (self._parameterized(project_root) / 'user-file.txt').write_text(
        'user data\n',
        encoding='utf-8')
      step = CreateMypyConfigurationStep(context)

      execute(step, context)

      self.assertEqual(
        'user mypy config\n',
        self._mypy_ini(project_root).read_text(encoding='utf-8'))
      self.assertEqual(
        'user data\n',
        (self._parameterized(project_root)
         / 'user-file.txt').read_text(encoding='utf-8'))

  def test_execute_prepare_failure_leaves_disk_untouched(self) -> None:
    """
      Verify a prepare failure in a real run propagates before any
      commit, leaving the file system untouched; the old hierarchy
      hit this same scenario midway through the run and needed
      rollback.

      :return: None
    """
    with project_context() as (project_root, context):
      self._parameterized_gitignore(project_root).mkdir(parents=True)
      step = CreateMypyConfigurationStep(context)

      with self.assertRaises(DralithusProjectError):
        execute(step, context)

      self.assertFalse(self._mypy_ini(project_root).exists())
      self.assertFalse(self._stubs_gitignore(project_root).exists())
      self.assertTrue(
        self._parameterized_gitignore(project_root).is_dir())

  # execute: dry run

  def test_execute_dry_run_validates_deeply_and_creates_nothing(
    self
  ) -> None:
    """
      Verify a dry run against an empty project root validates
      every child through its claims, skips nothing, and creates
      nothing.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateMypyConfigurationStep(context)

      execute(step, context, dry_run=True)

      self.assertFalse(self._mypy_ini(project_root).exists())
      self.assertFalse(self._stubs(project_root).exists())

  def test_execute_dry_run_rejects_unusable_existing_target(
    self
  ) -> None:
    """
      Verify a dry run rejects an existing but unusable mypy.ini
      target.

      :return: None
    """
    with project_context() as (project_root, context):
      self._mypy_ini(project_root).mkdir()
      step = CreateMypyConfigurationStep(context)

      with self.assertRaises(DralithusProjectError):
        execute(step, context, dry_run=True)

  # abort

  def test_abort_removes_created_artifacts(self) -> None:
    """
      Verify abort removes the artifacts commit created.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreateMypyConfigurationStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse(self._mypy_ini(project_root).exists())
      self.assertFalse(self._stubs(project_root).exists())

  def test_abort_preserves_preexisting_artifacts(self) -> None:
    """
      Verify abort preserves pre-existing files and directories.

      :return: None
    """
    with project_context() as (project_root, context):
      self._mypy_ini(project_root).write_text(
        'user mypy config\n',
        encoding='utf-8')
      self._parameterized(project_root).mkdir(parents=True)
      step = CreateMypyConfigurationStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertEqual(
        'user mypy config\n',
        self._mypy_ini(project_root).read_text(encoding='utf-8'))
      self.assertTrue(self._parameterized(project_root).is_dir())

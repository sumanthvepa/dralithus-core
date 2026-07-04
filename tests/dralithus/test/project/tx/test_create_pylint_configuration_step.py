"""
  test_create_pylint_configuration_step.py: Unit tests for
  dralithus.project.tx.create_pylint_configuration_step.
"""
# -------------------------------------------------------------------
# test_create_pylint_configuration_step.py: Unit tests for
# dralithus.project.tx.create_pylint_configuration_step.
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
from dralithus.project.tx.create_pylint_configuration_step import (
  CreatePylintConfigurationStep)
from dralithus.project.tx.project_state import ProjectState


class TestCreatePylintConfigurationStep(unittest.TestCase):
  """
    Unit tests for the CreatePylintConfigurationStep class.

    The step delegates every phase to an inner CreateFileStep built
    from the packaged pylintrc resource, so these tests cover the
    delegation and the generated content rather than re-testing the
    inner step's exhaustive file-type handling, which is covered by
    its own suite.
  """
  _INIT_HOOK = (
    'init-hook=\'import os, sys; sys.path.append(os.path.abspath('
    'os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, '
    'os.pardir, os.pardir, os.pardir, os.pardir, "src"))); '
    'sys.path.append(os.path.abspath(os.path.join('
    'os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, '
    'os.pardir, os.pardir, os.pardir, "tests")))\'')

  @staticmethod
  def _pylintrc(project_root: Path) -> Path:
    """
      Return the project Pylint configuration path.

      :param project_root: The project root directory
      :return: The pylintrc path
    """
    return project_root / 'pylintrc'

  @staticmethod
  def _pylintrc_template_content() -> str:
    """
      Read the packaged Pylint configuration template.

      :return: The packaged pylintrc resource text
    """
    return resources.files('dralithus.project.templates').joinpath(
      'pylintrc').read_text(encoding='utf-8')

  def test_pylintrc_resource_can_be_read(self) -> None:
    """
      Verify that the packaged pylintrc resource can be read.

      :return: None
    """
    self.assertNotEqual('', self._pylintrc_template_content())

  # prepare

  def test_prepare_creates_nothing_on_disk(self) -> None:
    """
      Verify prepare performs no file system mutation.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreatePylintConfigurationStep(context)

      step.prepare(ProjectState(project_root))

      self.assertFalse(self._pylintrc(project_root).exists())

  def test_prepare_rejects_unusable_existing_target(self) -> None:
    """
      Verify prepare rejects an unusable existing pylintrc target.

      :return: None
    """
    with project_context() as (project_root, context):
      self._pylintrc(project_root).mkdir()
      step = CreatePylintConfigurationStep(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  # commit

  def test_commit_creates_pylintrc_from_resource(self) -> None:
    """
      Verify commit creates pylintrc from the packaged resource.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreatePylintConfigurationStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertEqual(
        self._pylintrc_template_content(),
        self._pylintrc(project_root).read_text(encoding='utf-8'))

  def test_commit_preserves_portable_init_hook(self) -> None:
    """
      Verify the generated pylintrc contains the portable
      init-hook.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreatePylintConfigurationStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertIn(
        self._INIT_HOOK,
        self._pylintrc(project_root).read_text(encoding='utf-8'))

  def test_commit_preserves_preexisting_pylintrc(self) -> None:
    """
      Verify commit preserves a pre-existing regular pylintrc.

      :return: None
    """
    with project_context() as (project_root, context):
      pylintrc = self._pylintrc(project_root)
      pylintrc.write_text('user config\n', encoding='utf-8')
      step = CreatePylintConfigurationStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertEqual(
        'user config\n', pylintrc.read_text(encoding='utf-8'))

  # abort

  def test_abort_removes_created_pylintrc(self) -> None:
    """
      Verify abort removes a pylintrc created by commit.

      :return: None
    """
    with project_context() as (project_root, context):
      step = CreatePylintConfigurationStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse(self._pylintrc(project_root).exists())

  def test_abort_preserves_preexisting_pylintrc(self) -> None:
    """
      Verify abort preserves a pre-existing regular pylintrc.

      :return: None
    """
    with project_context() as (project_root, context):
      pylintrc = self._pylintrc(project_root)
      pylintrc.write_text('user config\n', encoding='utf-8')
      step = CreatePylintConfigurationStep(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertEqual(
        'user config\n', pylintrc.read_text(encoding='utf-8'))

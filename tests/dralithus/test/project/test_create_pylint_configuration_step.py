"""
  test_create_pylint_configuration_step.py: Unit tests for
  create_pylint_configuration_step.
"""
# -------------------------------------------------------------------
# test_create_pylint_configuration_step.py: Unit tests for
# create_pylint_configuration_step.
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
from tempfile import TemporaryDirectory
import unittest

from dralithus.project.context import ProjectContext
from dralithus.project.create_pylint_configuration_step import (
  CreatePylintConfigurationStep)
from dralithus.project.error import DralithusProjectError


class TestCreatePylintConfigurationStep(unittest.TestCase):
  """
    Unit tests for the CreatePylintConfigurationStep class.
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

  def test_run_creates_pylintrc_from_resource(self) -> None:
    """
      Verify run creates pylintrc from the packaged resource.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePylintConfigurationStep()

      step.run(context)

      self.assertEqual(
        self._pylintrc_template_content(),
        self._pylintrc(project_root).read_text(encoding='utf-8'))

  def test_run_preserves_portable_init_hook(self) -> None:
    """
      Verify generated pylintrc contains the portable init-hook.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePylintConfigurationStep()

      step.run(context)

      self.assertIn(
        self._INIT_HOOK,
        self._pylintrc(project_root).read_text(encoding='utf-8'))

  def test_run_preserves_representative_preexisting_artifacts(self) -> None:
    """
      Verify run preserves a pre-existing regular pylintrc.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      pylintrc = self._pylintrc(project_root)
      pylintrc.write_text('user config\n', encoding='utf-8')
      step = CreatePylintConfigurationStep()

      step.run(context)

      self.assertEqual('user config\n', pylintrc.read_text(encoding='utf-8'))

  def test_rollback_removes_created_artifacts(self) -> None:
    """
      Verify rollback removes a pylintrc created by the step.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePylintConfigurationStep()

      step.run(context)
      step.rollback(context)

      self.assertFalse(self._pylintrc(project_root).exists())

  def test_rollback_preserves_preexisting_artifacts(self) -> None:
    """
      Verify rollback preserves a pre-existing regular pylintrc.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      pylintrc = self._pylintrc(project_root)
      pylintrc.write_text('user config\n', encoding='utf-8')
      step = CreatePylintConfigurationStep()

      step.run(context)
      step.rollback(context)

      self.assertEqual('user config\n', pylintrc.read_text(encoding='utf-8'))

  def test_run_dry_run_creates_nothing(self) -> None:
    """
      Verify dry run creates no pylintrc.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePylintConfigurationStep()

      step.run(context, dry_run=True)

      self.assertFalse(self._pylintrc(project_root).exists())

  def test_run_dry_run_rejects_unusable_existing_target(self) -> None:
    """
      Verify dry run rejects an unusable existing pylintrc target.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._pylintrc(project_root).mkdir()
      step = CreatePylintConfigurationStep()

      with self.assertRaises(DralithusProjectError):
        step.run(context, dry_run=True)

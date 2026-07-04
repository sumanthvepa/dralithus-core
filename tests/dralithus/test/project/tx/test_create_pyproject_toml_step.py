"""
  test_create_pyproject_toml_step.py: Unit tests for
  dralithus.project.tx.create_pyproject_toml_step.
"""
# -------------------------------------------------------------------
# test_create_pyproject_toml_step.py: Unit tests for
# dralithus.project.tx.create_pyproject_toml_step.
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

from dralithus.test.project import project_context, write_package_artifacts
from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages
from dralithus.project.pyproject_toml import PyProjectToml
from dralithus.project.tx.create_pyproject_toml_step import (
  CreatePyProjectTomlStep)
from dralithus.project.tx.project_state import ProjectState


# pylint: disable-next=too-many-public-methods
class TestCreatePyProjectTomlStep(unittest.TestCase):
  """
    Unit tests for the CreatePyProjectTomlStep class.

    These tests port the behavioral contract of the run/rollback
    CreatePyProjectTomlStep to prepare/commit/abort. The dry-run
    fidelity win of the tx design is pinned here: prepare()
    validates pyproject.toml against a venv and dependency files
    that exist only as claims, which the old dry run could not do.

    The venv is faked with a directory holding a pyvenv.cfg, since
    both prepare and commit read only the venv metadata; real venv
    creation is covered by the CreateVenvStep suite.
  """
  _VENV_VERSION = '3.14.2'
  _PYTHON_REQUIREMENT = '>=3.14'
  _implicit_dev_dependencies = ['mypy', 'pylint', 'parameterized']

  @staticmethod
  def _make_fake_venv(
    context: ProjectContext,
    version: str = '3.14.2'
  ) -> None:
    """
      Create a fake venv directory with pyvenv.cfg metadata.

      :param context: The project context
      :param version: The version to record in pyvenv.cfg
      :return: None
    """
    context.venv_path.mkdir()
    (context.venv_path / 'pyvenv.cfg').write_text(
      f'version = {version}\n', encoding='utf-8')

  @staticmethod
  def _step(context: ProjectContext) -> CreatePyProjectTomlStep:
    """
      Return a configured pyproject.toml creation step.

      :param context: The shared project context
      :return: The configured pyproject.toml creation step
    """
    return CreatePyProjectTomlStep(
      context,
      project_name='sample-project',
      project_description='Sample project')

  @classmethod
  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def _pyproject_text(
    cls,
    project_name: str = 'sample-project',
    project_description: str = 'Sample project',
    package_name: str = 'sample',
    project_version: str = '0.1.0',
    python_requirement: str | None = None,
    dependencies: list[str] | None = None,
    dev_dependencies: list[str] | None = None
  ) -> str:
    """
      Return pyproject.toml text for tests.

      Renders by constructing a PyProjectToml and calling to_toml.

      :param project_name: The project distribution name
      :param project_description: The project description
      :param package_name: The Python package name
      :param project_version: The project version
      :param python_requirement: The requires-python value
      :param dependencies: The project dependencies
      :param dev_dependencies: The optional dev dependencies
      :return: pyproject.toml text
    """
    requirement = python_requirement or cls._PYTHON_REQUIREMENT
    if dependencies is None:
      dependencies = []
    if dev_dependencies is None:
      dev_dependencies = cls._implicit_dev_dependencies
    with TemporaryDirectory() as temp_directory:
      packages = write_package_artifacts(
        Path(temp_directory),
        production_dependencies=dependencies,
        dev_dependencies=dev_dependencies)
    pyproject = PyProjectToml(
      name=project_name,
      description=project_description,
      package_name=package_name,
      python_requirement=requirement,
      packages=packages,
      version=project_version)
    return pyproject.to_toml()

  def _validate_pyproject(
    self,
    context: ProjectContext,
    python_requirement: str | None = None,
    dependencies: list[str] | None = None
  ) -> None:
    """
      Verify that the on-disk pyproject.toml matches expectations.

      Rebuilds the package artifacts with the expected dependency
      lists, loads the file via PyProjectToml.from_file and
      delegates the field comparison to PyProjectToml.matches.

      :param context: The project context
      :param python_requirement: The expected requires-python value
      :param dependencies: The expected project dependencies
      :return: None
    """
    project_root = context.project_root
    expected_packages = write_package_artifacts(
      project_root,
      production_dependencies=dependencies or [])
    expected = PyProjectToml(
      name='sample-project',
      description='Sample project',
      package_name='sample',
      python_requirement=python_requirement or self._PYTHON_REQUIREMENT,
      packages=expected_packages,
      version='0.1.0')
    actual = PyProjectToml.from_file(
      project_root / 'pyproject.toml',
      expected_packages)
    actual.matches(expected)

  # prepare

  def test_prepare_claims_pyproject(self) -> None:
    """
      Verify prepare claims pyproject.toml when the venv and
      dependency files exist on the real file system.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      step = self._step(context)
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertTrue(state.is_file(project_root / 'pyproject.toml'))

  def test_prepare_validates_against_claimed_venv_and_packages(
    self
  ) -> None:
    """
      Verify prepare succeeds against an empty project root when
      the venv and packages.txt exist only as claims declared by
      earlier steps.

      :return: None
    """
    with project_context() as (project_root, context):
      step = self._step(context)
      state = ProjectState(project_root)
      state.claim_venv(context.venv_path, self._VENV_VERSION)
      state.claim_file(project_root / Packages.PACKAGES_FILENAME)

      step.prepare(state)

      self.assertTrue(state.is_file(project_root / 'pyproject.toml'))
      self.assertFalse((project_root / 'pyproject.toml').exists())

  def test_prepare_rejects_missing_packages_txt(self) -> None:
    """
      Verify prepare fails when packages.txt is neither real nor
      claimed.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      step = self._step(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_rejects_missing_venv(self) -> None:
    """
      Verify prepare fails when no venv is current or claimed.

      :return: None
    """
    with project_context() as (project_root, context):
      write_package_artifacts(project_root)
      step = self._step(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_rejects_venv_without_version(self) -> None:
    """
      Verify prepare fails when the real venv metadata has no
      version entry.

      :return: None
    """
    with project_context() as (project_root, context):
      context.venv_path.mkdir()
      (context.venv_path / 'pyvenv.cfg').write_text(
        'home = /usr/local/bin\n', encoding='utf-8')
      write_package_artifacts(project_root)
      step = self._step(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_accepts_valid_existing_pyproject(self) -> None:
    """
      Verify prepare accepts an existing pyproject.toml that
      matches the expected content.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      (project_root / 'pyproject.toml').write_text(
        self._pyproject_text(), encoding='utf-8')
      step = self._step(context)
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertTrue(state.is_file(project_root / 'pyproject.toml'))

  def test_prepare_rejects_pyproject_directory(self) -> None:
    """
      Verify prepare rejects a directory at the pyproject.toml
      path.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      (project_root / 'pyproject.toml').mkdir()
      step = self._step(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_rejects_malformed_pyproject(self) -> None:
    """
      Verify prepare rejects an existing pyproject.toml that does
      not parse or does not match the expected content.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      (project_root / 'pyproject.toml').write_text(
        '[project\n', encoding='utf-8')
      step = self._step(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_creates_nothing_on_disk(self) -> None:
    """
      Verify prepare performs no file system mutation.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      step = self._step(context)

      step.prepare(ProjectState(project_root))

      self.assertFalse((project_root / 'pyproject.toml').exists())

  # commit

  def test_commit_creates_pyproject_when_missing(self) -> None:
    """
      Verify commit creates pyproject.toml when it is absent.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      self._validate_pyproject(context)

  def test_commit_reads_context_venv_path(self) -> None:
    """
      Verify commit derives requires-python from the context's
      named venv directory.

      :return: None
    """
    with project_context(venv_name='env') as (project_root, context):
      self._make_fake_venv(context, version='3.13.7')
      write_package_artifacts(project_root)
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      pyproject = PyProjectToml.from_file(
        project_root / 'pyproject.toml',
        Packages(project_root))
      self.assertEqual('>=3.13', pyproject.python_requirement)

  def test_commit_creates_pyproject_with_packages_txt_dependencies(
    self
  ) -> None:
    """
      Verify the created pyproject.toml lists the packages.txt
      production dependencies.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      (project_root / Packages.PACKAGES_FILENAME).write_text(
        '# third-party packages\n'
        '\n'
        'requests\n'
        'rich\n',
        encoding='utf-8')
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      self._validate_pyproject(
        context,
        dependencies=['requests', 'rich'])

  def test_commit_creates_pyproject_with_dev_marked_dependencies(
    self
  ) -> None:
    """
      Verify the created pyproject.toml lists dev-marked
      dependencies in the dev optional-dependencies group.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      (project_root / Packages.PACKAGES_FILENAME).write_text(
        'requests\n'
        'coverage [dev]\n',
        encoding='utf-8')
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      expected_packages = Packages(project_root)
      expected = PyProjectToml(
        name='sample-project',
        description='Sample project',
        package_name='sample',
        python_requirement=self._PYTHON_REQUIREMENT,
        packages=expected_packages,
        version='0.1.0')
      actual = PyProjectToml.from_file(
        project_root / 'pyproject.toml',
        expected_packages)
      actual.matches(expected)
      text = (project_root / 'pyproject.toml').read_text(
        encoding='utf-8')
      self.assertIn('coverage', text)

  def test_commit_does_not_add_unmarked_local_dependencies(
    self
  ) -> None:
    """
      Verify unmarked local dependencies stay out of the generated
      pyproject.toml dependency lists.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(
        project_root,
        local_dependencies=['../common-lib'])
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      text = (project_root / 'pyproject.toml').read_text(
        encoding='utf-8')
      self.assertNotIn('common-lib', text)

  def test_commit_leaves_valid_existing_pyproject_unchanged(
    self
  ) -> None:
    """
      Verify commit leaves an acceptable existing pyproject.toml
      byte-identical and does not take ownership of it.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      existing = self._pyproject_text()
      (project_root / 'pyproject.toml').write_text(
        existing, encoding='utf-8')
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()

      self.assertEqual(
        existing,
        (project_root / 'pyproject.toml').read_text(encoding='utf-8'))

  def test_commit_rejects_mismatched_pyproject_created_after_prepare(
    self
  ) -> None:
    """
      Verify commit re-validates a pyproject.toml that appeared
      between prepare and commit and rejects a mismatched one
      (TOCTOU).

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      step = self._step(context)
      step.prepare(ProjectState(project_root))

      mismatched = self._pyproject_text(python_requirement='>=2.7')
      (project_root / 'pyproject.toml').write_text(
        mismatched, encoding='utf-8')

      with self.assertRaises(DralithusProjectError):
        step.commit()

      self.assertEqual(
        mismatched,
        (project_root / 'pyproject.toml').read_text(encoding='utf-8'))

  # abort

  def test_abort_removes_pyproject_created_by_commit(self) -> None:
    """
      Verify abort removes a pyproject.toml created by commit.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertFalse((project_root / 'pyproject.toml').exists())

  def test_abort_is_idempotent(self) -> None:
    """
      Verify abort can be called again after removing the created
      pyproject.toml.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()
      step.abort()

      self.assertFalse((project_root / 'pyproject.toml').exists())

  def test_abort_preserves_preexisting_pyproject(self) -> None:
    """
      Verify abort leaves a pre-existing pyproject.toml in place.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      existing = self._pyproject_text()
      (project_root / 'pyproject.toml').write_text(
        existing, encoding='utf-8')
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.abort()

      self.assertEqual(
        existing,
        (project_root / 'pyproject.toml').read_text(encoding='utf-8'))

  def test_repeated_commits_are_convergent_and_abort_removes_pyproject(
    self
  ) -> None:
    """
      Verify committing twice leaves one pyproject.toml and abort
      still removes it.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_fake_venv(context)
      write_package_artifacts(project_root)
      step = self._step(context)

      step.prepare(ProjectState(project_root))
      step.commit()
      step.commit()
      step.abort()

      self.assertFalse((project_root / 'pyproject.toml').exists())

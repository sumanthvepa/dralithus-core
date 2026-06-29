"""
  test_create_pyproject_toml_step.py: Unit tests for
  create_pyproject_toml_step.
"""
# -------------------------------------------------------------------
# test_create_pyproject_toml_step.py: Unit tests for
# create_pyproject_toml_step.
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
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from parameterized import parameterized

from dralithus.test.project import project_context, write_package_artifacts
from dralithus.project.context import ProjectContext
from dralithus.project.create_pyproject_toml_step import CreatePyProjectTomlStep
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages
from dralithus.project.pyproject_toml import PyProjectToml


# pylint: disable-next=too-many-public-methods,too-many-lines
class TestCreatePyProjectTomlStep(unittest.TestCase):
  """
    Unit tests for the CreatePyProjectTomlStep class.
  """
  _implicit_dev_dependencies = ['mypy', 'pylint', 'parameterized']

  @classmethod
  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def _packages(
    cls,
    project_root: Path,
    dependencies: list[str] | None = None,
    dev_dependencies: list[str] | None = None,
    local_dependencies: list[str] | None = None,
    local_dev_dependencies: list[str] | None = None
  ) -> Packages:
    """
      Write package artifacts and return their Packages model.

      :param project_root: The project root directory
      :param dependencies: The packages.txt dependencies
      :param dev_dependencies: The full expected dev dependency list
      :param local_dependencies: The local-packages.txt dependencies
      :param local_dev_dependencies: The local dev dependencies
      :return: The Packages model
    """
    return write_package_artifacts(
      project_root=project_root,
      production_dependencies=dependencies,
      dev_dependencies=dev_dependencies,
      local_dependencies=local_dependencies,
      local_dev_dependencies=local_dev_dependencies)

  @staticmethod
  def _python_requirement() -> str:
    """
      Return the Python requirement for the test interpreter.

      :return: The Python major/minor version requirement
    """
    return f'>={sys.version_info.major}.{sys.version_info.minor}'

  def _venv_python_requirement(self, context: ProjectContext) -> str:
    """
      Return the Python requirement from the test project's venv.

      :param context: The project context
      :return: The Python major/minor version requirement
    """
    pyvenv_cfg = context.venv_path / 'pyvenv.cfg'
    if not context.venv_path.is_dir():
      self.fail(f'Test venv does not exist: {context.venv_path}')
    if not pyvenv_cfg.is_file():
      self.fail(f'Test venv has no pyvenv.cfg: {pyvenv_cfg}')
    values: dict[str, str] = {}
    for line in pyvenv_cfg.read_text(encoding='utf-8').splitlines():
      name, separator, value = line.partition('=')
      if separator == '=':
        values[name.strip()] = value.strip()
    version = values.get('version')
    if version is None:
      self.fail(f'Test venv has no version entry: {pyvenv_cfg}')
    version_parts = version.split('.')
    if len(version_parts) < 2:
      self.fail(f'Test venv version is not major.minor: {version}')
    return f'>={version_parts[0]}.{version_parts[1]}'

  @classmethod
  def _malformed_pyproject_text(cls, malformed_case: str) -> str:
    """
      Return malformed pyproject.toml text for rejection tests.

      :param malformed_case: The malformed pyproject variant
      :return: The pyproject.toml text
    """
    text = cls._pyproject_text()
    match malformed_case:
      case 'invalid_toml':
        text = '[project\n'
      case 'missing_required_project_name':
        text = text.replace('name = "sample-project"\n', '')
      case 'project_name_mismatch':
        text = cls._pyproject_text(project_name='other-project')
      case 'python_version_mismatch':
        text = cls._pyproject_text(python_requirement='>=2.7')
      case 'missing_standard_dev_dependency':
        text = text.replace(
          '["mypy", "pylint", "parameterized"]',
          '["mypy", "pylint"]')
      case 'packages_txt_dependency_mismatch':
        text = cls._pyproject_text(dependencies=[])
      case 'package_find_where_mismatch':
        text = text.replace('where = ["src"]', 'where = ["."]')
      case 'package_find_include_mismatch':
        text = cls._pyproject_text(package_name='other_package')
      case _:
        raise AssertionError(
          f'Unknown malformed pyproject case: {malformed_case}')
    return text

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
      Use string replacement on the returned text for the rare
      cases (missing fields, non-M42 invariants) that PyProjectToml
      cannot express directly.

      :param project_name: The project distribution name
      :param project_description: The project description
      :param package_name: The Python package name
      :param project_version: The project version
      :param python_requirement: The requires-python value
      :param dependencies: The project dependencies
      :param dev_dependencies: The optional dev dependencies
      :return: pyproject.toml text
    """
    requirement = python_requirement or cls._python_requirement()
    if dependencies is None:
      dependencies = []
    if dev_dependencies is None:
      dev_dependencies = cls._implicit_dev_dependencies
    with TemporaryDirectory() as temp_directory:
      packages = cls._packages(
        Path(temp_directory),
        dependencies,
        dev_dependencies)
    pyproject = PyProjectToml(
      name=project_name,
      description=project_description,
      package_name=package_name,
      python_requirement=requirement,
      packages=packages,
      version=project_version)
    return pyproject.to_toml()

  @staticmethod
  def _create_venv(
    context: ProjectContext,
    create_packages_txt: bool = True
  ) -> None:
    """
      Create a real Python virtual environment for tests.

      :param context: The project context
      :param create_packages_txt: True if packages.txt should be
        created
      :return: None
    """
    subprocess.run(
      [sys.executable, '-m', 'venv', str(context.venv_path)],
      check=True)
    if create_packages_txt:
      (context.project_root / Packages.PACKAGES_FILENAME).write_text(
        '', encoding='utf-8')

  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def _validate_pyproject(
    self,
    context: ProjectContext,
    project_name: str = 'sample-project',
    project_description: str = 'Sample project',
    package_name: str = 'sample',
    project_version: str = '0.1.0',
    dependencies: list[str] | None = None
  ) -> None:
    """
      Verify that the on-disk pyproject.toml matches expectations.

      Loads the file via PyProjectToml.from_file and delegates the
      field comparison to PyProjectToml.matches.

      :param context: The project context
      :param project_name: The expected project distribution name
      :param project_description: The expected project description
      :param package_name: The expected Python package name
      :param project_version: The expected project version
      :param dependencies: The expected project dependencies
      :return: None
    """
    project_root = context.project_root
    expected_packages = self._packages(
      project_root,
      dependencies or [])
    expected = PyProjectToml(
      name=project_name,
      description=project_description,
      package_name=package_name,
      python_requirement=self._venv_python_requirement(context),
      packages=expected_packages,
      version=project_version)
    actual = PyProjectToml.from_file(
      project_root / 'pyproject.toml',
      expected_packages)
    actual.matches(expected)

  def test_run_creates_pyproject_when_missing(self) -> None:
    """
      Verify run creates pyproject.toml when it is missing.

      :return: None
    """
    with project_context() as (_project_root, context):
      self._create_venv(context)
      step = CreatePyProjectTomlStep(
        context,
        project_name='sample-project',
        project_description='Sample project')

      step.run()

      self._validate_pyproject(context)

  def test_run_reads_context_venv_path(self) -> None:
    """
      Verify run reads the venv path from ProjectContext.

      :return: None
    """
    with project_context(venv_name='env') as (project_root, context):
      self._create_venv(context)
      step = CreatePyProjectTomlStep(
        context,
        project_name='sample-project',
        project_description='Sample project')

      step.run()

      pyproject = PyProjectToml.from_file(
        project_root / 'pyproject.toml',
        Packages(project_root))
      self.assertEqual(self._python_requirement(),
                       pyproject.python_requirement)

  def test_run_creates_pyproject_with_packages_txt_dependencies(self) -> None:
    """
      Verify run copies packages.txt names into dependencies.

      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      (project_root / Packages.PACKAGES_FILENAME).write_text(
        '# third-party packages\n'
        '\n'
        'requests\n'
        'rich\n',
        encoding='utf-8')
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      step.run()

      self._validate_pyproject(
        context,
        dependencies=['requests', 'rich'])

  def test_run_creates_pyproject_with_dev_marked_dependencies(self) -> None:
    """
      Verify run copies [dev] marked dependencies into dev metadata.

      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      (project_root / Packages.PACKAGES_FILENAME).write_text(
        'requests\n'
        'pytest [dev]\n',
        encoding='utf-8')
      (project_root / Packages.LOCAL_PACKAGES_FILENAME).write_text(
        '../common-lib\n'
        '../test-lib [dev]\n',
        encoding='utf-8')
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      step.run()

      pyproject = PyProjectToml.from_file(
        project_root / 'pyproject.toml',
        Packages(project_root))
      self.assertEqual(
        pyproject.packages.production_dependencies,
        ['requests'])
      self.assertEqual(
        pyproject.packages.dev_dependencies,
        ['mypy', 'pylint', 'parameterized', 'pytest', '../test-lib'])
      self.assertEqual(
        pyproject.packages.local_dependencies,
        ['../common-lib'])

  def test_run_does_not_add_unmarked_local_dependencies(self) -> None:
    """
      Verify unmarked local packages are not pyproject dependencies.

      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      (project_root / Packages.LOCAL_PACKAGES_FILENAME).write_text(
        '../common-lib\n',
        encoding='utf-8')
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      step.run()

      parsed = PyProjectToml.from_file(
        project_root / 'pyproject.toml',
        Packages(project_root))
      self.assertEqual(parsed.packages.production_dependencies, [])
      self.assertEqual(parsed.packages.local_dependencies, ['../common-lib'])

  def test_run_dry_run_does_not_create_pyproject(self) -> None:
    """
      Verify dry-run mode does not create pyproject.toml.

      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      step.run(dry_run=True)

      self.assertFalse((project_root / 'pyproject.toml').exists())

  def test_run_rejects_missing_packages_txt(self) -> None:
    """
      Verify run rejects a project with no packages.txt.

      :return: None
    """
    with project_context() as (_project_root, context):
      self._create_venv(context, create_packages_txt=False)
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      with self.assertRaises(DralithusProjectError):
        step.run()

  def test_run_rejects_missing_venv(self) -> None:
    """
      Verify run rejects a project with no local venv.

      :return: None
    """
    with project_context() as (_project_root, context):
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      with self.assertRaises(DralithusProjectError):
        step.run()

  def test_run_rejects_venv_without_pyvenv_cfg(self) -> None:
    """
      Verify run rejects a venv without pyvenv.cfg.

      :return: None
    """
    with project_context() as (_project_root, context):
      context.venv_path.mkdir()
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      with self.assertRaises(DralithusProjectError):
        step.run()

  def test_run_rejects_venv_without_version(self) -> None:
    """
      Verify run rejects a venv with no version metadata.

      :return: None
    """
    with project_context() as (_project_root, context):
      context.venv_path.mkdir()
      (context.venv_path / 'pyvenv.cfg').write_text(
        'home = /usr/bin\n',
        encoding='utf-8')
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      with self.assertRaises(DralithusProjectError):
        step.run()

  def test_run_leaves_valid_existing_pyproject_unchanged(self) -> None:
    """
      Verify run leaves a valid existing pyproject.toml unchanged.

      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      pyproject = project_root / 'pyproject.toml'
      text = self._pyproject_text()
      pyproject.write_text(text, encoding='utf-8')
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      step.run()

      self.assertEqual(text, pyproject.read_text(encoding='utf-8'))

  def test_run_rejects_pyproject_directory(self) -> None:
    """
      Verify run rejects pyproject.toml when it is not a file.

      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      (project_root / 'pyproject.toml').mkdir()
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      with self.assertRaises(DralithusProjectError):
        step.run()

  # noinspection PyUnusedLocal
  # pylint: disable=unused-argument
  @parameterized.expand([
    ('invalid_toml', 'invalid_toml', ''),
    ('missing_required_project_name', 'missing_required_project_name', ''),
    ('project_name_mismatch', 'project_name_mismatch', ''),
    ('python_version_mismatch', 'python_version_mismatch', ''),
    ('missing_standard_dev_dependency',
     'missing_standard_dev_dependency',
     ''),
    ('packages_txt_dependency_mismatch',
     'packages_txt_dependency_mismatch',
     'requests\n'),
    ('package_find_where_mismatch', 'package_find_where_mismatch', ''),
    ('package_find_include_mismatch', 'package_find_include_mismatch', '')
  ])
  def test_run_rejects_malformed_pyproject(
    self,
    name: str,
    malformed_case: str,
    packages_text: str
  ) -> None:
    """
      Verify run rejects malformed pyproject.toml content.

      :param name: The parameterized case name
      :param malformed_case: The malformed pyproject variant
      :param packages_text: Optional packages.txt content override
      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      if packages_text:
        (project_root / Packages.PACKAGES_FILENAME).write_text(
          packages_text,
          encoding='utf-8')
      text = self._malformed_pyproject_text(malformed_case)
      (project_root / 'pyproject.toml').write_text(text, encoding='utf-8')
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      with self.assertRaises(DralithusProjectError):
        step.run()

  def test_rollback_removes_pyproject_created_by_step(self) -> None:
    """
      Verify rollback removes pyproject.toml created by this step.

      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      step.run()
      step.rollback()

      self.assertFalse((project_root / 'pyproject.toml').exists())

  def test_rollback_is_idempotent_after_removing_pyproject(self) -> None:
    """
      Verify rollback can be called again after removing pyproject.toml.

      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      step.run()
      step.rollback()
      step.rollback()

      self.assertFalse((project_root / 'pyproject.toml').exists())

  def test_rollback_removes_pyproject_after_multiple_runs(self) -> None:
    """
      Verify rollback removes pyproject.toml after multiple run calls.

      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      step.run()
      step.run()
      step.rollback()

      self.assertFalse((project_root / 'pyproject.toml').exists())

  def test_rollback_does_not_remove_preexisting_pyproject(self) -> None:
    """
      Verify rollback leaves preexisting pyproject.toml in place.

      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      pyproject = project_root / 'pyproject.toml'
      pyproject.write_text(self._pyproject_text(), encoding='utf-8')
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      step.run()
      step.rollback()

      self.assertTrue(pyproject.is_file())

  def test_rollback_dry_run_does_not_remove_pyproject(self) -> None:
    """
      Verify rollback dry-run leaves created pyproject.toml in place.

      :return: None
    """
    with project_context() as (project_root, context):
      self._create_venv(context)
      step = CreatePyProjectTomlStep(
        context,
        'sample-project',
        'Sample project')

      step.run()
      step.rollback(dry_run=True)

      self.assertTrue((project_root / 'pyproject.toml').is_file())

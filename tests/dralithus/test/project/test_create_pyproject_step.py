"""
  test_create_pyproject_step.py: Unit tests for create_pyproject_step.
"""
# -------------------------------------------------------------------
# test_create_pyproject_step.py: Unit tests for create_pyproject_step.
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

from dralithus.project.context import ProjectContext
from dralithus.project.create_pyproject_step import CreatePyProjectStep
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages3 import Packages3
from dralithus.project.pyproject_toml import PyProjectToml


# pylint: disable-next=too-many-public-methods,too-many-lines
class TestCreatePyProjectStep(unittest.TestCase):
  """
    Unit tests for the CreatePyProjectStep class.
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
  ) -> Packages3:
    """
      Write package artifacts and return their Packages3 model.

      :param project_root: The project root directory
      :param dependencies: The packages.txt dependencies
      :param dev_dependencies: The full expected dev dependency list
      :param local_dependencies: The local-packages.txt dependencies
      :param local_dev_dependencies: The local dev dependencies
      :return: The Packages3 model
    """
    if dependencies is None:
      dependencies = []
    if dev_dependencies is None:
      dev_dependencies = cls._implicit_dev_dependencies
    if local_dependencies is None:
      local_dependencies = []
    if local_dev_dependencies is None:
      local_dev_dependencies = []
    extra_dev_dependencies = [
      dependency for dependency in dev_dependencies
      if dependency not in cls._implicit_dev_dependencies]
    package_lines = [
      *dependencies,
      *[f'{dependency} [dev]'
        for dependency in extra_dev_dependencies]]
    local_lines = [
      *local_dependencies,
      *[f'{dependency} [dev]'
        for dependency in local_dev_dependencies]]
    (project_root / Packages3.PACKAGES_FILENAME).write_text(
      '\n'.join(package_lines),
      encoding='utf-8')
    if local_lines:
      (project_root / Packages3.LOCAL_PACKAGES_FILENAME).write_text(
        '\n'.join(local_lines),
        encoding='utf-8')
    return Packages3(project_root)

  @staticmethod
  def _python_requirement() -> str:
    """
      Return the Python requirement for the test interpreter.

      :return: The Python major/minor version requirement
    """
    return f'>={sys.version_info.major}.{sys.version_info.minor}'

  def _venv_python_requirement(self, project_root: Path) -> str:
    """
      Return the Python requirement from the test project's venv.

      :param project_root: The project root directory
      :return: The Python major/minor version requirement
    """
    venv_path = project_root / 'venv'
    pyvenv_cfg = venv_path / 'pyvenv.cfg'
    if not venv_path.is_dir():
      self.fail(f'Test venv does not exist: {venv_path}')
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
  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def _pyproject_text(
    cls,
    project_name: str = 'sample-project',
    project_description: str = 'Sample project',
    package_name: str = 'sample_project',
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
    project_root: Path,
    venv_name: str = 'venv',
    create_packages_txt: bool = True
  ) -> None:
    """
      Create a real Python virtual environment for tests.

      :param project_root: The project root directory
      :param venv_name: The venv directory name
      :param create_packages_txt: True if packages.txt should be
        seeded
      :return: None
    """
    subprocess.run(
      [sys.executable, '-m', 'venv', venv_name],
      cwd=project_root,
      check=True)
    if create_packages_txt:
      (project_root / Packages3.PACKAGES_FILENAME).write_text('', encoding='utf-8')

  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def _validate_pyproject(
    self,
    project_root: Path,
    project_name: str = 'sample-project',
    project_description: str = 'Sample project',
    package_name: str = 'sample_project',
    project_version: str = '0.1.0',
    dependencies: list[str] | None = None
  ) -> None:
    """
      Verify that the on-disk pyproject.toml matches expectations.

      Loads the file via PyProjectToml.from_file and delegates the
      field comparison to PyProjectToml.matches.

      :param project_root: The project root directory
      :param project_name: The expected project distribution name
      :param project_description: The expected project description
      :param package_name: The expected Python package name
      :param project_version: The expected project version
      :param dependencies: The expected project dependencies
      :return: None
    """
    expected_packages = self._packages(
      project_root,
      dependencies or [])
    expected = PyProjectToml(
      name=project_name,
      description=project_description,
      package_name=package_name,
      python_requirement=self._venv_python_requirement(project_root),
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
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      step = CreatePyProjectStep(
        project_name='sample-project',
        project_description='Sample project',
        package_name='sample_project')

      step.run(context)

      self._validate_pyproject(project_root)

  def test_run_creates_pyproject_with_packages_txt_dependencies(self) -> None:
    """
      Verify run copies packages.txt names into dependencies.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      (project_root / Packages3.PACKAGES_FILENAME).write_text(
        '# third-party packages\n'
        '\n'
        'requests\n'
        'rich\n',
        encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      step.run(context)

      self._validate_pyproject(
        project_root,
        dependencies=['requests', 'rich'])

  def test_run_creates_pyproject_with_dev_marked_dependencies(self) -> None:
    """
      Verify run copies [dev] marked dependencies into dev metadata.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      (project_root / Packages3.PACKAGES_FILENAME).write_text(
        'requests\n'
        'pytest [dev]\n',
        encoding='utf-8')
      (project_root / Packages3.LOCAL_PACKAGES_FILENAME).write_text(
        '../common-lib\n'
        '../test-lib [dev]\n',
        encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      step.run(context)

      pyproject = PyProjectToml.from_file(
        project_root / 'pyproject.toml',
        Packages3(project_root))
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
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      (project_root / Packages3.LOCAL_PACKAGES_FILENAME).write_text(
        '../common-lib\n',
        encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      step.run(context)

      parsed = PyProjectToml.from_file(
        project_root / 'pyproject.toml',
        Packages3(project_root))
      self.assertEqual(parsed.packages.production_dependencies, [])
      self.assertEqual(parsed.packages.local_dependencies, ['../common-lib'])

  def test_run_dry_run_does_not_create_pyproject(self) -> None:
    """
      Verify dry-run mode does not create pyproject.toml.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      step.run(context, dry_run=True)

      self.assertFalse((project_root / 'pyproject.toml').exists())

  def test_run_rejects_missing_packages_txt(self) -> None:
    """
      Verify run rejects a project with no packages.txt.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root, create_packages_txt=False)
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_missing_venv(self) -> None:
    """
      Verify run rejects a project with no local venv.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_venv_without_pyvenv_cfg(self) -> None:
    """
      Verify run rejects a venv without pyvenv.cfg.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      (project_root / 'venv').mkdir()
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_venv_without_version(self) -> None:
    """
      Verify run rejects a venv with no version metadata.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      venv_path = project_root / 'venv'
      venv_path.mkdir()
      (venv_path / 'pyvenv.cfg').write_text(
        'home = /usr/bin\n',
        encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_leaves_valid_existing_pyproject_unchanged(self) -> None:
    """
      Verify run leaves a valid existing pyproject.toml unchanged.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      pyproject = project_root / 'pyproject.toml'
      text = self._pyproject_text()
      pyproject.write_text(text, encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      step.run(context)

      self.assertEqual(text, pyproject.read_text(encoding='utf-8'))

  def test_run_rejects_pyproject_directory(self) -> None:
    """
      Verify run rejects pyproject.toml when it is not a file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      (project_root / 'pyproject.toml').mkdir()
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_invalid_toml(self) -> None:
    """
      Verify run rejects pyproject.toml with invalid TOML syntax.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      (project_root / 'pyproject.toml').write_text(
        '[project\n',
        encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_missing_required_project_name(self) -> None:
    """
      Verify run rejects pyproject.toml missing project.name.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      text = self._pyproject_text().replace(
        'name = "sample-project"\n',
        '')
      (project_root / 'pyproject.toml').write_text(text, encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_project_name_mismatch(self) -> None:
    """
      Verify run rejects pyproject.toml with the wrong project name.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      text = self._pyproject_text(project_name='other-project')
      (project_root / 'pyproject.toml').write_text(text, encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_python_version_mismatch(self) -> None:
    """
      Verify run rejects pyproject.toml with the wrong Python version.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      text = self._pyproject_text(python_requirement='>=2.7')
      (project_root / 'pyproject.toml').write_text(text, encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_missing_standard_dev_dependency(self) -> None:
    """
      Verify run rejects pyproject.toml missing standard dev packages.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      text = self._pyproject_text().replace(
        '["mypy", "pylint", "parameterized"]',
        '["mypy", "pylint"]')
      (project_root / 'pyproject.toml').write_text(text, encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_packages_txt_dependency_mismatch(self) -> None:
    """
      Verify run rejects dependencies out of sync with packages.txt.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      (project_root / Packages3.PACKAGES_FILENAME).write_text(
        'requests\n',
        encoding='utf-8')
      text = self._pyproject_text(dependencies=[])
      (project_root / 'pyproject.toml').write_text(text, encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_package_find_where_mismatch(self) -> None:
    """
      Verify run rejects package discovery not rooted at src.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      text = self._pyproject_text().replace(
        'where = ["src"]',
        'where = ["."]')
      (project_root / 'pyproject.toml').write_text(text, encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_run_rejects_package_find_include_mismatch(self) -> None:
    """
      Verify run rejects package discovery with the wrong include.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      text = self._pyproject_text(package_name='other_package')
      (project_root / 'pyproject.toml').write_text(text, encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      with self.assertRaises(DralithusProjectError):
        step.run(context)

  def test_rollback_removes_pyproject_created_by_step(self) -> None:
    """
      Verify rollback removes pyproject.toml created by this step.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      step.run(context)
      step.rollback(context)

      self.assertFalse((project_root / 'pyproject.toml').exists())

  def test_rollback_removes_pyproject_after_multiple_runs(self) -> None:
    """
      Verify rollback removes pyproject.toml after multiple run calls.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      step.run(context)
      step.run(context)
      step.rollback(context)

      self.assertFalse((project_root / 'pyproject.toml').exists())

  def test_rollback_does_not_remove_preexisting_pyproject(self) -> None:
    """
      Verify rollback leaves preexisting pyproject.toml in place.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      pyproject = project_root / 'pyproject.toml'
      pyproject.write_text(self._pyproject_text(), encoding='utf-8')
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      step.run(context)
      step.rollback(context)

      self.assertTrue(pyproject.is_file())

  def test_rollback_dry_run_does_not_remove_pyproject(self) -> None:
    """
      Verify rollback dry-run leaves created pyproject.toml in place.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      self._create_venv(project_root)
      step = CreatePyProjectStep(
        'sample-project',
        'Sample project',
        'sample_project')

      step.run(context)
      step.rollback(context, dry_run=True)

      self.assertTrue((project_root / 'pyproject.toml').is_file())

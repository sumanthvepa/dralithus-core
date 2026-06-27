"""
  test_pyproject_toml.py: Unit tests for pyproject_toml.
"""
# -------------------------------------------------------------------
# test_pyproject_toml.py: Unit tests for pyproject_toml.
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
import tomllib
import unittest

from dralithus.test.project import write_package_artifacts
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages
from dralithus.project.pyproject_toml import PyProjectToml


# pylint: disable-next=too-many-public-methods
class TestPyProjectToml(unittest.TestCase):
  """
    Unit tests for the PyProjectToml class.
  """
  _implicit_dev_dependencies = ['mypy', 'pylint', 'parameterized']

  @classmethod
  def _packages(
    cls,
    production_dependencies: list[str] | None = None,
    dev_dependencies: list[str] | None = None,
    local_dependencies: list[str] | None = None,
    local_dev_dependencies: list[str] | None = None
  ) -> Packages:
    """
      Construct a Packages fixture from package artifact contents.

      :param production_dependencies: The packages.txt dependencies
      :param dev_dependencies: The expected full dev dependency list
      :param local_dependencies: The local-packages.txt dependencies
      :param local_dev_dependencies: The local dev dependencies
      :return: The Packages fixture
    """
    with TemporaryDirectory() as tmpdir:
      packages = write_package_artifacts(
        project_root=Path(tmpdir),
        production_dependencies=production_dependencies,
        dev_dependencies=dev_dependencies,
        local_dependencies=local_dependencies,
        local_dev_dependencies=local_dev_dependencies)
    return packages

  @classmethod
  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def _make(
    cls,
    name: str = 'example-project',
    description: str = 'An example project',
    package_name: str = 'example',
    python_requirement: str = '>=3.13',
    dependencies: list[str] | None = None,
    dev_dependencies: list[str] | None = None,
    version: str = '0.1.0',
  ) -> PyProjectToml:
    """
      Construct a PyProjectToml with sensible defaults.

      :param name: The project distribution name
      :param description: The project description
      :param package_name: The Python package name
      :param python_requirement: The Python version requirement
      :param dependencies: The production dependencies
      :param dev_dependencies: The full dev dependency list
      :param version: The project version
      :return: The pyproject model
    """
    if dependencies is None:
      dependencies = []
    if dev_dependencies is None:
      dev_dependencies = cls._implicit_dev_dependencies
    return PyProjectToml(
      name=name,
      description=description,
      package_name=package_name,
      python_requirement=python_requirement,
      packages=cls._packages(dependencies, dev_dependencies),
      version=version)

  @staticmethod
  def _well_formed_toml() -> str:
    """
      Return well-formed pyproject.toml text for from_file tests.

      :return: The pyproject.toml text
    """
    return (
      '[build-system]\n'
      'requires = ["setuptools>=69", "wheel"]\n'
      'build-backend = "setuptools.build_meta"\n'
      '\n'
      '[project]\n'
      'name = "example-project"\n'
      'version = "0.1.0"\n'
      'description = "An example project"\n'
      'readme = "README.md"\n'
      'requires-python = ">=3.13"\n'
      'dependencies = []\n'
      '\n'
      '[project.optional-dependencies]\n'
      'dev = ["mypy", "pylint", "parameterized"]\n'
      '\n'
      '[tool.setuptools.packages.find]\n'
      'where = ["src"]\n'
      'include = ["example*"]\n'
      'namespaces = true\n')

  # -------------------- Construction --------------------

  def test_construction_stores_all_fields(self) -> None:
    """
      Verify the constructor stores every field and the properties
      return them.

      :return: None
    """
    pp = self._make(
      name='my-project',
      description='My project',
      package_name='my_pkg',
      python_requirement='>=3.14',
      dependencies=['requests', 'click'],
      dev_dependencies=['mypy', 'pylint', 'parameterized'],
      version='1.2.3')
    self.assertEqual(pp.name, 'my-project')
    self.assertEqual(pp.description, 'My project')
    self.assertEqual(pp.package_name, 'my_pkg')
    self.assertEqual(pp.python_requirement, '>=3.14')
    self.assertEqual(
      pp.packages.production_dependencies,
      ['requests', 'click'])
    self.assertEqual(
      pp.packages.dev_dependencies,
      ['mypy', 'pylint', 'parameterized'])
    self.assertEqual(pp.version, '1.2.3')

  def test_default_version_is_0_1_0(self) -> None:
    """
      Verify version defaults to '0.1.0' when omitted.

      :return: None
    """
    pp = PyProjectToml(
      name='x',
      description='y',
      package_name='z',
      python_requirement='>=3.13',
      packages=self._packages())
    self.assertEqual(pp.version, '0.1.0')

  # -------------------- to_toml --------------------

  def test_to_toml_output_parses_as_toml(self) -> None:
    """
      Verify to_toml output parses successfully with tomllib.

      :return: None
    """
    pp = self._make()
    parsed = tomllib.loads(pp.to_toml())
    self.assertIsInstance(parsed, dict)

  def test_to_toml_renders_build_system_block(self) -> None:
    """
      Verify the build-system block matches M42 invariants.

      :return: None
    """
    pp = self._make()
    parsed = tomllib.loads(pp.to_toml())
    self.assertEqual(
      parsed['build-system']['requires'],
      ['setuptools>=69', 'wheel'])
    self.assertEqual(
      parsed['build-system']['build-backend'],
      'setuptools.build_meta')

  def test_to_toml_renders_project_metadata(self) -> None:
    """
      Verify the project block contains all variable metadata.

      :return: None
    """
    pp = self._make(
      name='foo',
      description='Foo desc',
      python_requirement='>=3.13',
      version='1.2.3',
      dependencies=['requests'])
    parsed = tomllib.loads(pp.to_toml())
    self.assertEqual(parsed['project']['name'], 'foo')
    self.assertEqual(parsed['project']['version'], '1.2.3')
    self.assertEqual(parsed['project']['description'], 'Foo desc')
    self.assertEqual(parsed['project']['readme'], 'README.md')
    self.assertEqual(
      parsed['project']['requires-python'], '>=3.13')
    self.assertEqual(parsed['project']['dependencies'], ['requests'])

  def test_to_toml_renders_dev_dependencies(self) -> None:
    """
      Verify dev dependencies are written under
      [project.optional-dependencies].

      :return: None
    """
    pp = self._make(
      dev_dependencies=[
        'mypy', 'pylint', 'parameterized', 'pytest'])
    parsed = tomllib.loads(pp.to_toml())
    self.assertEqual(
      parsed['project']['optional-dependencies']['dev'],
      ['mypy', 'pylint', 'parameterized', 'pytest'])

  def test_to_toml_renders_tool_setuptools_block(self) -> None:
    """
      Verify the [tool.setuptools.packages.find] block.

      :return: None
    """
    pp = self._make(package_name='example')
    parsed = tomllib.loads(pp.to_toml())
    find = parsed['tool']['setuptools']['packages']['find']
    self.assertEqual(find['where'], ['src'])
    self.assertEqual(find['include'], ['example*'])
    self.assertEqual(find['namespaces'], True)

  def test_to_toml_escapes_double_quotes_in_strings(self) -> None:
    """
      Verify double quotes in string values are escaped so the
      output still parses as valid TOML.

      :return: None
    """
    pp = self._make(description='He said "hi"')
    parsed = tomllib.loads(pp.to_toml())
    self.assertEqual(
      parsed['project']['description'], 'He said "hi"')

  def test_to_toml_ignores_unmarked_local_dependencies(self) -> None:
    """
      Verify unmarked local dependencies are not rendered in pyproject.

      :return: None
    """
    pp = PyProjectToml(
      name='example-project',
      description='An example project',
      package_name='example',
      python_requirement='>=3.13',
      packages=self._packages(local_dependencies=['../common-lib']))
    parsed = tomllib.loads(pp.to_toml())
    self.assertEqual(parsed['project']['dependencies'], [])

  # -------------------- from_file --------------------

  def test_from_file_loads_well_formed_pyproject(self) -> None:
    """
      Verify from_file extracts every variable field from a
      well-formed pyproject.toml.

      :return: None
    """
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(self._well_formed_toml(), encoding='utf-8')
      pp = PyProjectToml.from_file(path, self._packages())
    self.assertEqual(pp.name, 'example-project')
    self.assertEqual(pp.version, '0.1.0')
    self.assertEqual(pp.description, 'An example project')
    self.assertEqual(pp.package_name, 'example')
    self.assertEqual(pp.python_requirement, '>=3.13')
    self.assertEqual(pp.packages.production_dependencies, [])
    self.assertEqual(
      pp.packages.dev_dependencies,
      ['mypy', 'pylint', 'parameterized'])

  def test_from_file_rejects_invalid_toml(self) -> None:
    """
      Verify from_file raises on malformed TOML.

      :return: None
    """
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text('not = valid = toml', encoding='utf-8')
      with self.assertRaises(DralithusProjectError):
        PyProjectToml.from_file(path, self._packages())

  def test_from_file_rejects_directory_path(self) -> None:
    """
      Verify from_file raises when path is a directory.

      :return: None
    """
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.mkdir()
      with self.assertRaises(DralithusProjectError):
        PyProjectToml.from_file(path, self._packages())

  def test_from_file_rejects_wrong_build_requires(self) -> None:
    """
      Verify from_file rejects a mismatched build-system.requires.

      :return: None
    """
    text = self._well_formed_toml().replace(
      '["setuptools>=69", "wheel"]',
      '["setuptools>=70"]')
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(text, encoding='utf-8')
      with self.assertRaises(DralithusProjectError):
        PyProjectToml.from_file(path, self._packages())

  def test_from_file_rejects_wrong_build_backend(self) -> None:
    """
      Verify from_file rejects a mismatched build-backend.

      :return: None
    """
    text = self._well_formed_toml().replace(
      'build-backend = "setuptools.build_meta"',
      'build-backend = "flit_core.buildapi"')
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(text, encoding='utf-8')
      with self.assertRaises(DralithusProjectError):
        PyProjectToml.from_file(path, self._packages())

  def test_from_file_rejects_wrong_readme(self) -> None:
    """
      Verify from_file rejects readme != "README.md".

      :return: None
    """
    text = self._well_formed_toml().replace(
      'readme = "README.md"',
      'readme = "Readme.txt"')
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(text, encoding='utf-8')
      with self.assertRaises(DralithusProjectError):
        PyProjectToml.from_file(path, self._packages())

  def test_from_file_rejects_wrong_packages_where(self) -> None:
    """
      Verify from_file rejects packages.find.where != ["src"].

      :return: None
    """
    text = self._well_formed_toml().replace(
      'where = ["src"]',
      'where = ["source"]')
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(text, encoding='utf-8')
      with self.assertRaises(DralithusProjectError):
        PyProjectToml.from_file(path, self._packages())

  def test_from_file_rejects_namespaces_false(self) -> None:
    """
      Verify from_file rejects namespaces = false.

      :return: None
    """
    text = self._well_formed_toml().replace(
      'namespaces = true',
      'namespaces = false')
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(text, encoding='utf-8')
      with self.assertRaises(DralithusProjectError):
        PyProjectToml.from_file(path, self._packages())

  def test_from_file_rejects_missing_project_name(self) -> None:
    """
      Verify from_file raises when project.name is missing.

      :return: None
    """
    text = self._well_formed_toml().replace(
      'name = "example-project"\n', '')
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(text, encoding='utf-8')
      with self.assertRaises(DralithusProjectError):
        PyProjectToml.from_file(path, self._packages())

  def test_from_file_rejects_missing_baseline_dev_dependency(
    self,
  ) -> None:
    """
      Verify from_file raises when an M42 baseline dev dependency
      is missing from the file.

      :return: None
    """
    text = self._well_formed_toml().replace(
      '["mypy", "pylint", "parameterized"]',
      '["pylint", "parameterized"]')
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(text, encoding='utf-8')
      with self.assertRaises(DralithusProjectError):
        PyProjectToml.from_file(path, self._packages())

  def test_from_file_rejects_malformed_include_pattern(self) -> None:
    """
      Verify from_file rejects an include without the trailing
      wildcard.

      :return: None
    """
    text = self._well_formed_toml().replace(
      'include = ["example*"]',
      'include = ["example"]')
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(text, encoding='utf-8')
      with self.assertRaises(DralithusProjectError):
        PyProjectToml.from_file(path, self._packages())

  def test_from_file_accepts_extra_dev_dependencies(self) -> None:
    """
      Verify from_file accepts dev dependencies beyond Packages.

      :return: None
    """
    text = self._well_formed_toml().replace(
      '["mypy", "pylint", "parameterized"]',
      '["mypy", "pylint", "parameterized", "pytest"]')
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(text, encoding='utf-8')
      pp = PyProjectToml.from_file(path, self._packages())
    self.assertEqual(pp.name, 'example-project')

  def test_from_file_rejects_dependency_mismatch(self) -> None:
    """
      Verify from_file rejects dependencies that differ from Packages.

      :return: None
    """
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(self._well_formed_toml(), encoding='utf-8')
      with self.assertRaises(DralithusProjectError):
        PyProjectToml.from_file(
          path,
          self._packages(production_dependencies=['requests']))

  def test_from_file_ignores_unmarked_local_dependencies(self) -> None:
    """
      Verify from_file ignores unmarked local dependencies.

      :return: None
    """
    with TemporaryDirectory() as tmpdir:
      path = Path(tmpdir) / 'pyproject.toml'
      path.write_text(self._well_formed_toml(), encoding='utf-8')
      pp = PyProjectToml.from_file(
        path,
        self._packages(local_dependencies=['../common-lib']))
    self.assertEqual(pp.packages.local_dependencies, ['../common-lib'])

  # -------------------- matches --------------------

  def test_matches_passes_when_all_fields_equal(self) -> None:
    """
      Verify matches() returns None when all fields are equal.

      :return: None
    """
    expected = self._make()
    actual = self._make()
    actual.matches(expected)

  def test_matches_rejects_name_mismatch(self) -> None:
    """
      Verify matches() raises when names differ.

      :return: None
    """
    expected = self._make(name='foo')
    actual = self._make(name='bar')
    with self.assertRaises(DralithusProjectError):
      actual.matches(expected)

  def test_matches_rejects_version_mismatch(self) -> None:
    """
      Verify matches() raises when versions differ.

      :return: None
    """
    expected = self._make(version='1.0.0')
    actual = self._make(version='2.0.0')
    with self.assertRaises(DralithusProjectError):
      actual.matches(expected)

  def test_matches_rejects_description_mismatch(self) -> None:
    """
      Verify matches() raises when descriptions differ.

      :return: None
    """
    expected = self._make(description='foo')
    actual = self._make(description='bar')
    with self.assertRaises(DralithusProjectError):
      actual.matches(expected)

  def test_matches_rejects_package_name_mismatch(self) -> None:
    """
      Verify matches() raises when package names differ.

      :return: None
    """
    expected = self._make(package_name='foo')
    actual = self._make(package_name='bar')
    with self.assertRaises(DralithusProjectError):
      actual.matches(expected)

  def test_matches_rejects_python_requirement_mismatch(self) -> None:
    """
      Verify matches() raises when python_requirement differs.

      :return: None
    """
    expected = self._make(python_requirement='>=3.13')
    actual = self._make(python_requirement='>=3.14')
    with self.assertRaises(DralithusProjectError):
      actual.matches(expected)

  def test_matches_rejects_dependencies_mismatch(self) -> None:
    """
      Verify matches() raises when dependencies differ.

      :return: None
    """
    expected = self._make(dependencies=['requests'])
    actual = self._make(dependencies=['urllib3'])
    with self.assertRaises(DralithusProjectError):
      actual.matches(expected)

  def test_matches_passes_with_dev_dependencies_superset(self) -> None:
    """
      Verify matches() accepts actual having extra dev deps.

      :return: None
    """
    expected = self._make(
      dev_dependencies=['mypy', 'pylint', 'parameterized'])
    actual = self._make(
      dev_dependencies=[
        'mypy', 'pylint', 'parameterized', 'pytest'])
    actual.matches(expected)

  def test_matches_rejects_missing_dev_dependency(self) -> None:
    """
      Verify matches() raises when actual is missing a dev
      dependency that expected requires.

      :return: None
    """
    expected = self._make(
      dev_dependencies=[
        'mypy', 'pylint', 'parameterized', 'pytest'])
    actual = self._make(
      dev_dependencies=['mypy', 'pylint', 'parameterized'])
    with self.assertRaises(DralithusProjectError):
      actual.matches(expected)

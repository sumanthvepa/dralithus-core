"""
  test_create_python_project_step.py: Unit tests for
  create_python_project_step.
"""
# -------------------------------------------------------------------
# test_create_python_project_step.py: Unit tests for
# create_python_project_step.
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
import contextlib
from pathlib import Path
import shutil
import unittest
from typing import cast, override
from unittest.mock import patch

from dralithus.test.project import project_context
from dralithus.project.context import ProjectContext
from dralithus.project.create_python_project_step import (
  CreatePythonProjectStep)
from dralithus.project.error import DralithusProjectError
from dralithus.project.execution_step import ExecutionStep
from dralithus.project.packages import Packages
from dralithus.project.pyproject_toml import PyProjectToml


_MODULE = 'dralithus.project.create_python_project_step'

# The child step class name as imported by the module under test,
# paired with the short label the fakes use in their recorded log.
_CHILD_LABELS = (
  ('CreatePackagesStep', 'packages'),
  ('CreateSourceTreeStep', 'source_tree'),
  ('CreateTestsTreeStep', 'tests_tree'),
  ('CreatePylintConfigurationStep', 'pylint'),
  ('CreateMypyConfigurationStep', 'mypy'),
  ('CreateVenvStep', 'venv'),
  ('CreatePyProjectTomlStep', 'pyproject'),
  ('InstallDependenciesStep', 'dependencies'))

_RUN_ORDER = [label for _name, label in _CHILD_LABELS]


class _RecordingStep(ExecutionStep):
  """
    A fake execution step that records run and rollback calls.

    Records each run and rollback, with its dry-run flag, into a
    shared log so tests can assert orchestration order without any
    real file-system work.
  """
  def __init__(
    self,
    context: ProjectContext,
    label: str,
    log: list[str],
    fails: bool = False
  ) -> None:
    """
      Initialize the recording step.

      :param context: The shared project creation context
      :param label: The short label identifying this step in the log
      :param log: The shared log of run and rollback calls
      :param fails: True if run should raise DralithusProjectError
      :return: None
    """
    super().__init__(context)
    self._label = label
    self._log = log
    self._fails = fails

  @override
  def run(self, dry_run: bool = False) -> None:
    """
      Record the run call and optionally fail.

      :param dry_run: True if this is a dry-run call
      :return: None
      :raises DralithusProjectError: When this step is set to fail
    """
    self._log.append(f'run {self._label} dry_run={dry_run}')
    if self._fails:
      raise DralithusProjectError(f'{self._label} failed')

  @override
  def rollback(self, dry_run: bool = False) -> None:
    """
      Record the rollback call.

      :param dry_run: True if this is a dry-run rollback
      :return: None
    """
    self._log.append(f'rollback {self._label} dry_run={dry_run}')


# pylint: disable-next=too-few-public-methods
class _StepFactory:
  """
    A callable that replaces a child step class in the module.

    Records the constructor arguments each child receives and returns
    a _RecordingStep in its place.
  """
  def __init__(
    self,
    label: str,
    log: list[str],
    calls: list[tuple[str, tuple[object, ...]]],
    failing_label: str | None = None
  ) -> None:
    """
      Initialize the step factory.

      :param label: The short label of the child this factory replaces
      :param log: The shared log of run and rollback calls
      :param calls: The shared record of constructor calls
      :param failing_label: The label whose run should fail, if any
      :return: None
    """
    self._label = label
    self._log = log
    self._calls = calls
    self._failing_label = failing_label

  def __call__(self, *args: object) -> _RecordingStep:
    """
      Record the constructor call and build a recording step.

      :param args: The constructor arguments the child received
      :return: A recording step standing in for the child
    """
    self._calls.append((self._label, args))
    context = cast(ProjectContext, args[0])
    return _RecordingStep(
      context,
      self._label,
      self._log,
      fails=self._label == self._failing_label)


class _FakeVenvStep(ExecutionStep):
  """
    A fake venv step that creates minimal venv metadata on disk.

    Creates pyvenv.cfg and an executable bin/python so the real
    downstream pyproject step can derive requires-python, without
    running the real venv module.
  """
  def __init__(
    self,
    context: ProjectContext,
    python_executable: Path
  ) -> None:
    """
      Initialize the fake venv step.

      :param context: The shared project creation context
      :param python_executable: The unused interpreter path
      :return: None
    """
    super().__init__(context)
    del python_executable

  @override
  def run(self, dry_run: bool = False) -> None:
    """
      Create the fake venv metadata.

      :param dry_run: True if the step should change nothing
      :return: None
    """
    if not dry_run:
      bin_directory = self._context.venv_path / 'bin'
      bin_directory.mkdir(parents=True, exist_ok=True)
      (self._context.venv_path / 'pyvenv.cfg').write_text(
        'version = 3.14.0\n', encoding='utf-8')
      python = bin_directory / 'python'
      python.write_text('', encoding='utf-8')
      python.chmod(0o755)

  @override
  def rollback(self, dry_run: bool = False) -> None:
    """
      Remove the fake venv directory.

      :param dry_run: True if the step should change nothing
      :return: None
    """
    if not dry_run and self._context.venv_path.exists():
      shutil.rmtree(self._context.venv_path)


class _FakeInstallDependenciesStep(ExecutionStep):
  """
    A fake dependency step that writes an empty requirements.txt.

    Stands in for the real pip-driven step so the integration test
    never installs packages.
  """
  def __init__(self, context: ProjectContext) -> None:
    """
      Initialize the fake dependency step.

      :param context: The shared project creation context
      :return: None
    """
    super().__init__(context)
    self._created = False

  @override
  def run(self, dry_run: bool = False) -> None:
    """
      Write an empty requirements.txt.

      :param dry_run: True if the step should change nothing
      :return: None
    """
    if not dry_run:
      (self._context.project_root / 'requirements.txt').write_text(
        '', encoding='utf-8')
      self._created = True

  @override
  def rollback(self, dry_run: bool = False) -> None:
    """
      Remove the requirements.txt this step created.

      :param dry_run: True if the step should change nothing
      :return: None
    """
    if not dry_run and self._created:
      (self._context.project_root / 'requirements.txt').unlink(
        missing_ok=True)
      self._created = False


class _FailingInstallDependenciesStep(ExecutionStep):
  """
    A fake dependency step whose run always fails.

    Simulates a late-step failure so the composite rolls back the
    real artifacts created by the earlier children.
  """
  @override
  def run(self, dry_run: bool = False) -> None:
    """
      Fail unless this is a dry run.

      :param dry_run: True if the step should change nothing
      :return: None
      :raises DralithusProjectError: Whenever this is not a dry run
    """
    if not dry_run:
      raise DralithusProjectError('dependencies failed')

  @override
  def rollback(self, dry_run: bool = False) -> None:
    """
      Do nothing; this step created no artifacts.

      :param dry_run: True if the step should change nothing
      :return: None
    """
    del dry_run


class TestCreatePythonProjectStep(unittest.TestCase):
  """
    Unit tests for the CreatePythonProjectStep class.

    CreatePythonProjectStep wires the leaf and composite project
    creation steps in dependency order and delegates orchestration,
    rollback, and dry-run to CompositeExecutionStep. These tests cover
    the step's own wiring, argument passing, and guarded dry-run
    behaviour rather than re-testing the exhaustive behaviour of the
    child steps, which is covered by their own suites.
  """
  _PYTHON = Path('/usr/bin/python3')

  @staticmethod
  def _labels(log: list[str], action: str) -> list[str]:
    """
      Return the step labels recorded for a given action.

      :param log: The shared log of run and rollback calls
      :param action: The action to filter for ('run' or 'rollback')
      :return: The step labels in the order they were recorded
    """
    return [
      entry.split()[1] for entry in log
      if entry.startswith(f'{action} ')]

  def _patch_children(
    self,
    log: list[str],
    calls: list[tuple[str, tuple[object, ...]]],
    failing_label: str | None = None
  ) -> None:
    """
      Patch every child step class with a recording factory.

      :param log: The shared log of run and rollback calls
      :param calls: The shared record of constructor calls
      :param failing_label: The label whose run should fail, if any
      :return: None
    """
    stack = contextlib.ExitStack()
    for name, label in _CHILD_LABELS:
      stack.enter_context(
        patch(
          f'{_MODULE}.{name}',
          _StepFactory(label, log, calls, failing_label)))
    self.addCleanup(stack.close)

  # constructor

  def test_constructor_wires_children_in_dependency_order(self) -> None:
    """
      Verify the constructor creates the child steps and runs them in
      the expected dependency order.
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls)
    with project_context() as (_project_root, context):
      step = CreatePythonProjectStep(context, self._PYTHON)

      step.run()

      self.assertEqual(_RUN_ORDER, self._labels(log, 'run'))

  def test_constructor_passes_expected_arguments_to_children(
    self
  ) -> None:
    """
      Verify each child step receives the constructor arguments it
      needs, including python_executable and the project metadata.
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls)
    with project_context() as (_project_root, context):
      CreatePythonProjectStep(context, self._PYTHON)

      call_map = dict(calls)
      for label in ('packages', 'source_tree', 'tests_tree',
                    'pylint', 'mypy', 'dependencies'):
        self.assertEqual((context,), call_map[label])
      self.assertEqual((context, self._PYTHON), call_map['venv'])
      self.assertEqual(
        (context,
         context.project_name,
         context.project_description,
         context.project_version),
        call_map['pyproject'])

  # run

  def test_run_rolls_back_children_and_reraises_on_failure(
    self
  ) -> None:
    """
      Verify that a child failure during run rolls back the children
      in reverse order and re-raises the error.
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls, failing_label='dependencies')
    with project_context() as (_project_root, context):
      step = CreatePythonProjectStep(context, self._PYTHON)

      with self.assertRaises(DralithusProjectError):
        step.run()

      self.assertEqual(
        list(reversed(_RUN_ORDER)),
        self._labels(log, 'rollback'))

  # dry run

  def test_run_dry_run_validates_independent_children_only_when_empty(
    self
  ) -> None:
    """
      Verify a dry run against an empty project root validates the
      independent children, skips the dependent children whose
      prerequisites are absent, and creates nothing.
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls)
    with project_context() as (project_root, context):
      step = CreatePythonProjectStep(context, self._PYTHON)

      step.run(dry_run=True)

      run_labels = self._labels(log, 'run')
      for label in ('packages', 'source_tree', 'tests_tree',
                    'pylint', 'mypy', 'venv'):
        self.assertIn(label, run_labels)
      self.assertNotIn('pyproject', run_labels)
      self.assertNotIn('dependencies', run_labels)
      self.assertEqual([], list(project_root.iterdir()))

  def test_run_dry_run_validates_pyproject_when_prerequisites_exist(
    self
  ) -> None:
    """
      Verify the dry run validates pyproject.toml when its
      prerequisites (packages.txt and venv metadata) already exist.
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls)
    with project_context() as (project_root, context):
      (project_root / Packages.PACKAGES_FILENAME).write_text(
        '', encoding='utf-8')
      context.venv_path.mkdir()
      (context.venv_path / 'pyvenv.cfg').write_text(
        'version = 3.14.0\n', encoding='utf-8')
      step = CreatePythonProjectStep(context, self._PYTHON)

      step.run(dry_run=True)

      self.assertIn('pyproject', self._labels(log, 'run'))

  def test_run_dry_run_validates_dependencies_when_prerequisites_exist(
    self
  ) -> None:
    """
      Verify the dry run reaches dependency validation when a venv
      Python and a package file already exist.
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls)
    with project_context() as (project_root, context):
      (project_root / Packages.PACKAGES_FILENAME).write_text(
        '', encoding='utf-8')
      bin_directory = context.venv_path / 'bin'
      bin_directory.mkdir(parents=True)
      python = bin_directory / 'python'
      python.write_text('', encoding='utf-8')
      python.chmod(0o755)
      step = CreatePythonProjectStep(context, self._PYTHON)

      step.run(dry_run=True)

      self.assertIn('dependencies', self._labels(log, 'run'))

  def test_run_dry_run_reraises_child_validation_error(self) -> None:
    """
      Verify a dry-run validation error from a child is not swallowed
      and does not trigger rollback.
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls, failing_label='source_tree')
    with project_context() as (_project_root, context):
      step = CreatePythonProjectStep(context, self._PYTHON)

      with self.assertRaises(DralithusProjectError):
        step.run(dry_run=True)

      self.assertEqual([], self._labels(log, 'rollback'))

  # rollback

  def test_rollback_rolls_back_children_in_reverse_order(self) -> None:
    """
      Verify an explicit rollback delegates to the children in reverse
      dependency order.
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls)
    with project_context() as (_project_root, context):
      step = CreatePythonProjectStep(context, self._PYTHON)

      step.rollback()

      self.assertEqual(
        list(reversed(_RUN_ORDER)),
        self._labels(log, 'rollback'))

  def test_rollback_dry_run_forwards_dry_run_to_children(self) -> None:
    """
      Verify rollback(dry_run=True) forwards the dry-run flag to every
      child rollback.
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls)
    with project_context() as (_project_root, context):
      step = CreatePythonProjectStep(context, self._PYTHON)

      step.rollback(dry_run=True)

      rollback_entries = [
        entry for entry in log if entry.startswith('rollback ')]
      self.assertEqual(len(_RUN_ORDER), len(rollback_entries))
      for entry in rollback_entries:
        self.assertIn('dry_run=True', entry)

  # integration

  def test_run_with_real_files_and_fake_expensive_steps_creates_shape(
    self
  ) -> None:
    """
      Verify the top-level composition produces a coherent project
      shape using real file-system children and faked venv and
      dependency steps.
    """
    with project_context() as (project_root, context):
      with patch(f'{_MODULE}.CreateVenvStep', _FakeVenvStep), \
          patch(f'{_MODULE}.InstallDependenciesStep',
                _FakeInstallDependenciesStep):
        step = CreatePythonProjectStep(context, self._PYTHON)

        step.run()

      package = context.package_name
      self.assertTrue(
        (project_root / Packages.PACKAGES_FILENAME).is_file())
      self.assertTrue(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).is_file())
      self.assertTrue(
        (project_root / 'src' / package / '.gitignore').is_file())
      self.assertFalse(
        (project_root / 'src' / package / '__init__.py').exists())
      self.assertTrue(
        (project_root / 'tests' / package / 'test'
         / '__init__.py').is_file())
      self.assertTrue((project_root / 'pylintrc').is_file())
      self.assertTrue((project_root / 'mypy.ini').is_file())
      self.assertTrue(
        (project_root / 'stubs' / 'parameterized'
         / '__init__.pyi').is_file())
      self.assertTrue((project_root / 'pyproject.toml').is_file())

      expected_packages = Packages(project_root)
      expected = PyProjectToml(
        name=context.project_name,
        description=context.project_description,
        package_name=context.package_name,
        python_requirement='>=3.14',
        packages=expected_packages,
        version=context.project_version)
      actual = PyProjectToml.from_file(
        project_root / 'pyproject.toml', expected_packages)
      actual.matches(expected)

  def test_failed_late_step_rolls_back_real_owned_artifacts(
    self
  ) -> None:
    """
      Verify that when a late child fails, the real artifacts created
      by earlier children are removed by rollback.
    """
    with project_context() as (project_root, context):
      with patch(f'{_MODULE}.CreateVenvStep', _FakeVenvStep), \
          patch(f'{_MODULE}.InstallDependenciesStep',
                _FailingInstallDependenciesStep):
        step = CreatePythonProjectStep(context, self._PYTHON)

        with self.assertRaises(DralithusProjectError):
          step.run()

      self.assertFalse((project_root / 'src').exists())
      self.assertFalse((project_root / 'tests').exists())
      self.assertFalse(
        (project_root / Packages.PACKAGES_FILENAME).exists())
      self.assertFalse(
        (project_root / Packages.LOCAL_PACKAGES_FILENAME).exists())
      self.assertFalse((project_root / 'pyproject.toml').exists())
      self.assertFalse((project_root / 'pylintrc').exists())
      self.assertFalse((project_root / 'mypy.ini').exists())
      self.assertFalse((project_root / 'stubs').exists())
      self.assertFalse(context.venv_path.exists())


if __name__ == '__main__':
  unittest.main()

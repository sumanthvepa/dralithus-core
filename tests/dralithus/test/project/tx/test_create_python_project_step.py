"""
  test_create_python_project_step.py: Unit tests for
  dralithus.project.tx.create_python_project_step.
"""
# -------------------------------------------------------------------
# test_create_python_project_step.py: Unit tests for
# dralithus.project.tx.create_python_project_step.
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
from dralithus.test.project.tx import RecordingStep
from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages
from dralithus.project.pyproject_toml import PyProjectToml
from dralithus.project.tx.create_python_project_step import (
  CreatePythonProjectStep)
from dralithus.project.tx.execution_step import ExecutionStep, execute
from dralithus.project.tx.project_state import ProjectState


_MODULE = 'dralithus.project.tx.create_python_project_step'

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

_STEP_ORDER = [label for _name, label in _CHILD_LABELS]


# pylint: disable-next=too-few-public-methods
class _StepFactory:
  """
    A callable that replaces a child step class in the module.

    Records the constructor arguments each child receives and
    returns a RecordingStep in its place.
  """
  # pylint: disable-next=too-many-arguments,too-many-positional-arguments
  def __init__(
    self,
    label: str,
    log: list[str],
    calls: list[tuple[str, tuple[object, ...]]],
    failing_label: str | None = None,
    failing_phase: str | None = None
  ) -> None:
    """
      Initialize the step factory.

      :param label: The short label of the child this factory
        replaces
      :param log: The shared log of phase calls
      :param calls: The shared record of constructor calls
      :param failing_label: The label whose step should fail, if any
      :param failing_phase: The phase in which the failing step
        should fail
      :return: None
    """
    self._label = label
    self._log = log
    self._calls = calls
    self._failing_label = failing_label
    self._failing_phase = failing_phase

  def __call__(self, *args: object) -> RecordingStep:
    """
      Record the constructor call and build a recording step.

      :param args: The constructor arguments the child received
      :return: A recording step standing in for the child
    """
    self._calls.append((self._label, args))
    context = cast(ProjectContext, args[0])
    fails_in = (
      self._failing_phase if self._label == self._failing_label
      else None)
    return RecordingStep(context, self._label, self._log, fails_in)


class _FakeVenvStep(ExecutionStep):
  """
    A fake venv step that creates minimal venv metadata on disk.

    Creates pyvenv.cfg and an executable bin/python so the real
    downstream pyproject step can derive requires-python, without
    running the real venv module. Its prepare declares the same
    claims the real step would, so downstream prepares validate
    against them.
  """
  _VERSION = '3.14.0'

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
  def prepare(self, state: ProjectState) -> None:
    """
      Claim the projected venv and its Python executable.

      :param state: The projected project state to read and extend
      :return: None
    """
    state.claim_venv(self._context.venv_path, self._VERSION)
    state.claim_executable(self._context.venv_python)

  @override
  def commit(self) -> None:
    """
      Create the fake venv metadata.

      :return: None
    """
    bin_directory = self._context.venv_path / 'bin'
    bin_directory.mkdir(parents=True, exist_ok=True)
    (self._context.venv_path / 'pyvenv.cfg').write_text(
      f'version = {self._VERSION}\n', encoding='utf-8')
    python = bin_directory / 'python'
    python.write_text('', encoding='utf-8')
    python.chmod(0o755)

  @override
  def abort(self) -> None:
    """
      Remove the fake venv directory.

      :return: None
    """
    if self._context.venv_path.exists():
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
  def prepare(self, state: ProjectState) -> None:
    """
      Claim the projected requirements.txt.

      :param state: The projected project state to read and extend
      :return: None
    """
    state.claim_file(
      self._context.project_root / 'requirements.txt')

  @override
  def commit(self) -> None:
    """
      Write an empty requirements.txt.

      :return: None
    """
    (self._context.project_root / 'requirements.txt').write_text(
      '', encoding='utf-8')
    self._created = True

  @override
  def abort(self) -> None:
    """
      Remove the requirements.txt this step created.

      :return: None
    """
    if self._created:
      (self._context.project_root / 'requirements.txt').unlink(
        missing_ok=True)
      self._created = False


class _FailingInstallDependenciesStep(ExecutionStep):
  """
    A fake dependency step whose commit always fails.

    Simulates a late-step failure so the global abort removes the
    real artifacts created by the earlier children.
  """
  @override
  def prepare(self, state: ProjectState) -> None:
    """
      Claim the projected requirements.txt.

      :param state: The projected project state to read and extend
      :return: None
    """
    state.claim_file(
      self._context.project_root / 'requirements.txt')

  @override
  def commit(self) -> None:
    """
      Fail the commit.

      :return: None
      :raises DralithusProjectError: Always
    """
    raise DralithusProjectError('dependencies failed')

  @override
  def abort(self) -> None:
    """
      Do nothing; this step created no artifacts.

      :return: None
    """


class TestCreatePythonProjectStep(unittest.TestCase):
  """
    Unit tests for the CreatePythonProjectStep class.

    CreatePythonProjectStep wires the leaf and composite project
    creation steps in dependency order and delegates all phase logic
    to CompositeExecutionStep. These tests cover the wiring,
    argument passing, and the driver-level behavior with recording
    fakes, plus two integration tests with real file-system children
    and faked expensive venv and dependency steps. The headline
    change from the old hierarchy is pinned here: a dry run against
    an empty project root prepares every child, including pyproject
    and dependencies, because claims replace prerequisite guards.
  """
  _PYTHON = Path('/usr/bin/python3')

  @staticmethod
  def _labels(log: list[str], phase: str) -> list[str]:
    """
      Return the step labels recorded for a given phase.

      :param log: The shared log of phase calls
      :param phase: The phase to filter for
      :return: The step labels in the order they were recorded
    """
    return [
      entry.split()[1] for entry in log
      if entry.startswith(f'{phase} ')]

  def _patch_children(
    self,
    log: list[str],
    calls: list[tuple[str, tuple[object, ...]]],
    failing_label: str | None = None,
    failing_phase: str | None = None
  ) -> None:
    """
      Patch every child step class with a recording factory.

      :param log: The shared log of phase calls
      :param calls: The shared record of constructor calls
      :param failing_label: The label whose step should fail, if any
      :param failing_phase: The phase in which the failing step
        should fail
      :return: None
    """
    stack = contextlib.ExitStack()
    for name, label in _CHILD_LABELS:
      stack.enter_context(
        patch(
          f'{_MODULE}.{name}',
          _StepFactory(
            label, log, calls, failing_label, failing_phase)))
    self.addCleanup(stack.close)

  # constructor

  def test_constructor_wires_children_in_dependency_order(self) -> None:
    """
      Verify the constructor creates the child steps in dependency
      order, so prepare and commit drive them in that order.

      :return: None
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls)
    with project_context() as (_project_root, context):
      step = CreatePythonProjectStep(context, self._PYTHON)

      execute(step, context)

      self.assertEqual(_STEP_ORDER, self._labels(log, 'prepare'))
      self.assertEqual(_STEP_ORDER, self._labels(log, 'commit'))

  def test_constructor_passes_expected_arguments_to_children(
    self
  ) -> None:
    """
      Verify each child step receives the constructor arguments it
      needs, including python_executable and the project metadata.

      :return: None
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

  # execute: dry run

  def test_execute_dry_run_prepares_all_children_and_creates_nothing(
    self
  ) -> None:
    """
      Verify a dry run against an empty project root prepares every
      child, including pyproject and dependencies, commits nothing,
      aborts nothing, and creates nothing on disk.

      :return: None
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls)
    with project_context() as (project_root, context):
      step = CreatePythonProjectStep(context, self._PYTHON)

      execute(step, context, dry_run=True)

      self.assertEqual(_STEP_ORDER, self._labels(log, 'prepare'))
      self.assertEqual([], self._labels(log, 'commit'))
      self.assertEqual([], self._labels(log, 'abort'))
      self.assertEqual([], list(project_root.iterdir()))

  def test_execute_prepare_failure_propagates_without_abort(
    self
  ) -> None:
    """
      Verify a child prepare failure propagates without committing
      or aborting, and later children are not prepared.

      :return: None
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(
      log,
      calls,
      failing_label='source_tree',
      failing_phase='prepare')
    with project_context() as (_project_root, context):
      step = CreatePythonProjectStep(context, self._PYTHON)

      with self.assertRaises(DralithusProjectError):
        execute(step, context)

      self.assertEqual(
        ['packages', 'source_tree'], self._labels(log, 'prepare'))
      self.assertEqual([], self._labels(log, 'commit'))
      self.assertEqual([], self._labels(log, 'abort'))

  # execute: commit failure

  def test_execute_aborts_all_children_and_reraises_on_commit_failure(
    self
  ) -> None:
    """
      Verify a late child commit failure makes execute abort every
      child in reverse order and re-raise the error.

      :return: None
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(
      log,
      calls,
      failing_label='dependencies',
      failing_phase='commit')
    with project_context() as (_project_root, context):
      step = CreatePythonProjectStep(context, self._PYTHON)

      with self.assertRaises(DralithusProjectError):
        execute(step, context)

      self.assertEqual(
        list(reversed(_STEP_ORDER)), self._labels(log, 'abort'))

  # abort

  def test_abort_aborts_children_in_reverse_order(self) -> None:
    """
      Verify an explicit abort delegates to the children in reverse
      dependency order.

      :return: None
    """
    log: list[str] = []
    calls: list[tuple[str, tuple[object, ...]]] = []
    self._patch_children(log, calls)
    with project_context() as (_project_root, context):
      step = CreatePythonProjectStep(context, self._PYTHON)

      step.abort()

      self.assertEqual(
        list(reversed(_STEP_ORDER)), self._labels(log, 'abort'))

  # integration

  def test_execute_with_real_files_and_fake_expensive_steps_creates_shape(
    self
  ) -> None:
    """
      Verify the top-level composition produces a coherent project
      shape using real file-system children and faked venv and
      dependency steps.

      :return: None
    """
    with project_context() as (project_root, context):
      with patch(f'{_MODULE}.CreateVenvStep', _FakeVenvStep), \
          patch(f'{_MODULE}.InstallDependenciesStep',
                _FakeInstallDependenciesStep):
        step = CreatePythonProjectStep(context, self._PYTHON)

        execute(step, context)

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

  def test_failed_late_commit_aborts_real_owned_artifacts(self) -> None:
    """
      Verify that when a late child commit fails, the real
      artifacts created by earlier children are removed by the
      global abort.

      :return: None
    """
    with project_context() as (project_root, context):
      with patch(f'{_MODULE}.CreateVenvStep', _FakeVenvStep), \
          patch(f'{_MODULE}.InstallDependenciesStep',
                _FailingInstallDependenciesStep):
        step = CreatePythonProjectStep(context, self._PYTHON)

        with self.assertRaises(DralithusProjectError):
          execute(step, context)

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

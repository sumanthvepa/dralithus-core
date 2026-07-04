"""
  test_install_dependencies_step.py: Unit tests for
  dralithus.project.tx.install_dependencies_step.
"""
# -------------------------------------------------------------------
# test_install_dependencies_step.py: Unit tests for
# dralithus.project.tx.install_dependencies_step.
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
import unittest
from unittest import mock

from dralithus.test.project import project_context
from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages
from dralithus.project.tx.install_dependencies_step import (
  InstallDependenciesStep)
from dralithus.project.tx.project_state import ProjectState


# pylint: disable-next=too-many-public-methods
class TestInstallDependenciesStep(unittest.TestCase):
  """
    Unit tests for the InstallDependenciesStep class.

    These tests port the behavioral contract of the run/rollback
    InstallDependenciesStep to prepare/commit/abort. prepare()
    validates shallowly by necessity: the venv Python must be
    current-or-projected and the dependency files must parse; pip
    resolution is only exercised at commit time, with subprocess
    calls replaced by recording fakes.
  """
  _FREEZE_OUTPUT = 'requests==2.31.0\nmypy==1.10.0\n'
  _PRE_CONTENT = 'old-pinned==0.0.0\n'

  @staticmethod
  def _venv_python(context: ProjectContext) -> Path:
    """
      Return the venv interpreter path for a project.

      :param context: The project context
      :return: The path to the venv's Python interpreter
    """
    return context.venv_python

  @staticmethod
  def _make_venv(context: ProjectContext) -> None:
    """
      Create a fake venv with a runnable interpreter file.

      :param context: The project context
      :return: None
    """
    context.venv_python.parent.mkdir(parents=True)
    interpreter = context.venv_python
    interpreter.write_text('', encoding='utf-8')
    interpreter.chmod(0o755)

  @staticmethod
  def _write_packages(
    project_root: Path,
    contents: str = 'requests\n'
  ) -> None:
    """
      Write a packages.txt file in the project root.

      :param project_root: The project root directory
      :param contents: The contents of packages.txt
      :return: None
    """
    (project_root / Packages.PACKAGES_FILENAME).write_text(
      contents, encoding='utf-8')

  @staticmethod
  def _write_local_packages(project_root: Path, contents: str) -> None:
    """
      Write a local-packages.txt file in the project root.

      :param project_root: The project root directory
      :param contents: The contents of local-packages.txt
      :return: None
    """
    (project_root / Packages.LOCAL_PACKAGES_FILENAME).write_text(
      contents, encoding='utf-8')

  @staticmethod
  def _requirements(project_root: Path) -> Path:
    """
      Return the requirements.txt path in a project root.

      :param project_root: The project root directory
      :return: The requirements.txt path
    """
    return (
      project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME)

  @classmethod
  def _ok_result(cls) -> mock.Mock:
    """
      Return a stand-in successful CompletedProcess for a mock.

      :return: A mock whose stdout is the canned freeze output
    """
    return mock.Mock(stdout=cls._FREEZE_OUTPUT, returncode=0)

  @staticmethod
  def _commands(run_mock: mock.Mock) -> list[list[str]]:
    """
      Extract the command lists passed to a mocked subprocess.run.

      :param run_mock: The patched subprocess.run mock
      :return: The first positional argument of each call
    """
    return [call.args[0] for call in run_mock.call_args_list]

  @staticmethod
  def _prepared_step(
    project_root: Path,
    context: ProjectContext
  ) -> InstallDependenciesStep:
    """
      Return a step that has been prepared against a fresh state.

      :param project_root: The project root directory
      :param context: The project context
      :return: The prepared dependency installation step
    """
    step = InstallDependenciesStep(context)
    step.prepare(ProjectState(project_root))
    return step

  # prepare

  def test_prepare_fails_when_venv_missing(self) -> None:
    """
      Verify prepare fails when the venv Python is neither real
      nor claimed.

      :return: None
    """
    with project_context() as (project_root, context):
      self._write_packages(project_root)
      step = InstallDependenciesStep(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_accepts_claimed_venv_python(self) -> None:
    """
      Verify prepare accepts a venv Python that exists only as an
      executable claim declared by an earlier step.

      :return: None
    """
    with project_context() as (project_root, context):
      self._write_packages(project_root)
      step = InstallDependenciesStep(context)
      state = ProjectState(project_root)
      state.claim_executable(context.venv_python)

      step.prepare(state)

      self.assertTrue(
        state.is_file(self._requirements(project_root)))

  def test_prepare_fails_when_packages_file_missing(self) -> None:
    """
      Verify prepare fails when packages.txt is neither real nor
      claimed.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      step = InstallDependenciesStep(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_accepts_claimed_packages_file(self) -> None:
    """
      Verify prepare accepts a packages.txt that exists only as a
      claim declared by an earlier step.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      step = InstallDependenciesStep(context)
      state = ProjectState(project_root)
      state.claim_file(project_root / Packages.PACKAGES_FILENAME)

      step.prepare(state)

      self.assertTrue(
        state.is_file(self._requirements(project_root)))

  def test_prepare_rejects_symlink_requirements_target(self) -> None:
    """
      Verify prepare rejects a symlink at the requirements.txt
      path.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root)
      external = project_root / 'external.txt'
      external.write_text('external\n', encoding='utf-8')
      requirements = self._requirements(project_root)
      requirements.symlink_to(external)
      step = InstallDependenciesStep(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

      self.assertTrue(requirements.is_symlink())
      self.assertEqual(
        'external\n', external.read_text(encoding='utf-8'))

  def test_prepare_rejects_directory_requirements_target(self) -> None:
    """
      Verify prepare rejects a directory at the requirements.txt
      path.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root)
      self._requirements(project_root).mkdir()
      step = InstallDependenciesStep(context)

      with self.assertRaises(DralithusProjectError):
        step.prepare(ProjectState(project_root))

  def test_prepare_claims_requirements_file(self) -> None:
    """
      Verify prepare claims requirements.txt as a
      current-or-projected file.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root)
      step = InstallDependenciesStep(context)
      state = ProjectState(project_root)

      step.prepare(state)

      self.assertTrue(
        state.is_file(self._requirements(project_root)))

  def test_prepare_creates_nothing_on_disk(self) -> None:
    """
      Verify prepare performs no file system mutation.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root)
      step = InstallDependenciesStep(context)

      step.prepare(ProjectState(project_root))

      self.assertFalse(self._requirements(project_root).exists())

  # commit: installation

  def test_commit_installs_and_writes_requirements(self) -> None:
    """
      Verify commit upgrades pip, installs the dependencies, and
      snapshots pip freeze output to requirements.txt.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      step = self._prepared_step(project_root, context)
      python = str(self._venv_python(context))
      packages = Packages(project_root)

      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.commit()

      commands = self._commands(run_mock)
      self.assertEqual(
        commands[0],
        [python, '-m', 'pip', 'install', '--upgrade', 'pip'])
      self.assertEqual(
        commands[1],
        [python, '-m', 'pip', 'install',
         *packages.production_dependencies,
         *packages.dev_dependencies])
      self.assertEqual(commands[-1], [python, '-m', 'pip', 'freeze'])
      requirements = self._requirements(project_root)
      self.assertEqual(
        requirements.read_text(encoding='utf-8'), self._FREEZE_OUTPUT)

  def test_commit_uses_context_venv_python(self) -> None:
    """
      Verify commit runs every pip command with the context's venv
      Python interpreter.

      :return: None
    """
    with project_context(venv_name='env') as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      step = self._prepared_step(project_root, context)
      python = str(context.venv_python)

      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.commit()

      commands = self._commands(run_mock)
      self.assertEqual(
        commands[0],
        [python, '-m', 'pip', 'install', '--upgrade', 'pip'])
      self.assertEqual(commands[-1], [python, '-m', 'pip', 'freeze'])

  def test_commit_skips_editable_install_without_local_deps(
    self
  ) -> None:
    """
      Verify commit issues no editable install command when there
      are no local dependencies.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.commit()

      commands = self._commands(run_mock)
      self.assertFalse(any('-e' in command for command in commands))

  def test_commit_installs_each_local_dep_editable(self) -> None:
    """
      Verify commit installs each local dependency with its own -e
      flag.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      self._write_local_packages(project_root, './libs/a\n./libs/b\n')
      step = self._prepared_step(project_root, context)
      python = str(self._venv_python(context))

      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.commit()

      commands = self._commands(run_mock)
      self.assertIn(
        [python, '-m', 'pip', 'install',
         '-e', './libs/a', '-e', './libs/b'],
        commands)

  def test_commit_installs_local_dev_dependency_non_editable(
    self
  ) -> None:
    """
      Verify commit installs a dev-marked local dependency through
      the flat dev list, not editable.

      Documents a known, deferred limitation: a local-packages.txt
      entry marked [dev] is routed by Packages into the dev
      dependencies and installed non-editable.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      self._write_local_packages(project_root, '../test-lib [dev]\n')
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.commit()

      commands = self._commands(run_mock)
      self.assertFalse(any('-e' in command for command in commands))
      self.assertIn('../test-lib', commands[1])

  def test_commit_uses_expected_subprocess_options(self) -> None:
    """
      Verify commit runs subprocesses in the project root with
      check, captured output, and text streams.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.commit()

      self.assertTrue(
        all(call.kwargs.get('cwd') == project_root
            and call.kwargs.get('check') is True
            and call.kwargs.get('capture_output') is True
            and call.kwargs.get('text') is True
            for call in run_mock.call_args_list))

  def test_commit_regenerates_existing_requirements(self) -> None:
    """
      Verify commit regenerates a pre-existing requirements.txt
      without taking ownership of it.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      requirements = self._requirements(project_root)
      requirements.write_text(self._PRE_CONTENT, encoding='utf-8')
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.commit()
      step.abort()

      self.assertEqual(
        requirements.read_text(encoding='utf-8'), self._FREEZE_OUTPUT)

  # commit: failure handling

  def test_commit_wraps_install_failure(self) -> None:
    """
      Verify commit wraps a pip install failure.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      step = self._prepared_step(project_root, context)
      error = subprocess.CalledProcessError(1, ['pip'], stderr='boom')

      with mock.patch('subprocess.run') as run_mock:
        run_mock.side_effect = [self._ok_result(), error]
        with self.assertRaises(DralithusProjectError):
          step.commit()

      self.assertFalse(self._requirements(project_root).exists())

  def test_commit_wraps_subprocess_os_error(self) -> None:
    """
      Verify commit wraps an OSError from launching a subprocess.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock:
        run_mock.side_effect = OSError('cannot run')
        with self.assertRaises(DralithusProjectError):
          step.commit()

  def test_commit_wraps_requirements_write_failure(self) -> None:
    """
      Verify commit wraps a failure writing requirements.txt and
      leaves no temporary file behind.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock, \
          mock.patch('os.replace', side_effect=OSError('disk full')):
        run_mock.return_value = self._ok_result()
        with self.assertRaises(DralithusProjectError):
          step.commit()

      self.assertFalse(self._requirements(project_root).exists())
      self.assertEqual(
        {entry.name for entry in project_root.iterdir()},
        {'venv', Packages.PACKAGES_FILENAME})

  def test_commit_wraps_temp_file_creation_failure(self) -> None:
    """
      Verify commit wraps a failure creating the temporary
      snapshot file.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock, \
          mock.patch('tempfile.mkstemp', side_effect=OSError('no temp')):
        run_mock.return_value = self._ok_result()
        with self.assertRaises(DralithusProjectError):
          step.commit()

      self.assertFalse(self._requirements(project_root).exists())

  def test_commit_preserves_existing_requirements_on_write_failure(
    self
  ) -> None:
    """
      Verify a snapshot write failure leaves a pre-existing
      requirements.txt intact, because the write is atomic via a
      temporary file and os.replace.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      requirements = self._requirements(project_root)
      requirements.write_text(self._PRE_CONTENT, encoding='utf-8')
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock, \
          mock.patch('os.replace', side_effect=OSError('disk full')):
        run_mock.return_value = self._ok_result()
        with self.assertRaises(DralithusProjectError):
          step.commit()

      self.assertEqual(
        requirements.read_text(encoding='utf-8'), self._PRE_CONTENT)

  # abort

  def test_abort_removes_created_requirements(self) -> None:
    """
      Verify abort removes a requirements.txt created by commit.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.commit()
      step.abort()

      self.assertFalse(self._requirements(project_root).exists())

  def test_abort_preserves_preexisting_requirements(self) -> None:
    """
      Verify abort preserves a pre-existing requirements.txt.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      requirements = self._requirements(project_root)
      requirements.write_text(self._PRE_CONTENT, encoding='utf-8')
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.commit()
      step.abort()

      self.assertTrue(requirements.is_file())

  def test_abort_preserves_externally_recreated_requirements(
    self
  ) -> None:
    """
      Verify abort clears ownership so a second abort preserves a
      requirements.txt recreated externally.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      requirements = self._requirements(project_root)
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.commit()
      step.abort()

      requirements.write_text('foreign content\n', encoding='utf-8')
      step.abort()

      self.assertEqual(
        'foreign content\n',
        requirements.read_text(encoding='utf-8'))

  def test_abort_removes_requirements_after_repeated_commit(
    self
  ) -> None:
    """
      Verify repeated commits preserve ownership so a later abort
      removes requirements.txt.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      step = self._prepared_step(project_root, context)

      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.commit()
        step.commit()
      step.abort()

      self.assertFalse(self._requirements(project_root).exists())

  def test_abort_is_a_noop_when_nothing_created(self) -> None:
    """
      Verify abort changes nothing when commit created nothing.

      :return: None
    """
    with project_context() as (project_root, context):
      self._make_venv(context)
      self._write_packages(project_root, 'requests\n')
      step = self._prepared_step(project_root, context)

      step.abort()

      self.assertFalse(self._requirements(project_root).exists())

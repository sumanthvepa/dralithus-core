"""
  test_install_dependencies_step.py: Unit tests for
  install_dependencies_step.
"""
# -------------------------------------------------------------------
# test_install_dependencies_step.py: Unit tests for
# install_dependencies_step.
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
import subprocess
import unittest
from unittest import mock

from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.install_dependencies_step import (
  InstallDependenciesStep)
from dralithus.project.packages import Packages


# pylint: disable-next=too-many-public-methods
class TestInstallDependenciesStep(unittest.TestCase):
  """
    Unit tests for the InstallDependenciesStep class.
  """
  _FREEZE_OUTPUT = 'requests==2.31.0\nmypy==1.10.0\n'
  _PRE_CONTENT = 'old-pinned==0.0.0\n'

  @staticmethod
  def _venv_python(project_root: Path, venv_name: str = 'venv') -> Path:
    """
      Return the venv interpreter path for a project.

      :param project_root: The project root directory
      :param venv_name: The venv directory name
      :return: The path to the venv's Python interpreter
    """
    return project_root / venv_name / 'bin' / 'python'

  @staticmethod
  def _make_venv(project_root: Path, venv_name: str = 'venv') -> None:
    """
      Create a fake venv with a runnable interpreter file.

      :param project_root: The project root directory
      :param venv_name: The venv directory name
      :return: None
    """
    bin_dir = project_root / venv_name / 'bin'
    bin_dir.mkdir(parents=True)
    interpreter = bin_dir / 'python'
    interpreter.write_text('', encoding='utf-8')
    interpreter.chmod(0o755)

  @staticmethod
  def _write_packages(project_root: Path, contents: str = 'requests\n') -> None:
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

  # run(): prerequisites

  def test_run_fails_when_venv_missing(self) -> None:
    """
      Verify that run fails loudly when the venv interpreter is
      missing.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._write_packages(project_root)
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run'):
        with self.assertRaises(DralithusProjectError):
          step.run(context)

  def test_run_fails_when_packages_file_missing(self) -> None:
    """
      Verify that run fails loudly when packages.txt is missing.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run'):
        with self.assertRaises(DralithusProjectError):
          step.run(context)

  # run(): installation

  def test_run_installs_and_writes_requirements(self) -> None:
    """
      Verify that run upgrades pip, installs production and dev
      dependencies, then writes requirements.txt from pip freeze.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      python = str(self._venv_python(project_root))
      packages = Packages(project_root)
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.run(context)
      commands = self._commands(run_mock)
      self.assertEqual(
        commands[0], [python, '-m', 'pip', 'install', '--upgrade', 'pip'])
      self.assertEqual(
        commands[1],
        [python, '-m', 'pip', 'install',
         *packages.production_dependencies,
         *packages.dev_dependencies])
      self.assertEqual(commands[-1], [python, '-m', 'pip', 'freeze'])
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      self.assertEqual(
        requirements.read_text(encoding='utf-8'), self._FREEZE_OUTPUT)

  def test_run_uses_context_venv_python(self) -> None:
    """
      Verify that run uses the venv Python path from ProjectContext.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root, venv_name='env')
      self._make_venv(project_root, context.venv_name)
      self._write_packages(project_root, 'requests\n')
      step = InstallDependenciesStep()
      python = str(context.venv_python)
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.run(context)
      commands = self._commands(run_mock)
      self.assertEqual(
        commands[0], [python, '-m', 'pip', 'install', '--upgrade', 'pip'])
      self.assertEqual(commands[-1], [python, '-m', 'pip', 'freeze'])

  def test_run_skips_editable_install_without_local_deps(self) -> None:
    """
      Verify that the editable install is not invoked when there are
      no local dependencies.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.run(context)
      commands = self._commands(run_mock)
      self.assertFalse(any('-e' in command for command in commands))

  def test_run_installs_each_local_dep_editable(self) -> None:
    """
      Verify that every local dependency is installed editable by
      repeating -e before each path.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      self._write_local_packages(project_root, './libs/a\n./libs/b\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      python = str(self._venv_python(project_root))
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.run(context)
      commands = self._commands(run_mock)
      self.assertIn(
        [python, '-m', 'pip', 'install',
         '-e', './libs/a', '-e', './libs/b'],
        commands)

  def test_run_installs_local_dev_dependency_non_editable(self) -> None:
    """
      Document a known, deferred limitation: a local-packages.txt entry
      marked [dev] is routed by Packages into the dev dependencies and
      installed non-editable, not via pip install -e. See the deferred
      note in status.md.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      self._write_local_packages(project_root, '../test-lib [dev]\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.run(context)
      commands = self._commands(run_mock)
      self.assertFalse(any('-e' in command for command in commands))
      self.assertIn('../test-lib', commands[1])

  def test_run_uses_text_mode_for_subprocess(self) -> None:
    """
      Verify that every subprocess call uses text mode so the freeze
      output is a string and is written without error.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.run(context)
      self.assertTrue(
        all(call.kwargs.get('text') is True
            for call in run_mock.call_args_list))

  # run(): failure handling

  def test_run_wraps_install_failure(self) -> None:
    """
      Verify that a non-zero pip install exit is wrapped as a
      DralithusProjectError and no requirements.txt is created.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      error = subprocess.CalledProcessError(1, ['pip'], stderr='boom')
      with mock.patch('subprocess.run') as run_mock:
        run_mock.side_effect = [self._ok_result(), error]
        with self.assertRaises(DralithusProjectError):
          step.run(context)
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      self.assertFalse(requirements.exists())

  def test_run_wraps_subprocess_os_error(self) -> None:
    """
      Verify that an OSError launching pip is wrapped as a
      DralithusProjectError.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock:
        run_mock.side_effect = OSError('cannot run')
        with self.assertRaises(DralithusProjectError):
          step.run(context)

  def test_run_wraps_requirements_write_failure(self) -> None:
    """
      Verify that a failure writing requirements.txt is wrapped as a
      DralithusProjectError and leaves no temporary file behind.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock, \
          mock.patch('os.replace', side_effect=OSError('disk full')):
        run_mock.return_value = self._ok_result()
        with self.assertRaises(DralithusProjectError):
          step.run(context)
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      self.assertFalse(requirements.exists())
      self.assertEqual(
        {entry.name for entry in project_root.iterdir()},
        {'venv', Packages.PACKAGES_FILENAME})

  def test_run_wraps_temp_file_creation_failure(self) -> None:
    """
      Verify that a failure creating the temporary snapshot file is
      wrapped as a DralithusProjectError rather than escaping raw, so
      the orchestrator can roll back earlier steps.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock, \
          mock.patch('tempfile.mkstemp', side_effect=OSError('no temp')):
        run_mock.return_value = self._ok_result()
        with self.assertRaises(DralithusProjectError):
          step.run(context)
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      self.assertFalse(requirements.exists())

  def test_run_preserves_existing_requirements_on_write_failure(
    self
  ) -> None:
    """
      Verify that a pre-existing requirements.txt is left unchanged
      when the atomic write fails.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      requirements.write_text(self._PRE_CONTENT, encoding='utf-8')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock, \
          mock.patch('os.replace', side_effect=OSError('disk full')):
        run_mock.return_value = self._ok_result()
        with self.assertRaises(DralithusProjectError):
          step.run(context)
      self.assertEqual(
        requirements.read_text(encoding='utf-8'), self._PRE_CONTENT)

  # run(): dry-run and regeneration

  def test_dry_run_is_a_no_op(self) -> None:
    """
      Verify that a dry run invokes no subprocess and writes no
      requirements.txt, even when the venv is absent.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock:
        step.run(context, dry_run=True)
      run_mock.assert_not_called()
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      self.assertFalse(requirements.exists())

  def test_run_regenerates_existing_requirements(self) -> None:
    """
      Verify that a pre-existing requirements.txt is replaced with the
      new freeze content.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      requirements.write_text(self._PRE_CONTENT, encoding='utf-8')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.run(context)
      self.assertEqual(
        requirements.read_text(encoding='utf-8'), self._FREEZE_OUTPUT)

  # run(): wrong-type targets

  def test_run_rejects_symlink_requirements_target(self) -> None:
    """
      Verify that run rejects a symlink at the requirements.txt path,
      even a valid symlink to a regular file, and changes nothing.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      external = project_root / 'external.txt'
      external.write_text(self._PRE_CONTENT, encoding='utf-8')
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      requirements.symlink_to(external)
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        with self.assertRaises(DralithusProjectError):
          step.run(context)
      run_mock.assert_not_called()
      self.assertTrue(requirements.is_symlink())
      self.assertEqual(
        external.read_text(encoding='utf-8'), self._PRE_CONTENT)

  def test_run_rejects_directory_requirements_target(self) -> None:
    """
      Verify that run rejects a directory at the requirements.txt path.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      requirements.mkdir()
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        with self.assertRaises(DralithusProjectError):
          step.run(context)
      run_mock.assert_not_called()
      self.assertTrue(requirements.is_dir())

  # rollback()

  def test_rollback_removes_created_requirements(self) -> None:
    """
      Verify that rollback removes a requirements.txt this step
      created and leaves the venv directory untouched.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.run(context)
        step.rollback(context)
      self.assertFalse(requirements.exists())
      self.assertTrue((project_root / 'venv').is_dir())

  def test_rollback_preserves_pre_existing_requirements(self) -> None:
    """
      Verify that rollback leaves a pre-existing requirements.txt in
      place.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      requirements.write_text(self._PRE_CONTENT, encoding='utf-8')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.run(context)
        step.rollback(context)
      self.assertTrue(requirements.exists())

  def test_rollback_preserves_externally_recreated_requirements(
    self
  ) -> None:
    """
      Verify that ownership is released after rollback: once this step
      has removed the requirements.txt it created, a later rollback
      does not delete a newly recreated file it no longer owns.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.run(context)
        step.rollback(context)
        requirements.write_text(self._PRE_CONTENT, encoding='utf-8')
        step.rollback(context)
      self.assertTrue(requirements.exists())
      self.assertEqual(
        requirements.read_text(encoding='utf-8'), self._PRE_CONTENT)

  def test_rollback_removes_requirements_after_repeated_run(self) -> None:
    """
      Verify that ownership is sticky: a requirements.txt created on
      the first run is still removed by a later rollback even after a
      second regenerating run.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      self._make_venv(project_root)
      self._write_packages(project_root, 'requests\n')
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      requirements = project_root / InstallDependenciesStep.REQUIREMENTS_FILENAME
      with mock.patch('subprocess.run') as run_mock:
        run_mock.return_value = self._ok_result()
        step.run(context)
        step.run(context)
        step.rollback(context)
      self.assertFalse(requirements.exists())

  def test_rollback_is_a_no_op_when_nothing_created(self) -> None:
    """
      Verify that rollback is a safe no-op when the step created
      nothing, and under dry-run.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(project_root=project_root)
      step = InstallDependenciesStep()
      step.rollback(context, dry_run=True)
      step.rollback(context)


if __name__ == '__main__':
  unittest.main()

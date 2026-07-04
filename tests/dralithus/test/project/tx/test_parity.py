"""
  test_parity.py: Differential tests between the old and tx step
  hierarchies.
"""
# -------------------------------------------------------------------
# test_parity.py: Differential tests between the old and tx step
# hierarchies.
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
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from dralithus.test.project import project_context
# The parity harness reuses the fake expensive steps of both
# top-level suites. It is Phase 4 migration scaffolding: it dies
# with the old hierarchy in Phase 6, so reaching into the test
# modules for their private fakes is acceptable.
from dralithus.test.project.test_create_python_project_step import (
  _FailingInstallDependenciesStep as OldFailingInstallStep,
  _FakeInstallDependenciesStep as OldFakeInstallStep,
  _FakeVenvStep as OldFakeVenvStep)
from dralithus.test.project.tx.test_create_python_project_step import (
  _FailingInstallDependenciesStep as TxFailingInstallStep,
  _FakeInstallDependenciesStep as TxFakeInstallStep,
  _FakeVenvStep as TxFakeVenvStep)
from dralithus.project.context import ProjectContext
from dralithus.project.create_python_project_step import (
  CreatePythonProjectStep as OldCreatePythonProjectStep)
from dralithus.project.error import DralithusProjectError
from dralithus.project.packages import Packages
from dralithus.project.tx.create_python_project_step import (
  CreatePythonProjectStep as TxCreatePythonProjectStep)
from dralithus.project.tx.execution_step import execute


_OLD_MODULE = 'dralithus.project.create_python_project_step'
_TX_MODULE = 'dralithus.project.tx.create_python_project_step'


class TestParity(unittest.TestCase):
  """
    Differential tests between the old and tx step hierarchies.

    Runs the old run/rollback hierarchy and the new
    prepare/commit/abort hierarchy against equivalent inputs and
    asserts byte-identical on-disk output. The old implementation is
    the oracle: any behavioral drift the port introduced shows up as
    a tree difference, even where the tx suite and implementation
    encode the same mistranslation. Only successful-run output can
    be compared; dry-run and failure-path behavior intentionally
    differ under the tx design.

    This module is Phase 4 migration scaffolding and is deleted
    together with the old hierarchy in Phase 6.
  """
  _PYTHON = Path('/usr/bin/python3')

  @staticmethod
  def _tree_digest(root: Path) -> dict[str, object]:
    """
      Map each path under root to a comparable content record.

      Directories map to a marker string; files map to their bytes
      paired with their executability, so content and the relevant
      metadata are compared while inode-level details are ignored.

      :param root: The project root directory to record
      :return: A mapping of relative paths to content records
    """
    digest: dict[str, object] = {}
    for path in sorted(root.rglob('*')):
      relative = str(path.relative_to(root))
      if path.is_dir():
        digest[relative] = 'directory'
      else:
        digest[relative] = (
          path.read_bytes(), os.access(path, os.X_OK))
    return digest

  def _run_old(self, context: ProjectContext) -> None:
    """
      Run the old hierarchy with faked expensive steps.

      :param context: The project context for the old-side root
      :return: None
      :raises DralithusProjectError: When the old hierarchy fails
    """
    with patch(f'{_OLD_MODULE}.CreateVenvStep', OldFakeVenvStep), \
        patch(f'{_OLD_MODULE}.InstallDependenciesStep',
              OldFakeInstallStep):
      OldCreatePythonProjectStep(context, self._PYTHON).run()

  def _run_new(self, context: ProjectContext) -> None:
    """
      Run the tx hierarchy with faked expensive steps.

      :param context: The project context for the tx-side root
      :return: None
      :raises DralithusProjectError: When the tx hierarchy fails
    """
    with patch(f'{_TX_MODULE}.CreateVenvStep', TxFakeVenvStep), \
        patch(f'{_TX_MODULE}.InstallDependenciesStep',
              TxFakeInstallStep):
      execute(
        TxCreatePythonProjectStep(context, self._PYTHON), context)

  @staticmethod
  def _write_preexisting_artifacts(project_root: Path) -> None:
    """
      Write the shared pre-existing artifacts for convergence runs.

      :param project_root: The project root directory to populate
      :return: None
    """
    (project_root / Packages.PACKAGES_FILENAME).write_text(
      'requests\n', encoding='utf-8')
    src = project_root / 'src'
    src.mkdir()
    (src / '.gitignore').write_text('user ignore\n', encoding='utf-8')
    (project_root / 'mypy.ini').write_text(
      'user mypy config\n', encoding='utf-8')

  def test_hierarchies_produce_identical_trees_from_empty_root(
    self
  ) -> None:
    """
      Verify both hierarchies produce byte-identical project trees
      from an empty project root.

      :return: None
    """
    with project_context() as (old_root, old_context):
      with project_context() as (new_root, new_context):
        self._run_old(old_context)
        self._run_new(new_context)

        old_digest = self._tree_digest(old_root)
        self.assertIn('pyproject.toml', old_digest)
        self.assertEqual(old_digest, self._tree_digest(new_root))

  def test_hierarchies_converge_identically_on_preexisting_artifacts(
    self
  ) -> None:
    """
      Verify both hierarchies converge identically when the same
      acceptable artifacts pre-exist in the project root.

      :return: None
    """
    with project_context() as (old_root, old_context):
      with project_context() as (new_root, new_context):
        self._write_preexisting_artifacts(old_root)
        self._write_preexisting_artifacts(new_root)

        self._run_old(old_context)
        self._run_new(new_context)

        old_digest = self._tree_digest(old_root)
        self.assertEqual(
          (b'user ignore\n', False),
          old_digest[str(Path('src') / '.gitignore')])
        self.assertEqual(old_digest, self._tree_digest(new_root))

  def test_hierarchies_clean_up_identically_on_late_failure(
    self
  ) -> None:
    """
      Verify both hierarchies leave identical, empty project roots
      after a late dependency-step failure is cleaned up.

      :return: None
    """
    with project_context() as (old_root, old_context):
      with project_context() as (new_root, new_context):
        with patch(
          f'{_OLD_MODULE}.CreateVenvStep', OldFakeVenvStep
        ), patch(
          f'{_OLD_MODULE}.InstallDependenciesStep',
          OldFailingInstallStep
        ):
          with self.assertRaises(DralithusProjectError):
            OldCreatePythonProjectStep(
              old_context, self._PYTHON).run()

        with patch(
          f'{_TX_MODULE}.CreateVenvStep', TxFakeVenvStep
        ), patch(
          f'{_TX_MODULE}.InstallDependenciesStep',
          TxFailingInstallStep
        ):
          with self.assertRaises(DralithusProjectError):
            execute(
              TxCreatePythonProjectStep(new_context, self._PYTHON),
              new_context)

        self.assertEqual({}, self._tree_digest(old_root))
        self.assertEqual({}, self._tree_digest(new_root))

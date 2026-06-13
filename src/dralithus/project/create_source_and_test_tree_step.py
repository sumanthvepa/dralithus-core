"""
  create_source_and_test_tree_step.py: Define the
  CreateSourceAndTestTreeStep class.
"""
# -------------------------------------------------------------------
# create_source_and_test_tree_step.py: Define the
# CreateSourceAndTestTreeStep class.
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
from datetime import date
import keyword
from pathlib import Path
from typing import override

from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError
from dralithus.project.execution_step import ExecutionStep
from dralithus.project.mkdir_step import MkdirStep


class CreateSourceAndTestTreeStep(ExecutionStep):
  """
    Represent a project creation step that creates the source and
    test package trees for a new Milestone 42 Python project.

    Creates src/<package_name>/ (a namespace package, no __init__.py)
    and tests/<package_name>/test/ (a real package with a seeded
    __init__.py), plus an empty .gitignore in each. Existing
    directories and files are left untouched (convergent, never
    overwrite). Creation and rollback are owned entirely by this
    step: it records exactly the files its own run created, and
    rollback removes only those and the directories the internal
    MkdirStep instances created.
  """
  _created_files: list[Path]

  def _init_py_content(self) -> str:
    """
      Build the seed content for the test package __init__.py.

      The content is a module docstring followed by the copyleft
      header in the Milestone 42 house style. The copyright year is
      taken from the current date at creation time.

      :return: The text to write to the seeded __init__.py
    """
    description = (
      f'{self._package_name}/test/__init__.py: '
      f'Unit tests for {self._package_name}.')
    year = date.today().year
    return (
      '"""\n'
      f'  {description}\n'
      '"""\n'
      '# -----------------------------------------------------------'
      '--------\n'
      f'# {description}\n'
      '#\n'
      f'# Copyright (C) {year} Sumanth Vepa.\n'
      '#\n'
      '# This program is free software: you can redistribute it'
      ' and/or\n'
      '# modify it under the terms of the GNU General Public License'
      ' a\n'
      '# published by the Free Software Foundation, either version 3'
      ' of the\n'
      '# License, or (at your option) any later version.\n'
      '#\n'
      '# This program is distributed in the hope that it will be'
      ' useful,\n'
      '# but WITHOUT ANY WARRANTY; without even the implied warranty'
      ' of\n'
      '# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See'
      ' the\n'
      '# GNU General Public License for more details.\n'
      '#\n'
      '# You should have received a copy of the GNU General Public'
      ' License\n'
      '# along with this program.  If not, see\n'
      '# <https://www.gnu.org/licenses/>.\n'
      '# -----------------------------------------------------------'
      '--------\n')

  def _create_file(self, path: Path, content: str) -> None:
    """
      Create path with content unless the path already exists.

      Creation is exclusive, so a pre-existing file (including a
      dangling symlink) is never overwritten or claimed. Ownership
      is recorded the instant exclusive creation succeeds, before
      the content write, so a write failure cannot leave an
      untracked partial file behind.

      :param path: The file to create
      :param content: The content to write
      :return: None
      :raises OSError: When the file cannot be created or written
    """
    try:
      # The with statement starts only after ownership is recorded.
      # pylint: disable-next=consider-using-with
      file = path.open('x', encoding='utf-8')
    except FileExistsError:
      pass
    else:
      self._created_files.append(path)
      with file:
        file.write(content)

  def _seed_files(self, project_root: Path) -> None:
    """
      Seed the test package __init__.py and the two .gitignore files.

      :param project_root: The project root directory
      :return: None
      :raises OSError: When a seeded file cannot be created or written
    """
    src_package = project_root / 'src' / self._package_name
    test_package = (
      project_root / 'tests' / self._package_name / 'test')
    self._create_file(
      test_package / '__init__.py', self._init_py_content())
    self._create_file(src_package / '.gitignore', '')
    self._create_file(test_package / '.gitignore', '')

  def _remove_created_files(self) -> None:
    """
      Remove the seeded files created by this step.

      Files already removed externally are accepted silently.

      :return: None
      :raises DralithusProjectError: When a created seeded file
        cannot be removed
    """
    for path in self._created_files:
      try:
        path.unlink(missing_ok=True)
      except OSError as error:
        raise DralithusProjectError(
          f'Could not remove seeded file: {path}') from error
    self._created_files = []

  @staticmethod
  def _validate_package_name(package_name: str) -> None:
    """
      Validate that package_name is a valid Python package name.

      :param package_name: The package name to validate
      :return: None
      :raises DralithusProjectError: When package_name is empty, not
        a valid identifier, a Python keyword, or not lowercase
    """
    if package_name == '':
      raise DralithusProjectError('Package name must not be empty')
    if not package_name.isidentifier():
      raise DralithusProjectError(
        f'Package name is not a valid identifier: {package_name}')
    if keyword.iskeyword(package_name):
      raise DralithusProjectError(
        f'Package name must not be a Python keyword: {package_name}')
    if package_name != package_name.lower():
      raise DralithusProjectError(
        f'Package name must be lowercase: {package_name}')

  def __init__(self, package_name: str) -> None:
    """
      Initialize the source and test tree creation step.

      :param package_name: The Python package name for the project
      :return: None
      :raises DralithusProjectError: When package_name is not a valid
        Python package name
    """
    self._validate_package_name(package_name)
    self._package_name = package_name
    self._src_mkdir = MkdirStep(Path('src') / package_name)
    self._tests_mkdir = MkdirStep(
      Path('tests') / package_name / 'test')
    self._created_files = []

  @override
  def run(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Run the source and test tree creation step.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When tree or file creation fails
    """
    self._src_mkdir.run(context, dry_run)
    self._tests_mkdir.run(context, dry_run)
    if not dry_run:
      self._seed_files(context.project_root)

  @override
  def rollback(self, context: ProjectContext, dry_run: bool = False) -> None:
    """
      Roll back the source and test tree creation step.

      Removes only the files this step's run created, then removes
      the directories the internal MkdirStep instances created, in
      reverse order. Pre-existing files and directories are left in
      place.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When tree or file removal fails
    """
    if not dry_run:
      self._remove_created_files()
      self._tests_mkdir.rollback(context, dry_run)
      self._src_mkdir.rollback(context, dry_run)

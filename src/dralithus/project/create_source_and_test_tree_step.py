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
from importlib import resources
import keyword
from pathlib import Path
from string import Template
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
    and tests/<package_name>/test/ (a real package with a generated
    __init__.py), plus an empty .gitignore in every directory the step
    is responsible for (src/, src/<package_name>/, tests/,
    tests/<package_name>/, and tests/<package_name>/test/) so the
    generated project follows the tracked-directory principle. Existing
    directories and files are left untouched (convergent, never
    overwrite). Creation and rollback are owned entirely by this
    step: it records exactly the files its own run created, and
    rollback removes only those and the directories the internal
    MkdirStep instances created.
  """
  _created_files: list[Path]

  def _copyleft_header(self, context: ProjectContext) -> str:
    """
      Build the generated Python copyleft header.

      :param context: The shared project creation context
      :return: The generated copyleft header
    """
    description = (
      f'{self._package_name}/test/__init__.py: '
      f'Unit tests for {self._package_name}.')
    year = context.copyright_year
    if year is None:
      year = date.today().year
    template = Template(self._copyleft_header_template())
    return template.substitute(
      description=description,
      year=year,
      copyright_holder=context.copyright_holder)

  def _init_py_content(self, context: ProjectContext) -> str:
    """
      Build the content for the test package __init__.py.

      The content is a module docstring followed by the generated
      copyleft header.

      :param context: The shared project creation context
      :return: The text to write to the __init__.py
    """
    description = (
      f'{self._package_name}/test/__init__.py: '
      f'Unit tests for {self._package_name}.')
    return (
      '"""\n'
      f'  {description}\n'
      '"""\n'
      f'{self._copyleft_header(context)}\n')

  def _create_file(self, path: Path, content: str) -> None:
    """
      Create path with content unless a regular file already exists.

      Creation is exclusive, so a pre-existing file is never
      overwritten or claimed. A pre-existing regular file - including a
      valid symlink that resolves to one - is accepted and left
      untouched (convergent); any path that does not resolve to a
      regular file - a directory, a dangling symlink, a symlink to a
      non-regular target, or any other non-regular file - fails loudly.
      Ownership is recorded the instant exclusive creation succeeds,
      before the content write, so a write failure cannot leave an
      untracked partial file behind.

      :param path: The file to create
      :param content: The content to write
      :return: None
      :raises DralithusProjectError: When path already exists but does
        not resolve to a regular file
      :raises OSError: When the file cannot be created or written
    """
    try:
      # The with statement starts only after ownership is recorded.
      # pylint: disable-next=consider-using-with
      file = path.open('x', encoding='utf-8')
    except FileExistsError:
      self._verify_regular_file(path)
    else:
      self._created_files.append(path)
      with file:
        file.write(content)

  def _create_initial_files(self, context: ProjectContext) -> None:
    """
      Create the test package __init__.py and a .gitignore in every
      directory this step is responsible for.

      The .gitignore files are written into all five directories - the
      src and tests parents, the src package, the tests/<package_name>
      parent, and the test package - so the generated project follows
      the tracked-directory principle (every durable directory carries
      a .gitignore).

      :param context: The shared project creation context
      :return: None
      :raises DralithusProjectError: When a path already
        exists but is not a regular file, or a file cannot be
        created or written
    """
    project_root = context.project_root
    src_directory = project_root / 'src'
    src_package = src_directory / self._package_name
    tests_directory = project_root / 'tests'
    tests_parent = tests_directory / self._package_name
    test_package = tests_parent / 'test'
    files = [
      (test_package / '__init__.py', self._init_py_content(context)),
      (src_directory / '.gitignore', ''),
      (src_package / '.gitignore', ''),
      (tests_directory / '.gitignore', ''),
      (tests_parent / '.gitignore', ''),
      (test_package / '.gitignore', ''),
    ]
    for path, content in files:
      try:
        self._create_file(path, content)
      except OSError as error:
        raise DralithusProjectError(
          f'Could not write {path.name} in: {path.parent}') from error

  def _remove_created_files(self) -> None:
    """
      Remove the files created by this step.

      Files already removed externally are accepted silently.

      :return: None
      :raises DralithusProjectError: When a created file
        cannot be removed
    """
    for path in self._created_files:
      try:
        path.unlink(missing_ok=True)
      except OSError as error:
        raise DralithusProjectError(
          f'Could not remove file: {path}') from error
    self._created_files = []

  @staticmethod
  def _copyleft_header_template() -> str:
    """
      Read the packaged Python copyleft header template.

      :return: The copyleft header template text
      :raises DralithusProjectError: When the template resource cannot
        be read
    """
    try:
      template = resources.files('dralithus.project.templates').joinpath(
        'python-copyleft-header.txt').read_text(encoding='utf-8')
    except (ImportError, OSError, UnicodeError) as error:
      raise DralithusProjectError(
        'Could not read Python copyleft header template') from error
    return template

  @staticmethod
  def _verify_regular_file(path: Path) -> None:
    """
      Verify that an existing path resolves to a regular file.

      Called when exclusive creation reports the path already exists.
      A regular file is accepted, including a valid symlink that
      resolves to one (convergent: the step leaves it untouched and
      never claims or removes it). Anything that does not resolve to a
      regular file - a directory, a dangling symlink, a symlink to a
      non-regular target, or any other non-regular file - is state the
      step could not have produced and fails loudly.

      :param path: The existing path to verify
      :return: None
      :raises DralithusProjectError: When path does not resolve to a
        regular file
    """
    if not path.is_file():
      raise DralithusProjectError(
        f'Path is not a regular file: {path}')

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

      On any failure this step cleans up its own partial work before
      re-raising, because the orchestrator never rolls back a step
      whose own run raised.

      :param context: The shared project creation context
      :param dry_run: True if the step should report what it would
        do without changing the file system
      :return: None
      :raises DralithusProjectError: When tree or file creation fails
    """
    try:
      self._src_mkdir.run(context, dry_run)
      self._tests_mkdir.run(context, dry_run)
      if not dry_run:
        self._create_initial_files(context)
    except DralithusProjectError:
      self.rollback(context, dry_run)
      raise

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

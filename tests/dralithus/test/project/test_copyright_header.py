"""
  test_copyright_header.py: Unit tests for copyright_header.
"""
# -------------------------------------------------------------------
# test_copyright_header.py: Unit tests for copyright_header.
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
from importlib import resources
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast
import unittest
from unittest import mock

from dralithus.project.context import ProjectContext
from dralithus.project.copyright_header import CopyrightHeader
from dralithus.project.error import DralithusProjectError


class TestCopyrightHeader(unittest.TestCase):
  """
    Unit tests for the CopyrightHeader class.
  """
  _TEMPLATE = (
    'Copyright (C) {{ copyright_year }} {{ copyright_holder }}.\n'
    'Released under the GPL.\n')

  @staticmethod
  def _context(project_root: Path) -> ProjectContext:
    """
      Return a project context for copyright header tests.

      :param project_root: The project root directory
      :return: The project context
    """
    return ProjectContext(
      project_root=project_root,
      copyright_holder='Milestone 42',
      copyright_year=2030)

  def test_init_stores_template(self) -> None:
    """
      Verify the constructor stores the template string.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      context = self._context(Path(temp_directory))
      header = CopyrightHeader('literal header\n')

      self.assertEqual('# literal header\n', header.text('python', context))

  def test_text_renders_python_header(self) -> None:
    """
      Verify text renders a Python comment header.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      context = self._context(Path(temp_directory))
      header = CopyrightHeader(self._TEMPLATE)

      self.assertEqual(
        '# Copyright (C) 2030 Milestone 42.\n'
        '# Released under the GPL.\n',
        header.text('python', context))

  def test_text_renders_javascript_header(self) -> None:
    """
      Verify text renders a JavaScript comment header.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      context = self._context(Path(temp_directory))
      header = CopyrightHeader(self._TEMPLATE)

      self.assertEqual(
        '// Copyright (C) 2030 Milestone 42.\n'
        '// Released under the GPL.\n',
        header.text('javascript', context))

  def test_text_uses_context_values(self) -> None:
    """
      Verify text renders values from the project context.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = ProjectContext(
        project_root=project_root,
        venv_name='env',
        copyright_holder='Milestone 42',
        copyright_year=2030)
      header = CopyrightHeader(
        'root={{ project_root }}\n'
        'venv={{ venv_name }}\n'
        'holder={{ copyright_holder }}\n'
        'year={{ copyright_year }}\n')

      self.assertEqual(
        f'# root={project_root}\n'
        '# venv=env\n'
        '# holder=Milestone 42\n'
        '# year=2030\n',
        header.text('python', context))

  def test_text_preserves_trailing_newline(self) -> None:
    """
      Verify text preserves a trailing newline in the rendered header.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      context = self._context(Path(temp_directory))
      header = CopyrightHeader('single line\n')

      self.assertEqual('# single line\n', header.text('python', context))

  def test_text_rejects_unknown_language(self) -> None:
    """
      Verify text rejects unsupported target languages.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      context = self._context(Path(temp_directory))
      header = CopyrightHeader(self._TEMPLATE)

      with self.assertRaises(DralithusProjectError):
        header.text(cast(Any, 'ruby'), context)

  def test_from_template_file_reads_template(self) -> None:
    """
      Verify from_template_file reads the template file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = self._context(project_root)
      template_filename = project_root / 'copyright.txt'
      template_filename.write_text(self._TEMPLATE, encoding='utf-8')

      header = CopyrightHeader.from_template_file(template_filename)

      self.assertEqual(
        '# Copyright (C) 2030 Milestone 42.\n'
        '# Released under the GPL.\n',
        header.text('python', context))

  def test_from_template_file_wraps_read_failure(self) -> None:
    """
      Verify from_template_file wraps template-file read failures.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      missing_template = Path(temp_directory) / 'missing.txt'

      with self.assertRaises(DralithusProjectError):
        CopyrightHeader.from_template_file(missing_template)

  def test_from_template_resource_reads_template(self) -> None:
    """
      Verify from_template_resource reads the package resource.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
      context = self._context(project_root)
      template_directory = project_root / 'templates'
      template_directory.mkdir()
      template = template_directory / 'copyright.txt'
      template.write_text(self._TEMPLATE, encoding='utf-8')
      with mock.patch.object(
        resources, 'files', return_value=template_directory
      ):
        header = CopyrightHeader.from_template_resource(
          'example.templates',
          'copyright.txt',
          context)

      self.assertEqual(
        '# Copyright (C) 2030 Milestone 42.\n'
        '# Released under the GPL.\n',
        header.text('python', context))

  def test_from_template_resource_wraps_read_failure(self) -> None:
    """
      Verify from_template_resource wraps resource read failures.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      context = self._context(Path(temp_directory))

      with self.assertRaises(DralithusProjectError):
        CopyrightHeader.from_template_resource(
          'dralithus.project',
          'missing-copyright-template.txt',
          context)

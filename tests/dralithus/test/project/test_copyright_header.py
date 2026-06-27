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
import datetime
from importlib import resources
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Literal, cast
import unittest
from unittest import mock

from dralithus.project.copyright_header import CopyrightHeader
from dralithus.project.error import DralithusProjectError


class TestCopyrightHeader(unittest.TestCase):
  """
    Unit tests for the CopyrightHeader class.
  """
  _TEMPLATE = (
    'Copyright (C) {{ copyright_year }} {{ copyright_holder }}.\n'
    'Released under the GPL.\n')
  _DESCRIPTION = 'example.py: An example module.'
  _COPYRIGHT_HOLDER = 'Milestone 42'
  _COPYRIGHT_YEAR = 2020

  @classmethod
  def _copyright_header(cls, template: str) -> CopyrightHeader:
    """
      Return a test copyright header renderer.

      :param template: The template string used to render the header
      :return: The configured copyright header renderer
    """
    return CopyrightHeader(
      template,
      cls._COPYRIGHT_HOLDER,
      cls._COPYRIGHT_YEAR)

  @classmethod
  def _text(
    cls,
    header: CopyrightHeader,
    language: Literal['python', 'javascript']
  ) -> str:
    """
      Render a test copyright header.

      :param header: The copyright header renderer
      :param language: The target language
      :return: The rendered copyright header text
    """
    return header.text(language, cls._DESCRIPTION)

  def test_init_stores_template(self) -> None:
    """
      Verify the constructor stores the template string.

      :return: None
    """
    header = self._copyright_header('literal header\n')

    self.assertEqual('# literal header\n', self._text(header, 'python'))

  def test_rejects_copyright_year_before_1710(self) -> None:
    """
      Verify that copyright years before 1710 are rejected.

      :return: None
    """
    with self.assertRaisesRegex(
      DralithusProjectError,
      'Copyright year must be 1710 or later'
    ):
      CopyrightHeader(self._TEMPLATE, self._COPYRIGHT_HOLDER, 1709)

  def test_rejects_future_copyright_year(self) -> None:
    """
      Verify that future copyright years are rejected.

      :return: None
    """
    future_year = datetime.date.today().year + 1

    with self.assertRaisesRegex(
      DralithusProjectError,
      'Copyright year must not be in the future'
    ):
      CopyrightHeader(
        self._TEMPLATE, self._COPYRIGHT_HOLDER, future_year)

  def test_text_renders_python_header(self) -> None:
    """
      Verify text renders a Python comment header.

      :return: None
    """
    header = self._copyright_header(self._TEMPLATE)

    self.assertEqual(
      '# Copyright (C) 2020 Milestone 42.\n'
      '# Released under the GPL.\n',
      self._text(header, 'python'))

  def test_text_renders_description(self) -> None:
    """
      Verify text renders the description into the header.

      :return: None
    """
    header = self._copyright_header('{{ description }}\n')

    self.assertEqual(
      f'# {self._DESCRIPTION}\n',
      self._text(header, 'python'))

  def test_text_emits_bare_prefix_for_blank_lines(self) -> None:
    """
      Verify text emits a bare comment prefix for blank lines, with
      no trailing space.

      :return: None
    """
    header = self._copyright_header('first\n\nsecond\n')

    self.assertEqual(
      '# first\n'
      '#\n'
      '# second\n',
      self._text(header, 'python'))

  def test_text_renders_javascript_header(self) -> None:
    """
      Verify text renders a JavaScript comment header.

      :return: None
    """
    header = self._copyright_header(self._TEMPLATE)

    self.assertEqual(
      '// Copyright (C) 2020 Milestone 42.\n'
      '// Released under the GPL.\n',
      self._text(header, 'javascript'))

  def test_text_uses_supplied_copyright_values(self) -> None:
    """
      Verify text renders the supplied copyright values.

      :return: None
    """
    header = self._copyright_header(
      'holder={{ copyright_holder }}\n'
      'year={{ copyright_year }}\n')

    self.assertEqual(
      '# holder=Milestone 42\n'
      '# year=2020\n',
      self._text(header, 'python'))

  def test_text_preserves_trailing_newline(self) -> None:
    """
      Verify text preserves a trailing newline in the rendered header.

      :return: None
    """
    header = self._copyright_header('single line\n')

    self.assertEqual('# single line\n', self._text(header, 'python'))

  def test_text_rejects_unknown_language(self) -> None:
    """
      Verify text rejects unsupported target languages.

      :return: None
    """
    header = self._copyright_header(self._TEMPLATE)

    with self.assertRaises(DralithusProjectError):
      self._text(header, cast(Any, 'ruby'))

  def test_from_template_file_reads_template(self) -> None:
    """
      Verify from_template_file reads the template file.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      template_filename = Path(temp_directory) / 'copyright.txt'
      template_filename.write_text(self._TEMPLATE, encoding='utf-8')

      header = CopyrightHeader.from_template_file(
        template_filename,
        self._COPYRIGHT_HOLDER,
        self._COPYRIGHT_YEAR)

      self.assertEqual(
        '# Copyright (C) 2020 Milestone 42.\n'
        '# Released under the GPL.\n',
        self._text(header, 'python'))

  def test_from_template_file_wraps_read_failure(self) -> None:
    """
      Verify from_template_file wraps template-file read failures.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      missing_template = Path(temp_directory) / 'missing.txt'

      with self.assertRaises(DralithusProjectError):
        CopyrightHeader.from_template_file(
          missing_template,
          self._COPYRIGHT_HOLDER,
          self._COPYRIGHT_YEAR)

  def test_from_template_resource_reads_template(self) -> None:
    """
      Verify from_template_resource reads the package resource.

      :return: None
    """
    with TemporaryDirectory() as temp_directory:
      project_root = Path(temp_directory)
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
          self._COPYRIGHT_HOLDER,
          self._COPYRIGHT_YEAR)

      self.assertEqual(
        '# Copyright (C) 2020 Milestone 42.\n'
        '# Released under the GPL.\n',
        self._text(header, 'python'))

  def test_from_template_resource_wraps_read_failure(self) -> None:
    """
      Verify from_template_resource wraps resource read failures.

      :return: None
    """
    with self.assertRaises(DralithusProjectError):
      CopyrightHeader.from_template_resource(
        'dralithus.project',
        'missing-copyright-template.txt',
        self._COPYRIGHT_HOLDER,
        self._COPYRIGHT_YEAR)

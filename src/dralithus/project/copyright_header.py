"""
  copyright_header.py: Define the CopyrightHeader class.
"""
# -------------------------------------------------------------------
# copyright_header.py: Define the CopyrightHeader class.
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
from typing import Literal, Self

from jinja2 import Environment, TemplateError

from dralithus.project.error import DralithusProjectError


class CopyrightHeader:
  """
    Render a copyright header from a template.

    The template text and copyright values are stored at construction
    time. The text method renders that template for one target source
    language and file description.
  """
  def _template_context(self, description: str) -> dict[str, object]:
    """
      Build the Jinja2 template context for a file description.

      :param description: The file description for the header
      :return: The template context dictionary
    """
    return {
      'copyright_holder': self._copyright_holder,
      'copyright_year': self._copyright_year,
      'description': description,
    }

  @staticmethod
  def _comment_prefix(language: str) -> str:
    """
      Return the line-comment prefix for a source language.

      :param language: The target language
      :return: The line-comment prefix
      :raises DralithusProjectError: When language is unsupported
    """
    if language == 'python':
      prefix = '#'
    elif language == 'javascript':
      prefix = '//'
    else:
      raise DralithusProjectError(
        f'Unsupported copyright header language: {language}')
    return prefix

  @staticmethod
  def _comment_text(text: str, prefix: str) -> str:
    """
      Convert rendered text to line-comment text.

      Lines with content are prefixed with the comment prefix and a
      space; blank lines get the bare prefix with no trailing space.

      :param text: The rendered template text
      :param prefix: The comment prefix to put before each line
      :return: The line-comment header text
    """
    commented: list[str] = []
    for line in text.splitlines(keepends=True):
      if line.rstrip('\n'):
        commented.append(f'{prefix} {line}')
      else:
        commented.append(f'{prefix}{line}')
    return ''.join(commented)

  def __init__(
    self,
    template: str,
    copyright_holder: str,
    copyright_year: int
  ) -> None:
    """
      Initialize the copyright header renderer.

      :param template: The template string used to render the header
      :param copyright_holder: The copyright holder name
      :param copyright_year: The copyright year
      :return: None
    """
    self._template = template
    self._copyright_holder = copyright_holder
    self._copyright_year = copyright_year

  def text(
    self,
    language: Literal['python', 'javascript'],
    description: str
  ) -> str:
    """
      Render the copyright header for a language.

      Python headers use leading # comment markers. JavaScript headers
      use JavaScript comment syntax. The description is the file
      description that appears in the header, available to the template
      as the description value.

      :param language: The target language, either python or
        javascript
      :param description: The file description for the header
      :return: The rendered copyright header text
      :raises DralithusProjectError: When language is unsupported or
        the template cannot be rendered
    """
    prefix = self._comment_prefix(language)
    try:
      rendered = Environment(keep_trailing_newline=True).from_string(
        self._template).render(
        self._template_context(description))
    except TemplateError as error:
      raise DralithusProjectError(
        'Could not render copyright header template') from error
    return self._comment_text(rendered, prefix)

  @classmethod
  def from_template_file(
    cls,
    template_filename: Path,
    copyright_holder: str,
    copyright_year: int
  ) -> Self:
    """
      Create a copyright header renderer from a template file.

      :param template_filename: The template file to read
      :param copyright_holder: The copyright holder name
      :param copyright_year: The copyright year
      :return: The configured copyright header renderer
    """
    try:
      template = template_filename.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
      raise DralithusProjectError(
        f'Could not read copyright header template: {template_filename}'
      ) from error
    return cls(template, copyright_holder, copyright_year)

  @classmethod
  def from_template_resource(
    cls,
    package: str,
    resource: str,
    copyright_holder: str,
    copyright_year: int
  ) -> Self:
    """
      Create a copyright header renderer from a package resource.

      :param package: The package containing the resource
      :param resource: The package-relative resource name
      :param copyright_holder: The copyright holder name
      :param copyright_year: The copyright year
      :return: The configured copyright header renderer
    """
    try:
      template = resources.files(package).joinpath(resource).read_text(
        encoding='utf-8')
    except (ImportError, OSError, TypeError, UnicodeError) as error:
      raise DralithusProjectError(
        f'Could not read copyright header resource: {package}/{resource}'
      ) from error
    return cls(template, copyright_holder, copyright_year)

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

from dralithus.project.context import ProjectContext
from dralithus.project.error import DralithusProjectError


class CopyrightHeader:
  """
    Render a copyright header from a template.

    The template text is stored at construction time. The text method
    renders that template for a target source language using values
    from the project context.
  """
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
  def _template_context(context: ProjectContext) -> dict[str, object]:
    """
      Convert a project context into a Jinja2 template context.

      :param context: The shared project creation context
      :return: The template context dictionary
    """
    return context.as_dict()

  @staticmethod
  def _comment_text(text: str, prefix: str) -> str:
    """
      Convert rendered text to line-comment text.

      :param text: The rendered template text
      :param prefix: The comment prefix to put before each line
      :return: The line-comment header text
    """
    lines = text.splitlines(keepends=True)
    return ''.join(f'{prefix} {line}' for line in lines)

  def __init__(self, template: str) -> None:
    """
      Initialize the copyright header renderer.

      :param template: The template string used to render the header
      :return: None
    """
    self._template = template

  def text(
    self,
    language: Literal['python', 'javascript'],
    context: ProjectContext
  ) -> str:
    """
      Render the copyright header for a language.

      Python headers use leading # comment markers. JavaScript headers
      use JavaScript comment syntax.

      :param language: The target language, either python or
        javascript
      :param context: The shared project creation context
      :return: The rendered copyright header text
    """
    prefix = self._comment_prefix(language)
    try:
      rendered = Environment(keep_trailing_newline=True).from_string(
        self._template).render(self._template_context(context))
    except TemplateError as error:
      raise DralithusProjectError(
        'Could not render copyright header template') from error
    return self._comment_text(rendered, prefix)

  @classmethod
  def from_template_file(cls, template_filename: Path) -> Self:
    """
      Create a copyright header renderer from a template file.

      :param template_filename: The template file to read
      :return: The configured copyright header renderer
    """
    try:
      template = template_filename.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
      raise DralithusProjectError(
        f'Could not read copyright header template: {template_filename}'
      ) from error
    return cls(template)

  @classmethod
  def from_template_resource(
    cls,
    package: str,
    resource: str,
    context: ProjectContext
  ) -> Self:
    """
      Create a copyright header renderer from a package resource.

      :param package: The package containing the resource
      :param resource: The package-relative resource name
      :param context: The shared project creation context
      :return: The configured copyright header renderer
    """
    del context
    try:
      template = resources.files(package).joinpath(resource).read_text(
        encoding='utf-8')
    except (ImportError, OSError, TypeError, UnicodeError) as error:
      raise DralithusProjectError(
        f'Could not read copyright header resource: {package}/{resource}'
      ) from error
    return cls(template)

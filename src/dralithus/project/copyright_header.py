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
from pathlib import Path
from typing import Literal, Self

from dralithus.project.context import ProjectContext


class CopyrightHeader:
  """
    Render a copyright header from a template.

    The template text is stored at construction time. The text method
    renders that template for a target source language using values
    from the project context.
  """
  def __init__(self, template: str) -> None:
    """
      Initialize the copyright header renderer.

      :param template: The template string used to render the header
      :return: None
    """
    raise NotImplementedError()

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
    raise NotImplementedError()

  @classmethod
  def from_template_file(cls, template_filename: Path) -> Self:
    """
      Create a copyright header renderer from a template file.

      :param template_filename: The template file to read
      :return: The configured copyright header renderer
    """
    raise NotImplementedError()

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
    raise NotImplementedError()

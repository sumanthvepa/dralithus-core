# -*- coding: utf-8 -*-
"""
  drl.py: Command line tool to deploy applications to various environments
"""
# -------------------------------------------------------------------
# drl.py: Command line tool to deploy applications to various environments
#
# Copyright (C) 2023-25 Sumanth Vepa.
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
import sys

from dralithus.command import make
from dralithus.errors import DralithusError


def main(args: list[str] | None = None) -> int:
  """
    Parse the command line and execute the command

    The function takes an optional main, so that python's
    packaging software can create a wrapper that calls main()
    with no arguments. But when invoked direcly as a script,
    the code in the if __name__ == '__main__' section will
    pass the argument list.

    :param args: The command line arguments (usually sys.argv, except
      in unit tests). If not provided, the args are taken from sys.argv.

    :return: int: The exit code of the command
  """
  try:
    if args is None:
      args = sys.argv
    cmd = make(args)
    return cmd.execute()
  except DralithusError as ex:
    print(ex, file=sys.stderr)
    return ex.exit_code
  # Note that we are not catching any other exceptions here. This is
  # intentional. Any other exceptions are bugs in the code and should
  # not be caught. They should be fixed instead.


if __name__ == '__main__':
  sys.exit(main(sys.argv))

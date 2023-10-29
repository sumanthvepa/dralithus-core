# -*- coding: utf-8 -*-
"""
main.py: Entry point function for the dralithus command line tool.
"""
# Copyright 2023. Sumanth Vepa. svepa@milestone42.com
#
# This file is part of dralithus-core.
#
# dralithus-core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dralithus-core is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dralithus-core. If not, see <https://www.gnu.org/licenses/>.

import sys

import yaml

from dralithus import configuration


def main():
  """
    Parse and print the contents of a file named network.yaml in the
    current directory.
  """
  try:
    config: dict = configuration.read('network.yaml')
    print(config)
  except yaml.YAMLError as ex:
    print(ex, file=sys.stderr)
    sys.exit(1)
  sys.exit(0)

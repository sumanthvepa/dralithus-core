"""
  multi_option.py: Define class MultiOption
"""
from __future__ import annotations
from typing import override

from dralithus.command_line.option import Option
from dralithus.command_line.help_option import HelpOption
from dralithus.command_line.verbosity_option import VerbosityOption


class MultiOption(Option):
  """
    A class to represent a multi-option argument.

    This class is used to handle multi-option arguments that are
    specified on the command line. A multi-option argument is an
    argument that starts with a single hyphen and is followed by one
    or more option letters. For example, -vh is a multi-option
    argument that specifies the -v and -h options. Multi options cannot
    have values. So, -hv=1 is not a valid multi-option argument.
  """
  def __init__(self, options: list[Option]) -> None:
    self._options = options

  @classmethod
  def supported_short_flags(cls) -> list[str]:
    """
      The short flag for this option.

      :return: A list containing the short flag '-h'
    """
    return HelpOption.supported_short_flags() \
      + VerbosityOption.supported_short_flags()

  @classmethod
  def supported_long_flags(cls) -> list[str]:
    """
      The long flags for this option.

      :return: MultiOption does not support long flags
    """
    return []

  @override
  def __eq__(self, other):
    """
      Check if two options are equal.

      :param other: The other option to compare to
      :return: True if the options are equal, False otherwise
    """
    if not isinstance(other, MultiOption):
      return False
    return self._options == other._options

  @override
  @property
  def flag(self) -> str:
    """
      The flag string which was used to create this option.

      :return: The flag string used to create this option
    """
    return ''.join([option.flag for option in self._options])

  @override
  @property
  def value(self) -> None:
    """
    Attempting to get the value of a multi-option argument will raise an
    exception. Multi-option arguments do not have a value.
    :return: None
    """
    raise NotImplementedError('value is not defined for multi-option arguments')

  @property
  def options(self) -> list[Option]:
    """
      The list of options in the multi-option argument.

      :return: The list of options
    """
    return self._options

  @override
  def add_to(self, dictionary: dict[str, None | bool | int | str | set[str]]) -> None:
    """
      Add the option to a dictionary.

      This method iterates over the options in the multi-option
      argument and adds them to the dictionary. Each option is added
      using its own add_to method. The dictionary is updated with
      the values of the options.

      :param dictionary: The dictionary to add the option to
    """
    for option in self._options:
      option.add_to(dictionary)

  @classmethod
  def is_option(cls, arg: str, next_arg: str | None) -> bool:  # pylint: disable=unused-argument
    """
      Check if the argument is a multi-option argument.

      :param arg: The argument string
      :param next_arg: The next argument string (unused)
      :return: True if the argument is a multi-option argument, False otherwise
    """
    short_flags = HelpOption.supported_short_flags() + VerbosityOption.supported_short_flags()
    return arg.startswith('-') and len(arg) > 2 and all(c in short_flags for c in arg[1:])

  @classmethod
  def is_valid_value_type(cls, str_value: str) -> bool:
    """
      Check if the value is valid for this option.

      :param str_value: The value to check
      :return: True if the value is valid, False otherwise
    """
    raise NotImplementedError('is_valid_value_type is not defined for multi-option arguments')

  @classmethod
  def make(cls, current_arg: str, next_arg: str | None) -> tuple[MultiOption, bool]:
    """
      Create a MultiOption object from command line arguments.

      :param current_arg: The current argument string
      :param next_arg: The next argument string
      :return: A tuple containing the MultiOption object and a boolean
               indicating if the option was created successfully
    """
    assert cls.is_option(current_arg, next_arg)
    options: list[Option] = []
    flags = list(current_arg[1:])
    for flag in flags:
      arg = '-' + flag
      if HelpOption.is_option(arg, next_arg):
        options.append(HelpOption.make(arg, next_arg)[0])
      elif VerbosityOption.is_option(arg, next_arg):
        options.append(VerbosityOption.make(arg, next_arg)[0])
    return MultiOption(options), False

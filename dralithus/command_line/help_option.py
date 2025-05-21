"""
  help_option.py: Define class HelpOption
"""
from __future__ import annotations
from typing import override

from dralithus.command_line.option import Option


class HelpOption(Option):
  """
    A class to represent a help option.
  """
  def __init__(self, flag) -> None:
    """
      Initialize the help option.
    """
    self._flag = flag

  @classmethod
  def supported_short_flags(cls) -> list[str]:
    """
      The short flag for this option.

      :return: A list containing the short flag '-h'
    """
    return ['h']

  @classmethod
  def supported_long_flags(cls) -> list[str]:
    """
      The long flags for this option.

      :return: A list containing the long flag '--help'
    """
    return ['help']

  @override
  def __eq__(self, other: object) -> bool:
    """
      Check if two options are equal.

      :param other: The other option to compare to
      :return: True if the options are equal, False otherwise
    """
    if not isinstance(other, HelpOption):
      return False
    return self._flag == other._flag

  @override
  @property
  def flag(self) -> str:
    """
      The flag string which was used to create this option.

      :return: The flag string used to create this option
    """
    return self._flag

  @override
  @property
  def value(self) -> bool:
    """
      Get the value of the help option. Is always True!

      :return: The value of the help option as a boolean
    """
    return True

  @override
  def add_to(self, dictionary: dict[str, None | bool | int | str | set[str]]) -> None:
    """
      Add the help option to a dictionary.

      :param dictionary: The dictionary to add the help option to
    """
    dictionary['requires_help'] = True

  @classmethod
  def is_option(cls, arg: str, next_arg: str | None) -> bool:  # pylint: disable=unused-argument
    """
      Check if the argument is a help option.

      :param arg: The argument string
      :param next_arg: The next argument string (unused)
      :return: True if the argument is a help option
    """
    for flag in cls.supported_short_flags():
      if arg == '-' + flag:
        return True
    for flag in cls.supported_long_flags():
      if arg == '--' + flag:
        return True
    return False

  @classmethod
  def is_valid_value_type(cls, str_value: str) -> bool:
    """
      Check if the value is a valid verbosity level.
      :param str_value:
      :return: False. No value is valid for help option.
    """
    return False

  @classmethod
  def make(cls, current_arg: str, next_arg: str | None) -> tuple[HelpOption, bool]:
    """
      Create a HelpOption object from command line arguments.

      :param current_arg: The current argument string
      :param next_arg: The next argument string
      :return: A tuple containing the HelpOption object and a boolean indicating
        whether to skip the next argument
    """
    assert cls.is_option(current_arg, next_arg)
    flag, value = cls._split_flag_value(current_arg)
    if value is not None:
      raise ValueError(f"Help option does not accept a value: {current_arg}")
    return HelpOption(flag), False

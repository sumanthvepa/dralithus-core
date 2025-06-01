"""
  verbosity_option.py: Define class VerbosityOption
"""
from __future__ import annotations
from typing import override

from dralithus.command_line.option import Option


def int_cast(value: str) -> int | None:
  """
    Cast a string to an integer or return None if it fails.

    :param value: The string to cast
    :return: The integer value
  """
  try:
    return int(value)
  except (ValueError, TypeError):
    return None


class VerbosityOption(Option):
  """
    A class to represent a verbosity option.
  """
  def __init__(self, flag: str, verbosity: int) -> None:
    """
      Initialize the verbosity option with a verbosity level.

      :param verbosity: The verbosity level
    """
    self._flag = flag
    self._verbosity = verbosity

  @classmethod
  def supported_short_flags(cls) -> list[str]:
    """
      The short flag for this option.

      :return: A list containing the short flag '-v'
    """
    return ['v']

  @classmethod
  def supported_long_flags(cls) -> list[str]:
    """
      The long flags for this option.

      :return: A list containing the long flags '--verbose' and '--verbosity'
    """
    return ['verbose', 'verbosity']

  @override
  def __eq__(self, other: object) -> bool:
    """
      Check if two options are equal.

      :param other: The other option to compare to
      :return: True if the options are equal, False otherwise
    """
    if not isinstance(other, VerbosityOption):
      return False
    return self._flag == other._flag and self._verbosity == other._verbosity

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
  def value(self) -> int:
    """
      Get the value of the verbosity option.

      :return: The value of the verbosity option
    """
    return self._verbosity

  @override
  def add_to(self, dictionary: dict[str, None | bool | int | str | set[str]]) -> None:
    """
      Add the verbosity option to a dictionary.

      :param dictionary: The dictionary to add the verbosity option to
    """
    verbosity = dictionary.get('verbosity', 0)
    verbosity = 0 if verbosity is None else verbosity
    assert isinstance(verbosity, int)
    dictionary['verbosity'] \
      = self.value if verbosity is None else verbosity + self.value

  @classmethod
  def is_option(cls, arg: str, next_arg: str | None) -> bool:
    """
      Check if the argument is a verbosity option.

      :param arg: The argument string
      :param next_arg: The next argument string
      :return: True if the argument is a verbosity option
    """
    flag, value = cls._split_flag_value(arg)
    if flag not in (cls.supported_short_flags() + cls.supported_long_flags()):
      return False
    if value is not None:
      if not cls.is_valid_value_type(value):
        return False
      if int(value) < 0:
        return False
    return True

  @classmethod
  def is_valid_value_type(cls, str_value: str) -> bool:
    """
      Check if the value is a valid verbosity level.
      :param str_value:
      :return:
    """
    value = int_cast(str_value)
    return value is not None

  @classmethod
  def make(cls, current_arg: str, next_arg: str | None) -> tuple[VerbosityOption, bool]:
    """
      Create a VerbosityOption object from command line arguments.

      :param current_arg: The current argument string
      :param next_arg: The next argument string
      :return: A tuple containing the VerbosityOption object and a boolean indicating
        whether to skip the next argument
      :raises ValueError: If the verbosity level is not a valid integer
      :raises AssertionError: If the current argument is not a valid option
    """
    assert cls.is_option(current_arg, next_arg)
    flag, str_value, skip_next_arg = cls._extract_value(current_arg, next_arg)
    value: int = int(str_value) if str_value is not None else 1
    if value < 1:
      raise ValueError(f'Verbosity must a positive number, not {value}')
    return VerbosityOption(flag, value), skip_next_arg

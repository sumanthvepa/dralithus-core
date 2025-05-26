"""
  option_terminator.py: Define the OptionTerminator class
"""
from __future__ import annotations
from typing import override

from dralithus.command_line.option import Option


class OptionTerminator(Option):
  """
    A class to represent an option terminator: --
  """
  @classmethod
  def supported_short_flags(cls) -> list[str]:
    """
      The short flag for this option.

      :return: A list containing the short flag '-'
    """
    return ['-']

  @classmethod
  def supported_long_flags(cls) -> list[str]:
    """
      The long flags for this option.

      :return: The option terminator does not have long flags.
    """
    return []

  @override
  def __eq__(self, other: object) -> bool:
    """
      Check if two options are equal.

      :param other: The other option to compare to
      :return: True if the options are equal, False otherwise
    """
    if not isinstance(other, OptionTerminator):
      return False
    return True

  @override
  @property
  def flag(self) -> str:
    """
      The flag string which was used to create this option.

      :return: The flag string used to create this option
    """
    return '-'

  @override
  @property
  def value(self) -> None:
    """
      Value of the option terminator.

      :return: None. As the option terminator does not have a value.
    """
    return None

  @override
  def add_to(self, dictionary: dict[str, None | bool | int | str | set[str]]) -> None:
    """
      Add the option terminator to a dictionary.

      :param dictionary: The dictionary to add the option terminator to
    """
    raise NotImplementedError("PROGRAM ERROR: OptionTerminator.add_to() should never be called")

  @classmethod
  def is_option(cls, arg: str, next_arg: str | None) -> bool:
    """
      Check if the argument is an option terminator.

      :param arg: The argument string
      :param next_arg: The next argument string (unused)
      :return: True if the argument is an option terminator
    """
    return arg == '--'

  @classmethod
  def is_valid_value_type(cls, str_value: str) -> bool:
    """
      Check if the value is a valid verbosity level.
      :param str_value:
      :return: False. No value is valid for option terminator.
    """
    return False

  # Note: You cannot use @override here because, @override only works with
  # normal methods. Not with class methods.
  @classmethod
  def make(cls, current_arg: str, next_arg: str | None) \
      -> tuple[OptionTerminator, bool]:
    """
      Create an OptionTerminator object from command line arguments.

      The reason for this signature is that the signature of the make
      method must match the signature of the make methods in other
      subclasses of Option.

      :param current_arg: The current arg. Used to check if it is, in
        fact, an option terminator.
      :param next_arg: The next argument string
      :return: A tuple containing the OptionTerminator object and a
        boolean indicating whether to skip the next argument (always False).
    """
    assert cls.is_option(current_arg, next_arg)
    return OptionTerminator(), False

"""
  create_option.py: Define class CreateOption
"""
# pylint: disable=cyclic-import,duplicate-code
from __future__ import annotations
from typing import override

from dralithus.command_line.option import Option


class CreateOption(Option):
  """
    A class to represent a create-project option.
  """
  def __init__(self, flag: str) -> None:
    """
      Initialize the create option.

      :param flag: The flag used to create this option
      :return: None
    """
    self._flag = flag

  @classmethod
  def supported_short_flags(cls) -> list[str]:
    """
      Return the supported short flags.

      :return: The supported short flags
    """
    return []

  @classmethod
  def supported_long_flags(cls) -> list[str]:
    """
      Return the supported long flags.

      :return: The supported long flags
    """
    return ['create']

  @override
  def __eq__(self, other: object) -> bool:
    """
      Check if two create options are equal.

      :param other: The other option to compare
      :return: True if the options are equal
    """
    if not isinstance(other, CreateOption):
      return False
    return self._flag == other._flag

  @override
  @property
  def flag(self) -> str:
    """
      Return the flag used to create this option.

      :return: The flag used to create this option
    """
    return self._flag

  @override
  @property
  def value(self) -> bool:
    """
      Return the create option value.

      :return: Always True
    """
    return True

  @override
  def add_to(
    self,
    dictionary: dict[str, None | bool | int | str | set[str]]
  ) -> None:
    """
      Add this option to the parsed options dictionary.

      :param dictionary: The options dictionary to update
      :return: None
    """
    dictionary['create_project'] = True

  @classmethod
  def is_option(cls, arg: str, next_arg: str | None) -> bool:
    """
      Return whether arg is a create option.

      :param arg: The current argument
      :param next_arg: The next argument, unused
      :return: True if arg is a create option
    """
    del next_arg
    return arg == '--create'

  @classmethod
  def is_valid_value_type(cls, str_value: str) -> bool:
    """
      Return whether str_value is a valid value for this option.

      :param str_value: The candidate option value
      :return: Always False for this flag option
    """
    del cls
    del str_value
    return False

  @classmethod
  def make(
    cls,
    current_arg: str,
    next_arg: str | None
  ) -> tuple[CreateOption, bool]:
    """
      Create a CreateOption from command-line arguments.

      :param current_arg: The current argument
      :param next_arg: The next argument
      :return: The create option and whether to skip the next arg
      :raises ValueError: When the option is given a value
    """
    assert cls.is_option(current_arg, next_arg)
    flag, value = cls._split_flag_value(current_arg)
    if value is not None:
      raise ValueError(
        f'Create option does not accept a value: {current_arg}')
    return CreateOption(flag), False

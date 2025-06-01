"""
  option.py: Define class Option
"""
from __future__ import annotations
from abc import ABC, abstractmethod
import re


class Option(ABC):
  """
    A class to represent a command line option.

    This is an abstract base class that defines the interface for
    all option objects.
  """
  flag_with_value = re.compile(r'^-[a-zA-Z][0-9]*$')
  flag_with_equal_value = re.compile(r'^-[a-zA-Z]=.+$')
  multi_option = re.compile(r'^-[a-zA-Z]+$')
  double_hyphen_option = re.compile(r'^--[a-zA-Z][a-zA-Z_-]+$')
  double_hyphen_option_with_value = re.compile(r'^--[a-zA-Z][a-zA-Z_-]+=.*$')

  @staticmethod
  def _split_flag_value(arg: str) -> tuple[str, str | None]:
    """
      Split the argument into flag and value parts.

      This is intended to be used by derived classes to parse command line
      arguments.

      :param arg: The argument string
      :return: A tuple containing the flag and value parts
    """
    # split the argument into flag and value parts
    flag_value: list[str] = arg.split('=', 1)
    if len(flag_value) > 1: # there is a value specified with an equal
      # Remove the leading '-' from the flag before returning it along
      # with the value.
      return flag_value[0].lstrip('-'), flag_value[1]
    # if the flag is a short flag with a value, split it into
    # flag and value parts. For example, -v1 becomes -v and 1.
    if not flag_value[0].startswith('--') and len(flag_value[0]) > 2:
      # Remove the leading '-' from the flag before returning it along
      # with the value.
      return flag_value[0][:2].lstrip('-'), flag_value[0][2:]
    # Otherwise, return the flag, after stripping leading hyphens,
    # and None as the value.
    return flag_value[0].lstrip('-'), None

  @staticmethod
  def _extract_flag(arg: str) -> str:
    """
      Extract the flag from the argument.

      :param arg: The argument string
      :return: The flag string
    """
    return Option._split_flag_value(arg)[0]

  @classmethod
  def _extract_value(cls, current_arg: str, next_arg: str | None) -> tuple[str, str | None, bool]:
    """
      Extract the value from the current argument or the next argument.

      :param current_arg: The current argument string
      :param next_arg: The next argument string
      :return: A tuple containing the flag string that was used to
      create the option, the value of the option, if present (on None if
        not) and a boolean indicating whether to skip the next argument
    """
    flag, str_value = Option._split_flag_value(current_arg)
    if str_value is not None:
      return flag, str_value, False
    if next_arg is not None and cls.is_valid_value_type(next_arg):
      return flag, next_arg, True
    return flag, None, False

  @staticmethod
  def _maybe_is_parameter(arg: str) -> bool:
    """
      Check if the argument is a parameter.

      A parameter is an argument that does not start with a hyphen.
      This is used to determine if the argument might be a parameter

      :param arg: The argument string
      :return: True if the argument is a parameter, False otherwise
    """
    return len(arg) > 0 and not arg.startswith('-')

  @classmethod
  @abstractmethod
  def supported_short_flags(cls) -> list[str]:
    """
      The short flag for this option.

      Derived classes must implement this method to return the
      specific short flags that correspond to the class they
      represent. For example, a verbosity option is represented by
      the flag 'v'.

      Note that this is NOT the actual flag that was used to create the
      option. The actual flag is stored in the flag property.

      :return: A list of short flag strings
    """
    return ['h', 'v', 'e']


  @classmethod
  @abstractmethod
  def supported_long_flags(cls) -> list[str]:
    """
      The long flags for this option.

      Derived classes must implement this method to return the
      specific long flags that correspond to the class they
      represent. For example, a verbosity option is represented by
      the flags 'verbose' and 'verbosity'.

      Note that this is NOT the actual flag that was used to create the
      option. The actual flag is stored in the flag property.

      :return: A list of long flag strings
    """
    return ['help', 'verbosity', 'environment']

  # @abstractmethod
  # def __eq__(self, other: object) -> bool:
  #   """
  #     Check if two options are equal.
  #
  #     :param other: The other option to compare to
  #     :return: True if the options are equal, False otherwise
  #   """
  #   raise NotImplementedError('Option.__eq__() is an abstract method')

  @property
  @abstractmethod
  def flag(self) -> str:
    """
    The actual flag string that was used to create this option.

    :return:
    """
    raise NotImplementedError('Option.flag is an abstract property')

  # pylint: disable=line-too-long
  # Note that the order of the decorators is important. The @abstractmethod
  # must be the innermost decorator.
  # See: https://stackoverflow.com/questions/72736760/making-abstract-property-in-python-3-results-in-attributeerror
  @property
  @abstractmethod
  def value(self) -> None | bool | int | str | set[str]:
    """
      Get the value of the option.

      :return: The value of the option
    """
    raise NotImplementedError('Option.value is an abstract property')

  @abstractmethod
  def add_to(self, dictionary: dict[str, None | bool | int | str | set[str]]) -> None:
    """
      Add the option to a dictionary.

      Derived classes must implement this method to add their specific
      option to the dictionary. The way each type of option is added
      will vary. For example, a boolean option may set a key to True,
      while the environments set will be added to any existing set
      via a set union operation.

      :param dictionary: The dictionary to add the option to
    """
    raise NotImplementedError('Option.add_to() is an abstract method')

  @classmethod
  def is_option(cls, arg: str, next_arg: str | None) -> bool:  # pylint: disable=unused-argument
    """
      Check if a string is an option that can be represented by this class.

      A string is an option if it starts with a single or double hyphen,
      followed by at least one letter (if a single hyphen) or multiple letters
      (if a double hyphen). The letters may optionally be followed by an equal
      sign and a value.

      :param arg: The argument string
      :param next_arg: The next argument string
      :return: True if the argument can be represented by this class
    """
    return arg == '--' \
      or (cls.flag_with_value.match(arg) is not None) \
      or (cls.flag_with_equal_value.match(arg) is not None) \
      or (cls.multi_option.match(arg) is not None) \
      or cls.double_hyphen_option.match(arg) is not None \
      or cls.double_hyphen_option_with_value.match(arg) is not None

  @classmethod
  def is_valid_value_type(cls, str_value: str) -> bool:
    """
      Check if the value is valid for this option.

      :param str_value: The value to check
      :return: True if the value is valid, False otherwise
    """
    raise NotImplementedError('Option.is_valid_value() is an abstract method')

  @staticmethod
  def supported_sub_types() -> list[type[Option]]:
    """
      Get the list of supported subtypes of this option.

      :return: A list of supported subtypes
    """
    # Note the import statements are inside the function. This is done
    # to avoid circular imports.
    # pylint: disable=import-outside-toplevel
    from dralithus.command_line.option_terminator import OptionTerminator
    from dralithus.command_line.help_option import HelpOption
    from dralithus.command_line.verbosity_option import VerbosityOption
    from dralithus.command_line.environment_option import EnvironmentOption
    from dralithus.command_line.multi_option import MultiOption
    return [OptionTerminator, HelpOption, VerbosityOption, EnvironmentOption, MultiOption]

  @staticmethod
  def type_of(arg: str, next_arg: str | None) -> type[Option] | None:
    """
      Determine the type of option based on the argument string.

      :param arg: The argument string
      :param next_arg: The next argument string
      :return: The type of option or None if not found
    """
    for cls in Option.supported_sub_types():
      if cls.is_option(arg, next_arg):
        return cls
    return None

  @classmethod
  def make(cls, current_arg: str, next_arg: str | None) -> tuple[Option | None, bool]:
    """
      Create an Option object from command line arguments.

      :param current_arg: The current argument string
      :param next_arg: The next argument string
      :return: A tuple containing the Option object or None if it is not a known option
        and a boolean indicating whether to skip the next argument
    """
    # Option.is_option() checks if an argument could be a valid option.
    # It checks that it conforms to the syntax for options, but not
    # whether an actual option subclass exists for which the argument
    # is valid.
    # Subclasses of Option must implement is_option() to check if the
    # argument is valid for the specific option. This includes checking
    # if the argument is a valid flag and if the value is valid. You are
    # guaranteed that if <Subclass>.is_option() returns True, then,
    # <Subclass>.make() is guaranteed to succeed in creating an object
    # of the subclass. Except, of course,  for system errors, like out of
    # memory etc.

    # If is Option.is_option() fails, the one of the following is true:
    # 1. The argument is a parameter.
    # 2. The argument is a mis-formed option. E.g. '-v='
    # Strictly, speaking it is not possible to distinguish between a
    # parameter and a mis-formed option. But in practice, if
    # Option.is_option() fails Option._maybe_is_parameter() fails, then
    # the argument should be considered a mis-formed option.
    # If the argument is a parameter then this function must return None.
    # Otherwise, is must raise a ValueError.

    # So if Option.is_option() succeeds, but <Subclass>.is_option() fails,
    # then one of the following is true:
    # 1. The flag does not correspond to any option subclass.
    # 2. The flag corresponds to an option subclass, but the value is not
    #   valid for that subclass. (It is either missing, or the wrong type
    #   or out of range.)

    # if the flag is not valid, then this function must raise a ValueError.
    # If the flag is valid, but the value is not valid, then this function
    # must also raise a ValueError.
    if not cls.is_option(current_arg, next_arg):
      if cls._maybe_is_parameter(current_arg):
        # This is a parameter, not an option.
        return None, False
      # This likely a mis-formed option. E.g. '-v='
      raise ValueError(f'Invalid option: {current_arg}')

    actual_class: type[Option] | None = Option.type_of(current_arg, next_arg)
    if actual_class is None:
      flag = Option._extract_flag(current_arg)
      if flag not in cls.supported_short_flags() and flag not in cls.supported_long_flags():
        # This is an unknown option.
        raise ValueError(f'Unknown option: {current_arg}')
      # This is a valid flag, but the value is not valid for this
      # option. It is either not present, if present is of the wrong
      # type or an invalid value.
      raise ValueError(f'Invalid option: {current_arg}')

    return actual_class.make(current_arg, next_arg)

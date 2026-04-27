"""
  environment_option.py: Define class Environment
"""
from __future__ import annotations
from typing import override

from dralithus.command_line.option import Option

def set_cast(value: str) -> set[str] | None:
  """
    Cast a string to a set of strings or return None if it fails.

    :param value: The string to cast
    :return: The set of strings
  """
  try:
    return set(value.split(','))
  except (ValueError, TypeError):
    return None

class EnvironmentOption(Option):
  """
    A class to represent an environment option.
  """
  def __init__(self, flag: str, environments: set[str]) -> None:
    """
      Initialize the environment option with a set of environment names.

      :param environments: The set of environment names
    """
    super().__init__()
    self._flag = flag
    self._environments = environments

  @classmethod
  def supported_short_flags(cls) -> list[str]:
    """
      The short flag for this option.

      :return: A list containing the short flag 'e'
    """
    return ['e']

  @classmethod
  def supported_long_flags(cls) -> list[str]:
    """
      The long flags for this option.

      :return: A list containing the long flags 'env' and 'environment'
    """
    return ['env', 'environment']

  @override
  def __eq__(self, other: object) -> bool:
    """
      Check if two options are equal.

      :param other: The other option to compare to
      :return: True if the options are equal, False otherwise
    """
    if not isinstance(other, EnvironmentOption):
      return False
    return self._flag == other._flag and self._environments == other._environments

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
  def value(self) -> set[str]:
    """
      Get the value of the environment option.

      :return: The value of the environment option
    """
    return self._environments

  @override
  def add_to(self, dictionary: dict[str, None | bool | int | str | set[str]]) -> None:
    """
      Add the option to a dictionary.

      :param dictionary: The dictionary to add the option to
    """
    environments = dictionary.get('environments', None)
    if environments is None:
      environments = self.value
    else:
      assert isinstance(environments, set) and all(isinstance(env, str) for env in environments)
      environments = environments | self.value
    dictionary['environments'] = environments

  @classmethod
  def is_option(cls, arg: str, next_arg: str | None) -> bool:
    """
      Check if the argument is an environment option.

      :param arg: The argument string
      :param next_arg: The next argument string
      :return: True if the argument is an environment option
    """
    flag, str_value, _ = cls._extract_value(arg, next_arg)
    if flag not in ('e', 'env', 'environment'):
      return False
    if str_value is None:
      return False
    if not cls.is_valid_value_type(str_value):
      return False
    environments = set_cast(str_value)
    assert environments is not None
    for environment in environments:
      if not cls.is_valid_environment(environment):
        return False
    return True

  @classmethod
  def is_valid_value_type(cls, str_value: str) -> bool:
    """
      Check if the value is a valid verbosity level.
      :param str_value:
      :return:
    """
    return set_cast(str_value) is not None

  @classmethod
  def is_valid_environment(cls, environment: str) -> bool:
    """
      Check if the environment name is valid.

      :param environment: The environment name
      :return: True if the environment name is valid
    """
    # return environment in ('local', 'development', 'test', 'staging', 'production')
    # For now all non-empty environment names are valid, except for --,
    # the option terminator. Note that we are not checking if an environment
    # with that name exists, as this is not the responsibility of this class.
    # That is the responsibility of the code that uses this option, such as
    # the deploy_command module (see deploy_command.make_environments.)
    return len(environment) > 0 and environment != '--'

  @classmethod
  def make(cls, current_arg: str, next_arg: str | None) -> tuple[EnvironmentOption, bool]:
    """
      Create an EnvironmentOption object from command line arguments.

      :param current_arg: The current argument string
      :param next_arg: The next argument string
      :return: A tuple containing the EnvironmentOption object and a boolean indicating
        whether to skip the next argument
    """
    assert cls.is_option(current_arg, next_arg)
    flag, str_value, skip_next_arg = cls._extract_value(current_arg, next_arg)
    if str_value is None:
      raise ValueError(f'Missing value for environment option: {current_arg}')
    environments: set[str] = {env.strip() for env in str_value.split(',')}
    for environment in environments:
      if not cls.is_valid_environment(environment):
        raise ValueError(f'Invalid environment name: {environment}')
    return EnvironmentOption(flag, environments), skip_next_arg

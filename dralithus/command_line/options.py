"""
  options.py: Define class Options
"""
from contextlib import contextmanager
from typing import Generator, Iterator, Mapping, override

from dralithus.command_line.option import Option
from dralithus.command_line.option_terminator import OptionTerminator


class Options(Mapping[str, None | bool | int | str | set[str]]):
  """
    A class to represent a mapping of options.
  """
  def _next_option(self) -> Option | None:
    """
      Get the next option

      This method assumes that the arguments have been split into
      individual options (i.e. no multi-option arguments).

      The index of the current argument, stored in self._i, is
      incremented by 1 for each option and by 2 if the next argument
      is a value for the option.

      :return: The next option or None if there are no more options
    """
    if self._end_index < len(self._args):
      current_arg = self._args[self._end_index]
      next_arg = self._args[self._end_index + 1] if self._end_index + 1 < len(self._args) else None
      option, skip_next_arg = Option.make(current_arg, next_arg)
      if option is not None:  # Only increment the end_index if the current arg was processed
        self._end_index += 2 if skip_next_arg else 1
      return None if isinstance(option, OptionTerminator) else option
    return None

  def _parse(self) -> list[Option]:
    """
      A generator to yield the next option and its value.

      Note the return type is list and not a dictionary.
      The list needs to be processed to combine multiple options
      appropriately to create a dictionary where each option type
      has a single value.

      :return: A list of options
    """
    options: list[Option] = []
    while (option := self._next_option()) is not None:
      options.append(option)
    return options

  @staticmethod
  def _to_dict(options: list[Option]) -> dict[str, None | bool | int | str | set[str]]:
    """
      Convert the options to a dictionary.

      :param options: The list of options
      :return: A dictionary of options
    """
    dictionary: dict[str, None | bool | int | str | set[str]] = {
      'requires_help': False,
      'verbosity': 0,
      'environments': set(),
    }
    for option in options:
      option.add_to(dictionary)
    return dictionary

  @contextmanager
  def _parser_state(self, args: list[str]) -> Generator[None, None, None]:
    """
      A context manager to save and restore the parser state.

      :return: A generator that yields the parser state
    """
    self._end_index: int  = 0
    self._args: list[str] = args[:]  # Make a copy of the args list
    try:
      yield
    finally:
      del self._args


  def __init__(self, args: list[str]) -> None:
    """
      Initialize the option object with the command line arguments.

      :param args: The command line arguments
    """
    with self._parser_state(args):
      self._options = self._to_dict(self._parse())

  @override
  def __getitem__(self, key: str) -> None | bool | int | str | set[str]:
    """
      Get the value of the option.

      :param key: The name of the option
      :return: The value of the option
    """
    return self._options[key]

  @override
  def __iter__(self) -> Iterator[str]:
    """
      Return an iterator over the option names.
      :return: An iterator over the option names
    """
    return iter(self._options)

  @override
  def __len__(self) -> int:
    """
      Get the number of options.

      :return: The number of options
    """
    return len(self._options)

  @property
  def end_index(self) -> int:
    """
      Returns of index that marks the end of the options.

      This marks the start of the parameter list. This
      always one past index of the last option. If there
      are no parameters after the options, then the end
      index is the length of the arguments list.

      :return: The end index of the options
    """
    return self._end_index

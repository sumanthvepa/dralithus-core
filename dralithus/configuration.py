"""
  configuration.py: Command line processing for dralithus
"""
from typing import TypedDict


class CommandLineError(RuntimeError):
  """
    CommandLineError: An error occurred while processing the command line
  """

  def __init__(self, verbosity, message: str) -> None:
    """
      Initialize the CommandLineError
      :param message: The error message
    """
    super().__init__(message)
    self.verbosity = verbosity


class Operation(TypedDict):
  """
    The operation that drl is expected to perform

    The operation that drl is expected to perform is described by this
    dictionary. The dictionary contains the following keys:
    - command: str: The command to be executed
    - about: None | str: If the command is help, then about will contain the
        command to get help on. Or it can be None if global help (about the
        whole program) is requested. If the command is not help,  then about
        will always be None.
    - applications: None | list[str]: The applications to be deployed. The value
        will be None if the command does not take a list of applications.
    - environment: None | list[str]: The environments to deploy the application
        to. The value will be None if the command does not take a list of
        environments.
    - verbosity: int:  The verbosity level. 0 is the default.
  """
  command: str
  about: str | None
  applications: list[str] | None
  environments: list[str] | None
  verbosity: int

def help_message(command: str | None, verbosity: int) -> str:
  """
    Generate a help message

    Generate a help message for the specified command. The verbosity level
    determines how much information is included in the help message.

    :param command: str: The command to generate help for
    :param verbosity: int: The verbosity level
  """
  # TODO: Implement help_message
  if command is None:
    return f"Global help message. Verbosity {verbosity}"
  return f"Help message for {command}. Verbosity {verbosity}"


# pylint: disable=unused-argument
# noinspection PyUnusedLocal
def process_command_line(args: list[str]) -> Operation:
  """
    Process command line arguments

    The function takes a list of command line arguments and returns a typed
    dictionary (Operation) that describes the operation that drl is expected to
    perform.


    If an error is encountered while processing the command line,
    a CommandLineError exception is raised.

    We pass the command line arguments as a parameter to the function rather
    than using sys.argv directly. This allows us to test the function with
    different command line arguments without having to modify the actual command
    line.

    TODO: args is not used, but will be, when the function is implemented.

    :param list[str] args: The command line arguments (typically sys.argv)

    :return: A dictionary containing details about the command to be executed
    The dictionary will contain the following keys:
    - command: str: The command to be executed
    - about: None | str: If the command is help, then about will contain the
        command to get help on. Or it can be None if global help (about the
        whole program) is requested. If the command is not help,  then about will
        always be None.
    - applications: None | list[str]: The applications to be deployed. The value
        will be None if the command is does not take a list of applications.
    - environment: None | list[str]: The environments to deploy the application
        to. The value will be None if the command does not take a list of
        environments.
    - verbosity: int:  The verbosity level. 0 is the default.
  """
  # TODO: Implement this.
  return {
    'command': 'help',
    'about': None,
    'applications': None,
    'environments': None,
    'verbosity': 0
  }

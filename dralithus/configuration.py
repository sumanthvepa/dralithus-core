"""
  configuration.py: Command line processing for dralithus
"""
import re
from typing import TypedDict


class CommandLineError(RuntimeError):
  """
    CommandLineError: An error occurred while processing the command line
  """

  def __init__(self, program, verbosity, message: str) -> None:
    """
      Initialize the CommandLineError
      :param message: The error message
    """
    super().__init__(message)
    self.program = program
    self.verbosity = verbosity

  def __str__(self):
    message = super().__str__()
    return ('CommandLineError('
      + f'program="{self.program}", verbosity={self.verbosity}, message="{message}")')


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

def is_valid_command(command: str) -> bool:
  """ Check if the given command is a valid command """
  return command in ['deploy']


def get_command(command_line: list[str]) -> str | None:
  """
    Get the command from the command line

    :param command_line: list[str]: The command line arguments
        no command is found, and rest of the command line arguments
    :return: str | None: The command if found, otherwise None
  """
  # Skip over options until the first non-option argument is found
  # This assumes that options taking values are specified as a single
  # argument, e.g. '-v3'. i.e. that the merge_option_values function
  # has been called to process the command line before this functon is called.
  for arg in command_line:
    if not arg.startswith('-'):
      return arg
  return None

def get_option_value(regex: str, option: str) -> int | None:
  """
    Get the value of an option from a flag.
    E.g. -v or -vv or -v=3 or --verbose=4 or -v 3
  """
  m= re.match(regex, option)
  if m:
    try:
      str_value = m.group(1)
      try:
        int_value = int(str_value)
        return int_value
      except ValueError:
        # The value is not an integer. However, it could be a string
        # like 'vv'. In that case, return the length of the string.
        # Otherwise, return None.
        m1 = re.match(r'^([a-zA-Z]+)$', str_value)
        if m1:
          return len(m1.group(1))
        return None
    except IndexError:
      return None # The regex matched but no value was found
  return None

def get_verbosity(command_line: list[str]) -> tuple[int, list[str]]:
  """ Get the verbosity level from the command line """
  verbosity = 0
  command_line_without_verbosity_options = []
  for arg in command_line:
    # If the argument is '-v' or '--verbose', then either
    # increment the verbosity value or set it to the value
    # specified in the argument.
    if arg.startswith('-v'):
      pattern = r'^-(v+)$'
      value = get_option_value(pattern, arg)
      if value is not None:
        verbosity += value
        continue
      pattern = r'^-v(\d+)$'
      value = get_option_value(pattern, arg)
      if value is not None:
        verbosity = value
        continue
      pattern = r'^-v=(\d+)$'
      value = get_option_value(pattern, arg)
      if value is not None:
        verbosity = value
        continue
      pattern = r'^-v (\d+)$'
      value = get_option_value(pattern, arg)
      if value is not None:
        verbosity = value
        continue
    elif arg.startswith('--verbose'):
      pattern = r'^--verbose=(\d+)$'
      value = get_option_value(pattern, arg)
      if value is not None:
        verbosity = value
        continue
      pattern = r'^--verbose (\d+)$'
      value = get_option_value(pattern, arg)
      if value is not None:
        verbosity = value
        continue
      verbosity += 1
    else:
      command_line_without_verbosity_options.append(arg)
  return verbosity, command_line_without_verbosity_options


def irrelevant_help_arguments(command_line: list[str]) -> bool:
  """
    Check if there are irrelevant arguments in the command line

    Check if there are irrelevant arguments in the command line. Irrelevant
    arguments are arguments that are not related to the help command.

    :param command_line: list[str]: The command line arguments
    :return: bool: True if there are irrelevant arguments, otherwise False
  """
  for arg in command_line:
    if arg not in ['-h', '--help']:
      return True
  return False

def merge_option_values(command_line: list[str]) -> list[str]:
  """
    Merge option values that are split into two arguments

    Some options are split into two arguments. For example, the verbosity
    option can be specified as '-v 3' or '--verbose 3'. This function
    merges such arguments into a single argument, example ['deploy' '-v' '3'] becomes
    ['deploy', '-v3']

    # Currently, this function only merges the verbosity option.

    :param command_line: list[str]: The command line arguments
    :return: list[str]: The command line arguments with the option values merged
  """
  merged = []
  i = 0
  while i < len(command_line):
    arg = command_line[i]
    if arg in ['-v', '--verbose']:
      if i + 1 < len(command_line): # Don't try to look beyond the end of the list
        # The next argument is a potential value for the verbosity option
        potential_option_value = command_line[i + 1]
        try:
          value = int(potential_option_value)
          if value >= 0: # Next argument is a positive integer
            merged.append(f'{arg} {value}')
            i += 1 # Skip the next argument as it has been processed already
        except ValueError: # The next argument was not an integer
          # just add the option to the merged list
          merged.append(arg)
      else:
        # The verbosity option is the last argument in the list
        merged.append(arg)
    elif arg in ['-e', '--environment']:
      # This option requires a value. So as long as the option is not the last
      # argument in the list, we can merge the option with the next argument,
      # provided the next argument is not also an option. This, latter condition,
      # is a user error, will be caught elsewhere.
      if i + 1 < len(command_line):
        potential_option_value = command_line[i + 1]
        # Only merge the potential option value if it does not start with a '-'.
        # The '-' indicates that the next argument is an option and not a value.
        if not potential_option_value.startswith('-'):
          merged.append(f'{arg} {potential_option_value}')
          i += 1
    else:
      # The argument is not -v, --verbose, -e, or --environment so just add it
      # to the merged list.
      merged.append(arg)
    i += 1
  return merged

def is_asking_for_help(
    program: str,
    command: str | None,
    verbosity: int,
    command_line: list[str]) -> Operation | None:
  """
    Check if the user is asking for help, and if so, return the command
    that help is being requested for.

    The user is considered to be asking for help if the '-h' or '--help' option
    is present in the command line arguments. Or if the command itself is help.

    :param program: str: The name of the program
    :param command: str | None: The command to be executed. If the command is None
        then the user is asking for global help.
    :param verbosity: int: The verbosity level
    :param command_line: list[str]: The command line arguments (with the program name removed)
    :return: Operation | None: If help is being requested, then an Operation
        dictionary is returned. Otherwise, None is
  """
  # Scan through the command line arguments to see if any argument is
  # either '-h' or '--help'.
  if command == 'help':
    return {
      'command': 'help',
      'about': None,
      'applications': None,
      'environments': None,
      'verbosity': verbosity
    }
  if '-h' in command_line or '--help' in command_line:
    if command is not None:
      if not is_valid_command(command):
        raise CommandLineError(
          program=program, verbosity=verbosity, message=f'Invalid command {command}')
      return {
        'command': 'help',
        'about': command,
        'applications': None,
        'environments': None,
        'verbosity': verbosity
      }
    # command is None
    if irrelevant_help_arguments(command_line):
      raise CommandLineError(
        program=program, verbosity=verbosity, message='Irrelevant arguments found')
    # The user is asking for global help
    return {
      'command': 'help',
      'about': None,
      'applications': None,
      'environments': None,
      'verbosity': verbosity
    }
  # No help is being sought
  return None


def get_global_and_command_specific_options(
    command: str, command_line: list[str]) -> tuple[list[str], list[str]]:
  """
    Get the global and command specific options from the command line
    :param command: str: The command to be executed
    :param command_line: list[str]: The command line arguments
    :return: tuple[list[str], list[str]]: A tuple containing two lists.
        The first list contains the global options, and the second list
        contains the command specific options.
  """
  command_index = command_line.index(command)
  global_options = command_line[:command_index]
  command_options = command_line[command_index + 1:]
  return global_options, command_options


def get_environments(program: str, command_line: list[str]) -> list[str]:
  """
    Get the environments from the command line
    :param program: str: The name of the program
    :param command_line: list[str]: The command line arguments
    :return: list[str]: The environments
  """
  environments = []
  i = 0
  while i < len(command_line):
    if command_line[i] in ['-e', '--environment']:
      if i + 1 < len(command_line):
        environments.append(command_line[i + 1])
        i += 1
    i += 1
  return environments

def get_applications(program: str, command_line: list[str]) -> list[str]:
  """
    Get the applications from the command line
    :param program: str: The name of the program
    :param command_line: list[str]: The command line arguments
    :return: list[str]: The applications
  """
  applications = []
  i = 0
  while i < len(command_line) and command_line[i].startswith('-'):
    i += 1
  while i < len(command_line):
    if not command_line[i].startswith('-'):
      applications.append(command_line[i])
    i += 1
  return applications

def remove_equality_signs(command_line: list[str]) -> list[str]:
  """
    Remove equality signs from the command line arguments

    This function removes the equality signs from the command line arguments.
    For example, '-e=env' becomes two elements, '-e', 'env'

    :param command_line: list[str]: The command line arguments
    :return: list[str]: The command line arguments with the equality signs removed
  """
  modified_command_line: list[str] = []
  for element in command_line:
    if element.startswith('-'):
      # The argument is an option, so check if it contains an equality sign
      if '=' in element:
        # Split the argument into two parts
        parts = element.split('=')
        # Remove the equality sign and add the two parts to the list
        modified_command_line.append(parts[0])
        modified_command_line.append(parts[1])
      else:
        # The argument is just an option, so add it to the list
        modified_command_line.append(element)
    else:
      # The argument is not an option, so just add it to the list
      modified_command_line.append(element)
  return command_line


def process_deploy_command(
    program: str, global_options: list[str], command_options: list[str], verbosity: int) -> Operation:
  """
    Process the 'deploy' command
    :param program: str: The name of the program
    :param global_options: list[str]: The global options list (not currently used)
    :param command_options: list[str]: The command options list
    :param verbosity: int: The verbosity level
    :return: Operation: The operation to be performed
  """
  command_options = remove_equality_signs(command_options)
  environments = get_environments(program, command_options)
  applications = get_applications(program, command_options)
  return {
    'command': 'deploy',
    'about': None,
    'applications': applications,
    'environments': environments,
    'verbosity': verbosity
  }


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

    :param list[str] args: The command line arguments (typically sys.argv)

    :return: A dictionary containing details about the command to be executed
    The dictionary will contain the following keys:
    - command: str: The command to be executed
    - about: None | str: If the command is help, then about will contain the
        command to get help on. Or it can be None if global help (about the
        whole program) is requested. If the command is not help,  then about will
        always be None.
    - applications: None | list[str]: The applications to be deployed. The value
        will be None if the command does not take a list of applications.
    - environment: None | list[str]: The environments to deploy the application
        to. The value will be None if the command does not take a list of
        environments.
    - verbosity: int:  The verbosity level. 0 is the default.
  """
  # Set the program name
  program = args[0] if len(args) > 0 else 'dralithus'
  # If no arguments are provided, raise an error.
  if len(args) < 2:
    raise CommandLineError(program=program, verbosity=0, message='Command not specified')

  command_line = args[1:]
  command_line = merge_option_values(command_line)

  command = get_command(command_line)
  # Get the verbosity level from the command line, and also remove the
  # verbosity options from the command line in the process.
  verbosity, command_line = get_verbosity(command_line)

  # If the user is asking for help, return the help operation
  operation = is_asking_for_help(program, command, verbosity, command_line)
  if operation is not None:
    return operation

  # There has to be a command for the program to do anything
  if command is None:
    raise CommandLineError(program=program, verbosity=verbosity, message='Command not specified')

  # But the command has to be valid
  if not is_valid_command(command):
    raise CommandLineError(
      program=program,
      verbosity=verbosity,
      message=f'Invalid command {command}')

  global_options, command_options = get_global_and_command_specific_options(command, command_line)
  if command == 'deploy':
    return process_deploy_command(program, global_options, command_options, verbosity)

  # TODO: Implement rest of process_command_line beyond this point
  raise NotImplementedError('Feature implementation is not complete')

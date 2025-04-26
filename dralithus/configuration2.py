"""
  configuration2.py: New configuration processing for dralithus
"""

from dralithus.errors import DralithusError, ExitCode


class CommandLineError(DralithusError):
  """
    Exception raised for invalid command line arguments passed
    by the user.

    Unlike other exceptions, this exception is caught by code
    that parses the command line and converted into a help command
    that is executed. The help command when executed will print
    the error, and then provide an appropriate help message.
  """
  def __init__(self, message: str) -> None:
    """
      Initialize the InvalidCommandLineError with a message.

      The exit code is set to ExitCode.INVALID_COMMAND_LINE.

      :param message: The error message
    """
    super().__init__(message, exit_code=ExitCode.INVALID_COMMAND_LINE)

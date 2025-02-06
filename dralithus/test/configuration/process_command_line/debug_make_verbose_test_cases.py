from dralithus.test.configuration.process_command_line import (
  Args,
  TestCaseData,
  make_verbose_test_cases,
  print_cases)

dummy_test_case: TestCaseData = {
  'args': Args(
    program='drl',
    global_options=[],
    command='deploy',
    command_options=["--environment='local'"],
    parameters=['sample']
  ),
  'expected': {
    'command': 'deploy',
    'about': None,
    'applications': ['sample'],
    'environments': ['local'],
    'verbosity': 0
  },
  'error': None
}

if __name__ == '__main__':
  cases = [(dummy_test_case,)] + make_verbose_test_cases(dummy_test_case)
  print_cases(cases)

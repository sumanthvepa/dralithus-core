Run this project's unit tests with Python's built-in unittest
discovery.

To run all unit tests, use:

```bash
PYTHONPATH=tests python -m unittest discover -s tests/dralithus/test
```

To run a single test module, use:

```bash
PYTHONPATH=tests python -m unittest discover -s tests/dralithus/test \
  -p 'test_name.py' -v
```

Use -v when you want individual test names in the output.

Do not use pytest for this project unless the user explicitly asks
for it. The repository is structured around unittest.TestCase.

Before running tests, make sure the correct Python environment is
active. If imports fail for project packages or dependencies, report
that the environment is not set up correctly instead of changing the
test command. Do not fall back to PYTHONPATH=src unless the user
explicitly asks to use the alternate non-installed workflow.

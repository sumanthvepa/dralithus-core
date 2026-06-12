# Dralithus

Dralithus is intended to be a command-line tool to "hydrate" a network of
virtual machines and containers in order to deploy applications across
various environments. The CLI binary is `drl`.

## Release Plan

### Release 0
When invoked as follows:

```bash
drl deploy --environment='local' sample
```

The program should print the following:

```json
{
  "application": "sample",
  "environment": "local"
}
```

## Development

### Create the virtual environment and install dependencies
Create a Python virtual environment and activate it from the project root:

```bash
python -m venv venv
source venv/bin/activate
```

You can either install the latest versions of the dependencies from
`packages.txt`:

```bash
packages3.sh
```

This should be done if you have just checked out a new branch and want
to create a venv with the latest versions of the dependencies.

Sometimes this is not desirable, for example, if you want to recreate a
known-good environment using the dependencies pinned in
`requirements.txt`. In that case, install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Install the project in editable mode
Install the project in editable mode from the project root:

```bash
pip install -e .
```

After the editable install, the `dralithus` package is importable from
the active Python environment while still using the source files in this
working tree, and the `drl` command is placed in the venv's `bin/`
directory so it can be invoked directly.

Now you can start doing development work. (See the section on testing
below for how to run the unit tests.)

### pyproject.toml vs requirements.txt vs packages.txt
For Milestone 42 projects, `packages.txt` is the source of truth for
top-level dependencies. The way we work at Milestone 42 is that there is
an expectation that the project will work with the latest versions of
its dependencies, so `packages.txt` does not specify versions. The
project should be tested with the latest versions of dependencies before
merging to `main`.

`requirements.txt` is a generated file that pins the exact versions of
dependencies that are known to work together. When you are ready to
deploy the project to production, regenerate `requirements.txt` in the
development environment first by re-running `packages3.sh`.

`pyproject.toml` is used to specify the project metadata and
dependencies in a standardized way. It is used by `pip` to install the
project and its dependencies. Currently, you are required to manually
keep `pyproject.toml` in sync with `packages.txt`; a future version of
the package management script (planned `packages4`) will read
dependencies directly from `pyproject.toml` and remove this duplication.

To rebuild the development environment from scratch:

```bash
rm -r venv
python -m venv venv
source venv/bin/activate
packages3.sh
pip install -e .
```

### Testing
Run the unit tests with:

```bash
PYTHONPATH=tests python -m unittest discover -s tests/dralithus/test
```

The `PYTHONPATH=tests` setting lets the tests import shared helpers
defined in `tests/dralithus/test/__init__.py` as the `dralithus.test`
package.

### Alternate workflow without editable install
If you prefer not to install the project, you can run it directly by
adding `src` to `PYTHONPATH`:

```bash
PYTHONPATH=src python -m dralithus.drl deploy --environment='local' sample
```

For tests in this alternate workflow, include both `src` and `tests`:

```bash
PYTHONPATH=src:tests python -m unittest discover -s tests/dralithus/test
```

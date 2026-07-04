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

## Building a Distributable Package

To build a production-style package instead of installing the project in
editable mode, run this from the project root:

```bash
python -m build
```

This creates the source distribution and wheel under `dist/`, for
example:

```text
dist/dralithus_core-0.2.0.tar.gz
dist/dralithus_core-0.2.0-py3-none-any.whl
```

To build only the wheel:

```bash
python -m build --wheel
```

Install the built wheel with:

```bash
python -m pip install dist/dralithus_core-0.2.0-py3-none-any.whl
```

Unlike `pip install -e .`, installing the wheel copies the packaged
files into `site-packages`. This is useful for checking production
packaging issues, such as missing template resources.

A simple smoke test in a fresh virtual environment is:

```bash
python3.14 -m venv /tmp/dralithus-install-test
/tmp/dralithus-install-test/bin/python -m pip install --upgrade pip
/tmp/dralithus-install-test/bin/python -m pip install dist/dralithus_core-0.2.0-py3-none-any.whl
/tmp/dralithus-install-test/bin/drl --help
```

If `python -m build` fails because the `build` package is not
installed, refresh the project venv with `~/bin/packages3.sh`; `build`
is listed in `packages.txt`.

## Distribution with Devpi

Devpi can host private wheels and also proxy public PyPI packages. This
lets pip use one internal package index for both Milestone 42 packages
and public dependencies.

Install the Devpi server and client tools in the environment that will
administer the index:

```bash
python -m pip install devpi-server devpi-client
```

Initialize and run a local Devpi server:

```bash
devpi-init --serverdir ~/devpi-server
devpi-server --serverdir ~/devpi-server --host 127.0.0.1 --port 3141
```

In another shell, configure a user index that inherits from Devpi's
public PyPI mirror:

```bash
devpi use http://127.0.0.1:3141
devpi user -m root password=<root-password>
devpi login root --password=<root-password>
devpi user -c milestone42 password=<user-password>
devpi user -m milestone42 pypi_whitelist='*'
devpi login milestone42 --password=<user-password>
devpi index -c dev bases=root/pypi
devpi use milestone42/dev
```

Build the dralithus wheel and upload it:

```bash
python -m build --wheel
devpi upload --from-dir dist
```

Install from the Devpi index:

```bash
python -m pip install --index-url http://127.0.0.1:3141/milestone42/dev/+simple/ dralithus-core
```

Or configure a venv to use Devpi by default:

```bash
python -m pip config set global.index-url http://127.0.0.1:3141/milestone42/dev/+simple/
```

With this setup, pip asks Devpi for every package. Devpi serves private
packages uploaded to `milestone42/dev` and falls back to `root/pypi` for
public packages. This avoids using pip's `extra-index-url`, where public
and private indexes are searched together and a public package with the
same name can be selected if it has the best matching version.

For a server reachable by other machines, run Devpi behind HTTPS and
use a stable service manager instead of an interactive shell. Devpi can
generate example service and web-server configuration with:

```bash
devpi-gen-config --serverdir ~/devpi-server
```

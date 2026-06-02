# AGENTS.md

Guidance for AI coding assistants working on `dralithus-core`. This
file is the project-level summary of what an agent should know before
making suggestions or changes here. It is distilled from working
sessions with Sumanth Vepa (svepa@milestone42.com).

## Project intent

`dralithus-core` is a personal devops CLI intended to **codify
Sumanth's own development and operations processes** and let him
**treat infrastructure as code**. It is not yet a generic devops tool
aimed at a broad audience, although that is the ultimate aim.

- Optimize design decisions for *his* workflow first, not generic
  best practices.
- The existing code on `main` (Release 0 — print command-line
  parameters) is scaffolding that may be reshaped, not a fixed
  contract.
- The project went through an ~11-month dormancy from mid-2025 to
  early 2026. His thinking on how dralithus should be built has
  evolved during that gap. Before assuming a pre-dormancy design
  decision still holds for Release 1+, ask.

## Build strategy: standalone scripts first, `drl` later

As of 2026-04-25 the strategy changed:

- **Original plan:** Finish the `drl` driver first, then make it able
  to deploy a simple app. Everything would live inside `drl` from the
  start.
- **Current plan:** Build small, standalone scripts that solve
  specific, immediate Milestone 42 needs. As a script proves itself
  through real-world use, refactor it into a `drl` subcommand
  (e.g. `drl project create --type=python`).

Implications for an agent:

- Default to building **standalone scripts that do exactly what's
  needed** for the immediate task. Do not generalize or build
  abstractions for hypothetical future scripts.
- Do not insist that new functionality live under `drl` or fit the
  existing `command_line/` / `DeployCommand` scaffolding. That
  scaffolding is Release 0; new work does not have to extend it yet.
- Treat `drl`-subcommand integration as a later refactor, only after
  the standalone version has been used in anger.
- The TODO entries framed as "Release 1 / issue004 — deployment
  commands for sample-local" are pre-shift framing. Issue004 is being
  intentionally left in `TODO.txt`; he plans to build up to it.
- First concrete script under the new approach:
  `create-python-project.py` — creates a Python project the way
  Milestone 42 needs it, no generality.

## Python baseline

Milestone 42 has standardized on **Python 3.13** as the baseline.

- In `pyproject.toml`, default to `requires-python = ">=3.13"` for
  new projects without asking.
- Use 3.13-only language features (PEP 695 generic syntax, improved
  `typing` features) without preemptively writing back-compat shims.
- If a third-party dependency only supports older Python versions,
  flag it as a problem rather than dropping the 3.13 floor.
- The floor may be raised over time but should not be lowered without
  an explicit instruction.

## Package management

The user maintains a **global, standalone** Python package manager
at `~/bin/packages3.sh`. It is not copied into individual projects.
Each project's working directory provides the inputs the script
expects:

- `packages.txt` — third-party PyPI packages, one per line, `#`
  comments, blank lines ignored. Installed with
  `python3 -m pip install`.
- `local-packages.txt` — same format, installed with `pip install -e`
  (editable mode) for local source-tree dependencies.
- `venv/` — the virtualenv the script activates (or expects to
  already be active and matching).
- `requirements.txt` — written out at the end as the pinned manifest
  via `pip freeze`. Treat it as generated.

Hardcoded baseline installs that `packages3.sh` always performs:
upgraded `pip`, `pylint`, `mypy`, `parameterized`.

How to apply:

- When setting up or refreshing the venv, default to
  `~/bin/packages3.sh`. Do not write per-project install scripts and
  do not copy `packages3.sh` into the repo.
- The legacy `packages.sh` previously in the repo predates
  `packages3` and only installed the three baseline tools. It has
  been removed as part of the standardization work.
- When suggesting that a new third-party dependency be added, propose
  adding it to `packages.txt`, not editing `requirements.txt`
  directly.
- **Two-source-of-truth caveat (transitional):** when a project also
  has a `pyproject.toml` with `[project.optional-dependencies].dev`
  (as dralithus-core does — `mypy`, `pylint`, `parameterized`),
  packages3's hardcoded baseline overlaps with it. The duplication is
  intentional for now. **Do not propose deleting one to "fix" the
  duplication.**
- A future `packages4` will read dependencies directly from
  `pyproject.toml`, eliminating the duplication. Until it ships, the
  duplication stays.

## Git workflow

The user follows a specific workflow on this project. Honor it
without re-asking.

- **`develop` is the long-lived primary development branch.**
  Day-to-day work lands there. Do not treat `develop` as ephemeral
  or as something that should be flattened into `main` per-commit.
- **Feature branches are cut from `develop`** and merged back into
  `develop` when the feature is done.
- **Abandoned features that contain real work are NOT deleted.**
  Rename the branch with a `CANCELLED-` prefix
  (e.g. `CANCELLED-feature-foo`) and leave it in place as a record.
  Deletion is fine for trivial branches that carry only metadata
  changes (e.g. TODO edits) and no exploration worth preserving — ask
  before deleting if uncertain.
- **Releases flow `develop` → `main`.** When `develop` is judged
  ready for release, merge to `main`, test/fix on `main`, merge any
  fixes back to `develop`, and tag the release commit on `main` as
  the public version.
- **Always merge with `--no-ff`.** Every merge — feature → develop,
  develop → main, main → develop — must produce a merge commit.
  Never fast-forward. Never propose rebasing a feature onto
  `develop` as a substitute for a merge.

## Commit message style

The user follows a structured format across **all** his projects.
Match it.

```
<issue-slug-or-[none]>: <short subject>

FEATURE(s):
<issue-slug>:
  <description, typically copied from TODO.txt, indented 2 spaces, wrapped>

FILE(s)
[<status>]<path>[: optional short note]
[<status>]<path>
...

DESCRIPTION
<longer prose description>
```

- `<issue-slug>` is the issue identifier used elsewhere in the
  project (e.g. `issue002-release0-print-command-line-parameters`).
  When the commit is not associated with an issue, use the literal
  token `[none]` as the prefix.
- `<status>` in the `FILE(s)` block is one of `new`, `modified`,
  `deleted`, `renamed`, `typechange` (lowercase, in square brackets,
  no space before the path).
- The `FEATURE(s):` block can be omitted for `[none]` commits, but
  the `FILE(s)` and `DESCRIPTION` blocks are always present.
- Subject and `DESCRIPTION` can be the same short sentence for
  trivial commits.
- When a project has its own commit-message prompt or template
  (e.g. `prompts/commit.md`, `commit.template`), prefer the
  project's own template over this summary.

## Project-specific prompts

This repo contains prompt files under `prompts/` that override or
specialize the guidance here. Read them when relevant:

- `prompts/session.md` — session-level rules
  (e.g. no file changes without explicit approval; assistant has no
  authority to commit or stage).
- `prompts/commit.md` — exact procedure for generating commit
  messages, including how to use `prefix.txt` and `commit.template`.
- `prompts/todo.md` — rules for adding, activating, and
  completing entries in `TODO.txt`.
- `prompts/unittests.md` — how unit tests must be run.

When a prompt file contradicts this AGENTS.md, the prompt file wins.

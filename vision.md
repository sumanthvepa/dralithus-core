# Dralithus Vision

Dralithus is intended to be "devops engineer in a box" for
Milestone 42.

Milestone 42 is currently a one-person operation, so dralithus should
first optimize for Sumanth's own development and operations workflow.
It may eventually become useful as a broader devops tool, but its
initial purpose is to codify the way one firm provisions machines,
manages infrastructure, tracks projects, and deploys software.

## Core Purpose

Dralithus should provide a cohesive collection of servers, tools, and
scripts that help manage the full lifecycle of Milestone 42's computing
environment:

- provision new physical computers for use in the firm
- create and provision virtual machines
- track where virtual machines live and how long they should exist
- support virtual machines hosted on internal servers, cloud providers,
  and people's laptops
- distinguish and manage both development and production virtual
  machines
- create, manage, and deploy containers to managed machines
- keep track of software projects across the firm
- manage project information locations such as wikis and Git
  repositories
- track local workspaces and production machines where software is
  deployed
- manage project configuration for development, test, and production
  use
- provide infrastructure for creating new projects
- provide infrastructure for creating new workspaces for existing
  projects
- manage continuous integration pipelines
- deploy project instances
- roll back deployed project instances when needed

## Design Bias

Dralithus should behave like a practical internal IT department for
Milestone 42, not like a generic platform designed in the abstract.

The system should grow from immediate operational needs. Standalone
scripts and focused tools are acceptable, and often preferred, when
they solve a real problem directly. As those tools prove themselves in
regular use, they can be refactored into more integrated `drl`
subcommands or shared services.

The long-term direction is an integrated system that knows about the
firm's computers, virtual machines, containers, projects, workspaces,
repositories, deployment targets, environments, configuration, CI
pipelines, releases, and rollbacks.

The immediate direction is to build the next useful piece of that
system in a way that serves Milestone 42's real workflow.

## Transactionality and the Project Lifecycle

A defining ambition of dralithus is that its lifecycle operations -
create a project, update a project, provision a machine, deploy a
release - are **transactional**: each operation either completes fully
or leaves the system exactly as it was before. A half-created project,
a half-upgraded one, or a half-deployed release should never be a state
the user is left in.

The intended mechanism is a **two-phase commit** discipline over the
ordered execution steps, rather than today's simpler run/rollback:

- **prepare** - each step does its work but preserves whatever it
  displaced, so the prior state can still be restored;
- **commit** - run only after *every* step's prepare succeeds; it
  discards the preserved prior state and finalizes;
- **abort** - run if any step fails; it restores the preserved prior
  state on the completed steps, in reverse.

Resources that cannot be mutated reversibly in place (a virtual
environment, an existing config file being overwritten, a deployed
artifact) are handled by **backup-and-swap**: preserve the prior copy,
build the new one at its canonical location, then on commit discard the
backup or on abort restore it. This treats inherently *regenerable*
artifacts - a venv is fully determined by its interpreter and its
declared dependencies - as disposable and rebuildable rather than
something to be surgically un-mutated.

### Update without losing customizations - the differentiator

The transactional foundation exists to enable what dralithus intends as
its key differentiator: **updating an existing, customized project to
the latest conventions without destroying the user's changes.** This is
fundamentally a three-way merge between the defaults the project was
originally generated from (*base*), the user's current project
(*current*), and the latest defaults (*new*). Doing it well requires:

- **provenance** - recording, inside each generated project, what
  dralithus produced and from which version, so a later update knows the
  *base* to diff against (conceptually like tracking the template a
  project was generated from);
- **structural / semantic merges** for known formats (TOML, INI,
  `pyproject.toml`) rather than blind line-based patching; and
- a **foundation-model fallback** for genuinely ambiguous
  reconciliations - where the user customized a region the new defaults
  also changed - to propose a merge that preserves intent.

Every such update must itself be transactional and idempotent, which is
why the two-phase-commit foundation is a prerequisite, not a polish
item. This capability - transactional, customization-preserving,
AI-assisted project update - is a strategic goal, not a near-term
deliverable; the near-term work builds the simpler create path first.

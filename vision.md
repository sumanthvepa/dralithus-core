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

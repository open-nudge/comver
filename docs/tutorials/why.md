<!--
SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
SPDX-FileContributor: szymonmaszke <github@maszke.co>

SPDX-License-Identifier: Apache-2.0
-->

# Why `comver`?

`comver` aims to address several common issues with pure
[semver](https://semver.org/), as discussed in articles like
[Semantic Versioning Will Not Save You](https://hynek.me/articles/semver-will-not-save-you/)

> [!NOTE]
> `comver` __is not__ and does __not claim to be__
> a silver bullet for versioning challenges. Its goal
> is to improve upon current practices where possible.

See the points below to understand the movitation and how
`comver` might help!

## Strict `semver` adherence

Projects that strictly follow `semver`
(e.g. [`setuptools`](https://pypi.org/project/setuptools/)
with over `80` major releases) exhibit:

- Informative versioning that communicates
    breaking changes and new features, but…
- Frequent releases can dilute the perceived
    importance of each version to end users

## Reluctance to version changes

Conversely, some projects are hesitant to increment versions, especially
the `major` version, due to the perceived impact. This is especially visible
when moving from `0.x.y` to `1.x.y`, which implies stability.

In some cases, breaking changes may go unacknowledged to avoid triggering
a `major` version bump, as it is often directly associated with
major announcements or formal release cycles.

## Irrelevant commits for the user

Large projects often include changes unrelated to the core
functionality such as CI workflows, tooling updates, or formatting adjustments.

Changes like `fix: unify formatting` __do not__ impact the behavior of the
software but may still influence versioning in traditional schemes.

## `comver` as an alternative

`comver` provides a more focused and automated approach to versioning:

- Enables strict `semver` adherence, with versions calculated
    directly from commits
- Supports a "double versioning scheme":
    use `comver` for the software version, while maintaining a separate,
    tag-oriented versioning scheme (e.g., via [python-semantic-release](https://python-semantic-release.readthedocs.io/en/latest/))
    for broader release messaging
- Allows simplified user-facing (public release) versions (e.g. `1`, `2`, `3`)
    while keeping a detailed internal version for software consistency
- Filters out irrelevant commits (e.g., those modifying `.github` workflows)
- Supports separate `comver` configurations for different parts of the project
    (e.g., CI, packages, documentation) (__WIP__)

> [!TIP]
> See [configuration](configuration.md) for practical setup examples.

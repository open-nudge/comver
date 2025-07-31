<!--
SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
SPDX-FileContributor: szymonmaszke <github@maszke.co>

SPDX-License-Identifier: Apache-2.0
-->

# Configuration

This section describes how to configure `comver`.

> [!IMPORTANT]
> You can configure `comver` via `.comver.toml`
> or under the `[tool.comver]` section in `pyproject.toml`.

Example of `pyproject.toml` configuration:

```toml
[tool.comver]
# Only commits to these paths are considered
path_includes = [
  "src/*",
  "pyproject.toml",
]

# Commits done by GitHub Actions bot are discarded
author_name_excludes = [
  "github-actions[bot]",
]
```

Equivalent `.comver.toml` configuration
(no `[tool.comver]` section needed):

```toml
# Only commits to these paths are considered
path_includes = [
  "src/*",
  "pyproject.toml",
]

# Commits done by GitHub Actions bot are discarded
author_name_excludes = [
  "github-actions[bot]",
]
```

## Options

> [!WARNING]
> All includes and excludes accept regex lists,
> evaluated using Python's [`re.match`](https://docs.python.org/3/library/re.html#re.match)
> (they are interpreted as raw strings, i.e., prefixed with `r`).

> [!WARNING]
> `excludes` always take precedence over `includes`

> [!WARNING]
> Conditions are composed via `and` (e.g. has to be a specific
> author `and` contain specific message)

You can configure the following options:

- `message_includes`:
    List of regex patterns to include commits based on message.
    __Default:__ all messages are included.
- `message_excludes`:
    List of regex patterns to exclude commits based on message.
    __Default:__ no messages are excluded.
- `path_includes`:
    Regex list matching changed file paths to include commits.
    __Default:__ every commit is included, no matter the changed file(s).
- `path_excludes`:
    Regex list matching changed file paths to exclude commits.
    __Default:__ no file is excluded based on path.
- `author_name_includes`:
    Regex list to include commits based on author name.
    __Default:__ commits from all authors are included.
- `author_name_excludes`:
    Regex list to exclude commits based on author name.
    __Default:__ no commits are excluded based on author.
- `author_email_includes`:
    Regex list to include commits based on author email.
    __Default:__ commits from all emails are included.
- `author_email_excludes`:
    Regex list to exclude commits based on author email.
    __Default:__ no commits are excluded based on email.
- `major_regexes`:
    List of regex patterns that indicate a MAJOR version bump.
    __Default:__ `fix(...)!:`/`feat(...)!:`
    or `BREAKING CHANGE` anywhere in the commit message.
- `minor_regexes`:
    List of regex patterns that indicate a MINOR version bump.
    __Default__: commits starting with `feat(...):`
- `patch_regexes`:
    List of regex patterns that indicate a PATCH version bump.
    __Default__: commits starting with `fix(...):`
- `unrecognized_message`:
    Action to take if the message doesn’t match any
    `major`, `minor`, or `patch` patterns.
    __Options__: `"ignore"` (default) or `"error"`.

## Suggested

This subsection includes example configurations for common use cases.

> [!IMPORTANT]
> The list is growing. Feel free to [open a pull request](https://github.com/open-nudge/comver/pulls)
> with yours configuration ideas!

> [!NOTE]
> These examples are modular; feel free to mix and match
> based on your project’s needs.

## Python package

For Python packages with a /src/<PACKAGE> layout, the following is recommended:

```toml
[tool.comver]
path_includes = [
  "src/*",
  "pyproject.toml",
]
```

> [!NOTE]
> Any change to `pyproject.toml` currently affects versioning.
> More granular handling is being considered on the [`ROADMAP`](../ROADMAP.md).

## Exclude `bot` commits

To ignore commits made by bots (e.g. GitHub Actions or [`renovatebot`](https://github.com/renovatebot/renovate)):

```toml
[tool.comver]
author_excludes = [
  ".*\[bot\].*",
]
```

> [!NOTE]
> This pattern excludes any author containing `[bot]`,
> which might unintentionally filter out human contributors.

## Github-style commit skips

GitHub allows skipping [skipping CI workflows](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs)
with commit annotations like [skip ci].

Similarly, comver supports skipping version bumps via:

```toml
[tool.comver]
message_excludes = [
  ".*\[no version\].*",
  ".*\[skip version\].*",
  ".*\[version skip\].*",
]
```

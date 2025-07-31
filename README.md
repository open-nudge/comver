<!--
SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
SPDX-FileContributor: szymonmaszke <github@maszke.co>

SPDX-License-Identifier: Apache-2.0
-->

# comver

<!-- mkdocs remove start -->

<!-- vale off -->

<!-- pyml disable-num-lines 30 line-length-->

<p align="center">
    <em>Commit-based semantic versioning — verifiable, immutable, and tag-free.</em>
</p>

<div align="center">

<a href="https://pypi.org/project/comver">![PyPI - Python Version](https://img.shields.io/pypi/v/comver?style=for-the-badge&label=release&labelColor=grey&color=blue)
</a>
<a href="https://pypi.org/project/comver">![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fopen-nudge%2Fcomver%2Fmain%2Fpyproject.toml&style=for-the-badge&label=python&labelColor=grey&color=blue)
</a>
<a href="https://opensource.org/licenses/Apache-2.0">![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=for-the-badge)
</a>
<a>![Coverage Hardcoded](https://img.shields.io/badge/coverage-100%25-green?style=for-the-badge)
</a>
<a href="https://scorecard.dev/viewer/?uri=github.com/open-nudge/comver">![OSSF-Scorecard Score](https://img.shields.io/ossf-scorecard/github.com/open-nudge/comver?style=for-the-badge&label=OSSF)
</a>

</div>

<p align="center">
✨ <a href="#features">Features</a>
🚀 <a href="#quick-start">Quick start</a>
📚 <a href="https://open-nudge.github.io/comver">Documentation</a>
🤝 <a href="#contribute">Contribute</a>
👍 <a href="https://github.com/open-nudge/comver/blob/main/ADOPTERS.md">Adopters</a>
📜 <a href="#legal">Legal</a>
</p>
<!-- vale on -->

______________________________________________________________________

<!-- mkdocs remove end -->

## Features

__comver__ is a tool for calculating __[semantic versioning](https://semver.org/)__
of your project __using only commit messages__ - no tags required!

- __Separation of concerns__: versioning focuses on technical aspects,
    not marketing. You can now use tags solely for communication.
- __Highly configurable__: include only relevant commits by filtering via
    `message`, `author`, `email`, __or even commit path__.
- __Immutable__: version is calculated directly from the commit history.
    Tags can now be used more meaningfully (e.g., to mark a major milestone
    or release).
- __Batteries-included__: integrate with [pdm](https://pdm-project.org/en/latest/),
    [Hatch](https://hatch.pypa.io/latest/) or [uv](https://docs.astral.sh/uv/).
- __Verifiable__: verify that a specific version was generated from a
    given commit chain - more resistant to tampering like
    [dependency substitution attacks](https://docs.aws.amazon.com/codeartifact/latest/ug/dependency-substitution-attacks.html)

## Why?

Semantic versioning based on Git tags has a few limitations:

- Teams may avoid bumping the `major` version due to the
    perceived weight of the change.
    [__Double versioning scheme__](https://open-nudge.github.io/comver/tutorials/why);
    one version for technical changes, another for public releases is
    a viable mitigation.
- Not all commits are relevant for release versions
    (e.g., CI changes, bot updates, or tooling config),
    yet many schemes count them in. With filtering, `comver` can exclude
    such noise.
- Tags are mutable by default and can be re-pointed. By calculating the version
    based on commits, and combining it with the commit
    `sha` and a config `checksum`, you get verifiable and reproducible results.

## Quick start

> [!NOTE]
> You can jump straight into the action and check `comver`
> [tutorials](https://open-nudge.github.io/comver/tutorials).

### Installation

```sh
> pip install comver
```

### Calculate version

> [!IMPORTANT]
> Although written in Python, comver can be used
> with any programming language.

If your commits follow the Conventional Commits format, run:

```sh
> comver calculate
```

This will output a version string in the `MAJOR.MINOR.PATCH` format:

```sh
23.1.3 # Output
```

> [!IMPORTANT]
> You can use [plugins](https://open-nudge.github.io/comver/tutorials/plugins)
> to integrate this versioning scheme
> with [`pdm`](https://github.com/pdm-project/pdm) or
> [`hatch`](https://github.com/pypa/hatch). More below!

<!-- mkdocs remove start -->

### Configuration

Configuration can be done either in `pyproject.toml`
(recommended for `Python`-first project) or in a separate
`.comver.toml` file (recommended for non-python projects):

<table>
<tr>
<th>pyproject.toml</th>
<th>.comver.toml</th>
</tr>
<tr>
<td>

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

</td>
<td>

```toml
# No [tool.comver] needed here
# Source only commits considered
path_includes = [
  "src/*",
]

# Commits messages with [no version] are discarded
message_excludes = [
  ".*\[no version\].*",
  ".*\[skipversion\].*",
]
```

</td>
</tr>
</table>

> [!TIP]
> See suggested configuration examples [here](https://open-nudge.github.io/comver/tutorials/configuration)

### Integrations

> [!NOTE]
> You can use `comver` with [`uv`](https://github.com/astral-sh/uv)
> by selecting the appropriate [build backend](https://docs.astral.sh/uv/concepts/build-backend/#choosing-a-build-backend),
> such as `hatchling`.

To integrate `comver` with [`pdm`](https://pdm-project.org/en/latest/)
or [`hatch`](https://hatch.pypa.io/latest/) add the following to
your `pyproject.toml`:

<table>
<tr>
<th>PDM</th>
<th>Hatch</th>
</tr>
<tr>
<td>

```toml
# Register comver for the build process
[build-system]
build-backend = "pdm.backend"

requires = [
  "pdm-backend",
  "comver>=0.1.0",
]

# Setup versioning for PDM
[tool.pdm.version]
source = "call"
getter = "comver.plugin:pdm"

# Comver-specific settings
[tool.comver]
...
```

</td>
<td>

```toml
# Register comver for the build process
[build-system]
build-backend = "hatchling.build"

requires = [
  "comver>=0.1.0",
  "hatchling",
]

# Setup versioning for Hatchling
[tool.hatch.version]
source = "comver"


# Comver-specific settings
[tool.comver]
...
```

</td>
</tr>
</table>

> [!TIP]
> See more in the [documentation](https://open-nudge.github.io/comver/tutorials/plugins)

### Verification

To verify that a version was produced from the same Git tree and configuration,
first use the calculate command with additional flags:

```sh
comver calculate --sha --checksum
```

This outputs three space-separated values:

```sh
<VERSION> <SHA> <CHECKSUM>
```

> [!TIP]
> Append `--format=json` for machine-friendly output

Before the next release provide these values to the `comver verify`
to ensure the version was previously generated from the
same codebase and config:

```sh
comver verify <VERSION> <SHA> <CHECKSUM>
```

If inconsistencies are found, you'll receive feedback, for example:

> Provided checksum and the checksum of configuration do not match.

> [!TIP]
> Explore verification workflows in the [tutorials](https://open-nudge.github.io/comver/tutorials/verification)

<!-- md-dead-link-check: off -->

## Contribute

We welcome your contributions! Start here:

- [Code of Conduct](/CODE_OF_CONDUCT.md)
- [Contributing Guide](/CONTRIBUTING.md)
- [Roadmap](/ROADMAP.md)
- [Changelog](/CHANGELOG.md)
- [Report security vulnerabilities](/SECURITY.md)
- [Open an Issue](https://github.com/open-nudge/comver/issues)

## Legal

- This project is licensed under the _Apache 2.0 License_ - see
    the [LICENSE](/LICENSE.md) file for details.
- This project is copyrighted by _open-nudge_ - the
    appropriate copyright notice is included in each file.

<!-- mkdocs remove end -->

<!-- md-dead-link-check: on -->

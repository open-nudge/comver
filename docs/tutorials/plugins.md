<!--
SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
SPDX-FileContributor: szymonmaszke <github@maszke.co>

SPDX-License-Identifier: Apache-2.0
-->

# Plugins

> `comver` includes plugins to simplify integration with popular
> Python packaging tools. Contributions adding support for other
> tools are welcome!

> [!NOTE]
> Core `comver` configuration is described in the
> [configuration](configuration.md) section.

## [PDM](https://pdm-project.org/en/latest/)

To integrate with `PDM`, update your `pyproject.toml` as follows:

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

## [Hatch](https://hatch.pypa.io/latest/)

To integrate with Hatch, edit your `pyproject.toml` as follows:

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

> [!NOTE]
> You may alternatively place comver settings under
> `[tool.hatch.version]`, which will take precedence if specified.

## [uv](https://docs.astral.sh/uv/)

`uv` may use `hatchling` as its build backend, so the configuration
is identical as for `hatch`.

See the [`uv` documentation](https://docs.astral.sh/uv/concepts/build-backend/#choosing-a-build-backend)
for details on setting the build backend.

<!--
SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
SPDX-FileContributor: szymonmaszke <github@maszke.co>

SPDX-License-Identifier: Apache-2.0
-->

# Tests of comver

- `test_smoke.py` - generic
    [smoke tests](https://grafana.com/blog/2024/01/30/smoke-testing/)
    to check if the package is importable
- `test_version.py` - version calculation from messages and `git` history
- `test_cli.py` - `comver calculate` and `comver verify` subcommands
- `test_plugin.py` - `pdm` and `hatchling` integrations

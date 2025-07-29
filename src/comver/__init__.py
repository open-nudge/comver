# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""comver official documentation.

This section of documentation should be mainly considered by people who:

- are curious how the project works under the hood
- want to provide integration of `comver` with third part tooling.

> [!CAUTION]
> Check out guidelines and tutorials for information about CLI/plugin
> as this is a more common starting point.

"""

from __future__ import annotations

from comver import error, plugin, type_definitions
from comver._version import Version, _version

__version__ = _version
"""Current comver version."""

__all__: list[str] = [
    "Version",
    "__version__",
    "error",
    "plugin",
    "type_definitions",
]

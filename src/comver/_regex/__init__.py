# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Regex related internal functionalities."""

from __future__ import annotations

from comver._regex import match, semantic
from comver._regex._process import process

__all__ = [
    "match",
    "process",
    "semantic",
]

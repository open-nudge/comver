# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Type definitions of `comver`.

> [!IMPORTANT]
> This module is a simplification for `typing` of complex types
> and should be used __eventually__ by third party plugin developers.

"""

from __future__ import annotations

import re

from collections.abc import Iterable

StringOrPattern = str | re.Pattern[str]
"""Either `string` or compiled `re.Pattern`."""

StringsOrPatterns = Iterable[StringOrPattern]
"""Iterable of `StringOrPattern`."""

OptionalStringsOrPatterns = Iterable[StringOrPattern] | None
"""Iterable of `StringOrPattern` or `None`."""

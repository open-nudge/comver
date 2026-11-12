# SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Compilation/performance related regex functionalities."""

from __future__ import annotations

import re
import typing

if typing.TYPE_CHECKING:
    from comver.type_definitions import OptionalStringsOrPatterns


def process(regexes: OptionalStringsOrPatterns, default: str | None = None) -> re.Pattern[str] | None:
    """Cached compilation of multiple regexes.

    > [!IMPORTANT]
    > `compile` should use internal cache, see
    > here: https://github.com/python/cpython/blob/v3.12.0/Lib/re/__init__.py#L271-L329

    `None` is used, as the regex matching might be slow
    and is avoided whenever possible throughout
    the whole `comver`.

    Args:
        regexes:
            Regexes (strings or compiled patterns) which should
            be compiled together (if provided).
        default:
            Default regex, if provided.

    Returns:
        Single compiled regex matching any of `regexes`, `default`
        regex if no `regexes` were provided or `None` if neither was.

    """
    if not regexes:
        if default is None:
            return None
        return re.compile(default)
    patterns = (r.pattern if isinstance(r, re.Pattern) else r for r in regexes)
    return re.compile(r"(" + r"|".join(rf"({p})" for p in patterns) + r")")

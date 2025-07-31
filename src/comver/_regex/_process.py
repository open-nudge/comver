# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Compilation/performance related regex functionalities."""

from __future__ import annotations

import re
import typing

if typing.TYPE_CHECKING:
    from comver.type_definitions import OptionalStringsOrPatterns


def process(
    regexes: OptionalStringsOrPatterns, default: str | None = None
) -> re.Pattern[str] | None:
    """Cached compilation of multiple regexes.

    > [!IMPORTANT]
    > `compile` should use internal cache, see
    > here: https://github.com/python/cpython/blob/v3.12.0/Lib/re/__init__.py#L271-L329

    `None` is used, as the regex matching might be slow
    and is avoided whenever possible throughout
    the whole `comver`.

    Arguments:
        regexes:
            Regexes which should be compiled together
            (if provided).
        default:
            Default regex, if provided.
    """
    if not regexes:
        if default is None:
            return None
        return re.compile(default)
    return re.compile(r"(" + r"|".join(rf"({r})" for r in regexes) + r")")

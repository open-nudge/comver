# SPDX-FileCopyrightText: © 2025 nosludge <https://github.com/nosludge>
# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Regex matching functions."""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import re

    import git


def item(
    what: str, include: re.Pattern[str] | None, exclude: re.Pattern[str] | None
) -> bool:
    """Check if the `what` is included based on the `include` and `exclude`.

    > [!IMPORTANT]
    > Empty `include` are treated as include-everything.

    > [!IMPORTANT]
    > Empty `exclude` are treated as include-everything.

    > [!IMPORTANT]
    > Exclude regexes take precedence over include regexes.

    Args:
        what:
            The string to check.
        include:
            The regex to include the string.
        exclude:
            The regex to exclude.

    Returns:
        True if the `what` is included, False otherwise.

    """
    return (include is None or include.search(what) is not None) and (
        exclude is None or exclude.search(what) is None
    )


def path(
    commit: git.Commit,
    include: re.Pattern[str] | None,
    exclude: re.Pattern[str] | None,
) -> bool:
    """Check if the commit touched the file based regexes.

    Note:
        Empty `include` are treated as include-everything.
        Empty `exclude` are treated as include-everything as well.

    Note:
        exclude regexes take precedence over include regexes.

    Args:
        commit:
            The commit to check.
        include:
            The regex to include the file.
        exclude:
            The regex to exclude the file.

    Returns:
        True if the commit touched the file, False otherwise.
    """
    if include is None and exclude is None:
        return True

    return not commit.diff() or any(
        item(diff.a_path, include, exclude) if diff.a_path else True
        for diff in commit.diff()
    )

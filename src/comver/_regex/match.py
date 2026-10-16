# SPDX-FileCopyrightText: © 2025 nosludge <https://github.com/nosludge>
# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Regex matching functions."""

from __future__ import annotations

import typing

import git

if typing.TYPE_CHECKING:
    import re


def item(
    what: str, include: re.Pattern[str] | None, exclude: re.Pattern[str] | None
) -> bool:
    """Check if the `what` is included based on the `include` and `exclude`.

    Note:
        Empty `include` are treated as include-everything.

    Note:
        Empty `exclude` are treated as include-everything.

    Warning:
        Exclude regexes take precedence over include regexes.

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

    Note:
        Empty `exclude` are treated as include-everything.

    Note:
        Commits which did not change any path are always included.

    Warning:
        Exclude regexes take precedence over include regexes.

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

    # Compare against the first parent (root commits against an empty tree),
    # not against the working tree (default of `commit.diff()`)
    diffs = commit.diff(commit.parents[0] if commit.parents else git.NULL_TREE)
    return not diffs or any(
        item(p, include, exclude)
        for diff in diffs
        for p in {diff.a_path, diff.b_path}
        if p is not None
    )

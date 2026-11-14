# SPDX-FileCopyrightText: © 2025 nosludge <https://github.com/nosludge>
# SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Regex matching functions."""

from __future__ import annotations

import pathlib
import typing

import git

from comver._regex._process import process

if typing.TYPE_CHECKING:
    import re

    from comver.type_definitions import OptionalStringsOrPatterns


# enq: filters are separate, optional and keyword-only options
def commit(  # noqa: PLR0913
    what: git.Commit,
    *,
    path_includes: OptionalStringsOrPatterns = None,
    path_excludes: OptionalStringsOrPatterns = None,
    author_name_includes: OptionalStringsOrPatterns = None,
    author_name_excludes: OptionalStringsOrPatterns = None,
    author_email_includes: OptionalStringsOrPatterns = None,
    author_email_excludes: OptionalStringsOrPatterns = None,
) -> bool:
    """Check whether to include a given commit.

    Args:
        what:
            Commit to verify.
        path_includes:
            Path regexes against which the commit is included.
            Default: All paths are included.
        path_excludes:
            Path regexes against which the commit is excluded.
            Default: No paths are excluded.
        author_name_includes:
            Commit author names regexes against
            which the commit is included.
            Default: All names are included.
        author_name_excludes:
            Commit author names regexes against
            which the commit is excluded.
            Default: No names are excluded.
        author_email_includes:
            Commit author email regexes against
            which the commit is included.
            Default: All emails are included.
        author_email_excludes:
            Commit author email regexes against
            which the commit is excluded.
            Default: No emails are excluded.

    Returns:
        `True` if the commit should be included, `False` otherwise.

    """
    return (
        _author(what.author.name, author_name_includes, author_name_excludes)
        and _author(what.author.email, author_email_includes, author_email_excludes)
        and path(what, process(path_includes), process(path_excludes))
    )


def item(what: str, include: re.Pattern[str] | None, exclude: re.Pattern[str] | None) -> bool:
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
    diffs = commit.diff(_base(commit))
    return not diffs or any(
        item(p, include, exclude) for diff in diffs for p in {diff.a_path, diff.b_path} if p is not None
    )


def _base(commit: git.Commit) -> git.Commit | git.DiffConstants:
    """Return what the commit's changes should be compared against.

    Args:
        commit:
            The commit whose changes are compared.

    Returns:
        The first parent of the commit or an empty tree for root commits.

    """
    if not commit.parents:
        return git.NULL_TREE
    # Shallow clones keep parent SHAs but not the parent objects;
    # boundary commits are treated as roots, like `git log` does
    shallow = pathlib.Path(commit.repo.common_dir, "shallow")
    if shallow.is_file() and commit.hexsha in shallow.read_text().split():
        return git.NULL_TREE
    return commit.parents[0]


def _author(
    what: str | None,
    includes: OptionalStringsOrPatterns,
    excludes: OptionalStringsOrPatterns,
) -> bool:
    """Optionally match commit author's data against includes and excludes.

    Important:
        `None` is considered as matching.

    Args:
        what:
            Author's name or email to be matched.
        includes:
            Optional list of includes.
        excludes:
            Optional list of excludes.

    Returns:
        `True` if the variable matches the constraints.

    """
    # enq: git cannot create commits without author name or email (defensive)
    if what is None:  # pragma: no cover
        return True
    return item(what, process(includes), process(excludes))

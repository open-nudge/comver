# SPDX-FileCopyrightText: © 2025 nosludge <https://github.com/nosludge>
# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Semantic versioning related regexes."""

from __future__ import annotations

import re
import typing

from comver._regex._process import process

if typing.TYPE_CHECKING:
    from comver.type_definitions import OptionalStringsOrPatterns

Key = typing.TypeVar("Key")

Semantic = tuple[Key, re.Pattern[str] | None]
Major = Semantic[typing.Literal["major"]]
Minor = Semantic[typing.Literal["minor"]]
Patch = Semantic[typing.Literal["patch"]]

StringOrPattern = str | re.Pattern[str]


def components(
    major_regexes: OptionalStringsOrPatterns,
    minor_regexes: OptionalStringsOrPatterns,
    patch_regexes: OptionalStringsOrPatterns,
) -> tuple[Major, Minor, Patch]:
    """Grouped semantic versioning regexes.

    This allows iteration over all necessary components
    with one function.

    Args:
        major_regexes:
            The regexes by which the major version is found.
            Default: From config OR matches `feat!:` and `fix!:`
            messages OR `BREAKING CHANGE` anywhere in the message.
        minor_regexes:
            The regex for the minor version.
            Default: From config OR matches messages starting with `feat:`.
        patch_regexes:
            The regex for the patch version.
            Default: From config OR matches messages starting with `fix:`.

    Returns:
        Dictionary mapping element of semantic versioning to the regex.

    """
    return (
        ("major", major(major_regexes)),
        ("minor", minor(minor_regexes)),
        ("patch", patch(patch_regexes)),
    )


def major(regexes: OptionalStringsOrPatterns) -> re.Pattern[str] | None:
    """Return compiled `major` regex.

    Args:
        regexes:
            Specified `major` version element regexes,
            if any.

    Returns:
        Compiled regular expression (either default or provided).

    """
    return process(regexes, r".*BREAKING CHANGE.*|^(feat|fix)(\(.*?\))?!: .*")


def minor(regexes: OptionalStringsOrPatterns) -> re.Pattern[str] | None:
    """Return compiled `mior` regex.

    Args:
        regexes:
            Specified `minor` version element regexes,
            if any.

    Returns:
        Compiled regular expression (either default or provided).

    """
    return process(regexes, "^feat(\\(.*?\\))?: .*")


def patch(regexes: OptionalStringsOrPatterns) -> re.Pattern[str] | None:
    """Return compiled `patch` regex.

    Args:
        regexes:
            Specified `patch` version element regexes,
            if any.

    Returns:
        Compiled regular expression (either default or provided).

    """
    return process(regexes, "^fix(\\(.*?\\))?: .*")

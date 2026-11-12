# SPDX-FileCopyrightText: © 2025 nosludge <https://github.com/nosludge>
# SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Semantic versioning related regexes."""

from __future__ import annotations

import typing

from comver._regex._process import process

if typing.TYPE_CHECKING:
    from comver.type_definitions import OptionalPattern, OptionalStringsOrPatterns


def components(
    major_regexes: OptionalStringsOrPatterns,
    minor_regexes: OptionalStringsOrPatterns,
    patch_regexes: OptionalStringsOrPatterns,
) -> tuple[OptionalPattern, OptionalPattern, OptionalPattern]:
    """Grouped semantic versioning regexes.

    This allows iteration over all necessary components
    with one function.

    Args:
        major_regexes:
            The regexes finding the `major` version.
        minor_regexes:
            The regexes finding the `minor` version.
        patch_regexes:
            The regexes finding the `patch` version.

    Returns:
        `major`, `minor` and `patch` regexes (in this order).

    """
    return major(major_regexes), minor(minor_regexes), patch(patch_regexes)


def major(regexes: OptionalStringsOrPatterns) -> OptionalPattern:
    """Return compiled `major` regex.

    Args:
        regexes:
            Specified `major` version element regexes.

    Returns:
        Compiled regular expression (either default or provided).

    """
    return process(regexes, r".*BREAKING CHANGE.*|^(feat|fix)(\(.*?\))?!: .*")


def minor(regexes: OptionalStringsOrPatterns) -> OptionalPattern:
    """Return compiled `minor` regex.

    Args:
        regexes:
            Specified `minor` version element regexes.

    Returns:
        Compiled regular expression (either default or provided).

    """
    return process(regexes, "^feat(\\(.*?\\))?: .*")


def patch(regexes: OptionalStringsOrPatterns) -> OptionalPattern:
    """Return compiled `patch` regex.

    Args:
        regexes:
            Specified `patch` version element regexes.

    Returns:
        Compiled regular expression (either default or provided).

    """
    return process(regexes, "^fix(\\(.*?\\))?: .*")

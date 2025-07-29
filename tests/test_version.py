# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Test `comver.Version` class."""

from __future__ import annotations

import typing

import pytest

from hypothesis import given
from hypothesis import strategies as st

import comver


def create_version(commit_types: list[str]) -> comver.Version:
    """Create version based on commit types.

    Args:
        commit_types:
            List of commit types. Contain only `fix` and `feat` types
            with optional `!` at the end.

    Returns:
        Version based on commit types.

    """
    version = pytest.ComverVersionTester()  # pyright: ignore [reportAttributeAccessIssue]
    for commit_type in commit_types:
        version.bump(commit_type)

    return comver.Version(*version.to_tuple())  # pyright: ignore [reportUnknownArgumentType]


@pytest.mark.parametrize("major_regexes", (None, (".*", "bbb")))
@pytest.mark.parametrize("minor_regexes", (None, (".*", "ccc")))
@pytest.mark.parametrize("patch_regexes", (None, (".*", "ddd")))
@given(commit_types=st.lists(st.sampled_from(["fix", "feat", "feat!", "fix!"])))
def test_version_from_messages(
    commit_types: list[str],
    major_regexes: tuple[str] | None,
    minor_regexes: tuple[str] | None,
    patch_regexes: tuple[str] | None,
) -> None:
    """Test `comver.Version.from_messages` method.

    This test focuses on regular expressions arguments and order
    of commit evaluation (from `major`, through `minor` to `patch`).

    > [!IMPORTANT]
    > This test function was separated from `test_plugin`
    > as it is __way faster__ to run than creating actual `git` repos.

    Args:
        commit_types:
            List of commit types. Contain only `fix` and `feat` types
            with optional `!` at the end.
        major_regexes:
            Regular expression for major version.
        minor_regexes:
            Regular expression for minor version.
        patch_regexes:
            Regular expression for patch version.
    """
    messages = [f"{commit_type}: bla bla bla" for commit_type in commit_types]
    test_version = create_version(commit_types)

    version = comver.Version()
    # Iterate over iterator to get the last element
    for version in comver.Version.from_messages(  # noqa: B007
        messages,
        major_regexes=major_regexes,
        minor_regexes=minor_regexes,
        patch_regexes=patch_regexes,
    ):
        pass

    # ".*" swallows all commits, all should be major versions
    if major_regexes:
        assert version.major == len(messages)
    # We can only assert something about major if minor swallows all
    elif not major_regexes and minor_regexes:
        assert version.major == test_version.major
    # If none are specified, it should be a standard version
    else:
        assert comver.Version.from_string(str(test_version)) == version


def test_unrecognized_commit_type() -> None:
    """Test `comver.Version.bump` method with unrecognized commit type."""
    with pytest.raises(comver.error.MessageUnrecognizedError):
        _ = comver.Version.from_message(
            "placeholder",
            unrecognized_message="error",
        )


def test_hash() -> None:
    """Smoke test __hash__ function."""
    assert hash(
        comver.Version.from_string(
            "0.1.0",
        )
    ) == hash(comver.Version(0, 1, 0))


@pytest.mark.parametrize("other", ("0.27.31", comver.Version(0, 0, 23)))
def test_comparison(other: str | comver.Version) -> None:
    """Generic test of version comparisons.

    > [!IMPORTANT]
    > This test goes through implemented `__lt__` and `__eq__`
    > at the same time due to functools.total_ordering
    > which uses under the hood `__le__` and `__eq__`

    """
    assert other <= comver.Version.from_string(
        "0.31.27",
    )


@pytest.mark.parametrize(
    ("other", "error"),
    (
        ("HakunaMatata", comver.error.VersionFormatError),
        ("0.1.245b+02435", comver.error.VersionNotNumericError),
        (12, NotImplementedError),
    ),
)
def test_incorrect_comparison(
    other: typing.Any, error: type[Exception]
) -> None:
    """Generic test of version comparisons.

    > [!IMPORTANT]
    > This test goes through implemented `__lt__` and `__eq__`
    > at the same time due to functools.total_ordering
    > which uses under the hood `__le__` and `__eq__`

    """
    with pytest.raises(error):
        assert other == comver.Version.from_string(
            "0.31.27",
        )

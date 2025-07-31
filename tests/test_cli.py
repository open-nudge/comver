# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Smoke test CLI entrypoint."""

from __future__ import annotations

import typing

import pytest

from comver import _cli, _subcommand


@pytest.mark.parametrize("format", ("line", "json"))
@pytest.mark.parametrize("sha", (True, False))
@pytest.mark.parametrize("checksum", (True, False))
def test_smoke_calculate(
    format: typing.Literal["line", "json"],  # noqa: A002
    sha: bool,  # noqa: FBT001
    checksum: bool,  # noqa: FBT001
) -> None:
    """Smoke test calculate subcommand.

    Args:
        format:
            Either `line` or `json` corresponding to `calculate`'s
            CLI arguments.
        sha:
            Whether to output `sha` as well.
        checksum:
            Whether to output `checksum` as well.

    """
    args = ["calculate", "--format", format]
    if sha:
        args.append("--sha")
    if checksum:
        args.append("--checksum")
    try:
        _cli.main(args)
    except SystemExit as e:
        assert e.code == 0  # noqa: PT017


@pytest.mark.parametrize(
    ("version", "sha", "checksum", "code"),
    (
        # Neither version, nor sha, nor checksum  will exist in this git tree
        (
            "99999.99999.99999",
            "randomShaNonExistent",
            "randomChecksumNonExistent",
            1,
        ),
        # Neither version, nor sha will exist in this git tree
        (
            "99999.99999.99999",
            "randomShaNonExistent",
            _subcommand._calculate(pytest.ComverCalculateArgs).split()[2],  # noqa: SLF001  # pyright: ignore [reportUnknownArgumentType, reportAttributeAccessIssue]
            1,
        ),
        # Version 0.0.1 is guaranteed to exist in this project
        (
            "0.0.1",
            "randomShaNonExistent",
            _subcommand._calculate(pytest.ComverCalculateArgs).split()[2],  # noqa: SLF001  # pyright: ignore [reportUnknownArgumentType, reportAttributeAccessIssue]
            1,
        ),
        # Obtain current commit sha (which is guaranteed to be within the tree)
        # Assign random version which has small chance of real life occurrence
        # Should return 1 but for different reasons
        (
            "99999.99999.99999",
            *_subcommand._calculate(pytest.ComverCalculateArgs).split()[1:],  # noqa: SLF001  # pyright: ignore [reportUnknownArgumentType, reportAttributeAccessIssue]
            1,
        ),
        # Calculate current version and its sha counterpart
        # Verify should not return an error in such case
        (*(_subcommand._calculate(pytest.ComverCalculateArgs).split()), 0),  # noqa: SLF001  # pyright: ignore [reportUnknownArgumentType, reportAttributeAccessIssue]
    ),
)
def test_verify(
    version: str,
    sha: str,
    checksum: str,
    code: typing.Literal[0, 1],
) -> None:
    """Test `verify` command.

    Actual exit command will be compared to the one assumed by the test.

    Args:
        version:
            Version to test.
        sha:
            Sha to verify version against.
        checksum:
            Checksum of the config file.
        code:
            Either `0` (proper execution) or `1` (error).

    """
    try:
        _cli.main(["verify", version, sha, checksum])
    except SystemExit as e:
        assert e.code == code  # noqa: PT017

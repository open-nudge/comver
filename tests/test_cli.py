# SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Smoke test CLI entrypoint."""

from __future__ import annotations

import argparse
import typing

import pytest

from comver import _cli, _subcommand

# enq: pytest requires the test_ prefix, which pynudger counts as a shared word
# noqa-file: PYNUDGER43

# enq: tests verify the output of the private implementation directly
_VERSION, _SHA, _CHECKSUM = _subcommand._calculate(  # noqa: SLF001
    argparse.Namespace(sha=True, checksum=True, format="line"),
).split()
"""Current version, its commit sha and configuration checksum."""


@pytest.mark.parametrize("output", ("line", "json"))
@pytest.mark.parametrize("sha", (True, False))
@pytest.mark.parametrize("checksum", (True, False))
def test_calculate(
    output: typing.Literal["line", "json"],
    *,
    sha: bool,
    checksum: bool,
) -> None:
    """Smoke test calculate subcommand.

    Args:
        output:
            Either `line` or `json` corresponding to `calculate`'s
            `--format` CLI argument.
        sha:
            Whether to output `sha` as well.
        checksum:
            Whether to output `checksum` as well.

    """
    args = ["calculate", "--format", output]
    if sha:
        args.append("--sha")
    if checksum:
        args.append("--checksum")
    with pytest.raises(SystemExit) as e:
        _cli.main(args)
    assert e.value.code == 0


@pytest.mark.parametrize(
    ("version", "sha", "checksum", "code"),
    (
        # Checksum of the configuration does not match
        (_VERSION, _SHA, "randomChecksumNonExistent", 1),
        # Neither version, nor sha will exist in this git tree
        ("99999.99999.99999", "randomShaNonExistent", _CHECKSUM, 1),
        # Sha is within the tree, but corresponds to a different version
        ("99999.99999.99999", _SHA, _CHECKSUM, 1),
        # Version is within the tree, but sha is not
        (_VERSION, "randomShaNonExistent", _CHECKSUM, 1),
        # Current version and its sha counterpart verify successfully
        (_VERSION, _SHA, _CHECKSUM, 0),
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
    with pytest.raises(SystemExit) as e:
        _cli.main(["verify", version, sha, checksum])
    assert e.value.code == code

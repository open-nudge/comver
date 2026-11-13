# SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Smoke test CLI entrypoint."""

from __future__ import annotations

import argparse
import typing

import git

import pytest

from comver import _cli, _subcommand

if typing.TYPE_CHECKING:
    import pathlib

# enq: pytest requires the test_ prefix, which pynudger counts as a shared word
# noqa-file: PYNUDGER43


@pytest.fixture(autouse=True)
# enq: autouse fixture is used (implicitly) by every test in this module
def _repository(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: PYNUDGER37
    """Run the CLI within a new repository with a single `feat` commit.

    History of this repository cannot be used, CI checks out only
    the (shallow) merge commit, which `[tool.comver]` may exclude
    (e.g. if it does not change `src`), leaving no commit sha.

    Args:
        tmp_path:
            Temporary directory where the repository is created.
        monkeypatch:
            Changes the working directory to the repository.

    """
    # Closed, as its `git cat-file` processes outlive the test otherwise
    with git.Repo.init(tmp_path) as repo:
        _ = repo.index.commit("feat: add feature")
    monkeypatch.chdir(tmp_path)


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
        (None, None, "randomChecksumNonExistent", 1),
        # Neither version, nor sha will exist in this git tree
        ("99999.99999.99999", "randomShaNonExistent", None, 1),
        # Sha is within the tree, but corresponds to a different version
        ("99999.99999.99999", None, None, 1),
        # Version is within the tree, but sha is not
        (None, "randomShaNonExistent", None, 1),
        # Current version and its sha counterpart verify successfully
        (None, None, None, 0),
    ),
)
def test_verify(
    version: str | None,
    sha: str | None,
    checksum: str | None,
    code: typing.Literal[0, 1],
) -> None:
    """Test `verify` command.

    Actual exit command will be compared to the one assumed by the test.

    Args:
        version:
            Version to test (`None` for the current one).
        sha:
            Sha to verify version against (`None` for the current one).
        checksum:
            Checksum of the config file (`None` for the current one).
        code:
            Either `0` (proper execution) or `1` (error).

    """
    # enq: tests verify the output of the private implementation directly
    current = _subcommand._calculate(  # noqa: SLF001
        argparse.Namespace(sha=True, checksum=True, format="line"),
    ).split()
    arguments = [
        given if given is not None else calculated
        for given, calculated in zip((version, sha, checksum), current, strict=True)
    ]
    with pytest.raises(SystemExit) as e:
        _cli.main(["verify", *arguments])
    assert e.value.code == code

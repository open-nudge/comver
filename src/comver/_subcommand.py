# SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Subcommands of the CLI `comver`."""

from __future__ import annotations

import collections
import hashlib
import json
import sys
import typing

import loadfig

from comver._version import Version, VersionCommit

if typing.TYPE_CHECKING:
    import argparse

# enq: subcommands share names with their (separately tested) implementations
# noqa-file: PYNUDGER43


def calculate(args: argparse.Namespace) -> int:
    """Calculate semantic versioning based on commit messages.

    Outputs version and (optionally) sha of a commit
    related to this version (the last one in commit chain).

    This output allows to later compare git trees and inferred
    versions if necessary.

    Args:
        args:
            Arguments from the CLI.

    Returns:
        Exit code of the command (always `0`).

    """
    # enq: printing the version is the purpose of this CLI subcommand
    print(_calculate(args))  # noqa: T201
    return 0


def verify(args: argparse.Namespace) -> int:
    """Verify commit sha and inferred version match.

    Given `version` (as string, e.g. `1.2.3`) and
    commit sha verify whether this version was created
    from this commit chain.

    Args:
        args:
            Arguments from the CLI.

    Returns:
        Exit code of the command (`1` on error, `0` on success).

    """
    return _verify(args)


def _calculate(args: argparse.Namespace) -> str:
    """Implementation of calculate cli command.

    Args:
        args:
            Arguments from the CLI.

    Returns:
        Either formatted dictionary (if `args.json`) string
        or space separated "version sha". `sha` component
        is optional based on `args.sha` flag.

    """
    last = VersionCommit()
    for output in Version.from_git_configured():
        last = output

    fields = {
        "version": f"{last.version}",
        "sha": last.commit.hexsha if last.commit is not None else None,
        "checksum": _checksum_config(),
    }
    requested = {"version": True, "sha": args.sha, "checksum": args.checksum}

    if args.format == "line":
        return " ".join(f"{value}" for key, value in fields.items() if requested[key])

    return json.dumps(
        {key: value for key, value in fields.items() if requested[key] and value is not None},
        indent=4,
    )


def _verify(args: argparse.Namespace) -> int:
    """Verify commit sha and inferred version match.

    Multiple commits may share the same version (e.g. commits
    excluded by their message), hence the commit with the specified
    `sha` is searched for and its version is compared.

    Warning:
        This subcommand also outputs messages for the end user

    Args:
        args:
            Arguments from the CLI.

    Returns:
        Code status of the command (`1` for error, `0`
        on successful verification).

    """
    if args.checksum != _checksum_config():
        # enq: user facing CLI error message
        print(  # noqa: T201
            "Provided checksum and the checksum of configuration do not match.",
            file=sys.stderr,
        )
        return 1

    versions = {
        output.commit.hexsha: f"{output.version}"
        for output in Version.from_git_configured()
        if output.commit is not None
    }
    version = versions.get(args.sha)

    if version is None:
        # enq: user facing CLI error message
        print(  # noqa: T201
            f"Specified sha: `{args.sha}` (version: `{args.version}`) was not found in the git tree",
            file=sys.stderr,
        )
        return 1

    if version != args.version:
        # enq: user facing CLI error message
        print(  # noqa: T201
            f"Specified sha: `{args.sha}` corresponds to version: `{version}`, "
            f"while expected version is: `{args.version}`",
            file=sys.stderr,
        )
        return 1

    return 0


def _checksum_config() -> str:
    """Get checksum of config.

    Returns:
        Checksum of subconfig.

    """
    config = collections.defaultdict(lambda: None, loadfig.config("comver"))
    keys = [
        "message_includes",
        "message_excludes",
        "path_includes",
        "path_excludes",
        "author_name_includes",
        "author_name_excludes",
        "author_email_includes",
        "author_email_excludes",
        "major_regexes",
        "minor_regexes",
        "patch_regexes",
        "unrecognized_message",
    ]

    # Get only relevant sections of the dict
    subconfig = {k: config[k] for k in keys}
    stringified = json.dumps(subconfig, sort_keys=True)
    return hashlib.sha256(stringified.encode()).hexdigest()

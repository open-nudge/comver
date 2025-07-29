# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Subcommands of the CLI `comver`."""

from __future__ import annotations

import json
import sys
import typing

from comver._version import Version, VersionCommit

if typing.TYPE_CHECKING:
    import argparse


def calculate(args: argparse.Namespace) -> typing.NoReturn:
    """Calculate semantic versioning based on commit messages.

    Outputs version and (optionally) sha of a commit
    related to this version (the last one in commit chain).

    This output allows to later compare git trees and inferred
    versions if necessary.

    Args:
        args:
            Arguments from the CLI.

    """
    print(_calculate(args))  # noqa: T201
    sys.exit(0)


def verify(args: argparse.Namespace) -> typing.NoReturn:
    """Verify commit sha and inferred version match.

    Given `version` (as string, e.g. `1.2.3`) and
    commit sha verify whether this version was created
    from this commit chain.

    Args:
        args:
            Arguments from the CLI.

    """
    sys.exit(_verify(args))


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
    version = VersionCommit()
    for version in Version.from_git_configured():  # noqa: B007
        pass

    sha = version.commit.hexsha if version.commit is not None else None

    version = str(version.version)

    if args.format == "line":
        if args.sha:
            return f"{version} {sha}"
        return version

    output = {"version": str(version)}
    if args.sha and isinstance(sha, str):
        output["sha"] = sha

    return json.dumps(output, indent=4)


def _verify(args: argparse.Namespace) -> bool:
    """Verify commit sha and inferred version match.

    > [!CAUTION]
    > This subcommand also outputs messages for the end user

    Args:
        args:
            Arguments from the CLI.

    Returns:
        Code status of the command (`True` for error, `False`
        on successful verification).

    """
    for output in Version.from_git_configured():
        version, commit = output.version, output.commit

        sha = commit.hexsha if commit is not None else None

        if args.version == version:
            if sha is not None and sha == args.sha:
                return False

            print(  # noqa: T201
                f"Specified version: `{args.version}` has sha: `{sha}`, while expected sha is: `{args.sha}`",
                file=sys.stderr,
            )
            return True

        if args.sha == sha:
            print(  # noqa: T201
                f"Specified sha: `{args.sha}` corresponds to version: `{version}`, while expected version is: `{args.version}`",  # noqa: E501
                file=sys.stderr,
            )
            return True

    print(  # noqa: T201
        f"Neither specified sha: `{args.sha}` nor its corresponding version: `{args.version}` was found in the git tree",  # noqa: E501
        file=sys.stderr,
    )
    return True

# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Parser of the `comver` CLI."""

from __future__ import annotations

import argparse
import textwrap

from comver._version import _version


def root() -> argparse.ArgumentParser:
    """Create and return the top-level CLI parser.

    This parser defines all available subcommands and any global flags.
    Each subcommand is parsed with its corresponding arguments and stored
    in the `subcommand` attribute for later dispatching.

    Returns:
        The argument parser configured with all CLI subcommands.

    """
    parser = argparse.ArgumentParser(
        description="Tool CLI with support for subcommands.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    _ = parser.add_argument(
        "--version",
        action="version",
        version=_version,
        help="Show the tool version and exit.",
    )

    subparsers = parser.add_subparsers(
        dest="subcommand",
        required=True,
    )
    _calculate(subparsers)
    _verify(subparsers)

    return parser


def _calculate(subparsers) -> None:  # noqa: ANN001  # pyright: ignore [reportUnknownParameterType, reportMissingParameterType]
    """Create `calculate` subcommand subparser.

    Args:
        subparsers:
            Object where this subparser is registered.

    """
    parser = subparsers.add_parser(
        "calculate",
        description=textwrap.dedent("""\
        Calculate semantic version based on commits.

        NOTE:

            - This command runs on the git-tree found in current
            working directory.
            - Each value (e.g. version and sha) is space separated
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--format",
        choices=["line", "json"],
        default="line",
        help="Format of the output (default: line, each output space separated)",
    )

    parser.add_argument(
        "--sha",
        action="store_true",
        required=False,
        help="Return sha of the commit related to the version",
    )


def _verify(subparsers) -> None:  # noqa: ANN001  # pyright: ignore [reportUnknownParameterType, reportMissingParameterType]
    """Create `verify` subcommand subparser.

    Args:
        subparsers:
            Object where this subparser is registered.

    """
    parser = subparsers.add_parser(
        "verify",
        description=textwrap.dedent("""
        Verify version consistency.

        NOTE:

            - This command runs on the git-tree found in current
            working directory.
            - You can feed the output of the `calculate` command here
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "version",
        help="Version to check (e.g. `1.37.21`)",
    )

    parser.add_argument(
        "sha",
        help="Sha of the commit to compare against",
    )

    return parser

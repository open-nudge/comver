# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""CLI entrypoint of comver."""

from __future__ import annotations

import sys

from comver import _parser, _subcommand


def main(args: list[str] | None = None) -> None:
    """Command-line entry point of the `comver`.

    Parses arguments and dispatches execution to the appropriate subcommand
    based on user input. If no arguments are provided explicitly, the arguments
    from `sys.argv[1:]` are used instead.

    Args:
        args:
            CLI arguments passed, if any (used mainly during testing).

    """
    parsed_args = _parser.root().parse_args(args)
    subcommand = getattr(_subcommand, parsed_args.subcommand, None)

    # Cannot be `None`, but left to make pyright feel at peace
    if subcommand is None:  # pragma: no cover
        print(  # noqa: T201
            "Unknown command chosen",
            file=sys.stderr,
        )
        sys.exit(1)

    subcommand(parsed_args)

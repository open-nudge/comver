# SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""CLI entrypoint of comver."""

from __future__ import annotations

import sys

from comver import _parser, _subcommand

# enq: CLI entrypoint (registered as a script), it only dispatches subcommands
# noqa-file: PYNUDGER46

_SUBCOMMANDS = {
    "calculate": _subcommand.calculate,
    "verify": _subcommand.verify,
}
"""Mapping of CLI subcommand names to their implementations."""


def main(args: list[str] | None = None) -> None:
    """Command-line entry point of the `comver`.

    Parses arguments and dispatches execution to the appropriate subcommand
    based on user input. If no arguments are provided explicitly, the arguments
    from `sys.argv[1:]` are used instead.

    Exits with the code returned by the subcommand.

    Args:
        args:
            CLI arguments passed, if any (used mainly during testing).

    """
    parsed_args = _parser.root().parse_args(args)
    sys.exit(_SUBCOMMANDS[parsed_args.subcommand](parsed_args))

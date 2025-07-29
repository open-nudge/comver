# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Shared tests functionality.

Each shared functionality should be placed in this file and
added to the `pytest` namespace (later reused by other tests).

"""

from __future__ import annotations

import argparse
import dataclasses
import typing

import pytest


@dataclasses.dataclass
class ComverVersionTester:
    """Stripped-down version tester for `comver`.

    Attributes:
        major:
            Major version number.
        minor:
            Minor version number.
        patch:
            Patch version

    """

    major: int = 0
    minor: int = 0
    patch: int = 0

    def to_tuple(self) -> tuple[int, int, int]:
        """Return version as tuple."""
        return self.major, self.minor, self.patch

    def bump(
        self, commit_type: typing.Literal["fix", "feat", "feat!", "fix!"]
    ) -> None:
        """Bump version based on commit type.

        Args:
            commit_type:
                Commit type to bump version for.

        """
        # Either of these may not be ran during fuzz-testing
        if commit_type in {"fix!", "feat!"}:  # pragma: no cover
            self.major += 1
            self.minor, self.patch = 0, 0
        elif commit_type == "feat":  # pragma: no cover
            self.minor += 1
            self.patch = 0
        elif commit_type == "fix":  # pragma: no cover
            self.patch += 1


pytest.ComverVersionTester = ComverVersionTester  # pyright: ignore [reportAttributeAccessIssue]
"""Hack making `ComverVersionTester` globally test available."""

ARGS = argparse.Namespace()
ARGS.sha = True
ARGS.format = "line"
pytest.ComverCalculateArgs = ARGS  # pyright: ignore [reportAttributeAccessIssue]
"""Hack making CLI args for calculate subcommand globally available."""

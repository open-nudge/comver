# SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Shared tests functionality."""

from __future__ import annotations

import typing

import pytest

import comver

if typing.TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


@pytest.fixture(scope="session", autouse=True)
def _git_isolation() -> Iterator[None]:
    """Detach test repositories from the repository running the tests.

    Exported by git to hooks (`git commit` -> prek -> pytest); if left out,
    they redirect `git` in temporary test repositories to the outer repository
    (see `git rev-parse --local-env-vars`).

    > Session scoped, as function scoped fixtures fail
    > `hypothesis` health checks.

    Yields:
        Nothing, environment is restored afterwards.

    """
    envs = (
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_COMMON_DIR",
        "GIT_CONFIG",
        "GIT_DIR",
        "GIT_GRAFT_FILE",
        "GIT_IMPLICIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_NO_REPLACE_OBJECTS",
        "GIT_OBJECT_DIRECTORY",
        "GIT_PREFIX",
        "GIT_REPLACE_REF_BASE",
        "GIT_SHALLOW_FILE",
        "GIT_WORK_TREE",
    )

    with pytest.MonkeyPatch.context() as monkeypatch:
        for name in envs:
            monkeypatch.delenv(name, raising=False)
        yield


class Oracle:
    """Expected version calculator (independent of `comver`)."""

    def __call__(self, commit_types: Iterable[str]) -> comver.Version:
        """Calculate the expected version.

        Args:
            commit_types:
                Types of the consecutive commits
                (one of `fix`, `feat`, `fix!` or `feat!`).

        Returns:
            Version after all of the commits.

        """
        major, minor, patch = 0, 0, 0
        for commit_type in commit_types:
            if commit_type.endswith("!"):
                major, minor, patch = major + 1, 0, 0
            elif commit_type == "feat":
                minor, patch = minor + 1, 0
            else:
                patch += 1
        return comver.Version(major, minor, patch)


@pytest.fixture(scope="session")
def expected() -> Oracle:
    """Expected version calculator (independent of `comver`).

    Returns:
        Callable calculating version from consecutive commit types.

    """
    return Oracle()

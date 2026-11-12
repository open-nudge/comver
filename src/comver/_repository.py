# SPDX-FileCopyrightText: © 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""`git` repository access."""

from __future__ import annotations

import contextlib

import git


def repository(repository: str | git.Repo | None) -> contextlib.AbstractContextManager[git.Repo]:
    """Open the repository, closing it on exit only if opened here.

    `git.Repo` keeps persistent `git cat-file` processes (running within
    the repository) until closed, which keeps its directory busy
    (e.g. Windows cannot remove it), see
    https://github.com/gitpython-developers/GitPython/issues/387

    Args:
        repository:
            Path to the repository, its parent directories are searched
            if `None`. Passed `git.Repo` is left open (owned by the caller).

    Returns:
        Context manager providing the repository.

    """
    if isinstance(repository, git.Repo):
        return contextlib.nullcontext(repository)
    return git.Repo(repository, search_parent_directories=repository is None)

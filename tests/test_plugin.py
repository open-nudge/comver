# SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Test `comver.plugin` module tests."""

from __future__ import annotations

import pathlib
import shutil
import stat
import tempfile
import typing
import uuid

import git

import pytest

from hypothesis import given, settings
from hypothesis import strategies as st

import comver

if typing.TYPE_CHECKING:
    from collections.abc import Callable

# enq: pytest requires the test_ prefix, which pynudger counts as a shared word
# noqa-file: PYNUDGER43

Strings = tuple[str, ...]
"""Regexes passed as parameters."""

CommitTypes = list[str]
"""Types of the consecutive commits."""


@st.composite
def repository(draw: st.DrawFn, *, n_commits: int = 10) -> tuple[str, CommitTypes]:
    """Create repository with `n_commits` commits.

    Commits will have the same text, but different scope,
    all are changing the same file over and over.

    Args:
        draw:
            Hypothesis draw function.
        n_commits:
            Number of commits to create.

    Returns:
        Path to the repository and types of its consecutive commits.
    """
    directory = pathlib.Path(tempfile.mkdtemp()).resolve()
    file = directory / "file.txt"

    commit_types: list[str] = []
    # Closed, as its `git` processes keep the directory busy (Windows)
    with git.Repo.init(directory) as repo:
        for _ in range(n_commits):
            commit_type = draw(st.sampled_from(["fix", "feat", "feat!", "fix!"]))
            author = draw(st.sampled_from(["Alice", "Bob"]))
            email = draw(st.sampled_from(["alice@example.com", "bob@example.com"]))

            _ = file.write_text(f"{uuid.uuid4()}")
            _ = repo.index.add(file)
            _ = repo.index.commit(
                f"{commit_type}: bla bla bla [no version]",
                author=git.Actor(author, email),
            )
            commit_types.append(commit_type)

    return f"{directory}", commit_types


# enq: Windows-only (read-only files), exercised there by test_plugin
def _writable(  # pragma: no cover
    function: Callable[[str], object],
    path: str,
    _exception: BaseException,
) -> None:
    """Make `path` writable and retry its removal (`shutil.rmtree` handler).

    `git` stores objects as read-only files, which Windows refuses
    to delete (`PermissionError: [WinError 5] Access is denied`).
    If the retry fails, its error is raised.

    Args:
        function:
            Function which failed to remove `path` (e.g. `os.unlink`).
        path:
            Path which could not be removed.
        _exception:
            Exception raised by `function` (unused).

    """
    pathlib.Path(path).chmod(stat.S_IWRITE)
    _ = function(path)


def _hatchling(*, repository: str, **kwargs: Strings | None) -> str:
    """Dummy function unifying `hatchling` plugin interface with `pdm`.

    This allows for later usage in `pytest.mark.parametrize` in `test_plugin`
    function.

    Args:
        repository:
            Path to the repository given as a string
        **kwargs:
            Configuration passed to the plugin (akin to the one
            which would be passed from `[tool.hatch.version]`
            in `pyproject.toml` configuration).

    Returns:
        Version as string

    """
    return comver.plugin.ComverVersionSource(root=repository, config=kwargs).get_version_data()["version"]


@pytest.mark.parametrize("plugin", (comver.plugin.pdm, _hatchling))
@pytest.mark.parametrize("message_includes", (None, (".*", "whatever")))
@pytest.mark.parametrize("message_excludes", (None, (r".*\[no version\].*",)))
@pytest.mark.parametrize("path_includes", (None, (".*", "whatever")))
@pytest.mark.parametrize("path_excludes", (None, (".*", "whatever")))
@pytest.mark.parametrize("author_name_includes", (None, (".*", "whatever")))
@pytest.mark.parametrize("author_name_excludes", (None, ("Alice", "Bob")))
@pytest.mark.parametrize("author_email_includes", (None, (".*@example.com",)))
@pytest.mark.parametrize("author_email_excludes", (None, (".*@example.com",)))
@settings(max_examples=2)
@given(repository_commits=repository())
# enq: every comver filter is tested as a separate parameter
def test_plugin(  # noqa: PLR0913
    *,
    expected: Callable[..., comver.Version],
    plugin: Callable[..., str],
    message_includes: Strings | None,
    message_excludes: Strings | None,
    path_includes: Strings | None,
    path_excludes: Strings | None,
    author_name_includes: Strings | None,
    author_name_excludes: Strings | None,
    author_email_includes: Strings | None,
    author_email_excludes: Strings | None,
    repository_commits: tuple[str, CommitTypes],
) -> None:
    """Test `comver.plugin.pdm` function and `hatchling` plugin.

    Tests if plugins return correct version
    and whether regular expression based filtering works.

    See `comver.plugin.pdm` docs for more details.

    Args:
        expected:
            Expected version calculator (independent of `comver`).
        plugin:
            Plugin function
        message_includes:
            Commit message regexes against which the commit is included.
        message_excludes:
            Commit message regexes against which the commit is excluded.
        path_includes:
            Path regexes against which the commit is included.
        path_excludes:
            Path regexes against which the commit is excluded.
        author_name_includes:
            Commit author names regexes against
            which the commit is included.
        author_name_excludes:
            Commit author names regexes against
            which the commit is excluded.
        author_email_includes:
            Commit author email regexes against
            which the commit is included.
        author_email_excludes:
            Commit author email regexes against
            which the commit is excluded.
        repository_commits:
            Path to repository and types of its consecutive commits.

    """
    repository, commit_types = repository_commits
    version = plugin(
        message_includes=message_includes,
        message_excludes=message_excludes,
        path_includes=path_includes,
        path_excludes=path_excludes,
        author_name_includes=author_name_includes,
        author_name_excludes=author_name_excludes,
        author_email_includes=author_email_includes,
        author_email_excludes=author_email_excludes,
        repository=repository,
    )
    shutil.rmtree(repository, onexc=_writable)

    # Every commit changes the same file, hence path_excludes excludes them all
    excluded = author_name_excludes or author_email_excludes or message_excludes or path_excludes
    assert version == f"{comver.Version() if excluded else expected(commit_types)}"


@pytest.mark.parametrize("plugin", (comver.plugin.pdm, _hatchling))
def test_regexes(tmp_path: pathlib.Path, plugin: Callable[..., str]) -> None:
    """Plugins pass version bump regexes to `comver`.

    Args:
        tmp_path:
            Temporary directory where the repository is created.
        plugin:
            Plugin function

    """
    with git.Repo.init(tmp_path) as repo:
        for message in ("docs: add readme", "chore: update tooling"):
            _ = repo.index.commit(message)

    assert plugin(major_regexes=(".*",), repository=f"{tmp_path}") == "2.0.0"


def test_smoke_pdm() -> None:
    """Test `comver.plugin.pdm` function on current repository.

    This is a smoke test to check if `comver.plugin.pdm`
    function works on current repository.

    Parsing commits from this project is complex and requires the same work
    as the library itself, so we only check if the function runs without
    errors.

    """
    _ = comver.plugin.pdm()


def test_smoke_hatchling() -> None:
    """Smoke test `comver.plugin.ComverVersionSource` hook."""
    assert comver.plugin.ComverVersionSource == comver.plugin.hatch_register_version_source()


def test_set_version(tmp_path: pathlib.Path) -> None:
    """Setting the version via `hatchling` plugin is not supported.

    Args:
        tmp_path:
            Temporary directory used as project's root.

    """
    source = comver.plugin.ComverVersionSource(root=f"{tmp_path}", config={})
    with pytest.raises(NotImplementedError):
        source.set_version("1.0.0", {})

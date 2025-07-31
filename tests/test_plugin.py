# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

# pyright: reportUnusedCallResult=false

"""Test `comver.plugin` module tests."""

from __future__ import annotations

import pathlib
import shutil
import tempfile
import typing
import uuid

import git

import pytest

from hypothesis import given, settings
from hypothesis import strategies as st

import comver


@st.composite
def repository(
    draw: st.DrawFn, *, n_commits: int = 10
) -> tuple[str, comver.Version]:
    """Create repository with `n_commits` commits.

    Commits will have the same text, but different scope,
    all are changing the same file over and over.

    Args:
        draw:
            Hypothesis draw function.
        n_commits:
            Number of commits to create.

    Returns:
        Repository with `n_commits` commits.
    """
    directory = pathlib.Path(tempfile.mkdtemp())
    repo = git.Repo.init(directory)
    file = directory / "file.txt"

    version = pytest.ComverVersionTester()  # pyright: ignore [reportAttributeAccessIssue]

    for _ in range(n_commits):
        commit_type = draw(st.sampled_from(["fix", "feat", "feat!", "fix!"]))
        author = draw(st.sampled_from(["Alice", "Bob"]))
        email = draw(st.sampled_from(["alice@example.com", "bob@example.com"]))

        with file.open("w") as f:
            f.write(str(uuid.uuid4()))

        repo.index.add(file)
        repo.index.commit(
            f"{commit_type}: bla bla bla [no version]",
            author=git.Actor(author, email),
        )

        version.bump(commit_type)

    if repo.working_tree_dir is not None:
        return str(repo.working_tree_dir), comver.Version(*version.to_tuple())  # pyright: ignore [reportUnknownArgumentType]
    return (
        "",
        comver.Version(
            *version.to_tuple()  # pragma: no cover  # pyright: ignore [reportUnknownArgumentType]
        ),
    )


def _hatchling(repository: str, **kwargs: dict[str, list[str] | None]) -> str:
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
    return comver.plugin.ComverVersionSource(
        root=repository, config=kwargs
    ).get_version_data()["version"]


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
@given(repository_test_version=repository())
def test_plugin(  # noqa: PLR0913
    plugin: typing.Callable[..., str],  # Takes all arguments below
    message_includes: tuple[str, ...] | None,
    message_excludes: tuple[str, ...] | None,
    path_includes: tuple[str, ...] | None,
    path_excludes: tuple[str, ...] | None,
    author_name_includes: tuple[str, ...] | None,
    author_name_excludes: tuple[str, ...] | None,
    author_email_includes: tuple[str, ...] | None,
    author_email_excludes: tuple[str, ...] | None,
    repository_test_version: tuple[str, comver.Version],
) -> None:
    """Test `comver.plugin.pdm` function.

    Tests if `comver.plugin.pdm.git` function returns
    correct version and whether regular expression based filtering works.

    See `comver.plugin.pdm` docs for more details.

    Args:
        plugin:
            Plugin function
        message_includes:
            Commit message regexes against which the commit is included.
            Default: From config OR all paths are included.
        message_excludes:
            Commit message regexes against which the commit is excluded.
            Default: From config OR no paths are excluded.
        path_includes:
            Path regexes against which the commit is included.
            Default: From config OR all paths are included.
        path_excludes:
            Path regexes against which the commit is excluded.
            Default: From config OR no paths are excluded.
        author_name_includes:
            Commit author names regexes against
            which the commit is included.
            Default: From config OR all names are included.
        author_name_excludes:
            Commit author names regexes against
            which the commit is excluded.
            Default: From config OR no names are excluded.
        author_email_includes:
            Commit author email regexes against
            which the commit is included.
            Default: From config OR all emails are included.
        author_email_excludes:
            Commit author email regexes against
            which the commit is excluded.
            Default: From config OR no emails are excluded.
        repository_test_version:
            Path to repository and its corresponding version.

    """
    repository, test_version = repository_test_version
    comver_version = plugin(
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

    if author_name_excludes or author_email_excludes or message_excludes:
        assert comver_version == "0.0.0"
    # In case of path_excludes, we will get either 0.1.0, 1.0.0 or 0.0.1
    elif path_excludes:
        assert comver_version in (
            comver.Version(0, 1, 0),
            comver.Version(1, 0, 0),
            comver.Version(0, 0, 1),
        )
    else:
        assert comver_version == test_version

    shutil.rmtree(repository)


def test_smoke_pdm() -> None:
    """Test `comver.plugin.pdm` function on current repository.

    This is a smoke test to check if `comver.plugin.pdm`
    function works on current repository.

    Parsing commits from this project is complex and requires the same work
    as the library itself, so we only check if the function runs without
    errors.

    """
    comver.plugin.pdm()


def test_smoke_hatchling() -> None:
    """Smoke test `comver.plugin.ComverVersionSource` hook."""
    assert (
        comver.plugin.ComverVersionSource
        == comver.plugin.hatch_register_version_source()
    )

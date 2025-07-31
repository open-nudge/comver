# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Versioning related core functionality of `comver`.

This module is responsible for heavy-lifting with respect to:

- version calculations based on multiple factors (from `string`s,
    `git` commits etc.)
- filtering based on user/config provided info (e.g. exclusion of
    specific committer name)

Usually `Version.from_git_configured()` is an entrypoint one
should be interested in.

Important:
    Check out guidelines and tutorials for information about CLI/plugin
    usage and suggested configuration. This section should be of interest
    to people wanting to use the API directly (e.g. new integrations).

"""

from __future__ import annotations

import collections
import dataclasses
import functools
import typing

import git
import loadfig

from comver import _regex, error

if typing.TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from comver.type_definitions import OptionalStringsOrPatterns

from importlib.metadata import version

_version = version("comver")
"""Current comver version."""

del version

T = typing.TypeVar("T")


@functools.total_ordering
@dataclasses.dataclass(frozen=True)
class Version:
    """Immutable class creating and keeping commit-based semantic versioning.

    Tip:
        This class will likely be instantiated by one of creation
        `classmethod`s, these are ordered by an abstraction level
        and the higher ups are composed of from the ones below them.

    Warning:
        This class is immutable, generator methods
        __will return new instances__.

    Attributes:
        major:
            The major version.
        minor:
            The minor version.
        patch:
            The patch version.
    """

    major: int = 0
    minor: int = 0
    patch: int = 0

    # Add commit message includes and commit message excludes
    @classmethod
    def from_git_configured(  # noqa: PLR0913
        cls,
        message_includes: OptionalStringsOrPatterns = None,
        message_excludes: OptionalStringsOrPatterns = None,
        path_includes: OptionalStringsOrPatterns = None,
        path_excludes: OptionalStringsOrPatterns = None,
        author_name_includes: OptionalStringsOrPatterns = None,
        author_name_excludes: OptionalStringsOrPatterns = None,
        author_email_includes: OptionalStringsOrPatterns = None,
        author_email_excludes: OptionalStringsOrPatterns = None,
        major_regexes: OptionalStringsOrPatterns = None,
        minor_regexes: OptionalStringsOrPatterns = None,
        patch_regexes: OptionalStringsOrPatterns = None,
        unrecognized_message: typing.Literal["ignore", "error"] | None = None,
        repository: str | git.Repo | None = None,
    ) -> Iterator[VersionCommit]:
        r"""Yield version and its respective commit.

        Important:
            This `classmethod`'s arguments, if not provided, will be
            inferred from `[tool.comver]` section in `pyproject.toml`
            (see [loadfig](https://github.com/open-nudge/loadfig)
            for more information)

        Example configuration (`pyproject.toml` in your project's git root):

        ```toml
        [tool.comver]
        # All commits will be included EXCEPT the ones with matching scopes
        # e.g. ("feat: add versioning [no version]")
        # Note: These are raw strings
        message_excludes = [
            ".*\[no version\].*",
            ".*\[skip version\].*",
            ".*\[version skip\].*",
        ]
        # Only changes to the src/* folder count or `pyproject.toml`
        # For version calculations
        path_includes = [
            "src/*",
            "pyproject.toml",
        ]

        # Commits done by GitHub bot are excluded from versioning
        author_name_excludes = [
            "github-actions[bot]",
        ]
        ```

        Example usage:

        ```python
        import comver

        # Every value taken from the configuration (if available)
        for output in comver.Version.git_configured():
            print(output.commit.hexsha, output.version)
        ```

        Commit messages are used to calculate versions based on the
        regexes (`major_regexes`, `minor_regexes` and `patch_regexes`).

        Tip:
            You can also configure this function via `.comver.toml`
            instead of `pyproject.toml`, in such case
            remove the `[tool.comver]` header, rest stays the same.

        Warning:
            `*_exclude` regexes take precedence over `*_include` regexes,
            the `*_include` regexes are checked first, then the `*_exclude`
            regexes might disinclude the `*_include` match

        Warning:
            `author_name`, `author_email` and `path` exclusions
            __will exclude them from output__ (unlike message based
            filtering). If the commit does not match it will not be yielded.

        Warning:
            Message based filtering will not change the version
            (the same will be returned),
            __but the Version-Commit pair will be returned__.

        Args:
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
            major_regexes:
                The regexes by which the major version is found.
                Default: From config OR matches `feat!:` and `fix!:`
                messages OR `BREAKING CHANGE` anywhere in the message.
            minor_regexes:
                The regex for the minor version.
                Default: From config OR matches messages starting with `feat:`.
            patch_regexes:
                The regex for the patch version.
                Default: From config OR matches messages starting with `fix:`.
            unrecognized_message:
                The behavior for unrecognized messages. It can be
                either "exclude" or "error".
                Default: From config OR "ignore"
            repository:
                The `git` repository.
                Default: From config OR will be searched
                in the parent directories.

        Yields:
            Version and its respective commit

        """
        config = collections.defaultdict(lambda: None, loadfig.config("comver"))

        yield from cls.from_git(
            message_includes=message_includes or config["message_includes"],
            message_excludes=message_excludes or config["message_excludes"],
            path_includes=path_includes or config["path_includes"],
            path_excludes=path_excludes or config["path_excludes"],
            author_name_includes=author_name_includes
            or config["author_name_includes"],
            author_name_excludes=author_name_excludes
            or config["author_name_excludes"],
            author_email_includes=author_email_includes
            or config["author_email_includes"],
            author_email_excludes=author_email_excludes
            or config["author_email_excludes"],
            major_regexes=major_regexes or config["major_regexes"],
            minor_regexes=minor_regexes or config["minor_regexes"],
            patch_regexes=patch_regexes or config["patch_regexes"],
            unrecognized_message=unrecognized_message
            or config["unrecognized_message"],
            repository=repository,
        )

    @classmethod
    def from_git(  # noqa: PLR0913
        cls,
        message_includes: OptionalStringsOrPatterns = None,
        message_excludes: OptionalStringsOrPatterns = None,
        path_includes: OptionalStringsOrPatterns = None,
        path_excludes: OptionalStringsOrPatterns = None,
        author_name_includes: OptionalStringsOrPatterns = None,
        author_name_excludes: OptionalStringsOrPatterns = None,
        author_email_includes: OptionalStringsOrPatterns = None,
        author_email_excludes: OptionalStringsOrPatterns = None,
        major_regexes: OptionalStringsOrPatterns = None,
        minor_regexes: OptionalStringsOrPatterns = None,
        patch_regexes: OptionalStringsOrPatterns = None,
        unrecognized_message: typing.Literal["ignore", "error"] | None = None,
        repository: str | git.Repo | None = None,
    ) -> Iterator[VersionCommit]:
        """Yield version and its respective commit.

        Commit messages are used to calculate versions based on the
        regexes (`major_regexes`, `minor_regexes` and `patch_regexes`).

        Example usage:

        ```python
        import comver

        # Will not take commits done by anyone with @foo.com email
        # into the account when creating versions
        for output in comver.Version.from_git(
            author_email_excludes=(r".*@foo.com",)
        ):
            print(output.commit.hexsha, output.version)
        ```

        Warning:
            `author_name`, `author_email` and `path` exclusions
            __will exclude them from output__ (unlike message based
            filtering). If the commit does not match it will not be yielded.

        Warning:
            Message based filtering will not change the version
            (the same will be returned),
            __but the Version-Commit pair will be returned__.

        Warning:
            `*_exclude` regexes take precedence over `*_include` regexes,
            the `*_include` regexes are checked first, then the `*_exclude`
            regexes might disinclude the `*_include` match

        Args:
            message_includes:
                Commit message regexes against which the commit is included.
                Default: All paths are included.
            message_excludes:
                Commit message regexes against which the commit is
                excluded. Default: No paths are excluded.
            path_includes:
                Path regexes against which the commit is included.
                Default: All paths are included.
            path_excludes:
                Path regexes against which the commit is excluded.
                Default: No paths are excluded.
            author_name_includes:
                Commit author names regexes against
                which the commit is included.
                Default: All names are included.
            author_name_excludes:
                Commit author names regexes against
                which the commit is excluded.
                Default: No names are excluded.
            author_email_includes:
                Commit author email regexes against
                which the commit is included.
                Default: All emails are included.
            author_email_excludes:
                Commit author email regexes against
                which the commit is excluded.
                Default: No emails are excluded.
            major_regexes:
                The regexes by which the major version is found.
                Default: Commit messages starting with `feat!:` and `fix!:`
                OR `BREAKING CHANGE` anywhere in the message.
            minor_regexes:
                The regex for the minor version.
                Default: Messages starting with `feat:`.
            patch_regexes:
                The regex for the patch version.
                Default: Matches messages starting with `fix:`.
            unrecognized_message:
                The behavior for unrecognized messages. It can be
                either "exclude" or "error".
                Default: "ignore"
            repository:
                The `git` repository.
                Default: Searched in the parent directories.

        Yields:
            Version and its respective commit

        """
        if isinstance(repository, str):
            repository = git.Repo(repository)
        if repository is None:
            repository = git.Repo(search_parent_directories=True)

        commits = [
            commit
            for commit in repository.iter_commits(reverse=True)
            if _include_commit(
                commit,
                path_includes,
                path_excludes,
                author_name_includes,
                author_name_excludes,
                author_email_includes,
                author_email_excludes,
            )
        ]

        for version, commit in zip(
            cls.from_messages(
                messages=(str(commit.message) for commit in commits),
                message_includes=message_includes,
                message_excludes=message_excludes,
                major_regexes=major_regexes,
                minor_regexes=minor_regexes,
                patch_regexes=patch_regexes,
                unrecognized_message=unrecognized_message,
            ),
            commits,
            strict=False,
        ):
            yield VersionCommit(version, commit)

    @classmethod
    def from_messages(  # noqa: PLR0913
        cls,
        messages: Iterable[str],
        message_includes: OptionalStringsOrPatterns = None,
        message_excludes: OptionalStringsOrPatterns = None,
        major_regexes: OptionalStringsOrPatterns = None,
        minor_regexes: OptionalStringsOrPatterns = None,
        patch_regexes: OptionalStringsOrPatterns = None,
        unrecognized_message: typing.Literal["ignore", "error"] | None = None,
    ) -> Iterator[Version]:
        """Yield versions from an iterable of messages.

        Warning:
            Every message will be returned, even if it is excluded
            (e.g. by `message_excludes` patterns). In such case
            the version __will not change__ (the same, previous one,
            is returned).

        Warning:
            `*_exclude` regexes take precedence over `*_include` regexes,
            the `*_include` regexes are checked first, then the `*_exclude`
            regexes might disinclude the `*_include` match

        Args:
            messages:
                Iterable containing messages from which versions
                are calculated.
            message_includes:
                Commit message regexes against which the commit is included.
                Default: All paths are included.
            message_excludes:
                Commit message regexes against which the commit is
                excluded. Default: No paths are excluded.
            major_regexes:
                The regexes by which the major version is found.
                Default: Commit messages starting with `feat!:` and `fix!:`
                OR `BREAKING CHANGE` anywhere in the message.
            minor_regexes:
                The regex for the minor version.
                Default: Messages starting with `feat:`.
            patch_regexes:
                The regex for the patch version.
                Default: Matches messages starting with `fix:`.
            unrecognized_message:
                The behavior for unrecognized messages. It can be
                either "exclude" or "error".
                Default: "ignore"

        Yields:
            Version (one for each message).
        """
        version = None

        for message in messages:
            version = cls.from_message(
                message,
                message_includes,
                message_excludes,
                major_regexes,
                minor_regexes,
                patch_regexes,
                unrecognized_message,
                version=version,
            )
            yield version

    @classmethod
    def from_message(  # noqa: PLR0913
        cls,
        message: str,
        message_includes: OptionalStringsOrPatterns = None,
        message_excludes: OptionalStringsOrPatterns = None,
        major_regexes: OptionalStringsOrPatterns = None,
        minor_regexes: OptionalStringsOrPatterns = None,
        patch_regexes: OptionalStringsOrPatterns = None,
        unrecognized_message: typing.Literal["ignore", "error"] | None = None,
        version: Version | None = None,
    ) -> Version:
        """Bump the version based on a message.

        Warning:
            The message will be returned, even if it should be excluded
            (e.g. by `message_excludes` patterns). In such case
            the version __will not change__ (the same, previous one,
            is returned).

        Args:
            message:
                Message from which the version is calculated.
            message_includes:
                Commit message regexes against which the commit is included.
                Default: All paths are included.
            message_excludes:
                Commit message regexes against which the commit is
                excluded. Default: No paths are excluded.
            major_regexes:
                The regexes by which the major version is found.
                Default: Commit messages starting with `feat!:` and `fix!:`
                OR `BREAKING CHANGE` anywhere in the message.
            minor_regexes:
                The regex for the minor version.
                Default: Messages starting with `feat:`.
            patch_regexes:
                The regex for the patch version.
                Default: Matches messages starting with `fix:`.
            unrecognized_message:
                The behavior for unrecognized messages. It can be
                either "exclude" or "error".
                Default: "ignore"
            version:
                Starting version from which a new version is calculated
                (version from which to bump). Default: `0.0.0` version.

        Raises:
            MessageUnrecognizedError: If the message is not recognized
                by any of the regexes and `unrecognized_message`
                is set to "error".

        Returns:
            Version corresponding to the message (possibly starting from
            initial version provided).
        """
        version = cls() if version is None else version

        if not _regex.match.item(
            what=message,
            include=_regex.process(message_includes),
            exclude=_regex.process(message_excludes),
        ):
            return version

        for semantic_component, regex in _regex.semantic.components(
            major_regexes, minor_regexes, patch_regexes
        ):
            if regex is not None and regex.match(message):
                return getattr(version, f"bump_{semantic_component}")()

        if unrecognized_message == "error":
            raise error.MessageUnrecognizedError(message)

        return version

    @classmethod
    def from_string(cls, version: str) -> Version:
        """Create a new version from a string.

        Version should be provided in `MAJOR.MINOR.PATCH` format.

        Args:
            version:
                The version as a string.

        Raises:
            VersionFormatError:
                When `version` does not comprise of `3` elements
                (e.g. `1.3` instead of `1.3.0`)
            VersionNotNumericError:
                When `version` elements are not numeric
                (e.g. `1.3.2a1` instead of `1.3.2`)

        Returns:
            Version object
        """
        try:
            major, minor, patch = version.split(".")
        except ValueError as e:
            raise error.VersionFormatError(version) from e
        try:
            return cls(
                major=int(major),
                minor=int(minor),
                patch=int(patch),
            )
        except ValueError as e:
            raise error.VersionNotNumericError(version) from e

    def bump_major(self) -> Version:
        """Bump the major version.

        Returns:
            Version with major bumped and the rest zeroed out.

        """
        return type(self)(1 + self.major, 0, 0)

    def bump_minor(self) -> Version:
        """Bump the minor version.

        Returns:
            Version with minor bumped and the patch zeroed out.

        """
        return type(self)(self.major, 1 + self.minor, 0)

    def bump_patch(self) -> Version:
        """Bump the patch version.

        Returns:
            Version with patch bumped.

        """
        return type(self)(self.major, self.minor, 1 + self.patch)

    def __str__(self) -> str:  # pyright: ignore [reportImplicitOverride]
        """Return the version as a string.

        Returns:
            String representation of version (e.g. `"1.37.21"`).

        """
        return f"{self.major}.{self.minor}.{self.patch}"

    def __hash__(self) -> int:  # pyright: ignore [reportImplicitOverride]
        """Unique hash of the version.

        Returns:
            Hashed major, minor and patch
        """
        return hash((self.major, self.minor, self.patch))

    def __eq__(self, other: object) -> bool:  # pyright: ignore [reportImplicitOverride]
        """Check if two versions are equal.

        Important:
            Versions are equal when their `major`, `minor`
            and `patch` are equal.

        Args:
            other:
                Object to compare against. Should be
                an instance of `Version` or string
                (e.g. `"2.3.7"`)

        Raises:
            NotImplementedError:
                Raised when comparing to object which is neither
                of `str`, nor `Version` type.

        Returns:
            Whether the object is equal

        """
        other = self._cast(other)

        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
        )

    def __lt__(self, other: object) -> bool:
        """Check if this version is smaller than `other`.

        Important:
            Version is smaller if its `major` is smaller
            or `fix` is smaller (and `major` equal) or `patch` is smaller
            (and `major` and `fix` equal)

        Args:
            other:
                Object to compare against. Should be
                an instance of `Version` or string
                (e.g. `"2.3.7"`).

        Raises:
            NotImplementedError:
                Raised when comparing to object which is neither
                of `str`, nor `Version` type.

        Returns:
            Whether the object is smaller

        """
        other = self._cast(other)

        return (
            self.major < other.major
            or (self.major == other.major and self.minor < other.minor)
            or (
                self.major == other.major
                and self.minor == other.minor
                and self.patch < other.patch
            )
        )

    def _cast(self, other: typing.Any) -> Version:
        """Cast `other` to `Version` (if possible).

        Raises:
            NotImplementedError:
                Raised when comparing to object which is neither
                of `str`, nor `Version` type.

        Returns:
            Casted version

        """
        if isinstance(other, str):
            return type(self).from_string(other)
        if not isinstance(other, Version):
            error = "Comparison of Version only works for strings (e.g. `2.37.1`) and other Version objects"
            raise NotImplementedError(error)

        return other


@dataclasses.dataclass(frozen=True)
class VersionCommit:
    """POD containing `Version` and its respective `git.Commit`.

    This container is returned from `git` related functionalities
    of `Version`.
    """

    version: Version = Version(0, 0, 0)
    commit: git.Commit | None = None


def _include_commit(  # noqa: PLR0913
    commit: git.Commit,
    path_includes: OptionalStringsOrPatterns = None,
    path_excludes: OptionalStringsOrPatterns = None,
    author_name_includes: OptionalStringsOrPatterns = None,
    author_name_excludes: OptionalStringsOrPatterns = None,
    author_email_includes: OptionalStringsOrPatterns = None,
    author_email_excludes: OptionalStringsOrPatterns = None,
) -> bool:
    """Check whether to include a given commit.

    Args:
        commit:
            Commit to verify.
        path_includes:
            Path regexes against which the commit is included.
            Default: All paths are included.
        path_excludes:
            Path regexes against which the commit is excluded.
            Default: No paths are excluded.
        author_name_includes:
            Commit author names regexes against
            which the commit is included.
            Default: All names are included.
        author_name_excludes:
            Commit author names regexes against
            which the commit is excluded.
            Default: No names are excluded.
        author_email_includes:
            Commit author email regexes against
            which the commit is included.
            Default: All emails are included.
        author_email_excludes:
            Commit author email regexes against
            which the commit is excluded.
            Default: No emails are excluded.

    """
    return (
        _maybe_match(
            commit.author.name, author_name_includes, author_name_excludes
        )
        and _maybe_match(
            commit.author.email, author_email_includes, author_email_excludes
        )
        and _regex.match.path(
            commit, _regex.process(path_includes), _regex.process(path_excludes)
        )
    )


def _maybe_match(
    variable: str | None,
    includes: OptionalStringsOrPatterns,
    excludes: OptionalStringsOrPatterns,
) -> bool:
    """Optionally match variable against includes and excludes.

    Important:
        `None` is considered as matching.

    Args:
        variable:
            Variable to be matched
        includes:
            Optional list of includes
        excludes:
            Optional list of excludes

    Returns:
        `True` if the variable matches the constraints.

    """
    # Escape hatch if commit's author name or email is missing
    # This situation is highly unlikely to happen
    if variable is None:  # pragma: no cover
        return True
    return _regex.match.item(
        variable, _regex.process(includes), _regex.process(excludes)
    )

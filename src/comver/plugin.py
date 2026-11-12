# SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Extensions and plugins integrating `comver` with third party systems.

Most of the extensions are tailored to the Python ecosystem, and its
package managers specifically.

__Currently supported third party tools:__

- [`pdm`](https://pdm-project.org/en/latest/) package manager.
- [`hatch`](https://hatch.pypa.io/latest/plugins/version-source/reference/)
    package manager.

Warning:
    Check out guidelines and tutorials for information about CLI/plugin
    usage and suggested configuration. This section should be of interest
    to people wanting to use the API directly (e.g. new integrations).

"""

from __future__ import annotations

import typing

from importlib.util import find_spec

from comver._version import Version, VersionCommit

if typing.TYPE_CHECKING:
    import git

    from comver.type_definitions import OptionalStringsOrPatterns


# enq: filters are separate, optional and keyword-only options
def pdm(  # noqa: PLR0913
    *,
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
) -> str:
    """Entrypoint for `pdm`'s `[tool.pdm.version]` `pyproject.toml` specifier.

    Example `pyproject.toml` usage:

    ```toml
    [build-system]
    build-backend = "pdm.backend"

    requires = [
        "comver>=2",
        "pdm-backend>=2",
    ]

    [tool.pdm.version]
    source = "call"
    getter = "comver.plugin:pdm"
    ```

    This function uses
    [`Version.from_git_configured`][comver._version.Version.from_git_configured]
    under the hood, __but only outputs the last yielded version `iterable`__.

    Tip:
        Plugin can be configured by `[tool.comver]` section.

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
            either "ignore" or "error".
            Default: From config OR "ignore"
        repository:
            The `git` repository.
            Default: Searched in the parent directories.

    Returns:
        Calculated version as string (compatible with `pdm` interface).

    """
    version = VersionCommit()
    for output in Version.from_git_configured(
        message_includes=message_includes,
        message_excludes=message_excludes,
        path_includes=path_includes,
        path_excludes=path_excludes,
        author_name_includes=author_name_includes,
        author_name_excludes=author_name_excludes,
        author_email_includes=author_email_includes,
        author_email_excludes=author_email_excludes,
        major_regexes=major_regexes,
        minor_regexes=minor_regexes,
        patch_regexes=patch_regexes,
        unrecognized_message=unrecognized_message,
        repository=repository,
    ):
        version = output

    return f"{version.version}"


# enq: tests always install the hatchling extra (hatchling is available)
if find_spec("hatchling"):  # pragma: no branch
    from hatchling.plugin import hookimpl
    from hatchling.version.source.plugin.interface import VersionSourceInterface

    # enq: class name is registered for hatchling (source = "comver")
    class ComverVersionSource(VersionSourceInterface):  # noqa: PYNUDGER43
        """Get the project version for the `hatchling` build backend.

        This class implements the `VersionSourceInterface` from Hatchling
        and allows integration of the `comver` plugin with Hatch-based
        projects.

        Tip:
            See [plugins](https://hatch.pypa.io/latest/plugins/version-source/reference/)
            for more information

        This function uses
        [`Version.from_git_configured`][comver._version.Version.from_git_configured]
        under the hood, __but only outputs the last version
        yielded from `iterable`__.

        > [!IMPORTANT]
        > Plugin can also be configured by `[tool.hatch.version]`, not only
        > `[tool.comver]`. The former takes precedence if both exist.

        """

        PLUGIN_NAME: str = "comver"

        @typing.override
        # enq: method name is required by hatchling's VersionSourceInterface
        def get_version_data(self) -> dict[str, str]:  # noqa: PYNUDGER4
            """Get the version data to be used by Hatchling.

            Returns:
                A dictionary with the resolved version string,
                under the "version" key.
            """
            version = VersionCommit()
            for output in Version.from_git_configured(
                message_includes=self.config.get("message_includes"),
                message_excludes=self.config.get("message_excludes"),
                path_includes=self.config.get("path_includes"),
                path_excludes=self.config.get("path_excludes"),
                author_name_includes=self.config.get("author_name_includes"),
                author_name_excludes=self.config.get("author_name_excludes"),
                author_email_includes=self.config.get("author_email_includes"),
                author_email_excludes=self.config.get("author_email_excludes"),
                major_regexes=self.config.get("major_regexes"),
                minor_regexes=self.config.get("minor_regexes"),
                patch_regexes=self.config.get("patch_regexes"),
                unrecognized_message=self.config.get("unrecognized_message"),
                repository=self.root,
            ):
                version = output

            return {"version": f"{version.version}"}

        @typing.override
        # enq: method name is required by hatchling's VersionSourceInterface
        def set_version(  # noqa: PYNUDGER1
            self,
            version: str,
            version_data: dict[str, str],
        ) -> None:
            """Setting the version is not supported by the comver plugin.

            This method exists to fulfill the interface, but always raises
            `NotImplementedError`.

            Args:
                version:
                    The version string (ignored).
                version_data:
                    Additional data (ignored).

            Raises:
                NotImplementedError:
                    Always raised to indicate that setting the
                    version is unsupported.
            """
            error = "comver plugin does not support setting the version."
            raise NotImplementedError(error)

    @hookimpl
    # enq: hook name is required by hatchling's plugin manager
    def hatch_register_version_source() -> type[ComverVersionSource]:  # noqa: PYNUDGER19, PYNUDGER43
        """Automatically register hatchling plugin.

        Note:
            This function is called implicitly to register
            `comver` for `hatchling` backend.

        Returns:
            ComverVersionSource class

        """
        return ComverVersionSource

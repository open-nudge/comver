# SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""Custom exceptions of `comver`."""

from __future__ import annotations


class ComverError(Exception):
    """Base class for all exceptions raised by `comver`."""


class MessageUnrecognizedError(ComverError):
    """Raised when the message is not recognized by any regexes."""

    def __init__(self, message: str) -> None:
        """Initialize the error.

        Args:
            message:
                The message which was not recognized by any regexes.

        """
        self.message: str = message

        super().__init__(
            f"Message '{message}' is not recognized by any of the provided regexes."
        )


class VersionFormatError(ComverError):
    """Raised when the string version is not properly formatted.

    Proper format should consist of three dot-separated elements,
    e.g. `7.23.1`.

    """

    def __init__(self, version: str) -> None:
        """Initialize the error.

        Args:
            version:
                String version with incorrect formatting.

        """
        self.version: str = version

        super().__init__(
            f"Version should consist of three dot separated elements (MAJOR.MINOR.PATCH), got: {version}"
        )


class VersionNotNumericError(ComverError):
    """Raised when the string version contains non-numeric elements.

    Proper format should consist of three dot-separated numeric elements,
    e.g. `7.23.1`. This error is raised, if there is a version like
    `1.2.0a1`.

    > [!CAUTION]
    > Only
    > [semantic Python versioning](https://packaging.python.org/en/latest/discussions/versioning/)
    > is allowed, e.g. no `1.2.0a1` for alpha releases

    """

    def __init__(self, version: str) -> None:
        """Initialize the error.

        Args:
            version:
                Properly formatted string version with non-numeric elements.

        """
        self.version: str = version

        super().__init__(
            f"One of the MAJOR, MINOR, PATCH is not an integer. Expected <INT>.<INT>.<INT>, got: {version}"
        )

# SPDX-FileCopyrightText: © 2025, 2026 open-nudge <https://github.com/open-nudge>
# SPDX-FileContributor: szymonmaszke <github@maszke.co>
#
# SPDX-License-Identifier: Apache-2.0

"""The `python -m comver` entrypoint."""

# enq: run only via `python -m comver`, never imported by the tests
from __future__ import annotations  # pragma: no cover

# enq: `python -m` entrypoint, it only dispatches to the CLI
# noqa-file: PYNUDGER46

# enq: run only via `python -m comver`, never imported by the tests
if __name__ == "__main__":  # pragma: no cover
    from comver._cli import main

    main()

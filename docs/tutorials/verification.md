<!--
SPDX-FileCopyrightText: © 2025 open-nudge <https://github.com/open-nudge>
SPDX-FileContributor: szymonmaszke <github@maszke.co>

SPDX-License-Identifier: Apache-2.0
-->

# Verification

`comver` supports release verification by:

- Comparing the current configuration to the one used when calculating the version.
- Validating that the commit SHA matches the one from the release.

## Why verify?

> This process ensures that __the release being calculated__ is generated
> with __the same configuration__ and __from the same Git tree__
> as the previous one.

As a result, you can be confident that neither the Git history nor
the versioning settings have changed since the last release was generated.

## Obtaining data

To retrieve the current `version`, commit `SHA`, and the configuration
`checksum`, run:

```sh
comver calculate --sha --checksum
```

This command outputs three space-separated values:

```sh
<VERSION> <SHA> <CHECKSUM>
```

Iti s recommended to store this output (e.g. attach it to the
[GitHub release](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases))
for later verification.

To get the output in a machine-readable format, add `--format=json`
(also better for storing):

```sh
comver calculate --sha --checksum --format=json
```

This will return a JSON-formatted result, ideal for automation.

## Verifying

To verify a previously published release, run:

```sh
comver verify <VERSION> <SHA> <CHECKSUM>
```

> [!WARNING]
> comver verify will return a non-zero exit code and an error message
> if any discrepancy is found.

If you’ve saved the output as a .json file (e.g., `input.json`),
you can automate the verification using the script below (requires jq):

```sh
#!/bin/bash

json=$(cat input.json)

# Parse fields using jq
version=$(echo "$json" | jq -r '.version')
sha=$(echo "$json" | jq -r '.sha')
checksum=$(echo "$json" | jq -r '.checksum')

# Call baz with the arguments in order: version, sha, checksum
comver verify "${version}" "${sha}" "${checksum}"
```

This method is especially useful when running verification in a CI pipeline.

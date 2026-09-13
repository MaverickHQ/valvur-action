# valvur-action

Scan a repository with [valvur](https://github.com/MaverickHQ/valvur) in GitHub
Actions and gate on the result. Local, offline, read-only, no account: the
Scanners run in one container on the runner and nothing leaves it — `run.json`
records `what_left_the_machine: nothing` on every `offline` scan.

```yaml
permissions:
  contents: read
  security-events: write     # only for the SARIF upload; drop it with sarif: "false"

steps:
  - uses: actions/checkout@v5
  - uses: MaverickHQ/valvur-action@v0
    with:
      fail-on: high
      no-inconclusive: "true"
```

That installs the shim, fetches the image, the vulnerability database and the
package-name index (the index is cached between runs; the first run is about a
minute and a half), scans, uploads `results.sarif` to code scanning, and runs
`valvur gate` — which fails the job on an incomplete run, a lapsed suppression, an
active finding at or above `fail-on`, or, with `no-inconclusive`, a scan whose data
was too old to be evidence or that never inspected part of the tree.

## Inputs

| input | default | |
|---|---|---|
| `path` | `.` | Directory to scan |
| `profile` | `offline` | `offline` sends nothing anywhere; `full` adds OSV and first-publish age, which send package names to public registries |
| `fail-on` | `high` | `critical`, `high`, `medium`, `low` or `any` |
| `no-inconclusive` | `false` | Fail an `inconclusive` scan rather than pass by omission |
| `gate` | `true` | Run `valvur gate`; `false` to only scan and report |
| `sarif` | `true` | Upload to code scanning (needs `security-events: write`) |
| `budget` | *(none)* | Seconds the Scanners may take together; past it the run is reported incomplete with the cut Scanners named |
| `jobs` | *(all)* | Scanners at once |
| `verify` | `true` | Install cosign so the name index's signature is verified on fetch |
| `version` | `0.3.0` | valvur version from PyPI (0.3.0 or later), or a `git+https://…` source; empty uses the `valvur` on PATH |

## Outputs

`status` (`findings`, `clean`, `inconclusive`), `complete`, `active`, and
`results` — the Results Folder, `<path>/.security-scan`, which ignores itself and
must never be committed.

## What it does not do

It never modifies your code, never sends it anywhere, and never fixes anything
(valvur proposes; you decide). Suppressions with mandatory expiry dates live in a
committed `.security-scan.toml`. The whole story is in valvur's README.

## Licence

Apache-2.0, like valvur.

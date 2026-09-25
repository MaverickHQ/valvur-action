"""The SARIF that goes to code scanning: `results.sarif` without its suppressed
results.

GitHub does not read SARIF `suppressions` (measured 2026-09-26 on valvur's own
repository: five suppressed results uploaded on every push for thirteen days,
five open alerts, none dismissed). A risk `.security-scan.toml` has recorded a
decision about would otherwise sit in the Security tab as an open alert for as
long as the decision stood. The file on disk keeps every result; this writes
`results.upload.sarif` beside it with the suppressed ones left out, and says how
many. An alert whose result is absent from the next upload is closed by GitHub
as fixed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def filter_sarif(sarif: dict) -> tuple[dict, int, int]:
    """(the document without suppressed results, kept, left out)."""
    kept = dropped = 0
    for run in sarif.get("runs") or []:
        before = run.get("results") or []
        run["results"] = [r for r in before if not r.get("suppressions")]
        kept += len(run["results"])
        dropped += len(before) - len(run["results"])
    return sarif, kept, dropped


def main(argv: list[str]) -> int:
    results = Path(argv[1])
    source = results / "results.sarif"
    sarif, kept, dropped = filter_sarif(json.loads(source.read_text(encoding="utf-8")))
    (results / "results.upload.sarif").write_text(json.dumps(sarif), encoding="utf-8")
    print(f"code scanning upload: {kept} result(s); {dropped} suppressed result(s) left out")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

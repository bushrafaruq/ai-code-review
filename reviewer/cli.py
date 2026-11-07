"""Command line.

    git diff main...HEAD | python -m reviewer.cli review -              # review a diff from stdin
    python -m reviewer.cli review changes.diff --format json
    python -m reviewer.cli review --git origin/main --repo .            # diff against a branch
    python -m reviewer.cli review pr.diff --repo . --post-github --pr 12 --github-repo owner/name
    python -m reviewer.cli review pr.diff --fail-on high               # non-zero exit for CI
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from .models import SEVERITIES
from .render import markdown
from .workflow import review


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="reviewer")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("review")
    r.add_argument("diff", nargs="?", help="diff file, or - for stdin")
    r.add_argument("--git", metavar="BASE", help="review `git diff BASE...HEAD` in --repo")
    r.add_argument("--repo", default=None, help="checkout root, lets AST checks see whole files")
    r.add_argument("--format", choices=["md", "json"], default="md")
    r.add_argument("--no-llm", action="store_true")
    r.add_argument("--fail-on", choices=SEVERITIES, help="exit 1 if a finding at or above this severity")
    r.add_argument("--post-github", action="store_true")
    r.add_argument("--pr", type=int)
    r.add_argument("--github-repo")
    r.add_argument("--link-base")
    a = ap.parse_args(argv)

    if a.git:
        text = subprocess.run(["git", "diff", f"{a.git}...HEAD"], cwd=a.repo or ".", capture_output=True,
                              text=True, check=True).stdout
    elif a.diff in (None, "-"):
        text = sys.stdin.read()
    else:
        with open(a.diff, encoding="utf-8") as fh:
            text = fh.read()

    llm = None
    if not a.no_llm:
        try:
            from .llm import LLMReviewer
            llm = LLMReviewer()
        except RuntimeError:
            llm = None
    res = review(text, a.repo, llm)
    out = json.dumps(res.to_dict(), indent=2) if a.format == "json" else markdown(res, a.link_base)
    print(out)
    if a.post_github:
        from .github import upsert_comment
        print(upsert_comment(a.github_repo, a.pr, markdown(res, a.link_base)), file=sys.stderr)
    if a.fail_on:
        floor = SEVERITIES.index(a.fail_on)
        if any(SEVERITIES.index(f.severity) >= floor for f in res.findings):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

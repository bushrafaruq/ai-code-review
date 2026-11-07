"""The multi-step review workflow.

    1 parse diff -> 2 static checks -> 3 LLM review (optional) -> 4 test recommendations
    -> 5 aggregate: de-duplicate, rank, decide a verdict

Every step is timed and recorded in `trace`, so a reviewer can see what ran and what was dropped.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import static
from .diff import FileDiff, parse
from .models import SEVERITIES, Finding, TestRecommendation
from .tests_advisor import recommend

MAX_FINDINGS_PER_FILE = 8
MIN_LLM_CONFIDENCE = 0.5


@dataclass
class Review:
    verdict: str                                   # approve | comment | request_changes
    summary: dict
    findings: list[Finding]
    tests: list[TestRecommendation]
    trace: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"verdict": self.verdict, "summary": self.summary,
                "findings": [asdict(f) for f in self.findings],
                "tests": [asdict(t) for t in self.tests], "trace": self.trace}


def file_contents(files: list[FileDiff], repo: str | Path | None) -> dict[str, str | None]:
    out = {}
    for f in files:
        if f.new_content is not None:
            out[f.path] = f.new_content
        elif repo and (Path(repo) / f.path).is_file():
            out[f.path] = (Path(repo) / f.path).read_text(encoding="utf-8", errors="ignore")
        else:
            out[f.path] = None
    return out


def aggregate(findings: list[Finding]) -> list[Finding]:
    best: dict[tuple, Finding] = {}
    for f in findings:
        if f.source == "llm" and f.confidence < MIN_LLM_CONFIDENCE:
            continue
        k = f.key()
        cur = best.get(k)
        # keep the more severe; on a tie prefer the deterministic finding
        if cur is None or (SEVERITIES.index(f.severity), f.source != "llm") > (SEVERITIES.index(cur.severity), cur.source != "llm"):
            best[k] = f
    ranked = sorted(best.values(), key=lambda f: (-SEVERITIES.index(f.severity), f.file, f.line))
    per_file: dict[str, int] = {}
    out = []
    for f in ranked:
        per_file[f.file] = per_file.get(f.file, 0) + 1
        if per_file[f.file] <= MAX_FINDINGS_PER_FILE:
            out.append(f)
    return out


def review(diff_text: str, repo: str | Path | None = None, llm=None) -> Review:
    trace = []

    def step(name, fn):
        t0 = time.perf_counter()
        res = fn()
        trace.append({"step": name, "ms": round((time.perf_counter() - t0) * 1000, 1)})
        return res

    files = step("parse_diff", lambda: parse(diff_text))
    trace[-1].update(files=len(files), added_lines=sum(len(f.added) for f in files))
    contents = file_contents(files, repo)

    found: list[Finding] = step("static_checks", lambda: [x for f in files for x in static.run(f, contents[f.path])])
    trace[-1]["findings"] = len(found)

    if llm is not None:
        t0 = time.perf_counter()
        llm_stats = {"returned": 0, "kept": 0, "dropped_unchanged_line": 0, "errors": []}
        for f in files:
            if not f.added or f.language == "other":
                continue
            got, s = llm.review(f, found)
            llm_stats["returned"] += s["returned"]
            llm_stats["dropped_unchanged_line"] += s["dropped_unchanged_line"]
            if s["error"]:
                llm_stats["errors"].append(f"{f.path}: {s['error']}")
            llm_stats["kept"] += len(got)
            found += got
        trace.append({"step": "llm_review", "model": llm.name, "ms": round((time.perf_counter() - t0) * 1000, 1), **llm_stats})
    else:
        trace.append({"step": "llm_review", "skipped": "no LLM configured"})

    recs, test_findings = step("test_recommendations", lambda: recommend(files, contents))
    trace[-1]["functions_without_tests"] = len(recs)
    found += test_findings

    final = step("aggregate", lambda: aggregate(found))
    counts = {s: sum(f.severity == s for f in final) for s in reversed(SEVERITIES)}
    verdict = "request_changes" if counts["high"] else "comment" if final else "approve"
    summary = {"files": len(files), "added_lines": sum(len(f.added) for f in files), "findings": counts,
               "functions_needing_tests": len(recs)}
    return Review(verdict, summary, final, recs, trace)

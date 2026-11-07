"""Measure precision and recall of the review workflow on the seeded-defect cases.

    python eval/run_eval.py              # static checks + test advisor (no API key)
    python eval/run_eval.py --llm        # adds the LLM step (ANTHROPIC_API_KEY or OPENAI_API_KEY)

A finding matches an expected issue when file and category match and the line is within 1.
Writes eval/results/<mode>/metrics.json, report.md and every case's diff and review.
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

from cases import CASES  # noqa: E402

from reviewer.render import markdown  # noqa: E402
from reviewer.workflow import review  # noqa: E402


def make_diff(files: dict[str, tuple[str, str]]) -> str:
    parts = []
    for path, (before, after) in files.items():
        parts.append(f"diff --git a/{path} b/{path}")
        old = "/dev/null" if before == "" else f"a/{path}"
        parts += list(difflib.unified_diff(before.splitlines(), after.splitlines(), old, f"b/{path}", lineterm="", n=3))
    return "\n".join(parts) + "\n"


def line_of(after: str, needle: str) -> int:
    for i, line in enumerate(after.splitlines(), start=1):
        if needle in line:
            return i
    raise ValueError(f"label text not found: {needle!r}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true")
    a = ap.parse_args()
    llm = None
    if a.llm:
        from reviewer.llm import LLMReviewer
        llm = LLMReviewer()
    mode = "llm" if llm else "static"
    out = ROOT / "eval" / "results" / mode
    (out / "cases").mkdir(parents=True, exist_ok=True)

    tp_c, fn_c, fp_c = Counter(), Counter(), Counter()
    per_case = []
    for case in CASES:
        diff = make_diff(case["files"])
        with tempfile.TemporaryDirectory() as repo:
            for path, (_, after) in case["files"].items():
                p = Path(repo) / path
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(after, encoding="utf-8")
            res = review(diff, repo, llm)
        expected = [(f, line_of(case["files"][f][1], text), cat) for f, text, cat in case["expect"]]
        found = [(x.file, x.line, x.category) for x in res.findings]
        used, matched_cats = set(), []
        for f, ln, cat in expected:
            match = next((i for i, (ff, fl, fc) in enumerate(found)
                          if i not in used and ff == f and fc == cat and abs(fl - ln) <= 1), None)
            if match is None:
                fn_c[cat] += 1
            else:
                used.add(match)
                matched_cats.append(cat)
                tp_c[cat] += 1
        for i, (_, _, cat) in enumerate(found):
            if i not in used:
                fp_c[cat] += 1
        per_case.append({"id": case["id"], "expected": len(expected), "matched": len(used),
                         "expected_non_test": sum(c != "testing" for _, _, c in expected),
                         "matched_non_test": sum(c != "testing" for c in matched_cats),
                         "false_positives": len(found) - len(used), "verdict": res.verdict,
                         "static_blind": case.get("static_blind", False)})
        (out / "cases" / f"{case['id']}.diff").write_text(diff, encoding="utf-8")
        (out / "cases" / f"{case['id']}.review.md").write_text(markdown(res), encoding="utf-8")

    def prf(tp, fp, fn):
        p = tp / (tp + fp) if tp + fp else None
        r = tp / (tp + fn) if tp + fn else None
        return {"tp": tp, "fp": fp, "fn": fn, "precision": None if p is None else round(p, 3),
                "recall": None if r is None else round(r, 3)}

    cats = sorted(set(tp_c) | set(fn_c) | set(fp_c))
    overall = prf(sum(tp_c.values()), sum(fp_c.values()), sum(fn_c.values()))
    non_test = prf(sum(v for k, v in tp_c.items() if k != "testing"), sum(v for k, v in fp_c.items() if k != "testing"),
                   sum(v for k, v in fn_c.items() if k != "testing"))
    clean = [c for c in per_case if c["expected"] == 0]
    blind = [c for c in per_case if c["static_blind"]]
    metrics = {
        "mode": mode, "cases": len(CASES), "expected_issues": sum(c["expected"] for c in per_case),
        "overall": overall, "excluding_testing": non_test,
        "by_category": {c: prf(tp_c[c], fp_c[c], fn_c[c]) for c in cats},
        "clean_cases_with_false_positives": sum(c["false_positives"] > 0 for c in clean),
        "clean_cases": len(clean),
        "static_blind_issues_found": sum(c["matched_non_test"] for c in blind),
        "static_blind_issues": sum(c["expected_non_test"] for c in blind),
        "per_case": per_case,
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    lines = [f"# Evaluation: {mode}", "",
             f"{metrics['cases']} cases, {metrics['expected_issues']} expected issues.", "",
             "| Scope | Precision | Recall | TP | FP | FN |", "|---|---|---|---|---|---|",
             f"| All findings | {overall['precision']} | {overall['recall']} | {overall['tp']} | {overall['fp']} | {overall['fn']} |",
             f"| Excluding test-coverage findings | {non_test['precision']} | {non_test['recall']} | {non_test['tp']} | {non_test['fp']} | {non_test['fn']} |"]
    lines += [f"| {c} | {v['precision']} | {v['recall']} | {v['tp']} | {v['fp']} | {v['fn']} |"
              for c, v in metrics["by_category"].items()]
    lines += ["", f"Clean cases with any false positive: {metrics['clean_cases_with_false_positives']} of {metrics['clean_cases']}.",
              f"Issues that no static rule targets (logic, indirect SQL injection): found "
              f"{metrics['static_blind_issues_found']} of {metrics['static_blind_issues']}.", "",
              "| Case | Expected | Matched | False positives | Verdict |", "|---|---|---|---|---|"]
    lines += [f"| {c['id']} | {c['expected']} | {c['matched']} | {c['false_positives']} | {c['verdict']} |" for c in per_case]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

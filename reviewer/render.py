"""Render a review as a pull-request comment (Markdown)."""

from __future__ import annotations

from .workflow import Review

MARKER = "<!-- ai-code-review -->"
ICON = {"high": "🔴", "medium": "🟠", "low": "🟡", "info": "⚪"}
VERDICT = {"request_changes": "Changes requested", "comment": "Comments", "approve": "No issues found"}


def markdown(r: Review, link_base: str | None = None) -> str:
    c = r.summary["findings"]
    lines = [MARKER, f"## AI-assisted code review: {VERDICT[r.verdict]}", "",
             f"{r.summary['files']} file(s), {r.summary['added_lines']} added line(s) · "
             f"{c['high']} high · {c['medium']} medium · {c['low']} low · {c['info']} info · "
             f"{r.summary['functions_needing_tests']} function(s) without tests", ""]
    if r.findings:
        lines += ["| | Location | Category | Finding | Suggestion |", "|---|---|---|---|---|"]
        for f in r.findings:
            loc = f"`{f.file}:{f.line}`"
            if link_base:
                loc = f"[{loc}]({link_base}/{f.file}#L{f.line})"
            src = "" if f.source == "static" else f" _({f.source})_"
            lines.append(f"| {ICON[f.severity]} | {loc} | {f.category} | {f.message}{src} | {f.suggestion} |")
        lines.append("")
    if r.tests:
        lines += ["### Suggested tests", ""]
        for t in r.tests:
            lines.append(f"- **`{t.function}`** (`{t.file}:{t.line}`, {t.reason})")
            lines += [f"  - {case}" for case in t.cases]
        lines.append("")
    llm = next((s for s in r.trace if s["step"] == "llm_review"), {})
    note = f"LLM: {llm['model']}" if "model" in llm else "LLM step skipped (no API key); static checks only"
    lines += ["<sub>Automated suggestions to support, not replace, human review. "
              f"{note}. Static rules: see docs/RULES.md.</sub>"]
    return "\n".join(lines) + "\n"

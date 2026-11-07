"""Step 4: test recommendations.

Finds functions that were added or changed in this diff and checks whether any test file in the
same diff mentions them. For each untested function it proposes concrete test cases derived from
the code itself: parameters with defaults, optional (None) parameters, exceptions it raises,
branches and loops.
"""

from __future__ import annotations

import ast

from .diff import FileDiff
from .models import Finding, TestRecommendation


def _cases(fn: ast.FunctionDef) -> list[str]:
    cases = ["typical input returns the expected result"]
    args = fn.args
    n_def = len(args.defaults)
    for i, a in enumerate(args.args):
        if a.arg in ("self", "cls"):
            continue
        has_default = i >= len(args.args) - n_def
        ann = ast.unparse(a.annotation) if a.annotation else ""
        if "None" in ann or "Optional" in ann:
            cases.append(f"`{a.arg}` is None")
        if any(t in ann for t in ("list", "dict", "str", "Sequence", "Iterable")):
            cases.append(f"`{a.arg}` is empty")
        if has_default:
            cases.append(f"`{a.arg}` left at its default")
    raises = {ast.unparse(n.exc.func if isinstance(n.exc, ast.Call) else n.exc)
              for n in ast.walk(fn) if isinstance(n, ast.Raise) and n.exc is not None}
    cases += [f"raises `{r}` on invalid input" for r in sorted(raises)]
    if any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(fn)):
        cases.append("zero, one and many iterations (boundary values)")
    if sum(isinstance(n, ast.If) for n in ast.walk(fn)) >= 2:
        cases.append("each branch of the conditional logic")
    if any(isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Div, ast.FloorDiv, ast.Mod)) for n in ast.walk(fn)):
        cases.append("divisor of zero")
    return cases


def recommend(files: list[FileDiff], contents: dict[str, str | None]) -> tuple[list[TestRecommendation], list[Finding]]:
    test_text = "\n".join("\n".join(f.added.values()) for f in files if f.is_test)
    recs, findings = [], []
    for f in files:
        if f.is_test or f.language != "python" or not contents.get(f.path):
            continue
        try:
            tree = ast.parse(contents[f.path])
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name.startswith("_"):
                continue
            body_lines = set(range(node.lineno, (node.end_lineno or node.lineno) + 1))
            if not body_lines & set(f.added):
                continue
            if node.name in test_text:
                continue
            new = node.lineno in f.added
            reason = "new function with no test in this change" if new else "changed function with no test update in this change"
            recs.append(TestRecommendation(f.path, node.name, node.lineno, reason, _cases(node)))
            findings.append(Finding(f.path, node.lineno, "low", "testing", "TEST001",
                                    f"`{node.name}` is {'new' if new else 'changed'} but no test in this change covers it.",
                                    "Add tests; see the test recommendations below.", source="tests"))
    return recs, findings

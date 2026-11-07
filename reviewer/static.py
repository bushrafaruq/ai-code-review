"""Step 2: deterministic checks on the changed lines.

Cheap, explainable and always on. They run before the LLM so the model can focus on what
rules cannot see (logic, intent, naming), and their findings are passed to the model to avoid
duplicates. Line rules run on any added Python line; AST rules run when the full new file is
available (new files, or --repo pointing at a checkout).
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass

from .diff import FileDiff
from .models import Finding


@dataclass(frozen=True)
class LineRule:
    id: str
    pattern: str
    severity: str
    category: str
    message: str
    suggestion: str
    skip_tests: bool = False
    unless: str | None = None


LINE_RULES = [
    LineRule("PY001", r"^\s*except\s*:", "medium", "error_handling",
             "Bare `except:` catches everything, including KeyboardInterrupt and SystemExit.",
             "Catch the specific exception you expect, e.g. `except ValueError:`."),
    LineRule("PY004", r"(?<![\w.])(eval|exec)\s*\(", "high", "security",
             "`eval`/`exec` on data can execute arbitrary code.",
             "Use `ast.literal_eval` for literals, or parse the input explicitly."),
    LineRule("PY005", r"subprocess\.\w+\(.*shell\s*=\s*True|os\.system\(", "high", "security",
             "Running a shell command built from strings allows command injection.",
             "Pass a list of arguments with `shell=False` and never interpolate user input."),
    LineRule("PY006", r"""(?i)\b\w*(api_?key|secret|password|passwd|token)\w*\s*=\s*['"][^'"\s]{8,}['"]""", "high", "security",
             "Hard-coded credential in source code.",
             "Load it from an environment variable or a secrets manager.", skip_tests=True),
    LineRule("PY007", r"""(?i)\.execute\(\s*(f['"]|['"].*['"]\s*(%|\+|\.format))|['"]\s*(select|insert|update|delete)\b[^'"]*['"]\s*\+""",
             "high", "security", "SQL built by string formatting is open to SQL injection.",
             "Use parameterised queries, e.g. `cursor.execute(sql, (value,))`."),
    LineRule("PY008", r"\brequests\.(get|post|put|patch|delete|head)\(", "medium", "reliability",
             "HTTP call without a timeout can hang forever.",
             "Add `timeout=` (e.g. `timeout=10`).", unless=r"timeout\s*="),
    LineRule("PY009", r"[=!]=\s*None\b", "low", "correctness",
             "Comparison to None with `==`/`!=`.", "Use `is None` / `is not None`."),
    LineRule("PY010", r"^\s*print\(", "info", "maintainability",
             "`print` left in library code.", "Use `logging`, or remove the debug output.", skip_tests=True),
    LineRule("PY012", r"\bpickle\.loads?\(|\byaml\.load\((?![^)]*Loader\s*=\s*yaml\.SafeLoader)", "high", "security",
             "Deserialising untrusted data with pickle / yaml.load can execute code.",
             "Use `json`, or `yaml.safe_load`."),
    LineRule("PY013", r"verify\s*=\s*False", "high", "security",
             "TLS certificate verification disabled.", "Remove `verify=False`; fix the certificate instead."),
    LineRule("PY015", r"#\s*(TODO|FIXME|HACK)\b", "info", "maintainability",
             "New TODO/FIXME added.", "Open an issue and reference it, or resolve before merging."),
]


# Rules that have a more precise AST version; the line version is only used when the whole
# file is not available. (The regex flagged "never eval()" inside a docstring: eval case C18.)
AST_PREFERRED = {"PY004"}


def line_checks(f: FileDiff, have_ast: bool = False) -> list[Finding]:
    out = []
    for ln, text in f.added.items():
        for r in LINE_RULES:
            if r.skip_tests and f.is_test:
                continue
            if have_ast and r.id in AST_PREFERRED:
                continue
            if re.search(r.pattern, text) and not (r.unless and re.search(r.unless, text)):
                out.append(Finding(f.path, ln, r.severity, r.category, r.id, r.message, r.suggestion))
    return out


class _Visitor(ast.NodeVisitor):
    def __init__(self, path: str, changed: set[int]):
        self.path, self.changed, self.out = path, changed, []

    def _add(self, node, *args):
        if node.lineno in self.changed:
            self.out.append(Finding(self.path, node.lineno, *args))

    def visit_FunctionDef(self, node):
        for d in node.args.defaults + node.args.kw_defaults:
            if isinstance(d, (ast.List, ast.Dict, ast.Set)) or (
                    isinstance(d, ast.Call) and getattr(d.func, "id", "") in {"list", "dict", "set"}):
                self._add(node, "medium", "correctness", "PY003",
                          f"Mutable default argument in `{node.name}` is shared between calls.",
                          "Default to `None` and create the object inside the function.")
                break
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec"}:
            self._add(node, "high", "security", "PY004", "`eval`/`exec` on data can execute arbitrary code.",
                      "Use `ast.literal_eval` for literals, or parse the input explicitly.")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        if node.type is not None and all(isinstance(s, (ast.Pass, ast.Continue)) or
                                         (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                                         for s in node.body):
            self._add(node, "medium", "error_handling", "PY002",
                      "Exception is caught and silently ignored.",
                      "Log it, re-raise, or handle it; if ignoring is intended, say why in a comment.")
        self.generic_visit(node)


def ast_checks(f: FileDiff, content: str | None) -> list[Finding]:
    if f.language != "python" or not content:
        return []
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        if e.lineno in f.added:
            return [Finding(f.path, e.lineno, "high", "correctness", "PY000", f"Syntax error: {e.msg}.",
                            "Fix the syntax error.")]
        return []
    v = _Visitor(f.path, set(f.added))
    v.visit(tree)
    return v.out


def _parses(content: str | None) -> bool:
    if not content:
        return False
    try:
        ast.parse(content)
        return True
    except SyntaxError:
        return False


def run(f: FileDiff, content: str | None) -> list[Finding]:
    if f.language != "python":
        return []
    return line_checks(f, have_ast=_parses(content)) + ast_checks(f, content)

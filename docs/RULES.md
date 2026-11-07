# Static rules

Deterministic checks on changed Python lines. Line rules need only the diff; AST rules need the
whole new file (new files, or `--repo` pointing at a checkout, as in the GitHub Action).

| Rule | Severity | Category | What it flags | Uses |
|---|---|---|---|---|
| PY000 | high | correctness | Syntax error on a changed line | AST |
| PY001 | medium | error_handling | Bare `except:` catches everything, including KeyboardInterrupt and SystemExit. | line |
| PY002 | medium | error_handling | Exception caught and silently ignored | AST |
| PY003 | medium | correctness | Mutable default argument | AST |
| PY004 | high | security | `eval`/`exec` on data can execute arbitrary code. | AST (line fallback) |
| PY005 | high | security | Running a shell command built from strings allows command injection. | line |
| PY006 | high | security | Hard-coded credential in source code. | line |
| PY007 | high | security | SQL built by string formatting is open to SQL injection. | line |
| PY008 | medium | reliability | HTTP call without a timeout can hang forever. | line |
| PY009 | low | correctness | Comparison to None with `==`/`!=`. | line |
| PY010 | info | maintainability | `print` left in library code. | line |
| PY012 | high | security | Deserialising untrusted data with pickle / yaml.load can execute code. | line |
| PY013 | high | security | TLS certificate verification disabled. | line |
| PY015 | info | maintainability | New TODO/FIXME added. | line |
| TEST001 | low | testing | Changed or new public function with no test in the same change | AST + diff |

Rules skipped in test files: PY006 (hard-coded credential) and PY010 (print).

## Adding a rule

Add a `LineRule` to `LINE_RULES` in `reviewer/static.py` (or a visitor method for AST rules),
add a seeded case to `eval/cases.py`, a clean case that must not trigger it, and re-run
`python eval/run_eval.py`.

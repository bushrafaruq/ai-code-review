<!-- ai-code-review -->
## AI-assisted code review: Changes requested

1 file(s), 2 added line(s) · 1 high · 0 medium · 1 low · 0 info · 1 function(s) without tests

| | Location | Category | Finding | Suggestion |
|---|---|---|---|---|
| 🔴 | `app/calc.py:2` | security | `eval`/`exec` on data can execute arbitrary code. | Use `ast.literal_eval` for literals, or parse the input explicitly. |
| 🟡 | `app/calc.py:1` | testing | `calculate` is new but no test in this change covers it. _(tests)_ | Add tests; see the test recommendations below. |

### Suggested tests

- **`calculate`** (`app/calc.py:1`, new function with no test in this change)
  - typical input returns the expected result
  - `expression` is empty

<sub>Automated suggestions to support, not replace, human review. LLM step skipped (no API key); static checks only. Static rules: see docs/RULES.md.</sub>

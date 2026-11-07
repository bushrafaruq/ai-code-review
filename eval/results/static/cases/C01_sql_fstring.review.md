<!-- ai-code-review -->
## AI-assisted code review: Changes requested

1 file(s), 4 added line(s) · 1 high · 0 medium · 1 low · 0 info · 1 function(s) without tests

| | Location | Category | Finding | Suggestion |
|---|---|---|---|---|
| 🔴 | `app/users.py:3` | security | SQL built by string formatting is open to SQL injection. | Use parameterised queries, e.g. `cursor.execute(sql, (value,))`. |
| 🟡 | `app/users.py:1` | testing | `find_user` is new but no test in this change covers it. _(tests)_ | Add tests; see the test recommendations below. |

### Suggested tests

- **`find_user`** (`app/users.py:1`, new function with no test in this change)
  - typical input returns the expected result

<sub>Automated suggestions to support, not replace, human review. LLM step skipped (no API key); static checks only. Static rules: see docs/RULES.md.</sub>

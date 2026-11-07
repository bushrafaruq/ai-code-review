<!-- ai-code-review -->
## AI-assisted code review: Comments

1 file(s), 5 added line(s) · 0 high · 1 medium · 1 low · 0 info · 1 function(s) without tests

| | Location | Category | Finding | Suggestion |
|---|---|---|---|---|
| 🟠 | `app/money.py:4` | error_handling | Exception is caught and silently ignored. | Log it, re-raise, or handle it; if ignoring is intended, say why in a comment. |
| 🟡 | `app/money.py:1` | testing | `parse_amount` is new but no test in this change covers it. _(tests)_ | Add tests; see the test recommendations below. |

### Suggested tests

- **`parse_amount`** (`app/money.py:1`, new function with no test in this change)
  - typical input returns the expected result

<sub>Automated suggestions to support, not replace, human review. LLM step skipped (no API key); static checks only. Static rules: see docs/RULES.md.</sub>

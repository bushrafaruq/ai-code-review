<!-- ai-code-review -->
## AI-assisted code review: Changes requested

1 file(s), 8 added line(s) · 1 high · 1 medium · 1 low · 0 info · 1 function(s) without tests

| | Location | Category | Finding | Suggestion |
|---|---|---|---|---|
| 🔴 | `app/rates.py:3` | security | Hard-coded credential in source code. | Load it from an environment variable or a secrets manager. |
| 🟠 | `app/rates.py:7` | reliability | HTTP call without a timeout can hang forever. | Add `timeout=` (e.g. `timeout=10`). |
| 🟡 | `app/rates.py:6` | testing | `fetch_rates` is new but no test in this change covers it. _(tests)_ | Add tests; see the test recommendations below. |

### Suggested tests

- **`fetch_rates`** (`app/rates.py:6`, new function with no test in this change)
  - typical input returns the expected result

<sub>Automated suggestions to support, not replace, human review. LLM step skipped (no API key); static checks only. Static rules: see docs/RULES.md.</sub>

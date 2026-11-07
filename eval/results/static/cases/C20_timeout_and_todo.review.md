<!-- ai-code-review -->
## AI-assisted code review: Comments

1 file(s), 8 added line(s) · 0 high · 1 medium · 1 low · 1 info · 1 function(s) without tests

| | Location | Category | Finding | Suggestion |
|---|---|---|---|---|
| 🟠 | `app/weather.py:6` | reliability | HTTP call without a timeout can hang forever. | Add `timeout=` (e.g. `timeout=10`). |
| 🟡 | `app/weather.py:4` | testing | `get_weather` is new but no test in this change covers it. _(tests)_ | Add tests; see the test recommendations below. |
| ⚪ | `app/weather.py:5` | maintainability | New TODO/FIXME added. | Open an issue and reference it, or resolve before merging. |

### Suggested tests

- **`get_weather`** (`app/weather.py:4`, new function with no test in this change)
  - typical input returns the expected result

<sub>Automated suggestions to support, not replace, human review. LLM step skipped (no API key); static checks only. Static rules: see docs/RULES.md.</sub>

<!-- ai-code-review -->
## AI-assisted code review: Comments

1 file(s), 3 added line(s) · 0 high · 0 medium · 1 low · 0 info · 1 function(s) without tests

| | Location | Category | Finding | Suggestion |
|---|---|---|---|---|
| 🟡 | `app/files.py:1` | testing | `count_lines` is new but no test in this change covers it. _(tests)_ | Add tests; see the test recommendations below. |

### Suggested tests

- **`count_lines`** (`app/files.py:1`, new function with no test in this change)
  - typical input returns the expected result

<sub>Automated suggestions to support, not replace, human review. LLM step skipped (no API key); static checks only. Static rules: see docs/RULES.md.</sub>

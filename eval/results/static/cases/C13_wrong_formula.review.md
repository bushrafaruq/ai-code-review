<!-- ai-code-review -->
## AI-assisted code review: Comments

1 file(s), 4 added line(s) · 0 high · 0 medium · 1 low · 0 info · 1 function(s) without tests

| | Location | Category | Finding | Suggestion |
|---|---|---|---|---|
| 🟡 | `app/pricing.py:1` | testing | `apply_discount` is new but no test in this change covers it. _(tests)_ | Add tests; see the test recommendations below. |

### Suggested tests

- **`apply_discount`** (`app/pricing.py:1`, new function with no test in this change)
  - typical input returns the expected result
  - raises `ValueError` on invalid input
  - divisor of zero

<sub>Automated suggestions to support, not replace, human review. LLM step skipped (no API key); static checks only. Static rules: see docs/RULES.md.</sub>

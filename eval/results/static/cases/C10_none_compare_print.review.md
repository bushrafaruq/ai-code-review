<!-- ai-code-review -->
## AI-assisted code review: Comments

1 file(s), 5 added line(s) · 0 high · 0 medium · 2 low · 1 info · 1 function(s) without tests

| | Location | Category | Finding | Suggestion |
|---|---|---|---|---|
| 🟡 | `app/lists.py:1` | testing | `first_or_default` is new but no test in this change covers it. _(tests)_ | Add tests; see the test recommendations below. |
| 🟡 | `app/lists.py:2` | correctness | Comparison to None with `==`/`!=`. | Use `is None` / `is not None`. |
| ⚪ | `app/lists.py:4` | maintainability | `print` left in library code. | Use `logging`, or remove the debug output. |

### Suggested tests

- **`first_or_default`** (`app/lists.py:1`, new function with no test in this change)
  - typical input returns the expected result
  - `default` left at its default

<sub>Automated suggestions to support, not replace, human review. LLM step skipped (no API key); static checks only. Static rules: see docs/RULES.md.</sub>

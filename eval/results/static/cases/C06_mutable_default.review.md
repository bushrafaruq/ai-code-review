<!-- ai-code-review -->
## AI-assisted code review: Comments

1 file(s), 3 added line(s) · 0 high · 1 medium · 1 low · 0 info · 1 function(s) without tests

| | Location | Category | Finding | Suggestion |
|---|---|---|---|---|
| 🟠 | `app/tags.py:1` | correctness | Mutable default argument in `add_tag` is shared between calls. | Default to `None` and create the object inside the function. |
| 🟡 | `app/tags.py:1` | testing | `add_tag` is new but no test in this change covers it. _(tests)_ | Add tests; see the test recommendations below. |

### Suggested tests

- **`add_tag`** (`app/tags.py:1`, new function with no test in this change)
  - typical input returns the expected result
  - `tags` left at its default

<sub>Automated suggestions to support, not replace, human review. LLM step skipped (no API key); static checks only. Static rules: see docs/RULES.md.</sub>

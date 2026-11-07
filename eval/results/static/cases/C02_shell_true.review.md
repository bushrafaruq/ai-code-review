<!-- ai-code-review -->
## AI-assisted code review: Changes requested

1 file(s), 5 added line(s) · 1 high · 0 medium · 1 low · 0 info · 1 function(s) without tests

| | Location | Category | Finding | Suggestion |
|---|---|---|---|---|
| 🔴 | `ops/backup.py:5` | security | Running a shell command built from strings allows command injection. | Pass a list of arguments with `shell=False` and never interpolate user input. |
| 🟡 | `ops/backup.py:4` | testing | `archive` is new but no test in this change covers it. _(tests)_ | Add tests; see the test recommendations below. |

### Suggested tests

- **`archive`** (`ops/backup.py:4`, new function with no test in this change)
  - typical input returns the expected result

<sub>Automated suggestions to support, not replace, human review. LLM step skipped (no API key); static checks only. Static rules: see docs/RULES.md.</sub>

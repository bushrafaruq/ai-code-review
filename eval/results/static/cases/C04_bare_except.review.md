<!-- ai-code-review -->
## AI-assisted code review: Comments

1 file(s), 9 added line(s) · 0 high · 1 medium · 1 low · 0 info · 1 function(s) without tests

| | Location | Category | Finding | Suggestion |
|---|---|---|---|---|
| 🟠 | `app/config.py:8` | error_handling | Bare `except:` catches everything, including KeyboardInterrupt and SystemExit. | Catch the specific exception you expect, e.g. `except ValueError:`. |
| 🟡 | `app/config.py:4` | testing | `load_config` is new but no test in this change covers it. _(tests)_ | Add tests; see the test recommendations below. |

### Suggested tests

- **`load_config`** (`app/config.py:4`, new function with no test in this change)
  - typical input returns the expected result

<sub>Automated suggestions to support, not replace, human review. LLM step skipped (no API key); static checks only. Static rules: see docs/RULES.md.</sub>

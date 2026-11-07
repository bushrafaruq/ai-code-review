# Evaluation: static

20 cases, 35 expected issues.

| Scope | Precision | Recall | TP | FP | FN |
|---|---|---|---|---|---|
| All findings | 1.0 | 0.857 | 30 | 0 | 5 |
| Excluding test-coverage findings | 1.0 | 0.737 | 14 | 0 | 5 |
| correctness | 1.0 | 1.0 | 2 | 0 | 0 |
| error_handling | 1.0 | 1.0 | 2 | 0 | 0 |
| logic | None | 0.0 | 0 | 0 | 3 |
| maintainability | 1.0 | 1.0 | 2 | 0 | 0 |
| reliability | 1.0 | 0.667 | 2 | 0 | 1 |
| security | 1.0 | 0.857 | 6 | 0 | 1 |
| testing | 1.0 | 1.0 | 16 | 0 | 0 |

Clean cases with any false positive: 0 of 4.
Issues that no static rule targets (logic, indirect SQL injection): found 0 of 5.

| Case | Expected | Matched | False positives | Verdict |
|---|---|---|---|---|
| C01_sql_fstring | 2 | 2 | 0 | request_changes |
| C02_shell_true | 2 | 2 | 0 | request_changes |
| C03_secret_and_timeout | 3 | 3 | 0 | request_changes |
| C04_bare_except | 2 | 2 | 0 | comment |
| C05_swallowed_exception | 2 | 2 | 0 | comment |
| C06_mutable_default | 2 | 2 | 0 | comment |
| C07_eval | 2 | 2 | 0 | request_changes |
| C08_yaml_load | 2 | 2 | 0 | request_changes |
| C09_verify_false | 2 | 2 | 0 | request_changes |
| C10_none_compare_print | 3 | 3 | 0 | comment |
| C11_off_by_one | 2 | 1 | 0 | comment |
| C12_divide_by_zero | 2 | 1 | 0 | comment |
| C13_wrong_formula | 2 | 1 | 0 | comment |
| C14_file_not_closed | 2 | 1 | 0 | comment |
| C15_clean_refactor_with_test | 0 | 0 | 0 | approve |
| C16_clean_docs_only | 0 | 0 | 0 | approve |
| C17_clean_new_function_with_test | 0 | 0 | 0 | approve |
| C18_clean_docstring_mentions_eval | 0 | 0 | 0 | approve |
| C19_indirect_sql_injection | 2 | 1 | 0 | comment |
| C20_timeout_and_todo | 3 | 3 | 0 | comment |

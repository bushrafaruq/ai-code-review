import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))

from cases import CASES  # noqa: E402
from run_eval import make_diff  # noqa: E402

from reviewer import github  # noqa: E402
from reviewer.cli import main as cli_main  # noqa: E402
from reviewer.diff import parse  # noqa: E402
from reviewer.llm import LLMReviewer  # noqa: E402
from reviewer.models import Finding  # noqa: E402
from reviewer.render import MARKER, markdown  # noqa: E402
from reviewer.workflow import aggregate, review  # noqa: E402

MODIFIED = """diff --git a/app/x.py b/app/x.py
--- a/app/x.py
+++ b/app/x.py
@@ -1,4 +1,5 @@
 import os
-def f(a):
-    return a
+def f(a, b=[]):
+    b.append(a)
+    return b

@@ -10,2 +11,3 @@ def g():
     x = 1
+    y = eval(x)
     return x
"""


def case(cid):
    return next(c for c in CASES if c["id"] == cid)


def test_parse_tracks_new_line_numbers():
    [f] = parse(MODIFIED)
    assert f.path == "app/x.py" and not f.is_new_file
    assert f.added == {2: "def f(a, b=[]):", 3: "    b.append(a)", 4: "    return b", 12: "    y = eval(x)"}
    assert len(f.hunks) == 2


def test_parse_new_and_deleted_files():
    diff = make_diff(case("C07_eval")["files"]) + "diff --git a/old.py b/old.py\n--- a/old.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-x = 1\n"
    files = parse(diff)
    assert [f.path for f in files] == ["app/calc.py"]            # deleted file is not reviewed
    assert files[0].is_new_file and "eval(expression)" in files[0].new_content


def test_line_rules_only_fire_on_added_lines():
    r = review(MODIFIED)
    rules = {(x.rule, x.line) for x in r.findings}
    assert ("PY004", 12) in rules
    assert all(x.line in {2, 3, 4, 12} for x in r.findings)


def test_ast_rules_need_whole_file(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app/x.py").write_text("import os\ndef f(a, b=[]):\n    b.append(a)\n    return b\n\n" + "\n" * 5
                                       + "def g():\n    x = 1\n    y = eval(x)\n    return x\n")
    without = {x.rule for x in review(MODIFIED).findings}
    with_repo = {x.rule for x in review(MODIFIED, repo=tmp_path).findings}
    assert "PY003" not in without and "PY003" in with_repo


def test_eval_in_docstring_is_not_flagged():
    r = review(make_diff(case("C18_clean_docstring_mentions_eval")["files"]))
    assert r.findings == [] and r.verdict == "approve"


def test_secret_rule_skips_test_files():
    diff = make_diff({"tests/test_api.py": ("", 'API_TOKEN = "dummy-token-for-tests"\n')})
    assert not [x for x in review(diff).findings if x.rule == "PY006"]


def test_test_advisor_recommends_cases_and_respects_tests():
    r = review(make_diff(case("C13_wrong_formula")["files"]))
    [rec] = r.tests
    assert rec.function == "apply_discount"
    assert any("ValueError" in c for c in rec.cases)
    clean = review(make_diff(case("C17_clean_new_function_with_test")["files"]))
    assert clean.tests == []


def test_aggregate_dedupes_and_ranks():
    a = Finding("f.py", 3, "low", "security", "LLM", "m", source="llm", confidence=0.9)
    b = Finding("f.py", 3, "high", "security", "PY004", "m")
    c = Finding("f.py", 9, "medium", "logic", "LLM", "m", source="llm", confidence=0.3)   # below confidence floor
    d = Finding("a.py", 1, "info", "maintainability", "PY010", "m")
    out = aggregate([a, b, c, d])
    assert [(x.file, x.line, x.severity) for x in out] == [("f.py", 3, "high"), ("a.py", 1, "info")]


class FakeLLM(LLMReviewer):
    def __init__(self, payload):
        self.payload, self.name, self.provider, self.model = payload, "fake", "fake", "fake"

    def _call(self, user):
        assert "Already reported" in user and "+" in user
        return self.payload


def test_llm_findings_validated_and_unchanged_lines_dropped():
    diff = make_diff(case("C12_divide_by_zero")["files"])
    payload = json.dumps({"findings": [
        {"line": 2, "severity": "medium", "category": "logic", "message": "ZeroDivisionError on empty list",
         "suggestion": "Return 0 or raise a clear error when values is empty", "confidence": 0.9},
        {"line": 40, "severity": "high", "category": "logic", "message": "hallucinated line"}]})
    r = review(diff, llm=FakeLLM(payload))
    assert any(x.source == "llm" and x.line == 2 for x in r.findings)
    llm_trace = next(s for s in r.trace if s["step"] == "llm_review")
    assert llm_trace["dropped_unchanged_line"] == 1 and llm_trace["kept"] == 1


def test_llm_invalid_output_does_not_break_review():
    r = review(make_diff(case("C07_eval")["files"]), llm=FakeLLM("sorry, I cannot do that"))
    assert any(x.rule == "PY004" for x in r.findings)
    assert next(s for s in r.trace if s["step"] == "llm_review")["errors"]


def test_markdown_has_marker_and_tests():
    md = markdown(review(make_diff(case("C03_secret_and_timeout")["files"])))
    assert md.startswith(MARKER) and "Changes requested" in md and "Suggested tests" in md


def test_cli_fail_on(tmp_path, capsys):
    p = tmp_path / "c.diff"
    p.write_text(make_diff(case("C02_shell_true")["files"]))
    assert cli_main(["review", str(p), "--no-llm", "--fail-on", "high"]) == 1
    capsys.readouterr()
    p.write_text(make_diff(case("C17_clean_new_function_with_test")["files"]))
    assert cli_main(["review", str(p), "--no-llm", "--fail-on", "low", "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["verdict"] == "approve"


def test_github_upsert_updates_existing_comment(monkeypatch):
    calls = []

    def fake(method, url, token, body=None):
        calls.append((method, url))
        if method == "GET":
            return [{"id": 7, "body": "hello"}, {"id": 9, "body": f"{MARKER}\nold review"}]
        return {"id": 9}

    monkeypatch.setattr(github, "_req", fake)
    assert github.upsert_comment("me/repo", 3, "new", token="t") == "updated comment 9"
    assert calls[-1][0] == "PATCH" and calls[-1][1].endswith("/issues/comments/9")


def test_api_services():
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient

    from reviewer.api import app
    c = TestClient(app)
    diff = make_diff(case("C01_sql_fstring")["files"])
    assert c.get("/health").json() == {"status": "ok"}
    files = c.post("/diff/parse", json={"diff": diff}).json()["files"]
    assert files[0]["path"] == "app/users.py" and files[0]["added_lines"] == 4
    rules = {f["rule"] for f in c.post("/checks/static", json={"diff": diff}).json()["findings"]}
    assert "PY007" in rules
    recs = c.post("/checks/tests", json={"diff": diff}).json()["recommendations"]
    assert recs[0]["function"] == "find_user"
    r = c.post("/review", json={"diff": diff, "use_llm": False})
    assert r.status_code == 200 and r.json()["verdict"] == "request_changes"
    assert c.post("/review/markdown", json={"diff": MODIFIED, "use_llm": False}).text.startswith(MARKER)
    assert c.post("/review", json={"diff": ""}).status_code == 422

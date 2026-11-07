"""Seeded-defect evaluation set: 20 small pull requests with labelled issues.

Each case is a set of file changes (before -> after) and a list of expected findings, given as
(file, text that appears on the expected line, category). Four cases are clean and measure false
positives. Labels name the line by its text, not its number, so cases stay readable; run_eval.py
resolves them to line numbers.

The cases were written by the author of the static rules, so static-rule recall on them is an
optimistic upper bound. Cases marked `static_blind` contain issues no line or AST rule targets
(logic errors and an indirect SQL injection); they show what the LLM step is for.
"""

CASES = [
    {"id": "C01_sql_fstring", "files": {"app/users.py": ("", '''def find_user(conn, username):
    cur = conn.cursor()
    cur.execute(f"SELECT id, email FROM users WHERE name = '{username}'")
    return cur.fetchone()
''')}, "expect": [("app/users.py", "cur.execute(f", "security"), ("app/users.py", "def find_user", "testing")]},

    {"id": "C02_shell_true", "files": {"ops/backup.py": ("", '''import subprocess


def archive(folder):
    subprocess.run(f"tar -czf backup.tgz {folder}", shell=True, check=True)
''')}, "expect": [("ops/backup.py", "shell=True", "security"), ("ops/backup.py", "def archive", "testing")]},

    {"id": "C03_secret_and_timeout", "files": {"app/rates.py": ("", '''import requests

API_KEY = "demo-key-1234567890abcdef"


def fetch_rates(currency):
    r = requests.get(f"https://api.example.com/rates/{currency}", headers={"Authorization": API_KEY})
    return r.json()
''')}, "expect": [("app/rates.py", "API_KEY = ", "security"), ("app/rates.py", "requests.get", "reliability"),
                  ("app/rates.py", "def fetch_rates", "testing")]},

    {"id": "C04_bare_except", "files": {"app/config.py": ("", '''import json


def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return {}
''')}, "expect": [("app/config.py", "except:", "error_handling"), ("app/config.py", "def load_config", "testing")]},

    {"id": "C05_swallowed_exception", "files": {"app/money.py": ("", '''def parse_amount(text):
    try:
        return float(text.replace(",", ""))
    except ValueError:
        pass
''')}, "expect": [("app/money.py", "except ValueError", "error_handling"), ("app/money.py", "def parse_amount", "testing")]},

    {"id": "C06_mutable_default", "files": {"app/tags.py": ("", '''def add_tag(item, tags=[]):
    tags.append(item)
    return tags
''')}, "expect": [("app/tags.py", "def add_tag", "correctness"), ("app/tags.py", "def add_tag", "testing")]},

    {"id": "C07_eval", "files": {"app/calc.py": ("", '''def calculate(expression: str) -> float:
    return eval(expression)
''')}, "expect": [("app/calc.py", "eval(expression)", "security"), ("app/calc.py", "def calculate", "testing")]},

    {"id": "C08_yaml_load", "files": {"app/settings.py": ("", '''import yaml


def read_settings(path):
    with open(path) as f:
        return yaml.load(f)
''')}, "expect": [("app/settings.py", "yaml.load", "security"), ("app/settings.py", "def read_settings", "testing")]},

    {"id": "C09_verify_false", "files": {"app/health.py": ("", '''import requests


def ping(url):
    return requests.get(url, verify=False, timeout=5).status_code
''')}, "expect": [("app/health.py", "verify=False", "security"), ("app/health.py", "def ping", "testing")]},

    {"id": "C10_none_compare_print", "files": {"app/lists.py": ("", '''def first_or_default(items, default=None):
    if items == None:
        return default
    print("items:", items)
    return items[0] if items else default
''')}, "expect": [("app/lists.py", "items == None", "correctness"), ("app/lists.py", "print(", "maintainability"),
                  ("app/lists.py", "def first_or_default", "testing")]},

    {"id": "C11_off_by_one", "static_blind": True, "files": {"app/window.py": ("", '''def last_n(items, n):
    """Return the last n items."""
    return items[len(items) - n - 1:]
''')}, "expect": [("app/window.py", "return items[", "logic"), ("app/window.py", "def last_n", "testing")]},

    {"id": "C12_divide_by_zero", "static_blind": True, "files": {"app/stats.py": ("", '''def average(values):
    return sum(values) / len(values)
''')}, "expect": [("app/stats.py", "return sum(values)", "logic"), ("app/stats.py", "def average", "testing")]},

    {"id": "C13_wrong_formula", "static_blind": True, "files": {"app/pricing.py": ("", '''def apply_discount(price, percent):
    if percent > 100 or percent < 0:
        raise ValueError("percent must be between 0 and 100")
    return price * percent / 100
''')}, "expect": [("app/pricing.py", "return price * percent", "logic"), ("app/pricing.py", "def apply_discount", "testing")]},

    {"id": "C14_file_not_closed", "static_blind": True, "files": {"app/files.py": ("", '''def count_lines(path):
    f = open(path)
    return len(f.readlines())
''')}, "expect": [("app/files.py", "f = open(path)", "reliability"), ("app/files.py", "def count_lines", "testing")]},

    {"id": "C15_clean_refactor_with_test", "files": {
        "app/text.py": ('''def slugify(text):
    return text.lower().replace(" ", "-")
''', '''import re


def slugify(text: str) -> str:
    """Lower-case, replace runs of non-alphanumerics with single hyphens."""
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
'''),
        "tests/test_text.py": ("", '''from app.text import slugify


def test_slugify_collapses_separators():
    assert slugify("Hello,  World!") == "hello-world"
''')}, "expect": []},

    {"id": "C16_clean_docs_only", "files": {"README.md": ("# Project\n", '''# Project

Run `make test` before opening a pull request.
''')}, "expect": []},

    {"id": "C17_clean_new_function_with_test", "files": {
        "app/mathutil.py": ("", '''def clamp(value: float, low: float, high: float) -> float:
    if low > high:
        raise ValueError("low must not exceed high")
    return max(low, min(value, high))
'''),
        "tests/test_mathutil.py": ("", '''import pytest

from app.mathutil import clamp


def test_clamp():
    assert clamp(5, 0, 3) == 3
    with pytest.raises(ValueError):
        clamp(1, 2, 0)
''')}, "expect": []},

    {"id": "C18_clean_docstring_mentions_eval", "files": {
        "app/secrets.py": ("", '''import os


def get_db_password() -> str:
    """Read the password from the environment; never eval() or hard-code secrets."""
    return os.environ["DB_PASSWORD"]
'''),
        "tests/test_secrets.py": ("", '''from app.secrets import get_db_password


def test_get_db_password(monkeypatch):
    monkeypatch.setenv("DB_PASSWORD", "x")
    assert get_db_password() == "x"
''')}, "expect": []},

    {"id": "C19_indirect_sql_injection", "static_blind": True, "files": {"app/orders.py": ('''def get_order(conn, order_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
    return cur.fetchone()
''', '''def get_order(conn, order_id, status=None):
    cur = conn.cursor()
    sql = "SELECT * FROM orders WHERE id = %s"
    if status:
        sql = sql + " AND status = '" + status + "'"
    cur.execute(sql, (order_id,))
    return cur.fetchone()
''')}, "expect": [("app/orders.py", "sql = sql +", "security"), ("app/orders.py", "def get_order", "testing")]},

    {"id": "C20_timeout_and_todo", "files": {"app/weather.py": ("", '''import requests


def get_weather(city):
    # TODO: add caching
    resp = requests.get("https://api.example.com/weather", params={"q": city})
    resp.raise_for_status()
    return resp.json()
''')}, "expect": [("app/weather.py", "requests.get", "reliability"), ("app/weather.py", "# TODO", "maintainability"),
                  ("app/weather.py", "def get_weather", "testing")]},
]

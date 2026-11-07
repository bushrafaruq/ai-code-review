"""Step 1: parse a unified diff (git diff / GitHub PR diff) into files, hunks and added lines.

Only added or changed lines are reviewed, and every finding must point at one of them, so
comments always land on code the author actually touched.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


@dataclass
class FileDiff:
    path: str
    old_path: str | None
    added: dict[int, str] = field(default_factory=dict)      # new line number -> text
    new_content: str | None = None                          # full new file, when available
    is_new_file: bool = False
    is_deleted: bool = False
    hunks: list[str] = field(default_factory=list)

    @property
    def language(self) -> str:
        return {"py": "python", "js": "javascript", "ts": "typescript", "go": "go", "java": "java"}.get(
            self.path.rsplit(".", 1)[-1], "other")

    @property
    def is_test(self) -> bool:
        name = self.path.rsplit("/", 1)[-1]
        return name.startswith("test_") or name.endswith("_test.py") or "/tests/" in f"/{self.path}"


def parse(diff_text: str) -> list[FileDiff]:
    files: list[FileDiff] = []
    cur: FileDiff | None = None
    new_ln = 0
    hunk_lines: list[str] = []

    def close_hunk():
        if cur is not None and hunk_lines:
            cur.hunks.append("\n".join(hunk_lines))
            hunk_lines.clear()

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            close_hunk()
            m = re.match(r"diff --git a/(.+?) b/(.+)$", line)
            cur = FileDiff(path=m.group(2) if m else line.split()[-1], old_path=m.group(1) if m else None)
            files.append(cur)
            continue
        if line.startswith("--- "):
            if cur is None:          # diff without "diff --git" header
                cur = FileDiff(path="", old_path=line[4:].removeprefix("a/"))
                files.append(cur)
            if line.strip() == "--- /dev/null":
                cur.is_new_file = True
            continue
        if line.startswith("+++ ") and cur is not None:
            target = line[4:].strip()
            if target == "/dev/null":
                cur.is_deleted = True
            else:
                cur.path = target.removeprefix("b/")
            continue
        m = HUNK.match(line)
        if m and cur is not None:
            close_hunk()
            new_ln = int(m.group(3))
            hunk_lines.append(line)
            continue
        if cur is None or not hunk_lines:
            continue
        hunk_lines.append(line)
        if line.startswith("+"):
            cur.added[new_ln] = line[1:]
            new_ln += 1
        elif line.startswith("-"):
            pass
        elif not line.startswith("\\"):
            new_ln += 1
    close_hunk()
    for f in files:
        if f.is_new_file:
            f.new_content = "\n".join(f.added[k] for k in sorted(f.added))
    return [f for f in files if not f.is_deleted]

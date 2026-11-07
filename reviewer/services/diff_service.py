from __future__ import annotations

from fastapi import APIRouter

from ..diff import parse
from .schemas import DiffRequest

router = APIRouter(prefix="/diff", tags=["1. diff"])


@router.post("/parse")
def parse_diff(req: DiffRequest) -> dict:
    files = parse(req.diff)
    return {"files": [{"path": f.path, "language": f.language, "is_new_file": f.is_new_file,
                       "is_test": f.is_test, "added_lines": len(f.added), "hunks": len(f.hunks)}
                      for f in files]}

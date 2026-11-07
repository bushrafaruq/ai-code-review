from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter

from ..diff import parse
from ..tests_advisor import recommend
from ..workflow import file_contents
from .schemas import DiffRequest

router = APIRouter(prefix="/checks", tags=["4. test recommendations"])


@router.post("/tests")
def test_recommendations(req: DiffRequest) -> dict:
    files = parse(req.diff)
    recs, _ = recommend(files, file_contents(files, None))
    return {"recommendations": [asdict(r) for r in recs]}

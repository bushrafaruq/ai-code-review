from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter

from .. import static
from ..diff import parse
from ..workflow import file_contents
from .schemas import DiffRequest

router = APIRouter(prefix="/checks", tags=["2. static checks"])


@router.post("/static")
def static_checks(req: DiffRequest) -> dict:
    files = parse(req.diff)
    contents = file_contents(files, None)
    findings = [f for fd in files for f in static.run(fd, contents[fd.path])]
    return {"findings": [asdict(f) for f in findings]}

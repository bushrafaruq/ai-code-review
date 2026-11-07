from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from ..render import markdown
from ..workflow import review
from .schemas import ReviewRequest

router = APIRouter(tags=["5. full review"])


def _llm(use: bool):
    if not use:
        return None
    try:
        from ..llm import LLMReviewer
        return LLMReviewer()
    except RuntimeError:          # no API key configured: static checks and test advice only
        return None


@router.post("/review")
def review_json(req: ReviewRequest) -> dict:
    return review(req.diff, llm=_llm(req.use_llm)).to_dict()


@router.post("/review/markdown", response_class=PlainTextResponse)
def review_markdown(req: ReviewRequest) -> str:
    return markdown(review(req.diff, llm=_llm(req.use_llm)))

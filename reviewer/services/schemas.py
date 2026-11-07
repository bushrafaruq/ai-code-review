from __future__ import annotations

from pydantic import BaseModel, Field


class DiffRequest(BaseModel):
    diff: str = Field(min_length=1, max_length=500_000, description="unified diff, e.g. from `git diff`")


class ReviewRequest(DiffRequest):
    use_llm: bool = Field(default=True, description="run the LLM step if an API key is configured")

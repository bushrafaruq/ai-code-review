"""FastAPI services, one module per step of the review workflow.

    diff_service     POST /diff/parse            step 1: parse a diff into files and added lines
    static_service   POST /checks/static         step 2: deterministic rule checks
    tests_service    POST /checks/tests          step 4: test recommendations
    review_service   POST /review, /review/markdown   the full workflow (steps 1-5, LLM if configured)

Each module exposes an APIRouter; reviewer/api.py mounts them. A service can be called on its own
(for example by another pipeline that only wants the static checks) or the full review can be used.
"""

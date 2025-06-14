from fastapi import APIRouter
from app.services.stack_watcher import sync_stack
from pydantic import BaseModel
from typing import Dict

stack_router = APIRouter(prefix="/v1/stack", tags=["Stack"])


class StackSyncResponse(BaseModel):
    status: Dict[str, str]


@stack_router.post(
    "/sync",
    response_model=StackSyncResponse,
    summary="Sync Swarm Stack from YAML",
    description=(
        "Parses the `fountainai-stack.yml` file, reconciles the declared services with "
        "the current Swarm state, and creates any missing services. This enables "
        "declarative, file-based infrastructure orchestration via API."
    )
)
def sync_stack_from_file():
    return {"status": sync_stack()}

import os

if os.getenv("RUN_TESTS") == "1":
    import sys
    import pytest
    sys.exit(pytest.main(["tests"]))  # ensures correct exit code

# fallback: normal app start
from fastapi import FastAPI
from app.routers.orchestrator import orchestrator_router

app = FastAPI()
app.include_router(orchestrator_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.entrypoint:app", host="0.0.0.0", port=8000, reload=True)

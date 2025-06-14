# app/main.py

from fastapi import FastAPI
from app.routers.orchestrator import orchestrator_router
from app.routers.stack import stack_router  # ✅ ADD THIS

app = FastAPI(title="FountainAI Swarm Orchestrator")

app.include_router(orchestrator_router)
app.include_router(stack_router)  # ✅ REGISTER NEW ROUTE

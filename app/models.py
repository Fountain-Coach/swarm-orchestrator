from typing import Dict, List, Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Column, JSON, create_engine

# Database URL
DATABASE_URL = "sqlite:///./orchestrator.db"
engine = create_engine(DATABASE_URL, echo=False)

class Service(SQLModel, table=True):
    name: str = Field(primary_key=True)
    image: str
    status: str
    ports: Dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON))
    secrets: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    configs: List[Dict[str, str]] = Field(default_factory=list, sa_column=Column(JSON))
    env: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))


class ClientStatus(SQLModel, table=True):
    service: str = Field(primary_key=True)
    last_generated_at: datetime
    checksum: str
    status: str
    error: Optional[str] = None

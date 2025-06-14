from typing import Optional, List, Dict
from pydantic import BaseModel, RootModel


class ServiceSpec(BaseModel):
    image: str
    ports: Optional[Dict[str, int]] = None
    secrets: Optional[List[str]] = None
    configs: Optional[List[Dict[str, str]]] = None


class ServiceDetail(BaseModel):
    name: str
    status: str
    ports: Optional[Dict[str, int]] = None
    secrets: Optional[List[str]] = None
    configs: Optional[List[Dict[str, str]]] = None


class ServiceListResponse(BaseModel):
    services: List[ServiceDetail]
    total: int
    limit: int
    offset: int


class DeployRequest(BaseModel):
    services: List[str]


class DeployResponse(BaseModel):
    status: str
    message: str


class BatchDeployResponse(RootModel[Dict[str, DeployResponse]]):
    pass


class ConfigDetail(BaseModel):
    env: Dict[str, str]
    ports: Dict[str, int]


class ConfigPatch(BaseModel):
    env: Optional[Dict[str, str]] = None
    ports: Optional[Dict[str, int]] = None


class ErrorResponse(BaseModel):
    code: int
    message: str

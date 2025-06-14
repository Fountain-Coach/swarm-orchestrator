from fastapi import APIRouter, HTTPException
from app.schemas import (
    ServiceSpec,
    ServiceDetail,
    ServiceListResponse,
    DeployRequest,
    DeployResponse,
    BatchDeployResponse,
    ConfigDetail,
    ConfigPatch,
)
import docker
import traceback

orchestrator_router = APIRouter(prefix="/v1", tags=["Orchestrator"])
docker_client = docker.from_env()


@orchestrator_router.get(
    "/health",
    response_model=dict,
    summary="Health Check",
    description="Returns service availability status and uptime indication."
)
def health_check():
    return {"status": "ok", "uptime": "unknown"}


@orchestrator_router.get(
    "/services",
    response_model=ServiceListResponse,
    summary="List Swarm Services",
    description="Lists all Docker Swarm services with optional status filtering and pagination."
)
def list_services(limit: int = 50, offset: int = 0, status: str = None):
    services = docker_client.services.list()
    result = []
    for s in services:
        ports = {}
        endpoint = s.attrs.get("Endpoint", {})
        if "Ports" in endpoint:
            for p in endpoint["Ports"]:
                ports[str(p["PublishedPort"])] = p["TargetPort"]
        result.append(ServiceDetail(
            name=s.name,
            status=s.attrs.get("UpdateStatus", {}).get("State", "unknown"),
            ports=ports
        ))
    return ServiceListResponse(
        services=result[offset:offset + limit],
        total=len(result),
        limit=limit,
        offset=offset
    )


@orchestrator_router.post(
    "/services",
    response_model=ServiceDetail,
    status_code=201,
    summary="Register New Service",
    description="Creates a new Docker Swarm service based on image, ports, and optional environment variables."
)
def register_service(spec: ServiceSpec):
    try:
        endpoint_spec = docker.types.EndpointSpec(
            ports={int(pub): int(tgt) for pub, tgt in (spec.ports or {}).items()}
        )
        service = docker_client.services.create(
            image=spec.image,
            name=spec.image.replace("/", "_").replace(":", "_"),
            endpoint_spec=endpoint_spec,
            env=spec.secrets or []
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ServiceDetail(
        name=service.name,
        status="running",
        ports=spec.ports or {}
    )


@orchestrator_router.get(
    "/services/{service}",
    response_model=ServiceDetail,
    summary="Get Service Info",
    description="Returns the current status and published ports of a named Swarm service."
)
def get_service(service: str):
    try:
        s = docker_client.services.get(service)
        endpoint = s.attrs.get("Endpoint", {})
        ports = {}
        if "Ports" in endpoint:
            for p in endpoint["Ports"]:
                ports[str(p["PublishedPort"])] = p["TargetPort"]
        return ServiceDetail(
            name=s.name,
            status=s.attrs.get("UpdateStatus", {}).get("State", "unknown"),
            ports=ports
        )
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Service not found")


@orchestrator_router.delete(
    "/services/{service}",
    status_code=204,
    summary="Remove Service",
    description="Deletes a Swarm service by name. No-op if service is missing."
)
def remove_service(service: str):
    try:
        s = docker_client.services.get(service)
        s.remove()
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Service not found")
    return


@orchestrator_router.post(
    "/services/{service}/deploy",
    response_model=DeployResponse,
    summary="Redeploy Service",
    description="Triggers a forced update (rolling restart) of a running service."
)
def deploy_service(service: str):
    try:
        s = docker_client.services.get(service)
        s.update(force_update=True)
        return DeployResponse(status="ok", message=f"{service} updated")
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Service not found")


@orchestrator_router.post(
    "/deploy",
    response_model=BatchDeployResponse,
    summary="Batch Redeploy Services",
    description="Forces an update for multiple listed services. Gracefully skips any missing ones."
)
def batch_deploy(request: DeployRequest):
    result = {}
    for service in request.services:
        try:
            s = docker_client.services.get(service)
            s.update(force_update=True)
            result[service] = DeployResponse(status="ok", message="updated")
        except docker.errors.NotFound:
            result[service] = DeployResponse(status="failed", message="not found")
    return result


@orchestrator_router.get(
    "/services/{service}/config",
    response_model=ConfigDetail,
    summary="Get Service Configuration",
    description="Returns current environment variables and port mappings of a Swarm service."
)
def get_config(service: str):
    try:
        s = docker_client.services.get(service)
        task_template = s.attrs["Spec"]["TaskTemplate"]
        env = {}
        for e in task_template.get("ContainerSpec", {}).get("Env", []):
            if "=" in e:
                k, v = e.split("=", 1)
                env[k] = v
        ports = {}
        for p in s.attrs.get("Endpoint", {}).get("Ports", []):
            ports[str(p["PublishedPort"])] = p["TargetPort"]
        return ConfigDetail(env=env, ports=ports)
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Service not found")


@orchestrator_router.patch(
    "/services/{service}/config",
    response_model=ConfigDetail,
    summary="Update Service Configuration",
    description="Patches the environment variables and/or port definitions of a running Swarm service."
)
def update_config(service: str, patch: ConfigPatch):
    try:
        s = docker_client.services.get(service)
        spec = s.attrs["Spec"]
        container_spec = spec["TaskTemplate"]["ContainerSpec"]
        image = container_spec["Image"]
        existing_env = container_spec.get("Env", [])
        env_dict = {e.split("=", 1)[0]: e.split("=", 1)[1] for e in existing_env if "=" in e}
        env_dict.update(patch.env or {})
        new_env = [f"{k}={v}" for k, v in env_dict.items()]
        endpoint_spec = None
        if patch.ports:
            ports_dict = {int(pub): int(tgt) for pub, tgt in patch.ports.items()}
            endpoint_spec = docker.types.EndpointSpec(ports=ports_dict)
        s.update(image=image, env=new_env, endpoint_spec=endpoint_spec)
        return get_config(service)
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Service not found")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@orchestrator_router.get(
    "/services/{service}/logs",
    response_model=str,
    summary="Fetch Service Logs",
    description="Returns recent stdout/stderr logs from the Swarm service (default tail=100)."
)
def fetch_logs(service: str, tail: int = 100):
    try:
        logs = docker_client.api.logs(service, tail=tail, stdout=True, stderr=True)
        return logs.decode()
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Service not found")


@orchestrator_router.post(
    "/services/{service}/rollback",
    response_model=DeployResponse,
    summary="Rollback Service (Not Implemented)",
    description="Reserved endpoint for future rollback logic. Currently responds with 'not supported'."
)
def rollback_service(service: str):
    try:
        return DeployResponse(status="failed", message="Rollback not supported via SDK")
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Service not found")

# app/services/stack_watcher.py

import yaml
import os
from docker import from_env
from docker.types import EndpointSpec

STACK_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'fountainai-stack.yml')
docker_client = from_env()

def load_stack_yaml():
    with open(STACK_FILE, 'r') as f:
        return yaml.safe_load(f)

def sync_stack():
    stack = load_stack_yaml()
    services = stack.get("services", {})
    live = {s.name for s in docker_client.services.list()}
    result = {}

    for name, conf in services.items():
        image = conf.get("image")
        ports = {}
        for p in conf.get("ports", []):
            try:
                ports[int(p["published"])] = int(p["target"])
            except: pass

        if name not in live:
            try:
                docker_client.services.create(
                    name=name,
                    image=image,
                    endpoint_spec=EndpointSpec(ports=ports),
                    env=conf.get("environment", [])
                )
                result[name] = "deployed"
            except Exception as e:
                result[name] = f"error: {e}"
        else:
            result[name] = "already running"

    return result

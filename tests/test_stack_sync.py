import os
import shutil

STACK_YAML = """
version: "3.9"
services:
  nginx_stack_test:
    image: nginx:alpine
    ports:
      - target: 80
        published: 8089
        protocol: tcp
        mode: host
"""

def write_temp_stack_file():
    root = os.path.dirname(__file__)
    stack_path = os.path.abspath(os.path.join(root, "..", "fountainai-stack.yml"))
    backup_path = stack_path + ".bak"

    if os.path.exists(stack_path):
        shutil.copy(stack_path, backup_path)

    with open(stack_path, "w") as f:
        f.write(STACK_YAML)

    return stack_path, backup_path

def restore_stack_file(stack_path, backup_path):
    if os.path.exists(stack_path):
        os.remove(stack_path)
    if os.path.exists(backup_path):
        shutil.move(backup_path, stack_path)


def test_stack_sync_deploys_service(client):
    stack_path, backup_path = write_temp_stack_file()
    try:
        response = client.post("/v1/stack/sync")
        assert response.status_code == 200
        body = response.json()["status"]
        assert "nginx_stack_test" in body
        assert body["nginx_stack_test"] in ["deployed", "already running"]
    finally:
        restore_stack_file(stack_path, backup_path)


def test_stack_sync_idempotent(client):
    stack_path, backup_path = write_temp_stack_file()
    try:
        # 🔁 Run twice to trigger idempotency
        client.post("/v1/stack/sync")  # first
        response = client.post("/v1/stack/sync")  # second
        assert response.status_code == 200
        body = response.json()["status"]
        assert "nginx_stack_test" in body, "Expected 'nginx_stack_test' to exist in sync status"
        assert body["nginx_stack_test"] in ["already running", "deployed"]
    finally:
        restore_stack_file(stack_path, backup_path)


def test_stack_sync_removes_test_service(client):
    response = client.delete("/v1/services/nginx_stack_test")
    assert response.status_code in [204, 404]

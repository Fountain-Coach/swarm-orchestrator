import time


def test_health_check(client):
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_service(client):
    payload = {
        "image": "nginx:alpine",
        "ports": {"8085": 80}
    }
    response = client.post("/v1/services", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["name"].startswith("nginx")
    assert body["status"] == "running"
    assert "8085" in body["ports"]


def test_get_service_existing(client):
    service_name = "nginx_alpine"
    response = client.get(f"/v1/services/{service_name}")
    assert response.status_code == 200
    assert response.json()["status"] in ["running", "unknown"]


def test_list_services(client):
    response = client.get("/v1/services")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert isinstance(data["services"], list)


def test_deploy_service(client):
    service_name = "nginx_alpine"
    response = client.post(f"/v1/services/{service_name}/deploy")
    assert response.status_code == 200
    assert "updated" in response.json()["message"]


def test_batch_deploy(client):
    response = client.post("/v1/deploy", json={"services": ["nginx_alpine", "nonexistent_service"]})
    assert response.status_code == 200
    result = response.json()
    assert result["nginx_alpine"]["status"] == "ok"
    assert result["nonexistent_service"]["status"] == "not found"


def test_get_config(client):
    service_name = "nginx_alpine"
    response = client.get(f"/v1/services/{service_name}/config")
    assert response.status_code == 200
    assert "env" in response.json()
    assert "ports" in response.json()


def test_patch_config(client):
    service_name = "nginx_alpine"
    response = client.patch(f"/v1/services/{service_name}/config", json={
        "env": {"TEST_VAR": "1234"},
        "ports": {"8086": 80}
    })
    assert response.status_code == 200
    config = response.json()
    assert config["env"].get("TEST_VAR") == "1234"
    assert config["ports"].get("8086") == 80


def test_logs(client):
    service_name = "nginx_alpine"
    time.sleep(2)
    response = client.get(f"/v1/services/{service_name}/logs?tail=10")
    assert response.status_code in [200, 404]


def test_rollback(client):
    service_name = "nginx_alpine"
    response = client.post(f"/v1/services/{service_name}/rollback")
    assert response.status_code == 200
    assert "not supported" in response.json()["message"]


def test_get_service_not_found(client):
    response = client.get("/v1/services/nonexistent")
    assert response.status_code == 404


def test_remove_service(client):
    service_name = "nginx_alpine"
    response = client.delete(f"/v1/services/{service_name}")
    assert response.status_code == 204

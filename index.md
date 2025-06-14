---
title: Swarm Orchestrator
description: Lightweight declarative container orchestrator for the FountainAI system.
image: https://raw.githubusercontent.com/Fountain-Coach/swarm-orchestrator/main/assets/logo/swarm-logo.png
---

![Swarm Orchestrator Logo](https://raw.githubusercontent.com/Fountain-Coach/swarm-orchestrator/main/assets/logo/swarm-logo.png#right-align)


# Swarm Orchestrator

The **Swarm Orchestrator** is a lightweight control service designed to manage and deploy container-based services within a Docker Swarm setup. It serves as the execution backend in the [FountainAI](https://github.com/Fountain-Coach) ecosystem, dynamically interpreting YAML-based deployment definitions and translating them into real-time, actionable service updates.

This orchestrator provides developers with a clean HTTP API to:
- Deploy, inspect, and remove container services.
- Synchronize the running stack with a versioned `fountainai-stack.yml` file.
- Roll out or roll back updates with intent-aware safety.

---

## 🚀 Getting Started

1. **Clone this repository**:
   ```bash
   git clone https://github.com/Fountain-Coach/swarm-orchestrator.git
   cd swarm-orchestrator
   ```

2. **Edit the stack definition**:
   Customize `fountainai-stack.yml` to define your services declaratively.

3. **Start the orchestrator** (locally or via container):
   ```bash
   docker build -t swarm-orchestrator .
   docker run -p 8000:8000 --name swarm swarm-orchestrator
   ```

4. **Ping the health endpoint**:
   ```
   curl http://localhost:8000/v1/health
   ```

---

## 🛠 API Summary

| Endpoint                    | Method | Description                         |
|----------------------------|--------|-------------------------------------|
| `/v1/health`               | GET    | Check service health                |
| `/v1/services`             | GET    | List all services                   |
| `/v1/services/{name}`      | GET    | Get details of a service            |
| `/v1/services`             | POST   | Register and deploy a new service   |
| `/v1/services/{name}`      | DELETE | Remove a service                    |
| `/v1/services/{name}/logs` | GET    | Fetch logs for a service            |
| `/v1/stack/sync`           | POST   | Sync actual Docker state to YAML    |

---

## 🧠 About FountainAI

The orchestrator is part of a larger composable system of tools for semantically aware service management and AI-driven planning. Learn more at [Fountain-Coach](https://github.com/Fountain-Coach).

---

## 🐝 Logo

Logo: a black-and-white Teatro-style illustration of a minimalist flocking swarm of three birds — simple, abstract, and expressive.

---

© 2025 Fountain-Coach. All rights reserved.

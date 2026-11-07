# Future Architectures & Blueprints

This directory archives experimental and forward-looking blueprints that are not part of the active production runtime.

## Contents

- **`deployment/docker/`**: Individual Dockerfiles for running each ARGUS agent (`decision`, `detector`, `knowledge`, `orchestrator`, `risk`, `streaming`) as a standalone containerized microservice.
- **`deployment/compose/`**: Multi-container Docker Compose file (`docker-compose.yml`) orchestrating the distributed microservice topology with Apache Kafka, Zookeeper, and Redis.

## Architecture Context

Per **[ADR 0001: Modular Monolith Architecture](file:///home/bhumi/GitHub/ARGUS/docs/adr/0001-modular-monolith.md)**:
- ARGUS's authoritative production runtime is a **Modular Monolith** running within a single container (`Dockerfile` at repository root).
- The distributed multi-container setup is preserved here as a future scaling blueprint for enterprise multi-node deployments requiring horizontal agent distribution.

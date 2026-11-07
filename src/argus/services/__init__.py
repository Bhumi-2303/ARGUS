"""ARGUS microservice implementations.

DEPRECATION NOTE:
Per ADR 0001 (docs/adr/0001-modular-monolith.md), ARGUS operates as an in-process
modular monolith under `argus.api.main` and `argus.orchestrator.pipeline`.
The standalone microservices in this package are legacy implementations preserved
for isolated testing and future distributed scale-out reference.
"""

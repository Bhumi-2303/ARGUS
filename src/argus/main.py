"""ARGUS — Autonomous Risk-aware Grid Understanding & Security.

Main entry point for the ARGUS platform.
Use `argus` CLI command or `python -m argus.main` to start.
"""
import argparse
import sys


def main():
    """ARGUS CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ARGUS — Autonomous Risk-aware Grid Understanding & Security"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand: start a specific service
    start_parser = subparsers.add_parser("start", help="Start an ARGUS service")
    start_parser.add_argument(
        "service",
        choices=["detector", "decision-agent", "risk-agent", "knowledge-agent", "orchestrator", "consumer"],
        help="Service to start",
    )
    start_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    start_parser.add_argument("--port", type=int, default=None, help="Port to bind to")

    # Subcommand: version
    subparsers.add_parser("version", help="Print ARGUS version")

    args = parser.parse_args()

    if args.command == "version":
        from argus import __version__
        print(f"ARGUS v{__version__}")
        return

    if args.command == "start":
        _start_service(args.service, args.host, args.port)
        return

    parser.print_help()
    sys.exit(1)


SERVICE_MAP = {
    "detector": ("argus.services.detector.main:app", 8000),
    "decision-agent": ("argus.services.decision_agent.main:app", 8001),
    "risk-agent": ("argus.services.risk_agent.main:app", 8002),
    "knowledge-agent": ("argus.services.knowledge_agent.main:app", 8003),
    "orchestrator": ("argus.services.orchestrator.main:app", 8004),
}


def _start_service(service: str, host: str, port: int | None) -> None:
    """Start a specific ARGUS microservice via uvicorn."""
    if service == "consumer":
        from argus.services.streaming.stream_consumer import main as consumer_main
        consumer_main()
        return

    import uvicorn
    app_path, default_port = SERVICE_MAP[service]
    uvicorn.run(app_path, host=host, port=port or default_port)


if __name__ == "__main__":
    main()

"""Command-line entry point for the endpoint prototype."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .discovery import DiscoveryResponder
from .model import DEFAULT_DISCOVERY_PORT, HostConfig
from .server import EndpointServer


def load_config(path: Path) -> HostConfig:
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise ValueError("endpoint configuration must contain a JSON object")
    return HostConfig.from_dict(raw)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Run a PlayBook Surface endpoint")
    result.add_argument("--config", type=Path, required=True, help="Path to local endpoint JSON")
    result.add_argument("--bind", default="0.0.0.0", help="Control/discovery bind address")
    result.add_argument("--discovery-port", type=int, default=DEFAULT_DISCOVERY_PORT)
    return result


def main() -> int:
    args = parser().parse_args()
    config = load_config(args.config)
    discovery = DiscoveryResponder(config.endpoint, args.bind, args.discovery_port)
    server = EndpointServer((args.bind, config.endpoint.control_port), config)
    discovery.start()
    print(f"PlayBook Surface endpoint {config.endpoint.name!r} listening on {args.bind}:{config.endpoint.control_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
        discovery.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


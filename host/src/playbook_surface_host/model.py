"""Validated endpoint, deck, and action configuration models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PROTOCOL_VERSION = 1
DISCOVERY_REQUEST = b"PBSURFACE_DISCOVER/1"
DEFAULT_CONTROL_PORT = 47880
DEFAULT_DISCOVERY_PORT = 47881
ALLOWED_CAPABILITIES = frozenset({"actions", "deck", "display", "input", "audio", "camera", "microphone"})


class ConfigError(ValueError):
    """Raised when endpoint configuration violates the public contract."""


def _required_text(value: Any, field: str, *, maximum: int = 128) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{field} must be a non-empty string")
    result = value.strip()
    if len(result) > maximum:
        raise ConfigError(f"{field} is longer than {maximum} characters")
    return result


@dataclass(frozen=True)
class Endpoint:
    endpoint_id: str
    name: str
    control_port: int
    capabilities: tuple[str, ...]

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Endpoint":
        endpoint_id = _required_text(raw.get("id"), "endpoint.id")
        name = _required_text(raw.get("name"), "endpoint.name", maximum=64)
        port = raw.get("control_port", DEFAULT_CONTROL_PORT)
        if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
            raise ConfigError("endpoint.control_port must be an integer from 1 to 65535")
        raw_capabilities = raw.get("capabilities", [])
        if not isinstance(raw_capabilities, list) or not all(isinstance(item, str) for item in raw_capabilities):
            raise ConfigError("endpoint.capabilities must be a list of strings")
        capabilities = tuple(sorted(set(raw_capabilities)))
        unknown = set(capabilities) - ALLOWED_CAPABILITIES
        if unknown:
            raise ConfigError(f"unsupported endpoint capabilities: {', '.join(sorted(unknown))}")
        return cls(endpoint_id, name, port, capabilities)

    def discovery_payload(self) -> dict[str, Any]:
        return {
            "schema": "playbook-surface.discovery/v1",
            "protocol": PROTOCOL_VERSION,
            "id": self.endpoint_id,
            "name": self.name,
            "control_port": self.control_port,
            "capabilities": list(self.capabilities),
        }


@dataclass(frozen=True)
class Action:
    action_id: str
    label: str
    command: tuple[str, ...]
    cwd: str | None = None

    @classmethod
    def from_pair(cls, action_id: str, raw: Any) -> "Action":
        safe_id = _required_text(action_id, "action id", maximum=64)
        if not all(character.isalnum() or character in "-_" for character in safe_id):
            raise ConfigError(f"unsafe action id: {safe_id!r}")
        if not isinstance(raw, dict):
            raise ConfigError(f"action {safe_id} must be an object")
        label = _required_text(raw.get("label", safe_id), f"actions.{safe_id}.label", maximum=64)
        command = raw.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
            raise ConfigError(f"actions.{safe_id}.command must be a non-empty argument array")
        cwd = raw.get("cwd")
        if cwd is not None and (not isinstance(cwd, str) or not cwd.strip()):
            raise ConfigError(f"actions.{safe_id}.cwd must be a non-empty string when present")
        return cls(safe_id, label, tuple(command), cwd.strip() if isinstance(cwd, str) else None)


@dataclass(frozen=True)
class HostConfig:
    endpoint: Endpoint
    auth_token: str
    actions: dict[str, Action]
    deck: dict[str, Any]

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "HostConfig":
        if raw.get("schema") != "playbook-surface.endpoint/v1":
            raise ConfigError("unsupported or missing endpoint configuration schema")
        endpoint_raw = raw.get("endpoint")
        if not isinstance(endpoint_raw, dict):
            raise ConfigError("endpoint must be an object")
        token = _required_text(raw.get("auth_token"), "auth_token", maximum=1024)
        if len(token) < 20:
            raise ConfigError("auth_token must contain at least 20 characters")
        actions_raw = raw.get("actions", {})
        if not isinstance(actions_raw, dict):
            raise ConfigError("actions must be an object")
        actions = {key: Action.from_pair(key, value) for key, value in actions_raw.items()}
        deck = raw.get("deck", {})
        if not isinstance(deck, dict):
            raise ConfigError("deck must be an object")
        return cls(Endpoint.from_dict(endpoint_raw), token, actions, deck)


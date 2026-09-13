from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "host" / "src"))

from playbook_surface_host.actions import ActionExecutor, UnknownAction
from playbook_surface_host.discovery import response_for
from playbook_surface_host.model import Action, ConfigError, DISCOVERY_REQUEST, Endpoint, HostConfig


class ModelTests(unittest.TestCase):
    def test_discovery_response_contains_no_token(self) -> None:
        endpoint = Endpoint.from_dict({"id": "pc-1", "name": "PC", "control_port": 47880, "capabilities": ["deck", "actions"]})
        response = response_for(DISCOVERY_REQUEST, endpoint)
        self.assertIsNotNone(response)
        payload = json.loads(response)
        self.assertEqual(payload["schema"], "playbook-surface.discovery/v1")
        self.assertEqual(payload["capabilities"], ["actions", "deck"])
        self.assertNotIn("token", payload)

    def test_unknown_discovery_request_is_ignored(self) -> None:
        endpoint = Endpoint.from_dict({"id": "pc-1", "name": "PC"})
        self.assertIsNone(response_for(b"something else", endpoint))

    def test_configuration_requires_long_token(self) -> None:
        with self.assertRaises(ConfigError):
            HostConfig.from_dict({
                "schema": "playbook-surface.endpoint/v1",
                "endpoint": {"id": "pc-1", "name": "PC"},
                "auth_token": "short",
            })

    def test_action_requires_argument_array(self) -> None:
        with self.assertRaises(ConfigError):
            Action.from_pair("unsafe", {"command": "calc.exe & other.exe"})


class ActionTests(unittest.TestCase):
    @patch("playbook_surface_host.actions.subprocess.Popen")
    def test_executor_disables_shell(self, popen: Mock) -> None:
        popen.return_value.pid = 42
        action = Action.from_pair("notes", {"label": "Notes", "command": ["notepad.exe", "notes.txt"]})
        result = ActionExecutor({"notes": action}).run("notes")
        self.assertEqual(result.pid, 42)
        self.assertEqual(popen.call_args.args[0], ["notepad.exe", "notes.txt"])
        self.assertFalse(popen.call_args.kwargs["shell"])

    def test_unknown_action_fails_closed(self) -> None:
        with self.assertRaises(UnknownAction):
            ActionExecutor({}).run("not-configured")


if __name__ == "__main__":
    unittest.main()

